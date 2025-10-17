---
ce_updated: true
context_sync:
  ce_updated: true
  last_sync: '2025-10-17T10:44:01.067113+00:00'
  serena_updated: false
description: 'Extract drift analysis logic from ce update-context into new ce analyze-context
  command.

  Enable fast drift checking (2-3s) without full sync overhead (~10-15s).

  Support CI/CD integration with exit codes and JSON output.

  Add smart caching to avoid redundant analysis when running update-context after
  analyze-context.

  '
executed_at: 2025-10-17 00:00:00+00:00
executed_by: claude-code
issue: BLA-31
issue_url: https://linear.app/blaise78/issue/BLA-31/prp-17-extract-drift-analysis-into-separate-command
last_sync: 2025-10-17 00:00:00+00:00
project: Context Engineering
prp_id: 17
serena_updated: true
status: executed
title: Extract Drift Analysis into Separate Command
updated: '2025-10-17T10:44:01.067295+00:00'
updated_by: update-context-command
---

# Extract Drift Analysis into Separate Command

## Feature

Extract drift analysis logic from `ce update-context` into new `ce analyze-context` command for fast drift checking without full sync overhead.

**Command Name**: `analyze-context` (US spelling, primary) with `analyse-context` alias (UK spelling)

**Current State**: `ce update-context` does everything (PRP metadata updates + drift analysis + remediation)
- Heavy operation (~10-15s)
- Can't check drift quickly
- Drift analysis coupled with metadata updates

**Target State**: Two focused commands
- `ce analyze-context`: Fast drift check (scan → detect → report) (~2-3s)
- `ce update-context`: Full sync with smart caching (analyze + metadata + remediation)

## Context

### Problem

**Use Case 1 - Quick Drift Check**: Developer wants to check drift score before committing
```bash
# Current: Must run full sync (10-15s)
ce update-context

# Desired: Fast analysis only (2-3s)
ce analyze-context
```

**Use Case 2 - CI/CD Integration**: Pre-commit hook needs drift score
```bash
# Current: Heavy operation blocks commit
ce update-context

# Desired: Lightweight check with exit codes
ce analyze-context --json
exit $?  # 0=healthy, 1=warning, 2=critical
```

**Use Case 3 - Repeated Checks**: Running `update-context` multiple times wastes cycles
```bash
# Current: Re-analyzes every time
ce update-context  # Analyzes drift
ce update-context --remediate  # Re-analyzes same drift (wasteful)

# Desired: Cache optimization
ce analyze-context  # Analyzes once
ce update-context  # Reuses cached analysis (< 5 min)
```

### Existing Infrastructure

**PRP-15.2**: Drift detection functions exist
- `verify_codebase_matches_examples()` - pattern conformance
- `detect_missing_examples_for_prps()` - documentation gaps
- `generate_drift_report()` - report generation

**PRP-15.3**: Remediation workflow exists
- `remediate_drift_workflow()` - fix application
- Separate from analysis logic

**Current Architecture** (`update_context.py:sync_context()`):
```python
def sync_context(target_prp: Optional[str] = None) -> Dict:
    # 1. Update PRP metadata (10s)
    for prp in prps:
        update_metadata(prp)

    # 2. Drift analysis (3s)
    if not target_prp:
        drift = verify_codebase_matches_examples()
        missing = detect_missing_examples_for_prps()
        report = generate_drift_report(drift, missing)

    return result
```

**Problem**: Analysis always runs, even if unchanged codebase

## Implementation References

### Existing Functions to Extract (update_context.py)

**Drift Detection Functions** (already exist, reuse as-is):
- `verify_codebase_matches_examples()` - Lines 1042-1098
  - Scans tools/ce/ for pattern violations
  - Returns violations list + drift score
  - Uses pattern_detectors.check_file_for_violations()

- `detect_missing_examples_for_prps()` - Lines 1101-1149
  - Checks executed PRPs for missing examples
  - Returns list of PRPs needing documentation
  - Uses pattern_detectors.check_prp_for_missing_examples()

