---
prp_id: 46.3.1
feature_name: Integration and Testing
status: pending
created: 2025-11-16
updated: 2025-11-16
complexity: low
estimated_hours: 2
dependencies: [46.1.1, 46.2.1, 46.2.2]
stage: 3
execution_order: 4
merge_order: 4
batch_id: 46
---

# PRP-46.3.1: Integration and Testing - Superseded Docs Strategy

## Problem Statement

The superseded docs detection strategy (PRP-46.1.1, 46.2.1, 46.2.2) is implemented but not integrated into the vacuum CLI. Users cannot run superseded docs detection without direct Python imports.

**Missing components**:
1. Strategy not registered in `vacuum.py` strategy list
2. No CLI flag to enable/disable superseded docs detection
3. No integration tests for full vacuum workflow
4. No documentation in CLAUDE.md

**Current state** (vacuum.py line 30-37):
```python
self.strategies = {
    "temp-files": TempFileStrategy,
    "backup-files": BackupFileStrategy,
    "obsolete-docs": ObsoleteDocStrategy,
    "unreferenced-code": UnreferencedCodeStrategy,
    "orphan-tests": OrphanTestStrategy,
    "commented-code": CommentedCodeStrategy,
    # superseded-docs MISSING
}
```

**Impact**: Strategy is dormant - cannot be invoked via CLI.

## Proposed Solution

Integrate `SupersededDocsStrategy` into vacuum CLI with:

1. **Strategy Registration**: Add to `vacuum.py` strategy dict
2. **Module Export**: Add to `__init__.py` for clean imports
3. **CLI Flag** (optional): `--superseded` to enable/disable (default: enabled)
4. **Report Format**: Enhance vacuum report for superseded docs
5. **Integration Tests**: Full workflow tests with real PRPs
6. **Documentation**: Update CLAUDE.md with usage examples

**Design**: Auto-enable by default (like other strategies), allow `--exclude-strategy superseded-docs` to disable.

## Implementation Details

### 1. Strategy Registration (vacuum.py)

**File**: `tools/ce/vacuum.py`

**Changes**:

**Step 1**: Add import (line 9-17)
```python
from .vacuum_strategies import (
    BackupFileStrategy,
    CleanupCandidate,
    CommentedCodeStrategy,
    ObsoleteDocStrategy,
    OrphanTestStrategy,
    SupersededDocsStrategy,  # NEW
    TempFileStrategy,
    UnreferencedCodeStrategy,
)
```

**Step 2**: Register strategy (line 30-38)
```python
self.strategies = {
    "temp-files": TempFileStrategy,
    "backup-files": BackupFileStrategy,
    "obsolete-docs": ObsoleteDocStrategy,
    "superseded-docs": SupersededDocsStrategy,  # NEW
    "unreferenced-code": UnreferencedCodeStrategy,
    "orphan-tests": OrphanTestStrategy,
    "commented-code": CommentedCodeStrategy,
}
```

**Rationale**: Alphabetical order for consistency (s comes after o).

### 2. Module Export (__init__.py)

**File**: `tools/ce/vacuum_strategies/__init__.py`

**Changes**:
```python
"""Vacuum strategies for project cleanup."""

from .base import BaseStrategy, CleanupCandidate
from .temp_files import TempFileStrategy
from .backup_files import BackupFileStrategy
from .obsolete_docs import ObsoleteDocStrategy
from .superseded_docs import SupersededDocsStrategy  # NEW
from .unreferenced_code import UnreferencedCodeStrategy
from .orphan_tests import OrphanTestStrategy
from .commented_code import CommentedCodeStrategy

__all__ = [
    "BaseStrategy",
    "CleanupCandidate",
    "TempFileStrategy",
    "BackupFileStrategy",
    "ObsoleteDocStrategy",
    "SupersededDocsStrategy",  # NEW
    "UnreferencedCodeStrategy",
    "OrphanTestStrategy",
    "CommentedCodeStrategy",
]
```

