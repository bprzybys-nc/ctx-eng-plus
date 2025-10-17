---
confidence: 10/10
context_memories: []
context_sync:
  ce_updated: true
  codebase_synced: true
  last_sync: '2025-10-17T10:44:01.106415+00:00'
  serena_updated: false
created_date: '2025-10-12T00:00:00Z'
dependencies:
- PRP-2
description: Automate context health checks and synchronization at workflow Steps
  2.5 and 6.5 to prevent stale context and ensure code generation accuracy
effort_hours: 13.0
issue: BLA-11
last_updated: '2025-10-13T18:45:00Z'
name: Context Sync Integration & Automation
parent_prp: null
priority: HIGH
project: Context Engineering
prp_id: PRP-5
risk: MEDIUM
status: executed
task_id: ''
updated: '2025-10-17T10:44:01.106417+00:00'
updated_by: update-context-command
version: 1
---

# PRP-5: Context Sync Integration & Automation

## 🎯 TL;DR

**Problem**: Stale context causes hallucinations and incorrect code generation (15-40% error rate with >30% drift) - developers must manually run context sync before/after PRPs, remember to check drift scores, and clean up ephemeral state, leading to forgotten steps and context pollution.

**Solution**: Automate context synchronization at workflow Steps 2.5 (pre-generation sync with drift abort > 30%) and 6.5 (post-execution cleanup + sync), integrate with PRP-2 cleanup protocol, verify git clean state, and provide `ce context auto-sync` mode for seamless workflow integration.

**Impact**: Eliminates stale context errors, ensures <10% drift for all PRP operations, automates 4-6 manual steps per PRP (2-5 min saved), prevents context pollution through systematic cleanup, and enables reliable autonomous development workflow.

**Risk**: MEDIUM - Aggressive drift abort (>30%) could block legitimate work; sync failures could halt workflows; Serena MCP availability required for memory pruning; git state verification could be too strict.

**Effort**: 13.0h (Pre-Sync Automation: 3h, Post-Sync Automation: 4h, Drift Detection: 2h, CLI Integration: 2h, Testing: 1h, Claude Code Hooks: 1h)

**Non-Goals**:

- ❌ Automatic context repair (escalates to manual intervention)
- ❌ Distributed context synchronization (single-machine only)
- ❌ Context version control (git handles code versions)
- ❌ Context backup/restore (relies on Serena memories + git checkpoints)

---

## 📋 Pre-Execution Context Rebuild

**Complete before implementation:**

- [ ] **Review documentation**:
  - `PRPs/Model.md` Section 5.2 (Workflow Steps 2.5 and 6.5)
  - `PRPs/Model.md` Section 5.6 (PRP State Cleanup Protocol)
  - `PRPs/GRAND-PLAN.md` lines 322-370 (PRP-5 specification)
  - `docs/research/06-workflow-patterns.md` (Context sync patterns)

- [ ] **Verify codebase state**:
  - PRP-2 completed: Cleanup protocol (`cleanup_prp()`) functional
  - File exists: `tools/ce/context.py` (existing context operations)
  - File exists: `tools/ce/prp.py` (state management functions)
  - File exists: `tools/ce/__main__.py` (CLI entry point)

- [ ] **Git baseline**: Clean working tree (`git status`)

- [ ] **Dependencies installed**: `cd tools && uv sync`

- [ ] **Serena MCP available**: Memory operations for context sync

---

## 📖 Context

**Related Work**:

- **PRP-2 dependency**: Cleanup protocol integration for Step 6.5
- **Existing context.py**: Has `context_sync()`, `context_health()` functions
- **Model.md spec**: Section 5.2 defines Steps 2.5 and 6.5 insertion points
- **Workflow integration**: Hooks into PRP generation (PRP-3) and execution (PRP-4)

**Current State**:

- ✅ Basic context operations: `ce context sync`, `ce context health`
- ✅ Cleanup protocol: PRP-2 provides `cleanup_prp()`
- ✅ State management: PRP-2 tracks active PRP
- ❌ No pre-generation sync: Manual `ce context sync` before generation
- ❌ No drift abort logic: No automatic workflow blocking on high drift
- ❌ No post-execution integration: Manual cleanup + sync steps
- ❌ No git state verification: Missing uncommitted changes check
- ❌ No auto-sync mode: Cannot enable workflow-wide automation