- `generate_drift_report()` - Lines 1152-1269
  - Creates formatted Markdown report
  - Groups violations by category
  - Includes troubleshooting guidance

**Current Drift Detection Call Site** (sync_context() - Lines 1357-1380):
```python
# Drift detection (universal sync only)
if not target_prp:
    logger.info("Running drift detection...")
    drift_result = verify_codebase_matches_examples()
    missing_examples = detect_missing_examples_for_prps()

    if drift_result["violations"] or missing_examples:
        report = generate_drift_report(
            drift_result["violations"],
            drift_result["drift_score"],
            missing_examples
        )

        # Save report
        ce_dir = project_root / ".ce"
        ce_dir.mkdir(exist_ok=True)
        report_path = ce_dir / "drift-report.md"
        report_path.write_text(report)
```

**This section needs to be extracted into new `analyze_context_drift()` function.**

### Caching Pattern Reference (profiling.py)

**Existing Cache Decorator** - Lines 56-113:
```python
def cache_result(ttl_seconds: int = 300, max_size: int = 128):
    """Decorator to cache function results with TTL and size limit."""
```

**Features**:
- TTL-based expiration
- LRU eviction for size limit
- Thread-safe (for single process)
- cache_clear() and cache_info() methods

**Note**: For this PRP, we'll implement simpler file-based caching (parse drift-report.md timestamp) rather than decorator-based caching, since:
1. Drift report is already saved to disk
2. No need to cache in-memory (infrequent operation)
3. TTL validation can read timestamp from report

### CLI Pattern Reference (__main__.py)

**Existing Subcommand Pattern**:
```python
# Example: update-context subcommand
update_parser = subparsers.add_parser(
    "update-context",
    help="Sync context with codebase changes"
)
update_parser.add_argument("--prp", help="Target specific PRP")
update_parser.set_defaults(func=handle_update_context)
```

**Follow this pattern for `analyze-context` with `analyse-context` alias.**

### Config Reading Pattern

**No existing YAML config reader** - need to create simple helper:
```python
def get_cache_ttl(cli_ttl: Optional[int] = None) -> int:
    """Get TTL from CLI > config > default (3-tier priority)."""
    if cli_ttl is not None:
        return cli_ttl

    config_path = Path(".ce/config.yml")
    if config_path.exists():
        import yaml
        config = yaml.safe_load(config_path.read_text())
        ttl = config.get("cache", {}).get("analysis_ttl_minutes")
        if ttl is not None:
            return int(ttl)

    return 5  # Default
```

**Config File Structure** (create .ce/config.yml):
```yaml
cache:
  analysis_ttl_minutes: 5
```

## Examples

### Example 1: Fast Drift Check

**Command**:
```bash
ce analyze-context
```

**Output**:
```
🔍 Analyzing context drift...
   📊 Pattern conformance: 28 files scanned
   📚 Documentation gaps: 5 PRPs checked

✅ Analysis complete (2.3s)
   Drift Score: 17.9% (🚨 CRITICAL)
   Violations: 5
   Report: .ce/drift-report.md
```

**Exit Code**: 2 (critical drift)

### Example 2: JSON Output for Scripting

**Command**:
```bash
ce analyze-context --json
```

**Output**:
```json
{
  "drift_score": 17.9,
  "drift_level": "critical",
  "violations": 5,
  "missing_examples": 0,
  "report_path": ".ce/drift-report.md",
  "generated_at": "2025-10-16T20:15:00Z",
  "duration_seconds": 2.3
}
```

**Exit Code**: 2

### Example 3: Cached Analysis

**Scenario**: Run analysis, then update-context within 5 minutes

```bash
# First run - full analysis
$ ce analyze-context
✅ Analysis complete (2.3s)
   Drift Score: 17.9%

# Second run - uses cache
$ ce update-context
🔍 Checking drift analysis cache...
   ✅ Recent analysis found (2 minutes old)
   📊 Using cached results: 17.9% drift

✅ Context sync completed
   PRPs scanned: 19
   Drift analysis: cached (0s)
```