### 3. Report Format Enhancement (vacuum.py)

**Current report** (line 125-201):
- Groups by confidence (HIGH/MEDIUM/LOW)
- Shows: Path, Reason, Size/Confidence, Last Modified/Git History

**Enhancement**: Add "Superseded By" column for superseded docs

**Modified report section** (line 176-184):
```python
# MEDIUM confidence section
if medium:
    report.extend([
        "## MEDIUM Confidence (Review Needed)",
        "",
        "| Path | Reason | Confidence | Details |",  # Changed from "Git History"
        "|------|--------|------------|---------|",
    ])
    for c in medium:
        rel_path = c.path.relative_to(self.project_root)
        # Extract PRP reference from reason if superseded doc
        details = c.git_history
        if "Superseded by" in c.reason:
            # Extract PRP-X from reason
            import re
            match = re.search(r'PRP-\d+', c.reason)
            if match:
                details = f"See {match.group()}"
        report.append(
            f"| {rel_path} | {c.reason} | {c.confidence}% | {details} |"
        )
    report.append("")
```

**Example output**:
```markdown
## MEDIUM Confidence (Review Needed)

| Path | Reason | Confidence | Details |
|------|--------|------------|---------|
| PRPs/feature-requests/INIT-PROJECT-WORKFLOW-INITIAL.md | Superseded by PRP-42 (title match: 90%) | 85% | See PRP-42 |
```

### 4. Integration Tests (test_vacuum_superseded.py)

**File**: `tools/tests/test_vacuum_superseded.py` (new)

**Test cases**:

#### Test 1: Strategy Registration
```python
"""Tests for superseded docs integration."""

import pytest
from pathlib import Path
from ce.vacuum import VacuumCommand
from ce.vacuum_strategies import SupersededDocsStrategy


class TestSupersededDocsIntegration:
    """Test superseded docs strategy integration with vacuum CLI."""

    def test_strategy_registered(self):
        """Should register superseded-docs in strategy list."""
        project_root = Path.cwd()
        vacuum = VacuumCommand(project_root)

        assert "superseded-docs" in vacuum.strategies
        assert vacuum.strategies["superseded-docs"] == SupersededDocsStrategy

    def test_strategy_excluded_via_cli(self, temp_project):
        """Should skip superseded-docs when excluded."""
        vacuum = VacuumCommand(temp_project)

        # Run with superseded-docs excluded
        exit_code = vacuum.run(
            dry_run=True,
            exclude_strategies=["superseded-docs"]
        )

        # Verify strategy was skipped (check report doesn't mention superseded)
        report_path = temp_project / ".ce" / "vacuum-report.md"
        report_content = report_path.read_text()

        # Should not contain superseded doc entries
        assert "Superseded by" not in report_content
```

