---
prp_id: PRP-34.2.1
feature_name: Detection Module (Phase A)
status: pending
created: 2025-11-05T00:00:00Z
updated: 2025-11-05T00:00:00Z
complexity: medium
estimated_hours: 1.5
dependencies: PRP-34.1.1
batch_id: 34
stage: stage-2-parallel
execution_order: 2
merge_order: 2
conflict_potential: NONE
worktree_path: ../ctx-eng-plus-prp-34-2-1
branch_name: prp-34-2-1-detection-module
issue: PRP-34.2.1-created
---

# Detection Module (Phase A)

## 1. TL;DR

**Objective**: Implement legacy file scanner that detects CE files in multiple locations with symlink resolution and garbage filtering

**What**: Create `LegacyFileDetector` class in `tools/ce/blending/detection.py` that scans PRPs/, examples/, context-engineering/, .serena/, and .claude/ directories for CE framework files. Includes smart filtering to exclude garbage files and proper symlink handling.

**Why**: Phase A of the 4-phase initialization pipeline. Provides adaptive detection that works with 0 files (greenfield) or 1000+ files (mature projects), enabling subsequent migration and blending phases.

**Effort**: 1.5 hours (medium complexity)

**Dependencies**: PRP-34.1.1 (must be completed first)

## 2. Context

### Background