### Example 4: Force Re-analysis

**Command**:
```bash
ce analyze-context --force
```

**Behavior**: Bypass cache, always run fresh analysis

## Implementation Plan

### Phase 1: Extract Analysis Function (~1h)

**File**: `tools/ce/update_context.py`

**Create new function**:
```python
def analyze_context_drift() -> Dict[str, Any]:
    """Run drift analysis and generate report.

    Returns:
        {
            "drift_score": 17.9,
            "drift_level": "critical",  # ok, warning, critical
            "violations": ["..."],
            "missing_examples": [...],
            "report_path": ".ce/drift-report.md",
            "generated_at": "2025-10-16T20:15:00Z",
            "duration_seconds": 2.3
        }

    Raises:
        RuntimeError: If analysis fails
    """
    import time
    start_time = time.time()

    # Run drift detection (existing functions)
    drift_result = verify_codebase_matches_examples()
    missing_examples = detect_missing_examples_for_prps()

    # Generate report
    report = generate_drift_report(
        drift_result["violations"],
        drift_result["drift_score"],
        missing_examples
    )

    # Save report
    report_path = Path(".ce/drift-report.md")
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(report)

    # Calculate duration
    duration = time.time() - start_time

    # Classify drift level
    drift_score = drift_result["drift_score"]
    if drift_score < 5:
        drift_level = "ok"
    elif drift_score < 15:
        drift_level = "warning"
    else:
        drift_level = "critical"

    return {
        "drift_score": drift_score,
        "drift_level": drift_level,
        "violations": drift_result["violations"],
        "missing_examples": missing_examples,
        "report_path": str(report_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(duration, 1)
    }
```

### Phase 2: Create CLI Command (~0.5h)

**File**: `tools/ce/cli_handlers.py`

**Add handler**:
```python
def handle_analyze_context(args) -> int:
    """Handle ce analyze-context command.

    Returns:
        Exit code: 0 (ok), 1 (warning), 2 (critical)
    """
    try:
        # Get cache TTL (CLI flag > config > default)
        cache_ttl = get_cache_ttl(args.cache_ttl)

        # Check cache if not forced
        if not args.force:
            cached = get_cached_analysis()
            if cached and is_cache_valid(cached, ttl_minutes=cache_ttl):
                if not args.json:
                    print(f"✅ Using cached analysis (TTL: {cache_ttl}m, use --force to re-analyze)")
                result = cached
            else:
                result = analyze_context_drift()
        else:
            result = analyze_context_drift()

        # Display or output JSON
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            display_analysis_summary(result)

        # Return exit code based on drift level
        exit_codes = {"ok": 0, "warning": 1, "critical": 2}
        return exit_codes[result["drift_level"]]

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1
```

**Add to CLI parser** (`tools/ce/__main__.py`):
```python
# Add subcommand (US spelling primary)
analyze_parser = subparsers.add_parser(
    "analyze-context",
    aliases=["analyse-context"],  # UK spelling alias
    help="Analyze context drift without updating metadata"
)
analyze_parser.add_argument(
    "--json",
    action="store_true",
    help="Output JSON for scripting"
)
analyze_parser.add_argument(
    "--force",
    action="store_true",
    help="Force re-analysis, bypass cache"
)
analyze_parser.add_argument(
    "--cache-ttl",
    type=int,
    default=None,
    help="Cache TTL in minutes (default: from config or 5)"
)
analyze_parser.set_defaults(func=handle_analyze_context)
```

### Phase 3: Add Cache Optimization (~1h)

**File**: `tools/ce/update_context.py`

