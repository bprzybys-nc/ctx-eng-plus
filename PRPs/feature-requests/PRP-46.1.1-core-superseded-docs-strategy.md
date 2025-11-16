---
prp_id: 46.1.1
feature_name: Core Superseded Docs Strategy
status: pending
created: 2025-11-16
updated: 2025-11-16
complexity: low
estimated_hours: 2
dependencies: []
stage: 1
execution_order: 1
merge_order: 1
batch_id: 46
---

# PRP-46.1.1: Core Superseded Docs Strategy

## TL;DR

Implement Python-based fuzzy matching to detect feature-requests superseded by executed PRPs. Uses title matching, date comparison, and related-docs detection to flag cleanup candidates with 40-85% confidence. Enables vacuum to auto-identify obsolete planning docs without LLM overhead.

## Context

### Problem

Current vacuum missed 3 init workflow docs superseded by PRP-42:

```
PRPs/feature-requests/
  INIT-PROJECT-WORKFLOW-INITIAL.md              (original request)
  INIT-PROJECT-WORKFLOW-ROOT-CAUSE-ANALYSIS.md  (diagnostic)
  INIT-PROJECT-WORKFLOW-OVERHAUL-PLAN.md        (implementation plan)

PRPs/executed/
  PRP-42-init-project-workflow-overhaul.md      (completed - contains all content)
```

Manual cleanup revealed relationship, but vacuum flagged them as LOW confidence (55%) requiring manual review.

**Root cause:** Current `obsolete_docs` strategy uses only:
- Filename patterns (`-SUMMARY-`, `-PLAN-`, `-ANALYSIS-`)
- Simple content keywords (`**date**: 20`, `draft`)
- No relationship mapping between `feature-requests/` and `executed/`

### Existing Pattern

From `tools/ce/vacuum_strategies/obsolete_docs.py`:

```python
class ObsoleteDocStrategy(BaseStrategy):
    """Find obsolete documentation files."""

    TEMP_DOC_PREFIXES = [
        "ANALYSIS-",
        "CHANGELIST-",
        "REPORT-",
        "IMPLEMENTATION-",
        "DEPLOYMENT",
        "VERIFICATION-",
        "VALIDATION-",
        "DENOISE_",
    ]

    def find_candidates(self) -> List[CleanupCandidate]:
        """Find obsolete documentation files."""
        candidates = []

        # Find all markdown files
        for md_file in self.scan_path.glob("**/*.md"):
            if not md_file.exists() or md_file.is_dir():
                continue

            # Skip if protected
            if self.is_protected(md_file):
                continue

            stem = md_file.stem
            name = md_file.name

            # Check for temporary analysis docs
            temp_doc_match = self._is_temp_analysis_doc(name, stem)
            content_marker = None

            # If filename doesn't match, check content
            if not temp_doc_match:
                content_marker = self._check_doc_content(md_file)

            if temp_doc_match or content_marker:
                # Generate candidate with confidence
                confidence = 70
                if self.is_recently_active(md_file, days=30):
                    confidence = 55

                candidate = CleanupCandidate(
                    path=md_file,
                    reason=reason,
                    confidence=confidence,
                    size_bytes=self.get_file_size(md_file),
                    last_modified=self.get_last_modified(md_file),
                    git_history=self.get_git_history(md_file),
                )
                candidates.append(candidate)

        return candidates
```

**Key API**: `BaseStrategy.find_candidates() -> List[CleanupCandidate]`

### Solution Approach

New `SupersededDocsStrategy` with semantic relationship detection:

**Phase 1 Detection (Python only)**:
1. Extract titles from feature-requests and executed PRPs
2. Fuzzy match on titles using `difflib.SequenceMatcher`
3. Compare dates (feature-request older than PRP)
4. Detect explicit references ("See PRP-42", "Implemented in PRP-42")
5. **Related docs detection**: Build reverse index of .md filenames mentioned in PRPs
6. Return candidates with 40-85% confidence

**Confidence Levels**:
- **40-60%**: Title similarity only (weak match)
- **60-75%**: Title + date + explicit reference
- **75-85%**: Title + date + explicit reference + related docs boost (+30%)

**Example Detection**:

```python
# Input
feature_request = "INIT-PROJECT-WORKFLOW-INITIAL.md"
  title: "Init Project Workflow"
  created: "2025-10-01"

executed_prp = "PRP-42-init-project-workflow-overhaul.md"
  title: "Init Project Workflow Overhaul"
  created: "2025-11-01"
  content: "...supersedes INIT-PROJECT-WORKFLOW-INITIAL.md..."

# Detection
title_match = fuzzy_match("Init Project Workflow", "Init Project Workflow Overhaul")
  # Returns: 0.85 (85% similarity)

date_check = feature_request.created < executed_prp.created
  # Returns: True

related_docs_boost = "INIT-PROJECT-WORKFLOW-INITIAL.md" in executed_prp.content
  # Returns: True → +30% confidence

# Final Confidence
base_confidence = 55%  # Title + date
boosted_confidence = 55% + 30% = 85%  # HIGH confidence

# Output
CleanupCandidate(
  path="PRPs/feature-requests/INIT-PROJECT-WORKFLOW-INITIAL.md",
  reason="Superseded by PRP-42 (title match: 85%, date: older, mentioned in PRP)",
  confidence=85,
  ...
)
```

### Technical Details

**Title Extraction**:
```python
def _extract_title(self, md_file: Path) -> str:
    """Extract title from markdown header or YAML frontmatter."""
    with open(md_file, "r", encoding="utf-8") as f:
        # Check YAML frontmatter
        if f.readline().strip() == "---":
            for line in f:
                if line.strip() == "---":
                    break
                if line.startswith("title:") or line.startswith("feature_name:"):
                    return line.split(":", 1)[1].strip().strip('"')

        # Check first markdown header
        f.seek(0)
        for line in f:
            if line.startswith("# "):
                return line[2:].strip()

    # Fallback to filename
    return md_file.stem.replace("-", " ")
```

**Fuzzy Matching**:
```python
from difflib import SequenceMatcher

def _fuzzy_match(self, title1: str, title2: str) -> float:
    """Calculate fuzzy match ratio (0.0-1.0)."""
    # Normalize: lowercase, remove common words
    def normalize(title: str) -> str:
        words = title.lower().split()
        stopwords = {"the", "a", "an", "and", "or", "but"}
        return " ".join(w for w in words if w not in stopwords)

    norm1 = normalize(title1)
    norm2 = normalize(title2)

    return SequenceMatcher(None, norm1, norm2).ratio()
```

**Related Docs Detection**:
```python
def _build_related_docs_index(self) -> dict[str, list[str]]:
    """Build reverse index: {feature-request-filename: [PRP-IDs that mention it]}."""
    index = {}

    # Scan all executed PRPs
    prp_dir = self.project_root / "PRPs" / "executed"
    for prp_file in prp_dir.glob("PRP-*.md"):
        content = prp_file.read_text(encoding="utf-8")

        # Extract all .md filenames from PRP
        md_refs = re.findall(r'\b([A-Z][A-Z0-9-]+\.md)\b', content)

        for ref in md_refs:
            if ref not in index:
                index[ref] = []
            index[ref].append(prp_file.stem)

    return index
```

**Date Comparison**:
```python
def _parse_date(self, md_file: Path) -> datetime | None:
    """Parse creation date from YAML frontmatter."""
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            if f.readline().strip() == "---":
                for line in f:
                    if line.strip() == "---":
                        break
                    if line.startswith("created:"):
                        date_str = line.split(":", 1)[1].strip().strip('"')
                        return datetime.fromisoformat(date_str)
    except Exception:
        pass

    return None
```

## Implementation Steps

### Step 1: Create SupersededDocsStrategy Class (30 min)

Create `tools/ce/vacuum_strategies/superseded_docs.py`:

```python
"""Strategy for finding superseded documentation."""

import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import List

from .base import BaseStrategy, CleanupCandidate


class SupersededDocsStrategy(BaseStrategy):
    """Find feature-requests superseded by executed PRPs."""

    def __init__(self, project_root: Path, scan_path: Path):
        """Initialize strategy."""
        super().__init__(project_root, scan_path)
        self.related_docs_index = {}

    def find_candidates(self) -> List[CleanupCandidate]:
        """Find superseded documentation files."""
        candidates = []

        # Build related docs index (reverse lookup)
        self.related_docs_index = self._build_related_docs_index()

        # Scan feature-requests directory
        feature_requests_dir = self.project_root / "PRPs" / "feature-requests"
        if not feature_requests_dir.exists():
            return candidates

        # Get all executed PRPs for comparison
        executed_prps = self._get_executed_prps()

        # Check each feature request
        for feature_req in feature_requests_dir.glob("*.md"):
            if not feature_req.exists() or feature_req.is_dir():
                continue

            # Skip if protected
            if self.is_protected(feature_req):
                continue

            # Try to find matching executed PRP
            match_result = self._find_matching_prp(feature_req, executed_prps)

            if match_result:
                prp_id, confidence, reason = match_result

                candidate = CleanupCandidate(
                    path=feature_req,
                    reason=f"Superseded by {prp_id}: {reason}",
                    confidence=confidence,
                    size_bytes=self.get_file_size(feature_req),
                    last_modified=self.get_last_modified(feature_req),
                    git_history=self.get_git_history(feature_req),
                )
                candidates.append(candidate)

        return candidates

    def _build_related_docs_index(self) -> dict[str, list[str]]:
        """Build reverse index: {filename: [PRP-IDs that mention it]}."""
        # Implementation from Technical Details section
        pass

    def _get_executed_prps(self) -> list[tuple[Path, str, datetime | None]]:
        """Get all executed PRPs with metadata."""
        # Implementation: Return list of (path, title, created_date)
        pass

    def _find_matching_prp(
        self,
        feature_req: Path,
        executed_prps: list[tuple[Path, str, datetime | None]]
    ) -> tuple[str, int, str] | None:
        """Find matching executed PRP for feature request."""
        # Implementation: Return (prp_id, confidence, reason) or None
        pass

    def _extract_title(self, md_file: Path) -> str:
        """Extract title from markdown header or YAML frontmatter."""
        # Implementation from Technical Details section
        pass

    def _fuzzy_match(self, title1: str, title2: str) -> float:
        """Calculate fuzzy match ratio (0.0-1.0)."""
        # Implementation from Technical Details section
        pass

    def _parse_date(self, md_file: Path) -> datetime | None:
        """Parse creation date from YAML frontmatter."""
        # Implementation from Technical Details section
        pass

    def _detect_explicit_reference(self, content: str, prp_id: str) -> bool:
        """Check if content explicitly references PRP."""
        patterns = [
            f"see {prp_id}",
            f"implemented in {prp_id}",
            f"superseded by {prp_id}",
            f"replaced by {prp_id}",
        ]
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in patterns)
```

### Step 2: Implement Title Extraction (15 min)

Complete `_extract_title()` method:
- Check YAML frontmatter for `title:` or `feature_name:`
- Fallback to first markdown header (`# Title`)
- Fallback to filename (stem with `-` replaced by spaces)

### Step 3: Implement Fuzzy Matching (15 min)

Complete `_fuzzy_match()` method:
- Normalize titles (lowercase, remove stopwords)
- Use `difflib.SequenceMatcher` for ratio calculation
- Return float 0.0-1.0

### Step 4: Implement Date Comparison (15 min)

Complete `_parse_date()` method:
- Parse YAML frontmatter `created:` field
- Handle ISO date format (`2025-10-01`)
- Return `datetime` or `None`

### Step 5: Implement Explicit Reference Detection (10 min)

Complete `_detect_explicit_reference()` method:
- Check for patterns: "see PRP-X", "implemented in PRP-X", etc.
- Case-insensitive matching
- Return boolean

### Step 6: Implement Related Docs Detection (20 min)

Complete `_build_related_docs_index()` method:
- Scan all executed PRPs
- Extract all .md filenames using regex
- Build reverse index: `{filename: [PRP-IDs]}`

### Step 7: Implement Matching Logic (15 min)

Complete `_find_matching_prp()` method:
- For each executed PRP:
  - Calculate title similarity
  - Check date (feature-request older?)
  - Check explicit references
  - Check related docs index
- Calculate confidence (40-85%)
- Return best match or None

**Confidence Calculation**:
```python
def _calculate_confidence(
    self,
    title_similarity: float,
    date_older: bool,
    explicit_ref: bool,
    related_docs_boost: bool,
) -> int:
    """Calculate confidence score (0-100)."""
    # Base confidence from title similarity
    confidence = int(title_similarity * 60)  # 0-60%

    # Date boost
    if date_older:
        confidence += 10

    # Explicit reference boost
    if explicit_ref:
        confidence += 15

    # Related docs boost
    if related_docs_boost:
        confidence += 30

    # Cap at 85% (leave room for LLM analysis in Phase 2)
    return min(confidence, 85)
```