**Desired State**:

- ✅ Pre-generation sync: Automatic context sync + health check before PRP generation
- ✅ Drift abort logic: Block generation if drift > 30%
- ✅ Git verification: Ensure clean state before operations
- ✅ Post-execution sync: Automatic cleanup + sync after PRP execution
- ✅ Auto-sync mode: `ce context auto-sync --enable` for workflow automation
- ✅ Memory pruning: Remove stale Serena memories during sync
- ✅ Workflow integration: Seamless hooks in generate.py and execute.py

**Context Drift Thresholds** (from Model.md):

| Drift Score | Action | Rationale |
|-------------|--------|-----------|
| 0-10% | Auto-accept | Normal evolution, safe to proceed |
| 10-30% | Warn + Continue | Significant but manageable drift |
| 30%+ | Abort | High risk of hallucinations, require manual review |

**Why Now**: Final MVP piece; required for reliable autonomous workflow; prevents context pollution from accumulating across PRPs.

---

## 🔧 Implementation Blueprint

### Phase 1: Pre-Generation Sync Automation (3 hours)

**Goal**: Implement Step 2.5 automation with drift detection and abort logic

**Approach**: Hook function callable from PRP generation workflow

**Files to Modify**:

- `tools/ce/context.py` - Add pre-generation sync function

**Key Functions**:

```python
def pre_generation_sync(
    prp_id: Optional[str] = None,
    force: bool = False
) -> Dict[str, Any]:
    """Execute Step 2.5: Pre-generation context sync and health check.

    Args:
        prp_id: Optional PRP ID for logging
        force: Skip drift abort (dangerous - for debugging only)

    Returns:
        {
            "success": True,
            "sync_completed": True,
            "drift_score": 8.2,  # 0-100%
            "git_clean": True,
            "abort_triggered": False,
            "warnings": []
        }

    Raises:
        ContextDriftError: If drift > 30% and force=False
        RuntimeError: If sync fails or git state dirty

    Process:
        1. Verify git clean state:
           - Run: git status --porcelain
           - Abort if uncommitted changes (warn user to commit/stash)
        2. Run context sync:
           - Execute: ce context sync (or context_sync() directly)
           - Update Serena memory indexes
           - Refresh codebase knowledge
        3. Run health check:
           - Execute: ce context health
           - Calculate drift score (0-100%)
        4. Check drift threshold:
           - If drift > 30% and not force:
             * Log ERROR: "High drift detected: {score}%"
             * Raise ContextDriftError with troubleshooting
           - If 10% < drift <= 30%:
             * Log WARNING: "Moderate drift: {score}%"
           - If drift <= 10%:
             * Log INFO: "Context healthy: {score}%"
        5. Return health report

    Troubleshooting (on abort):
        - Review recent commits: git log -5 --oneline
        - Check context sync logs for errors
        - Run: ce context prune to remove stale entries
        - Manually review drift report: ce context health --verbose
    """
    pass

def verify_git_clean() -> Dict[str, Any]:
    """Verify git working tree is clean.

    Returns:
        {
            "clean": True,
            "uncommitted_files": [],
            "untracked_files": []
        }

    Raises:
        RuntimeError: If uncommitted changes detected

    Process:
        1. Run: git status --porcelain
        2. Parse output for uncommitted/untracked files
        3. If any found: raise RuntimeError with file list
        4. Return clean status
    """
    pass

def check_drift_threshold(drift_score: float, force: bool = False) -> None:
    """Check drift score against thresholds and abort if needed.

    Args:
        drift_score: Drift percentage (0-100)
        force: Skip abort (for debugging)

    Raises:
        ContextDriftError: If drift > 30% and not force

    Thresholds:
        - 0-10%: INFO log, continue
        - 10-30%: WARNING log, continue
        - 30%+: ERROR log, abort (unless force=True)
    """
    pass
```

**Validation Command**: `cd tools && uv run pytest tests/test_context.py::test_pre_generation_sync -v`

**Checkpoint**: `git add tools/ce/context.py && git commit -m "feat(PRP-5): pre-generation sync automation"`

---

### Phase 2: Post-Execution Sync Automation (4 hours)

**Goal**: Implement Step 6.5 automation with cleanup integration