**Cache helpers**:
```python
def get_cached_analysis() -> Optional[Dict[str, Any]]:
    """Read cached drift analysis from report file.

    Returns:
        Cached analysis dict or None if not found
    """
    report_path = Path(".ce/drift-report.md")
    if not report_path.exists():
        return None

    try:
        content = report_path.read_text()

        # Extract timestamp from report
        # Format: **Generated**: 2025-10-16T20:03:32.185604+00:00
        timestamp_match = re.search(
            r'\*\*Generated\*\*: (.+?)$',
            content,
            re.MULTILINE
        )
        if not timestamp_match:
            return None

        generated_at = timestamp_match.group(1).strip()

        # Extract drift score
        score_match = re.search(r'\*\*Drift Score\*\*: ([\d.]+)%', content)
        if not score_match:
            return None

        drift_score = float(score_match.group(1))

        # Extract violation count
        violations_match = re.search(r'\*\*Violations Found\*\*: (\d+)', content)
        violation_count = int(violations_match.group(1)) if violations_match else 0

        # Classify drift level
        if drift_score < 5:
            drift_level = "ok"
        elif drift_score < 15:
            drift_level = "warning"
        else:
            drift_level = "critical"

        return {
            "drift_score": drift_score,
            "drift_level": drift_level,
            "violation_count": violation_count,
            "report_path": str(report_path),
            "generated_at": generated_at,
            "cached": True
        }

    except Exception as e:
        logger.debug(f"Failed to read cache: {e}")
        return None


def is_cache_valid(cached: Dict[str, Any], ttl_minutes: int = 5) -> bool:
    """Check if cached analysis is still valid.

    Args:
        cached: Cached analysis dict
        ttl_minutes: Cache time-to-live in minutes

    Returns:
        True if cache is fresh (< TTL), False otherwise
    """
    try:
        generated_at = datetime.fromisoformat(
            cached["generated_at"].replace("+00:00", "+00:00")
        )
        now = datetime.now(timezone.utc)
        age_minutes = (now - generated_at).total_seconds() / 60

        return age_minutes < ttl_minutes

    except Exception:
        return False
```

### Phase 4: Refactor update-context (~1h)

**File**: `tools/ce/update_context.py`

**Update sync_context()**:
```python
def sync_context(target_prp: Optional[str] = None, force_analysis: bool = False) -> Dict[str, Any]:
    """Execute context sync workflow with smart caching.

    Args:
        target_prp: Optional specific PRP for targeted sync
        force_analysis: Force drift re-analysis even if cached
    """
    # ... existing PRP metadata update logic ...

    # Drift detection (universal sync only) with caching
    if not target_prp:
        logger.info("Running drift detection...")

        # Check cache unless forced
        if not force_analysis:
            cached = get_cached_analysis()
            if cached and is_cache_valid(cached):
                logger.info(f"Using cached drift analysis ({cached['drift_score']:.1f}%)")
                # Skip re-analysis, report already exists
                return result

        # Run fresh analysis
        analysis_result = analyze_context_drift()
        logger.info(f"Drift analysis complete: {analysis_result['drift_score']:.1f}%")

    return result
```

### Phase 5: Testing (~1.5h)

**File**: `tools/tests/test_analyze_context.py` (create new)

**Unit Tests**:
```python
def test_analyze_context_drift():
    """Test drift analysis returns expected structure."""

def test_get_cached_analysis_exists():
    """Test reading cached analysis from report."""

def test_get_cached_analysis_missing():
    """Test cache miss when report doesn't exist."""

def test_is_cache_valid_fresh():
    """Test cache validation for fresh cache (< 5 min)."""

def test_is_cache_valid_stale():
    """Test cache validation for stale cache (> 5 min)."""
```

**Integration Tests**:
```python
def test_cli_analyze_context():
    """Test CLI command execution."""

def test_cli_analyze_context_json():
    """Test JSON output format."""

def test_update_context_uses_cache():
    """Test update-context reuses cached analysis."""
```

### Phase 6: Documentation (~0.5h)

**File**: `tools/CLAUDE.md`

Add to Context Sync section:

```markdown
### Fast Drift Check - ce analyze-context

**Quick drift score without full sync**:

```bash
# Basic usage
ce analyze-context
# Output: Drift score, violation count, report path