The CE 1.1 initialization process requires detecting existing framework files across multiple locations before migration can begin. Legacy installations may have files in:
- **PRPs/** - Feature requests and executed PRPs
- **examples/** - User code examples
- **context-engineering/** - CE 1.0 installations
- **.serena/memories/** - Serena memories (user + framework)
- **.claude/** - Settings and commands
- **CLAUDE.md** - May be symlink or regular file

This detection phase must:
1. Handle symlinks correctly (resolve without following circular refs)
2. Filter garbage files (REPORT, INITIAL, summary, analysis, PLAN, backups)
3. Return organized inventory by domain (prps, examples, claude_md, settings, commands, memories)
4. Work gracefully with missing directories or empty projects

### Constraints and Considerations

**Plan Context**: Phase A of 4-phase pipeline. Adaptive: works with 0 files or 1000 files.

**Edge Cases**:
- Missing directories (greenfield projects)
- Broken symlinks (must not crash)
- Circular symlink references (must detect and skip)
- Empty directories (valid, return empty inventory)
- Mixed CE 1.0 + CE 1.1 installations

**Performance**:
- Target: <1s for typical project (50-100 files)
- Must not follow symlinks recursively
- Use Path.resolve() for symlink resolution

### Documentation References

- Python pathlib: https://docs.python.org/3/library/pathlib.html
- Symlink handling: Path.is_symlink(), Path.resolve()
- Glob patterns: Path.glob(), Path.rglob()

## 3. Implementation Steps

### Phase 1: Setup Module Structure (15 min)

1. Create `tools/ce/blending/detection.py` module
2. Import required dependencies:
   ```python
   from pathlib import Path
   from typing import Dict, List, Set
   import logging
   ```
3. Define module logger: `logger = logging.getLogger(__name__)`

### Phase 2: Define Search Patterns (15 min)

4. Create `SEARCH_PATTERNS` dict with domain keys:
   ```python
   SEARCH_PATTERNS = {
       "prps": ["PRPs/", "context-engineering/PRPs/"],
       "examples": ["examples/", "context-engineering/examples/"],
       "claude_md": ["CLAUDE.md"],
       "settings": [".claude/settings.local.json"],
       "commands": [".claude/commands/"],
       "memories": [".serena/memories/"]
   }
   ```

5. Define garbage filter patterns:
   ```python
   GARBAGE_PATTERNS = [
       "REPORT", "INITIAL", "summary", "analysis",
       "PLAN", ".backup", "~", ".tmp", ".log"
   ]
   ```

### Phase 3: Implement LegacyFileDetector Class (30 min)

6. Create `LegacyFileDetector` class:
   ```python
   class LegacyFileDetector:
       """Detect legacy CE files across multiple locations."""

       def __init__(self, project_root: Path):
           self.project_root = Path(project_root).resolve()
           self.visited_symlinks: Set[Path] = set()
   ```

7. Implement `scan_all()` method:
   ```python
   def scan_all(self) -> Dict[str, List[Path]]:
       """Scan all domains and return inventory.

       Returns:
           Dict with keys: prps, examples, claude_md, settings, commands, memories
           Each value is List[Path] of detected files
       """
       inventory = {domain: [] for domain in SEARCH_PATTERNS.keys()}

       for domain, patterns in SEARCH_PATTERNS.items():
           for pattern in patterns:
               search_path = self.project_root / pattern

               if not search_path.exists():
                   continue

               if search_path.is_file():
                   # Single file (e.g., CLAUDE.md)
                   resolved = self._resolve_symlink(search_path)
                   if resolved and not self._is_garbage(resolved):
                       inventory[domain].append(resolved)
               else:
                   # Directory - collect .md files
                   files = self._collect_files(search_path)
                   inventory[domain].extend(files)

       return inventory
   ```

### Phase 4: Implement Helper Methods (30 min)

8. Implement `_resolve_symlink()` with circular detection:
   ```python
   def _resolve_symlink(self, path: Path) -> Path | None:
       """Resolve symlink, detect circular references.

       Returns:
           Resolved path or None if circular/broken
       """
       if not path.is_symlink():
           return path

       if path in self.visited_symlinks:
           logger.warning(f"Circular symlink detected: {path}")
           return None

       self.visited_symlinks.add(path)

       try:
           resolved = path.resolve(strict=True)
           return resolved
       except (OSError, RuntimeError) as e:
           logger.warning(f"Broken symlink: {path} - {e}")
           return None
   ```

9. Implement `_collect_files()` recursive walker:
   ```python
   def _collect_files(self, directory: Path) -> List[Path]:
       """Recursively collect .md files from directory.

       Returns:
           List of .md file paths (garbage filtered)
       """
       files = []

       try:
           for item in directory.rglob("*.md"):
               if item.is_file() and not self._is_garbage(item):
                   resolved = self._resolve_symlink(item)
                   if resolved:
                       files.append(resolved)
       except PermissionError as e:
           logger.warning(f"Permission denied: {directory} - {e}")

       return files
   ```

10. Implement `_is_garbage()` filter:
    ```python
    def _is_garbage(self, path: Path) -> bool:
        """Check if file matches garbage patterns.

        Returns:
            True if file should be filtered out
        """
        name = path.name
        return any(pattern in name for pattern in GARBAGE_PATTERNS)
    ```

## 4. Validation Gates

### Gate 1: Unit Tests - Empty Project

**Command**: `uv run pytest tests/test_detection.py::test_empty_project -v`

**Success Criteria**:
- Returns empty inventory with all 7 domain keys
- No exceptions on missing directories
- Completes in <100ms

### Gate 2: Unit Tests - Legacy Detection

**Command**: `uv run pytest tests/test_detection.py::test_detect_legacy_files -v`

**Success Criteria**:
- Detects files in PRPs/ and examples/
- Detects context-engineering/ CE 1.0 structure
- Returns files grouped by correct domain

### Gate 3: Unit Tests - Symlink Resolution

**Command**: `uv run pytest tests/test_detection.py::test_symlink_resolution -v`

**Success Criteria**:
- Resolves CLAUDE.md symlink correctly
- Detects circular symlinks without crash
- Skips broken symlinks gracefully

### Gate 4: Unit Tests - Garbage Filtering

**Command**: `uv run pytest tests/test_detection.py::test_garbage_filtering -v`

**Success Criteria**:
- Filters *REPORT*.md files
- Filters *INITIAL*.md files
- Filters *-summary.md, *-analysis.md files
- Filters .backup, ~, .tmp, .log files
- Keeps valid PRPs and examples

### Gate 5: Integration Test - Full Scan

**Command**: `uv run pytest tests/test_detection.py::test_full_scan_integration -v`

**Success Criteria**:
- `scan_all()` returns Dict with 7 keys
- All values are List[Path]
- No duplicate files in inventory
- Performance: <1s for 100 files

## 5. Testing Strategy

### Test Framework

pytest

### Test Command

```bash
cd tools
uv run pytest tests/test_detection.py -v
```

### Test Structure

**Test File**: `tools/tests/test_detection.py`

**Test Cases**:
1. `test_empty_project` - Greenfield project (0 files)
2. `test_detect_prps` - Detect PRPs in multiple locations
3. `test_detect_examples` - Detect examples in multiple locations
4. `test_detect_ce_10_structure` - Detect context-engineering/ CE 1.0
5. `test_resolve_symlinks` - CLAUDE.md symlink resolution
6. `test_circular_symlinks` - Circular symlink detection
7. `test_broken_symlinks` - Broken symlink handling
8. `test_garbage_filtering` - Filter REPORT/INITIAL/summary/analysis
9. `test_backup_filtering` - Filter .backup/~/etc
10. `test_full_scan_integration` - End-to-end scan

**Test Fixtures**:
```python
@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project structure for testing."""
    project = tmp_path / "project"
    project.mkdir()

    # Create directories
    (project / "PRPs").mkdir()
    (project / "examples").mkdir()
    (project / ".claude" / "commands").mkdir(parents=True)
    (project / ".serena" / "memories").mkdir(parents=True)

    return project
```

### Coverage Requirements

- Unit test coverage: ≥ 90%
- All methods in LegacyFileDetector tested
- Edge cases: empty dirs, missing dirs, symlinks, garbage files

## 6. Rollout Plan

### Phase 1: Development

1. Create `tools/ce/blending/detection.py` module
2. Implement `LegacyFileDetector` class with all methods
3. Create test file with 10 test cases
4. Run tests and iterate until all pass

### Phase 2: Review

1. Self-review code for:
   - KISS principle (simple solutions)
   - 50-line function limit
   - Actionable error messages
   - No silent failures
2. Verify test coverage ≥ 90%
3. Run `uv run pytest tests/test_detection.py -v --cov=ce/blending/detection`

### Phase 3: Integration

1. Merge to worktree branch: `prp-34-2-1-detection-module`
2. Verify no conflicts with PRP-34.1.1
3. Ready for stage 2 parallel execution
4. Prepare for merge order 2 (after PRP-34.2.1)

---

## Batch Generation Metadata

**Batch ID**: 34
**Stage**: stage-2-parallel
**Execution Order**: 2
**Merge Order**: 2
**Conflict Potential**: NONE

**Worktree Setup**:
```bash
git worktree add ../ctx-eng-plus-prp-34-2-1 -b prp-34-2-1-detection-module
cd ../ctx-eng-plus-prp-34-2-1
# Execute PRP-34.2.1
```

**Dependencies**:
- **Depends on**: PRP-34.1.1 (must complete first)
- **Blocks**: PRP-34.3.1, PRP-34.3.2 (stage 3 depends on stage 2)

**Parallel Execution**:
- Can execute in parallel with other stage-2 PRPs
- No file conflicts expected (dedicated module path)

---

## Research Findings

### Implementation Notes

**Module Organization**:
- Path: `tools/ce/blending/detection.py`
- Size: ~200 lines (well under 500-line limit)
- Functions: 5 methods (~40 lines each, under 50-line limit)

**Symlink Handling Strategy**:
- Use `Path.is_symlink()` to detect
- Use `Path.resolve(strict=True)` to resolve
- Track visited symlinks in Set to detect circular refs
- Catch OSError/RuntimeError for broken symlinks

**Garbage Filtering Strategy**:
- Simple substring matching in filename
- Patterns: REPORT, INITIAL, summary, analysis, PLAN, .backup, ~, .tmp, .log
- Case-sensitive (matches common patterns)

**Performance Considerations**:
- Use `rglob("*.md")` for directory scanning (efficient)
- Early exit on missing directories (no wasted work)
- Symlink resolution cached via visited set
- Target: <1s for 100 files

### Example Usage

```python
from ce.blending.detection import LegacyFileDetector

detector = LegacyFileDetector(Path("/project/root"))
inventory = detector.scan_all()

print(f"Found {len(inventory['prps'])} PRPs")
print(f"Found {len(inventory['examples'])} examples")
print(f"Found {len(inventory['memories'])} memories")

# Example output:
# Found 23 PRPs
# Found 5 examples
# Found 18 memories
```