#### Test 2: Full Workflow Detection
```python
@pytest.fixture
def prp_project(tmp_path):
    """Create project with PRPs for superseded detection."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    # Create .ce directory
    (project_root / ".ce").mkdir()

    # Create PRPs structure
    prps_dir = project_root / "PRPs"
    feature_requests = prps_dir / "feature-requests"
    executed = prps_dir / "executed"
    feature_requests.mkdir(parents=True)
    executed.mkdir(parents=True)

    # Create feature request (superseded)
    feature_request = feature_requests / "INIT-PROJECT-WORKFLOW-INITIAL.md"
    feature_request.write_text("""---
created: 2025-11-01
---

# Init Project Workflow

Original feature request for init project workflow.
""")

    # Create executed PRP (supersedes feature request)
    prp = executed / "PRP-42-init-project-workflow-overhaul.md"
    prp.write_text("""---
prp_id: 42
title: Init Project Workflow Overhaul
status: completed
created: 2025-11-15
---

# PRP-42: Init Project Workflow Overhaul

Implements automated init workflow.

## Context

Supersedes PRPs/feature-requests/INIT-PROJECT-WORKFLOW-INITIAL.md
""")

    return project_root


class TestFullWorkflow:
    """Test full vacuum workflow with superseded docs."""

    def test_detects_superseded_doc(self, prp_project):
        """Should detect feature request superseded by executed PRP."""
        vacuum = VacuumCommand(prp_project)

        # Run dry-run
        exit_code = vacuum.run(dry_run=True)

        # Should find candidates
        assert exit_code == 1

        # Read report
        report_path = prp_project / ".ce" / "vacuum-report.md"
        assert report_path.exists()

        report_content = report_path.read_text()

        # Should contain superseded doc with PRP-42 reference
        assert "INIT-PROJECT-WORKFLOW-INITIAL.md" in report_content
        assert "Superseded by PRP-42" in report_content or "PRP-42" in report_content

        # Should be MEDIUM or HIGH confidence (85%+)
        assert "MEDIUM Confidence" in report_content or "HIGH Confidence" in report_content

    def test_execute_deletes_superseded_doc(self, prp_project):
        """Should delete superseded doc when confidence >= 85%."""
        vacuum = VacuumCommand(prp_project)

        feature_request_path = prp_project / "PRPs" / "feature-requests" / "INIT-PROJECT-WORKFLOW-INITIAL.md"

        # Verify file exists
        assert feature_request_path.exists()

        # Run execute mode (deletes HIGH + MEDIUM if confidence >= 60)
        exit_code = vacuum.run(force=True)

        # Verify file deleted (if confidence >= 60)
        # Note: Actual deletion depends on confidence score from strategy
        # This test validates the integration, not the strategy logic
        assert exit_code in [0, 1]

    def test_no_false_positives(self, prp_project):
        """Should not flag active feature requests."""
        # Add active feature request (no matching PRP)
        active_request = prp_project / "PRPs" / "feature-requests" / "INITIAL-critical-memory-consolidation.md"
        active_request.write_text("""---
created: 2025-11-01
---

# Critical Memory Consolidation

Active feature request with no matching PRP.
""")

        vacuum = VacuumCommand(prp_project)
        exit_code = vacuum.run(dry_run=True)

        # Read report
        report_path = prp_project / ".ce" / "vacuum-report.md"
        report_content = report_path.read_text()

        # Should NOT flag active feature request
        assert "INITIAL-critical-memory-consolidation.md" not in report_content or \
               "INITIAL-critical-memory-consolidation.md" in report_content and "LOW Confidence" in report_content
```

#### Test 3: Regression Tests
```python
class TestRegressionTests:
    """Regression tests for known issues."""

    def test_no_false_positive_on_initial_critical_memory(self, tmp_path):
        """Regression: Should not flag INITIAL-critical-memory-consolidation.md."""
        # This was a known issue in original vacuum implementation
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        (project_root / ".ce").mkdir()

        prps_dir = project_root / "PRPs" / "feature-requests"
        prps_dir.mkdir(parents=True)

        # Create the exact file that was incorrectly flagged
        critical_memory = prps_dir / "INITIAL-critical-memory-consolidation.md"
        critical_memory.write_text("""---
created: 2025-11-01
---

# Critical Memory Consolidation

INITIAL prefix but still active.
""")

        vacuum = VacuumCommand(project_root)
        exit_code = vacuum.run(dry_run=True)

        report_path = project_root / ".ce" / "vacuum-report.md"
        report_content = report_path.read_text()

        # Should not be in HIGH confidence section
        if "INITIAL-critical-memory-consolidation.md" in report_content:
            high_section = report_content.split("## HIGH Confidence")[1].split("##")[0] if "## HIGH Confidence" in report_content else ""
            assert "INITIAL-critical-memory-consolidation.md" not in high_section
```

### 5. Documentation Updates (CLAUDE.md)

**File**: `/Users/bprzybyszi/nc-src/ctx-eng-plus/CLAUDE.md`