# JSON for scripting
ce analyze-context --json | jq '.drift_score'

# Force re-analysis (bypass cache)
ce analyze-context --force
```

**Exit Codes** (for CI/CD):
- 0: Healthy (drift < 5%)
- 1: Warning (drift 5-15%)
- 2: Critical (drift > 15%)

**Caching**: Results cached for 5 minutes, reused by `ce update-context` for performance.

**Use Cases**:
- Pre-commit hook: Fast drift check before commit
- CI/CD: Automated drift monitoring
- Development: Quick status check without metadata updates
```

**File**: `tools/README.md`

Update Quick Commands section.

## Acceptance Criteria

### Functional Requirements
- [ ] `ce analyze-context` command runs drift analysis only (no metadata updates)
- [ ] Exit codes: 0 (ok), 1 (warning), 2 (critical) based on drift score
- [ ] `--json` flag outputs structured JSON for scripting
- [ ] `--force` flag bypasses cache, always runs fresh analysis
- [ ] Cache mechanism: reuse analysis if < 5 minutes old
- [ ] `ce update-context` uses cached analysis when valid
- [ ] Backwards compatibility: `ce update-context` works as before

### Quality Requirements
- [ ] Analysis completes in < 5 seconds
- [ ] Cache validation accurate (timestamp parsing)
- [ ] Error handling with troubleshooting guidance
- [ ] Test coverage: unit + integration tests
- [ ] No regression in existing workflows

### Documentation Requirements
- [ ] CLAUDE.md updated with new command usage
- [ ] README.md updated with quick reference
- [ ] Exit codes documented for CI/CD integration
- [ ] Caching behavior explained

## Testing Strategy

### Unit Tests (5 tests)
1. `test_analyze_context_drift()` - Core analysis function
2. `test_get_cached_analysis_exists()` - Cache read (hit)
3. `test_get_cached_analysis_missing()` - Cache read (miss)
4. `test_is_cache_valid_fresh()` - Cache TTL (valid)
5. `test_is_cache_valid_stale()` - Cache TTL (expired)

### Integration Tests (3 tests)
1. `test_cli_analyze_context()` - CLI execution
2. `test_cli_analyze_context_json()` - JSON output
3. `test_update_context_uses_cache()` - Cache integration

**Run Tests**:
```bash
cd tools
uv run pytest tests/test_analyze_context.py -v
```

## Risk Assessment

**Complexity**: LOW-MEDIUM ⭐⭐
- Extracts existing logic into new function
- Adds caching layer (timestamp parsing)
- New CLI command (straightforward)
- No architectural changes

**Dependencies**: MINIMAL
- Reuses existing drift detection functions (PRP-15.2)
- No new external dependencies

**Risk Factors**:
- ✅ Backwards compatible - no breaking changes
- ✅ Graceful degradation if cache fails (falls back to analysis)
- ⚠️ Cache timestamp parsing fragile (mitigated by try-except)

**Estimated Effort**: 5.5 hours
- Extract function: 1h
- CLI command: 0.5h
- Caching: 1h
- Refactor update-context: 1h
- Testing: 1.5h
- Documentation: 0.5h

## Related PRPs

- **PRP-15.2**: Blueprint Generation (provides drift detection functions)
- **PRP-15.3**: Workflow Automation (provides remediation workflow)
- **PRP-16**: Serena Verification (uses context sync)

## Future Enhancements (Deferred to Separate PRPs)

### 1. Watch Mode (Future PRP)
- `ce analyze-context --watch` for continuous monitoring
- Auto-refresh on file changes
- Live drift score updates

### 2. Linear Integration Workflow (Future PRP)
- **Current State**: Linear issue creation embedded in `/generate-prp`
- **Future State**: Extract into separate `create-linear-issue` workflow
  - Triggered workflow: Can be called by any command
  - Composable: `/generate-prp`, `/analyze-context`, etc. can trigger
  - Configurable: Toggle via `.ce/linear-config.yml`