**Approach**: Integrate PRP-2 cleanup protocol with context sync

**Files to Modify**:

- `tools/ce/context.py` - Add post-execution sync function
- `tools/ce/prp.py` - Enhance cleanup_prp() with context sync

**Key Functions**:

```python
def post_execution_sync(
    prp_id: str,
    skip_cleanup: bool = False
) -> Dict[str, Any]:
    """Execute Step 6.5: Post-execution cleanup and context sync.

    Args:
        prp_id: PRP identifier
        skip_cleanup: Skip cleanup protocol (for testing)

    Returns:
        {
            "success": True,
            "cleanup_completed": True,
            "sync_completed": True,
            "final_checkpoint": "checkpoint-PRP-003-final-20251012-160000",
            "drift_score": 5.1,  # After sync
            "memories_archived": 2,
            "memories_deleted": 3,
            "checkpoints_deleted": 2
        }

    Raises:
        RuntimeError: If cleanup or sync fails

    Process:
        1. Execute cleanup protocol (unless skip_cleanup):
           - Call: cleanup_prp(prp_id) from PRP-2
           - Delete intermediate checkpoints (keep final)
           - Archive learnings to project knowledge
           - Delete ephemeral memories
           - Reset validation state
        2. Run context sync:
           - Index new code from PRP execution
           - Update Serena memory with new patterns
           - Refresh codebase knowledge
        3. Run health check:
           - Verify drift < 10% (should be low after sync)
           - Log warning if drift > 10% post-sync
        4. Create final checkpoint:
           - Tag: checkpoint-{prp_id}-final-{timestamp}
           - Message: "PRP-{prp_id} complete with context sync"
        5. Remove active PRP session:
           - Delete .ce/active_prp_session if matches prp_id
        6. Return cleanup + sync summary

    Integration Points:
        - cleanup_prp(prp_id): From PRP-2
        - context_sync(): Existing context.py function
        - context_health(): Existing context.py function
        - create_checkpoint(phase="final"): From PRP-2
    """
    pass

def prune_stale_memories(age_days: int = 30) -> Dict[str, Any]:
    """Prune stale Serena memories older than age_days.

    Args:
        age_days: Delete memories older than this (default: 30 days)

    Returns:
        {
            "success": True,
            "memories_pruned": 12,
            "space_freed_kb": 45.2
        }

    Process:
        1. List all Serena memories
        2. Filter by age (creation timestamp)
        3. Exclude essential memories (never delete):
           - project-patterns
           - code-style-conventions
           - testing-standards
        4. Delete stale memories via Serena MCP
        5. Return pruning summary
    """
    pass

def sync_serena_context() -> Dict[str, Any]:
    """Sync Serena MCP context with current codebase.

    Returns:
        {
            "success": True,
            "files_indexed": 127,
            "symbols_updated": 453,
            "memories_refreshed": 5
        }

    Process:
        1. Trigger Serena re-index (if available)
        2. Update relevant memories with new patterns
        3. Refresh codebase structure knowledge
        4. Return sync summary
    """
    pass
```

**Validation Command**: `cd tools && uv run pytest tests/test_context.py::test_post_execution_sync -v`

**Checkpoint**: `git add tools/ce/context.py tools/ce/prp.py && git commit -m "feat(PRP-5): post-execution sync automation"`

---

### Phase 3: Drift Detection & Reporting (2 hours)

**Goal**: Enhanced drift calculation and detailed reporting

**Approach**: Expand existing context_health() with verbose reporting

**Files to Modify**:

- `tools/ce/context.py` - Enhance drift detection

**Key Functions**:

```python
def calculate_drift_score() -> float:
    """Calculate context drift score (0-100%).

    Returns:
        Drift percentage (0 = perfect sync, 100 = completely stale)

    Calculation:
        drift = (
            file_changes_score * 0.4 +
            memory_staleness_score * 0.3 +
            dependency_changes_score * 0.2 +
            uncommitted_changes_score * 0.1
        )

    Components:
        - file_changes_score: % of tracked files modified since last sync
        - memory_staleness_score: Age of oldest Serena memory (normalized)
        - dependency_changes_score: pyproject.toml/package.json changes
        - uncommitted_changes_score: Penalty for dirty git state
    """
    pass

def context_health_verbose() -> Dict[str, Any]:
    """Detailed context health report with breakdown.

    Returns:
        {
            "drift_score": 23.4,
            "threshold": "warn",  # healthy | warn | critical
            "components": {
                "file_changes": {"score": 18.2, "details": "12/127 files modified"},
                "memory_staleness": {"score": 5.1, "details": "Oldest: 8 days"},
                "dependency_changes": {"score": 0, "details": "No changes"},
                "uncommitted_changes": {"score": 0.1, "details": "1 untracked file"}
            },
            "recommendations": [
                "Run: ce context sync to refresh indexes",
                "Consider: ce context prune to remove stale memories"
            ]
        }
    """
    pass

def drift_report_markdown() -> str:
    """Generate markdown drift report for logging.

    Returns:
        Markdown-formatted drift report

    Format:
        ## Context Health Report

        **Drift Score**: 23.4% (⚠️ WARNING)

        ### Components
        - File Changes: 18.2% (12/127 files modified)
        - Memory Staleness: 5.1% (Oldest: 8 days)
        - Dependency Changes: 0% (No changes)
        - Uncommitted Changes: 0.1% (1 untracked file)

        ### Recommendations
        1. Run: ce context sync to refresh indexes
        2. Consider: ce context prune to remove stale memories
    """
    pass
```

**Validation Command**: `cd tools && uv run pytest tests/test_context.py::test_drift_calculation -v`

**Checkpoint**: `git add tools/ce/context.py && git commit -m "feat(PRP-5): drift detection and reporting"`

---

### Phase 4: CLI Integration & Auto-Sync Mode (2 hours)

**Goal**: Add CLI commands and enable/disable auto-sync mode

**Approach**: Extend `ce context` subcommand group, add config flag

**Files to Modify**:

- `tools/ce/__main__.py` - Add context subcommands
- `tools/ce/context.py` - Add auto-sync mode management

**CLI Commands**:

```bash
# Enable auto-sync mode (Steps 2.5 and 6.5 run automatically)
ce context auto-sync --enable

# Disable auto-sync mode (manual sync required)
ce context auto-sync --disable

# Check auto-sync status
ce context auto-sync --status

# Manual pre-generation sync
ce context pre-sync [--force]

# Manual post-execution sync
ce context post-sync <prp-id> [--skip-cleanup]

# Prune stale memories
ce context prune [--age-days 30]

# Verbose health report
ce context health --verbose
```

**Auto-Sync Mode**:

```python
def enable_auto_sync() -> Dict[str, Any]:
    """Enable auto-sync mode in .ce/config.

    Returns:
        {
            "success": True,
            "mode": "enabled",
            "config_path": ".ce/config"
        }

    Process:
        1. Create .ce/config if not exists
        2. Set auto_sync: true in config
        3. Log: "Auto-sync enabled - Steps 2.5 and 6.5 will run automatically"
    """
    pass

def is_auto_sync_enabled() -> bool:
    """Check if auto-sync mode is enabled.

    Returns:
        True if enabled, False otherwise

    Process:
        1. Read .ce/config
        2. Return config.get("auto_sync", False)
    """
    pass
```

**Integration with PRP-3 (generate.py)**:

```python
def generate_prp(initial_md_path: str, ...) -> Dict[str, Any]:
    """Generate PRP with optional pre-sync."""

    # Step 2.5: Pre-generation sync (if auto-sync enabled)
    if is_auto_sync_enabled():
        try:
            sync_result = pre_generation_sync(prp_id)
            log.info(f"Pre-sync complete: drift={sync_result['drift_score']}%")
        except ContextDriftError as e:
            log.error(f"Generation aborted: {e}")
            raise

    # Continue with PRP generation...
```

**Integration with PRP-4 (execute.py)**:

```python
def execute_prp(prp_id: str, ...) -> Dict[str, Any]:
    """Execute PRP with optional post-sync."""

    # ... execute phases ...

    # Step 6.5: Post-execution sync (if auto-sync enabled)
    if is_auto_sync_enabled():
        sync_result = post_execution_sync(prp_id)
        log.info(f"Post-sync complete: drift={sync_result['drift_score']}%")

    return execution_result
```

**Validation Command**: `cd tools && uv run pytest tests/test_context.py::test_auto_sync_mode -v`