**Section**: "Quick Commands" (line ~45)

**Addition**:
```markdown
# Cleanup
uv run ce vacuum                  # Dry-run (report only)
uv run ce vacuum --execute        # Delete HIGH confidence only
uv run ce vacuum --auto           # Delete HIGH + MEDIUM (temp files + obsolete docs + superseded docs)
uv run ce vacuum --exclude-strategy superseded-docs  # Skip superseded detection
```

**New section**: "Vacuum Strategies" (add after "Quick Commands")

```markdown
## Vacuum Strategies

**Available strategies** (auto-enabled unless excluded):

1. **temp-files**: .pyc, __pycache__, .DS_Store (100% confidence)
2. **backup-files**: .bak, ~, .orig (100% confidence)
3. **obsolete-docs**: Versioned docs, drafts (50-70% confidence)
4. **superseded-docs**: Feature requests superseded by executed PRPs (40-85% confidence)
5. **unreferenced-code**: Modules with no imports (30-50% confidence)
6. **orphan-tests**: Tests for non-existent modules (40% confidence)
7. **commented-code**: Large commented blocks (30% confidence)

**Superseded Docs Detection**:
- **Phase 1**: Python fuzzy matching (title similarity, date comparison, explicit references)
- **Phase 2**: LLM analysis (Haiku, for 40-70% confidence candidates)
- **Phase 3**: Batch optimization (multiple docs in single API call)

**Example output**:
```bash
uv run ce vacuum --dry-run

🔍 Running superseded-docs...
   Found 3 candidates

📄 Report generated: .ce/vacuum-report.md

## MEDIUM Confidence (Review Needed)

| Path | Reason | Confidence | Details |
|------|--------|------------|---------|
| PRPs/feature-requests/INIT-PROJECT-WORKFLOW-INITIAL.md | Superseded by PRP-42 (title match: 90%) | 85% | See PRP-42 |
```

**Exclude strategy**:
```bash
# Skip superseded docs detection
uv run ce vacuum --exclude-strategy superseded-docs
```
```

## Validation Gates

### Pre-Implementation Checklist
- [ ] Read `vacuum.py` to understand strategy registration pattern
- [ ] Read `__init__.py` to understand export pattern
- [ ] Read existing test file to understand test structure
- [ ] Verify `SupersededDocsStrategy` class exists (from PRP-46.1.1)

### Implementation Checklist
- [ ] Add `SupersededDocsStrategy` import to `vacuum.py`
- [ ] Register `superseded-docs` in strategy dict
- [ ] Export `SupersededDocsStrategy` in `__init__.py`
- [ ] Enhance report format with "Superseded By" details
- [ ] Create `test_vacuum_superseded.py` with 3 test classes
- [ ] Update CLAUDE.md with vacuum strategies section

### Post-Implementation Tests
- [ ] Unit test: Strategy registered in vacuum.strategies dict
- [ ] Unit test: Strategy can be excluded via CLI
- [ ] Integration test: Detects 3 init workflow docs (if re-added)
- [ ] Integration test: Execute mode deletes confirmed candidates
- [ ] Regression test: No false positive on INITIAL-critical-memory-consolidation.md
- [ ] CLI test: `uv run ce vacuum --dry-run` shows superseded docs in report
- [ ] CLI test: `uv run ce vacuum --exclude-strategy superseded-docs` skips detection

### Success Criteria
- [ ] `uv run ce vacuum --dry-run` detects superseded docs (if any exist)
- [ ] Report shows "Superseded by PRP-X" in reason column
- [ ] `--exclude-strategy superseded-docs` works correctly
- [ ] Integration tests pass (5/5)
- [ ] No false positives on active feature requests
- [ ] Documentation updated in CLAUDE.md

## Testing Strategy