- **Benefit**: Separation of concerns, reusable across commands

### 3. Serena Integration for Drift Detection (This PRP)
- **Included**: `analyze-context` integrates with Serena verification
- **Mechanism**: Reuses existing `verify_implementation_with_serena()` (PRP-16)
- **Behavior**:
  - If Serena available: Enhanced drift detection with semantic analysis
  - If Serena unavailable: Graceful degradation to pattern-only detection
- **Output**: JSON includes `serena_available: true/false` flag

## Technical Notes

### Cache TTL Configuration

**Default**: 5 minutes (reasonable for development workflow)
**Configuration**: Configurable via `.ce/config.yml` and `--cache-ttl` flag

**Config File** (`.ce/config.yml`):
```yaml
cache:
  analysis_ttl_minutes: 5  # Default TTL for drift analysis cache
```

**Priority** (highest to lowest):
1. `--cache-ttl` command-line flag
2. `.ce/config.yml` value
3. Hardcoded default (5 minutes)

**Helper Function**:
```python
def get_cache_ttl(cli_ttl: Optional[int] = None) -> int:
    """Get cache TTL from CLI arg, config, or default.

    Args:
        cli_ttl: TTL from command-line --cache-ttl flag

    Returns:
        TTL in minutes (priority: CLI > config > default)
    """
    # Priority 1: CLI flag
    if cli_ttl is not None:
        return cli_ttl

    # Priority 2: Config file
    config_path = Path(".ce/config.yml")
    if config_path.exists():
        try:
            import yaml
            config = yaml.safe_load(config_path.read_text())
            ttl = config.get("cache", {}).get("analysis_ttl_minutes")
            if ttl is not None:
                return int(ttl)
        except Exception:
            pass  # Fall back to default

    # Priority 3: Default
    return 5
```

### Exit Code Semantics

**Standard**: Follow Unix conventions
- 0: Success (drift < 5%)
- 1: Warning (5-15%, non-zero but not critical)
- 2: Error/Critical (> 15%, requires action)

### JSON Schema

**Output structure** for `--json`:
```json
{
  "drift_score": 17.9,
  "drift_level": "critical",
  "violations": 5,
  "violations_by_category": {
    "error_handling": 0,
    "naming_conventions": 0,
    "kiss_violations": 0,
    "missing_troubleshooting": 5
  },
  "missing_examples": 0,
  "recently_fixed": [
    {
      "file": "tools/ce/resilience.py",
      "issue": "deep_nesting",
      "fixed_at": "2025-10-16T20:03:32Z",
      "commits": ["0a0a134"]
    },
    {
      "file": "tools/ce/validation_loop.py",
      "issue": "deep_nesting",
      "fixed_at": "2025-10-16T20:03:32Z",
      "commits": ["0a0a134"]
    }
  ],
  "report_path": ".ce/drift-report.md",
  "generated_at": "2025-10-16T20:15:00Z",
  "duration_seconds": 2.3
}
```

**Troubleshooting Feature**: `recently_fixed` shows violations resolved in last 24h
- **Use Case**: Drift still high after fix? Check `recently_fixed` to see what was already addressed
- **Detection**: Parse git log for commits touching violation files in last 24h
- **Helps**: Avoid re-fixing same issue, focus on actual remaining violations

### Caching Strategy

**Storage**: Reuse existing `.ce/drift-report.md` (no new files)
**Validation**: Parse timestamp from report Markdown
**Invalidation**: Natural (overwrites on new analysis)
**TTL**: 5 minutes (tunable future)

## Confidence Score

**7/10** - Good confidence for one-pass success

**Reasoning**:
- ✅ Clear requirements and existing functions to reuse
- ✅ Straightforward extraction (no complex refactoring)
- ✅ Caching logic well-defined
- ⚠️ Cache timestamp parsing needs careful testing
- ⚠️ CLI integration may need iteration for UX polish