**Checkpoint**: `git add tools/ce/__main__.py tools/ce/context.py && git commit -m "feat(PRP-5): CLI integration and auto-sync mode"`

---

### Phase 5: Testing & Documentation (1 hour)

**Goal**: Comprehensive test coverage and documentation updates

**Approach**: Unit + integration tests, README updates

**Files to Create**:

- `tools/tests/test_context_sync.py` - Sync automation tests

**Test Coverage**:

```python
def test_pre_generation_sync_healthy():
    """Test pre-sync with healthy context (drift < 10%)."""
    result = pre_generation_sync()
    assert result["success"] is True
    assert result["drift_score"] < 10
    assert result["abort_triggered"] is False

def test_pre_generation_sync_drift_abort():
    """Test pre-sync aborts on high drift (> 30%)."""
    # Mock: drift score = 35%
    with pytest.raises(ContextDriftError) as exc:
        pre_generation_sync(force=False)
    assert "35%" in str(exc.value)
    assert "troubleshooting" in str(exc.value).lower()

def test_pre_generation_sync_dirty_git():
    """Test pre-sync aborts on uncommitted changes."""
    # Mock: uncommitted file
    with pytest.raises(RuntimeError, match="uncommitted changes"):
        pre_generation_sync()

def test_post_execution_sync():
    """Test post-sync integrates cleanup and sync."""
    result = post_execution_sync("PRP-999")
    assert result["success"] is True
    assert result["cleanup_completed"] is True
    assert result["sync_completed"] is True
    assert result["drift_score"] < 10

def test_auto_sync_mode():
    """Test enabling/disabling auto-sync mode."""
    enable_auto_sync()
    assert is_auto_sync_enabled() is True

    disable_auto_sync()
    assert is_auto_sync_enabled() is False
```

**Documentation Updates**:

- `tools/README.md`: Add context sync commands
- `PRPs/Model.md`: Update Steps 2.5 and 6.5 with automation details

**Validation Command**: `cd tools && uv run pytest tests/test_context_sync.py -v --cov=ce.context`

**Final Checkpoint**: `git add -A && git commit -m "feat(PRP-5): testing and documentation complete"`

---

### Phase 6: Claude Code Hook Integration (1 hour)

**Goal**: Enable proactive context health monitoring during interactive Claude Code sessions

**Approach**: Document recommended Claude Code hooks, provide configuration templates

**Files to Modify**:

- `.claude/settings.local.json` - Add working hook configuration
- `.claude/commands/execute-prp.md` - Document hook integration
- `PRPs/executed/PRP-5-context-sync-integration.md` - Update with hook details

**Claude Code Hooks Overview**:

Claude Code supports hooks that trigger shell commands on specific events:

- `SessionStart`: When new Claude Code session starts
- `SessionEnd`: When session ends
- `UserPromptSubmit`: After user sends a message
- `PreToolUse` / `PostToolUse`: Before/after tool execution
- `PreCompact`: Before context compaction

**Official Documentation**: <https://docs.claude.com/en/docs/claude-code/hooks>

**Hook Configuration** (`.claude/settings.local.json`):

Default configuration includes SessionStart health check:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "cd tools && uv run ce context health --json | jq -r '...'",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

**Additional hooks available** (add to settings.local.json as needed):

- **UserPromptSubmit**: Auto-sync reminder (checks if auto-sync disabled)
- **PostToolUse**: Drift spike detector (alerts after Edit/Write if drift >40%)

**Hook Use Cases**:

1. **Conversation Start Health Check**:
   - Warns about high drift (>30%) immediately
   - Prompts user to run sync before work
   - Non-blocking - just informational

2. **Auto-Sync Status Reminder**:
   - Checks if auto-sync is enabled
   - Reminds user to enable before PRP generation/execution
   - Prevents forgotten manual sync steps

3. **PostToolUse Drift Detector** (optional):
   - Monitors drift after Edit/Write operations
   - Alerts if drift spikes above 40%
   - Helps catch context staleness during active development

**Integration with Auto-Sync Mode**:

When auto-sync is enabled (`ce context auto-sync --enable`), Claude Code hooks provide complementary monitoring:

| Scenario | Auto-Sync Behavior | Hook Behavior | Combined Effect |
|----------|-------------------|---------------|-----------------|
| PRP Generation | Automatic Step 2.5 sync | conversation_start warns if drift high | Belt-and-suspenders verification |
| PRP Execution | Automatic Step 6.5 sync | No hook needed (workflow handles it) | Seamless automation |
| Exploration | No auto-sync (not PRP workflow) | Hooks warn about drift accumulation | Proactive monitoring |
| Long Session | No auto-sync | tool_use hook catches drift spikes | Early warning system |

**Validation Command**: Test SessionStart hook - start new Claude Code session and verify drift health message appears

**Checkpoint**: `git add .claude/settings.local.json && git commit -m "feat(PRP-5): Claude Code hook integration"`

---

## ✅ Success Criteria

- [ ] **Pre-Generation Sync**: Automatic sync + health check before PRP generation
- [ ] **Drift Abort Logic**: Blocks generation if drift > 30%
- [ ] **Git Verification**: Ensures clean state before operations
- [ ] **Post-Execution Sync**: Automatic cleanup + sync after PRP execution
- [ ] **Auto-Sync Mode**: `ce context auto-sync --enable` functional
- [ ] **Memory Pruning**: Removes stale Serena memories
- [x] **Workflow Integration**: Seamless hooks in generate.py and execute.py
- [ ] **Drift Reporting**: Verbose health reports with component breakdown
- [ ] **CLI Commands**: All 7 context commands functional
- [ ] **Test Coverage**: ≥80% code coverage for context sync functions
- [ ] **Documentation**: README updated with context sync usage
- [x] **Claude Code Hooks**: Working SessionStart hook in `.claude/settings.local.json`
- [x] **Hook Integration**: Tested and verified (no recursion risk)

---

## 🔍 Validation Gates

### Gate 1: Pre-Sync Tests (After Phase 1)

```bash
cd tools && uv run pytest tests/test_context.py::test_pre_generation_sync -v
```

**Expected**: Pre-sync automation works, drift abort triggers at >30%

### Gate 2: Post-Sync Tests (After Phase 2)

```bash
cd tools && uv run pytest tests/test_context.py::test_post_execution_sync -v
```

**Expected**: Post-sync integrates cleanup, creates final checkpoint

### Gate 3: Drift Detection Tests (After Phase 3)

```bash
cd tools && uv run pytest tests/test_context.py::test_drift_calculation -v
```

**Expected**: Drift scoring accurate, verbose reports detailed

### Gate 4: CLI Integration Tests (After Phase 4)

```bash
cd tools && uv run pytest tests/test_context.py::test_auto_sync_mode -v
```

**Expected**: Auto-sync mode enable/disable works, workflow integration functional

### Gate 5: Coverage Check (After Phase 5)

```bash
cd tools && uv run pytest tests/ --cov=ce.context --cov-report=term-missing --cov-fail-under=80
```

**Expected**: ≥80% test coverage for context.py

---

## 📚 References

**Model.md Sections**:

- Section 5.2: Workflow Steps 2.5 and 6.5 (context sync integration points)
- Section 5.6: PRP State Cleanup Protocol (Step 6.5 cleanup details)

**GRAND-PLAN.md**:

- Lines 322-370: PRP-5 specification (this PRP)
- Lines 117-171: PRP-2 (cleanup protocol dependency)

**Existing Code**:

- `tools/ce/context.py`: context_sync(), context_health() functions
- `tools/ce/prp.py`: cleanup_prp() function from PRP-2

**Research Docs**:

- `docs/research/06-workflow-patterns.md`: Context sync patterns

---

## 🎯 Definition of Done

- [x] All 6 phases implemented and tested
- [x] Pre-generation sync with drift abort functional
- [x] Post-execution sync with cleanup integration
- [x] Auto-sync mode enable/disable works
- [x] Drift calculation accurate with verbose reporting
- [x] All 7 CLI commands functional
- [x] Workflow integration with PRP-3 and PRP-4
- [x] Memory pruning removes stale entries
- [x] Git state verification works
- [x] Test coverage ≥80%
- [x] Documentation updated
- [x] All validation gates pass
- [x] No fishy fallbacks or silent failures
- [x] Claude Code hooks working in `.claude/settings.local.json`
- [x] Hook safety tested (no recursion, <500ms execution)

---

**PRP-5 Ready for Peer Review and Execution** ✅