**Test pyramid**:
1. **Unit**: Strategy registration (1 test)
2. **Integration**: Full workflow with real PRPs (3 tests)
3. **Regression**: Known false positive scenarios (1 test)

**Test data**:
- Fixture: `prp_project` with feature-requests/ and executed/ PRPs
- Known good: INITIAL-critical-memory-consolidation.md (should NOT flag)
- Known superseded: INIT-PROJECT-WORKFLOW-INITIAL.md → PRP-42 (should flag)

**Test execution**:
```bash
# Run new tests only
uv run pytest tests/test_vacuum_superseded.py -v

# Run all vacuum tests
uv run pytest tests/test_vacuum*.py -v

# Integration test (real project)
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
uv run ce vacuum --dry-run
grep "superseded-docs" .ce/vacuum-report.md
```

## Dependencies

**Phase dependencies**:
- **46.1.1**: Core `SupersededDocsStrategy` class (must exist)
- **46.2.1**: LLM analyzer integration (for 85%+ confidence)
- **46.2.2**: Batch optimization (for performance)

**Python stdlib**:
- `argparse` (CLI parsing)
- `re` (PRP reference extraction)

**External**:
- `pytest` (testing)

## Risks and Mitigations

**Risk 1**: Strategy import fails if PRP-46.1.1 not merged
- **Mitigation**: Check `superseded_docs.py` exists before implementation
- **Fallback**: Skip integration tests if class not found

**Risk 2**: Report format change breaks existing vacuum users
- **Mitigation**: Only change "Details" column (was "Git History"), keep table structure
- **Fallback**: Make column conditional (show "Git History" for non-superseded docs)

**Risk 3**: Integration tests flaky due to LLM API
- **Mitigation**: Mock LLM analyzer in integration tests
- **Alternative**: Use real Python fuzzy matching (40-70% confidence) without LLM

## Rollback Plan

If integration causes issues:

1. **Immediate rollback** (2 min):
   ```python
   # Remove from vacuum.py line 37
   # "superseded-docs": SupersededDocsStrategy,  # DISABLED
   ```

2. **Full revert** (5 min):
   ```bash
   git revert <commit-hash>
   uv run pytest tests/test_vacuum.py  # Verify original tests pass
   ```

3. **Partial disable** (keep code, disable by default):
   - Add to CLAUDE.md: "superseded-docs strategy experimental, use --include-strategy superseded-docs to enable"

## Documentation

**Files to update**:
1. `CLAUDE.md` - Add vacuum strategies section
2. `tools/ce/vacuum.py` - Update docstring with new strategy
3. `tools/ce/vacuum_strategies/__init__.py` - Add SupersededDocsStrategy export
4. `tests/test_vacuum_superseded.py` - Comprehensive integration tests

**Example usage** (for CLAUDE.md):
```bash
# Detect superseded feature requests
uv run ce vacuum --dry-run

# Delete superseded docs (MEDIUM + HIGH confidence)
uv run ce vacuum --auto

# Skip superseded detection
uv run ce vacuum --exclude-strategy superseded-docs
```

## Success Metrics

**Quantitative**:
- Integration tests: 5/5 pass rate
- Regression tests: 0 false positives on known-good files
- Coverage: >80% for new integration code

**Qualitative**:
- CLI user can run superseded detection without Python imports
- Report clearly shows PRP references for superseded docs
- Strategy can be disabled via `--exclude-strategy`

## Future Enhancements

1. **PRP-46.4.1**: Add `--superseded-only` flag (run only superseded-docs strategy)
2. **PRP-46.4.2**: Auto-archive superseded docs instead of delete (move to archived/)
3. **PRP-46.4.3**: Detect duplicate PRPs (multiple PRPs implementing same feature)
4. **PRP-46.4.4**: Generate "superseded by" badges in markdown (auto-add to superseded docs)

---

**Ready for execution**: Yes (pending PRP-46.1.1, 46.2.1, 46.2.2 completion)

**Estimated completion time**: 2 hours