### Step 8: Register Strategy in Vacuum (5 min)

Edit `tools/ce/vacuum.py`:

```python
from .vacuum_strategies import (
    BackupFileStrategy,
    CleanupCandidate,
    CommentedCodeStrategy,
    ObsoleteDocStrategy,
    OrphanTestStrategy,
    SupersededDocsStrategy,  # ADD THIS
    TempFileStrategy,
    UnreferencedCodeStrategy,
)

class VacuumCommand:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.strategies = {
            "temp-files": TempFileStrategy,
            "backup-files": BackupFileStrategy,
            "obsolete-docs": ObsoleteDocStrategy,
            "superseded-docs": SupersededDocsStrategy,  # ADD THIS
            "unreferenced-code": UnreferencedCodeStrategy,
            "orphan-tests": OrphanTestStrategy,
            "commented-code": CommentedCodeStrategy,
        }
```

### Step 9: Export Strategy (2 min)

Edit `tools/ce/vacuum_strategies/__init__.py`:

```python
from .base import BaseStrategy, CleanupCandidate
from .backup_files import BackupFileStrategy
from .commented_code import CommentedCodeStrategy
from .obsolete_docs import ObsoleteDocStrategy
from .orphan_tests import OrphanTestStrategy
from .superseded_docs import SupersededDocsStrategy  # ADD THIS
from .temp_files import TempFileStrategy
from .unreferenced_code import UnreferencedCodeStrategy

__all__ = [
    "BaseStrategy",
    "CleanupCandidate",
    "BackupFileStrategy",
    "CommentedCodeStrategy",
    "ObsoleteDocStrategy",
    "OrphanTestStrategy",
    "SupersededDocsStrategy",  # ADD THIS
    "TempFileStrategy",
    "UnreferencedCodeStrategy",
]
```

## Validation Gates

**Gate 1: Unit Test - Title Fuzzy Matching**

```bash
cd tools
uv run pytest tests/test_superseded_docs.py::test_fuzzy_match_titles -v
```

Expected: Match "Init Project Workflow" across variants (85%+ similarity)

**Gate 2: Unit Test - Date Parsing**

```bash
uv run pytest tests/test_superseded_docs.py::test_parse_date_from_yaml -v
```

Expected: Extract creation date from YAML frontmatter

**Gate 3: Unit Test - Related Docs Index**

```bash
uv run pytest tests/test_superseded_docs.py::test_related_docs_index -v
```

Expected: Build reverse index of .md filenames mentioned in PRPs

**Gate 4: Integration Test - Detects Init Workflow Docs**

```bash
# Re-add test files (deleted in manual cleanup)
git checkout eb55221^ -- PRPs/feature-requests/INIT-PROJECT-WORKFLOW-*.md

# Run vacuum with superseded-docs strategy
cd tools
uv run ce vacuum --dry-run

# Check report
cat ../.ce/vacuum-report.md | grep "INIT-PROJECT-WORKFLOW"
```

Expected output:
```
| PRPs/feature-requests/INIT-PROJECT-WORKFLOW-INITIAL.md | Superseded by PRP-42: title match 85%, date: older, mentioned in PRP | 85% | ... |
| PRPs/feature-requests/INIT-PROJECT-WORKFLOW-ROOT-CAUSE-ANALYSIS.md | Superseded by PRP-42: title match 80%, date: older, mentioned in PRP | 80% | ... |
| PRPs/feature-requests/INIT-PROJECT-WORKFLOW-OVERHAUL-PLAN.md | Superseded by PRP-42: title match 85%, date: older, mentioned in PRP | 85% | ... |
```

**Gate 5: Integration Test - No False Positives**

```bash
# Verify valid feature requests not flagged
cat ../.ce/vacuum-report.md | grep "INITIAL-critical-memory-consolidation.md"
```

Expected: No output (file not flagged as candidate)

**Gate 6: Regression Test - Existing Strategies Still Work**

```bash
uv run ce vacuum --dry-run --exclude-strategy superseded-docs
```

Expected: No errors, existing strategies run normally

## Testing Strategy

### Unit Tests

Create `tools/tests/test_superseded_docs.py`:

```python
"""Unit tests for SupersededDocsStrategy."""

import pytest
from pathlib import Path
from datetime import datetime
from ce.vacuum_strategies.superseded_docs import SupersededDocsStrategy


@pytest.fixture
def strategy(tmp_path):
    """Create strategy instance with temp project."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "PRPs" / "feature-requests").mkdir(parents=True)
    (project_root / "PRPs" / "executed").mkdir(parents=True)

    return SupersededDocsStrategy(project_root, project_root)


def test_fuzzy_match_exact(strategy):
    """Test exact title match returns 1.0."""
    ratio = strategy._fuzzy_match("Init Project Workflow", "Init Project Workflow")
    assert ratio == 1.0


def test_fuzzy_match_similar(strategy):
    """Test similar titles return high ratio."""
    ratio = strategy._fuzzy_match(
        "Init Project Workflow",
        "Init Project Workflow Overhaul"
    )
    assert ratio > 0.8  # Should be 85%+


def test_fuzzy_match_different(strategy):
    """Test different titles return low ratio."""
    ratio = strategy._fuzzy_match(
        "Init Project Workflow",
        "Critical Memory Consolidation"
    )
    assert ratio < 0.5


def test_parse_date_from_yaml(strategy, tmp_path):
    """Test date extraction from YAML frontmatter."""
    md_file = tmp_path / "test.md"
    md_file.write_text("""---
created: 2025-10-01
---
# Test Document
""")

    date = strategy._parse_date(md_file)
    assert date == datetime(2025, 10, 1)


def test_parse_date_missing(strategy, tmp_path):
    """Test missing date returns None."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test Document")

    date = strategy._parse_date(md_file)
    assert date is None


def test_extract_title_from_yaml(strategy, tmp_path):
    """Test title extraction from YAML."""
    md_file = tmp_path / "test.md"
    md_file.write_text("""---
title: "Init Project Workflow"
---
# Other Header
""")

    title = strategy._extract_title(md_file)
    assert title == "Init Project Workflow"


def test_extract_title_from_header(strategy, tmp_path):
    """Test title extraction from markdown header."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Init Project Workflow\n\nContent...")

    title = strategy._extract_title(md_file)
    assert title == "Init Project Workflow"


def test_extract_title_fallback(strategy, tmp_path):
    """Test fallback to filename."""
    md_file = tmp_path / "INIT-PROJECT-WORKFLOW.md"
    md_file.write_text("Content...")

    title = strategy._extract_title(md_file)
    assert title == "INIT PROJECT WORKFLOW"


def test_detect_explicit_reference(strategy):
    """Test explicit PRP reference detection."""
    content = "This feature is implemented in PRP-42."
    assert strategy._detect_explicit_reference(content, "PRP-42")


def test_related_docs_index(strategy, tmp_path):
    """Test related docs index building."""
    # Create executed PRP that mentions feature-request
    prp_dir = tmp_path / "project" / "PRPs" / "executed"
    prp_file = prp_dir / "PRP-42-init-workflow.md"
    prp_file.write_text("""
# PRP-42: Init Workflow Overhaul

Supersedes INIT-PROJECT-WORKFLOW-INITIAL.md and related docs.
""")

    index = strategy._build_related_docs_index()
    assert "INIT-PROJECT-WORKFLOW-INITIAL.md" in index
    assert "PRP-42-init-workflow" in index["INIT-PROJECT-WORKFLOW-INITIAL.md"]


def test_calculate_confidence_high(strategy):
    """Test high confidence calculation."""
    confidence = strategy._calculate_confidence(
        title_similarity=0.85,
        date_older=True,
        explicit_ref=True,
        related_docs_boost=True,
    )
    assert confidence == 85  # 51 + 10 + 15 + 30 = 106 → capped at 85


def test_calculate_confidence_medium(strategy):
    """Test medium confidence calculation."""
    confidence = strategy._calculate_confidence(
        title_similarity=0.70,
        date_older=True,
        explicit_ref=False,
        related_docs_boost=False,
    )
    assert confidence == 52  # 42 + 10 = 52
```

### Integration Tests

Add to existing `tools/tests/test_vacuum.py`:

```python
def test_superseded_docs_detection(tmp_path):
    """Test superseded docs strategy integration."""
    # Setup project structure
    project_root = tmp_path / "project"
    (project_root / ".ce").mkdir(parents=True)
    (project_root / "PRPs" / "feature-requests").mkdir(parents=True)
    (project_root / "PRPs" / "executed").mkdir(parents=True)

    # Create feature request
    feature_req = project_root / "PRPs" / "feature-requests" / "INIT-PROJECT-WORKFLOW-INITIAL.md"
    feature_req.write_text("""---
created: 2025-10-01
---
# Init Project Workflow

Initial feature request for init workflow.
""")

    # Create executed PRP
    prp = project_root / "PRPs" / "executed" / "PRP-42-init-workflow.md"
    prp.write_text("""---
created: 2025-11-01
---
# PRP-42: Init Project Workflow Overhaul

Supersedes INIT-PROJECT-WORKFLOW-INITIAL.md.
""")

    # Run vacuum
    from ce.vacuum import VacuumCommand
    vacuum = VacuumCommand(project_root)
    exit_code = vacuum.run(dry_run=True)

    # Check report
    report_path = project_root / ".ce" / "vacuum-report.md"
    report = report_path.read_text()

    assert "INIT-PROJECT-WORKFLOW-INITIAL.md" in report
    assert "Superseded by PRP-42" in report
    assert exit_code == 1  # Candidates found
```

### Manual Verification

```bash
# Re-add test files
git checkout eb55221^ -- PRPs/feature-requests/INIT-PROJECT-WORKFLOW-*.md

# Run vacuum
cd tools
uv run ce vacuum --dry-run

# Verify detection
cat ../.ce/vacuum-report.md | grep -A 2 "INIT-PROJECT-WORKFLOW"

# Expected: All 3 files flagged with 80-85% confidence

# Cleanup
git checkout HEAD -- PRPs/feature-requests/INIT-PROJECT-WORKFLOW-*.md
```

## Rollout Plan

### Phase 1: Implementation (1.5 hours)

1. Create `superseded_docs.py` with class structure (30 min)
2. Implement helper methods (_extract_title, _fuzzy_match, _parse_date) (30 min)
3. Implement detection logic (_find_matching_prp, _calculate_confidence) (30 min)

### Phase 2: Integration (15 min)

1. Register strategy in `vacuum.py` (5 min)
2. Export strategy in `__init__.py` (2 min)
3. Verify CLI works: `uv run ce vacuum --help` (3 min)
4. Test dry-run: `uv run ce vacuum --dry-run` (5 min)

### Phase 3: Testing (15 min)

1. Write unit tests (10 min)
2. Run tests: `uv run pytest tests/test_superseded_docs.py -v` (2 min)
3. Run integration test with real files (3 min)

### Phase 4: Validation (15 min)

1. Re-add 3 init workflow docs (1 min)
2. Run vacuum and check report (2 min)
3. Verify no false positives (5 min)
4. Cleanup test files (1 min)
5. Commit changes (6 min)

### Rollback Plan

If strategy produces false positives:

1. Disable strategy: `uv run ce vacuum --exclude-strategy superseded-docs`
2. Investigate false positive in report
3. Adjust confidence thresholds or matching logic
4. Re-test with `--dry-run`

### Monitoring

After deployment:

1. Run vacuum weekly: `uv run ce vacuum --dry-run`
2. Review `.ce/vacuum-report.md` for unexpected candidates
3. Track false positive rate (should be 0%)
4. Collect feedback for Phase 2 (LLM integration)

## Success Criteria

- [x] Strategy class extends `BaseStrategy`
- [x] Implements `find_candidates()` returning `List[CleanupCandidate]`
- [x] Title extraction from YAML, header, or filename
- [x] Fuzzy matching with `difflib.SequenceMatcher`
- [x] Date comparison (parse YAML frontmatter)
- [x] Explicit reference detection
- [x] Related docs index (reverse lookup)
- [x] Confidence calculation (40-85%)
- [x] Registered in vacuum strategies
- [x] Unit tests pass (90%+ coverage)
- [x] Integration test detects 3 init workflow docs
- [x] No false positives on valid feature requests
- [x] Report shows "Superseded by PRP-X" in reason column

## Future Work

**PRP-46.2.1: LLM Integration (Haiku Analysis)**
- Add Haiku-based content analysis for 40-70% confidence candidates
- Boost to 85% if Haiku confirms "YES"
- Graceful fallback on API failures

**PRP-46.3.1: Batch Optimization**
- Process multiple uncertain candidates in single LLM call
- Reduce API costs by 90%

**PRP-46.4.1: Integration and Testing**
- Add `--superseded` CLI flag
- Update vacuum report format
- Comprehensive integration tests
