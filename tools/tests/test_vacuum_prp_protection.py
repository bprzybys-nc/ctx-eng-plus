"""Test that PRPs are protected but analysis files are not."""

import pytest
from pathlib import Path
from ce.vacuum_strategies import ObsoleteDocStrategy


@pytest.fixture
def temp_project_with_prps(tmp_path):
    """Create temporary project with PRPs and analysis files."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    # Create .ce directory
    (project_root / ".ce").mkdir()

    # Create PRPs directory with actual PRP files (with YAML headers)
    prps_dir = project_root / "PRPs" / "executed"
    prps_dir.mkdir(parents=True)
    (prps_dir / "PRP-1-feature.md").write_text("---\nid: PRP-1\nstatus: executed\n---\n# PRP-1\nActual PRP content")
    (prps_dir / "PRP-2-bugfix.md").write_text("---\nid: PRP-2\nstatus: executed\n---\n# PRP-2\nAnother PRP")

    # Create analysis/report files (should NOT be protected)
    (project_root / "CHANGELIST-REVIEW-PRP-1.md").write_text("# Review\nAnalysis content")
    (project_root / "ANALYSIS-PRP-2.md").write_text("# Analysis\nDetailed analysis")
    (project_root / "IMPLEMENTATION-COMPLETE.md").write_text("# Done\nImplementation notes")

    # Create old versioned analysis files
    (project_root / "ANALYSIS-v1.md").write_text("# Old analysis")
    (project_root / "ANALYSIS.md").write_text("# Current analysis")

    # Create garbage doc in PRPs/ without YAML header (should NOT be protected)
    (prps_dir / "random-notes.md").write_text("# Random notes\nSome garbage doc")

    return project_root


def test_prp_files_are_protected(temp_project_with_prps):
    """PRPs in PRPs/** should be protected."""
    from ce.vacuum_strategies.base import BaseStrategy

    strategy = ObsoleteDocStrategy(temp_project_with_prps)

    # Check PRP files are protected
    prp_file = temp_project_with_prps / "PRPs" / "executed" / "PRP-1-feature.md"
    assert strategy.is_protected(prp_file), "PRP files should be protected"


def test_analysis_files_not_protected(temp_project_with_prps):
    """Analysis files outside PRPs/** should NOT be protected."""
    from ce.vacuum_strategies.base import BaseStrategy

    strategy = ObsoleteDocStrategy(temp_project_with_prps)

    # Check analysis files are NOT protected
    changelist = temp_project_with_prps / "CHANGELIST-REVIEW-PRP-1.md"
    assert not strategy.is_protected(changelist), "Changelist files should NOT be protected"

    analysis = temp_project_with_prps / "ANALYSIS-PRP-2.md"
    assert not strategy.is_protected(analysis), "Analysis files should NOT be protected"

    impl = temp_project_with_prps / "IMPLEMENTATION-COMPLETE.md"
    assert not strategy.is_protected(impl), "Implementation files should NOT be protected"


def test_obsolete_analysis_files_detected(temp_project_with_prps):
    """Old versioned analysis files should be detected by ObsoleteDocStrategy."""
    strategy = ObsoleteDocStrategy(temp_project_with_prps)
    candidates = strategy.find_candidates()

    # Should find ANALYSIS-v1.md but not ANALYSIS.md
    old_analysis = [c for c in candidates if "ANALYSIS-v1" in c.path.name]
    assert len(old_analysis) == 1, "Should find old versioned analysis file"

    # Should not include current ANALYSIS.md
    current_analysis = [c for c in candidates if c.path.name == "ANALYSIS.md"]
    assert len(current_analysis) == 0, "Should not flag current analysis file"


def test_prps_never_in_candidates(temp_project_with_prps):
    """PRP files should never appear as cleanup candidates."""
    strategy = ObsoleteDocStrategy(temp_project_with_prps)
    candidates = strategy.find_candidates()

    # No candidates should be PRP files
    prp_candidates = [c for c in candidates if "PRPs/" in str(c.path)]
    assert len(prp_candidates) == 0, "PRP files should never be cleanup candidates"


@pytest.mark.skip(reason="DeadLinkStrategy not yet implemented")
def test_dead_links_in_analysis_files_detected(temp_project_with_prps):
    """Dead links in analysis files should be detected (files can be flagged)."""
    # TODO: Implement DeadLinkStrategy
    # Add dead link to analysis file
    changelist = temp_project_with_prps / "CHANGELIST-REVIEW-PRP-1.md"
    changelist.write_text("# Review\n[broken link](nonexistent.md)")

    # strategy = DeadLinkStrategy(temp_project_with_prps)
    # candidates = strategy.find_candidates()

    # Should find the changelist file with dead link
    # changelist_candidates = [c for c in candidates if "CHANGELIST" in c.path.name]
    # assert len(changelist_candidates) == 1, "Should detect dead links in analysis files"
    pass


def test_garbage_docs_in_prps_not_protected(temp_project_with_prps):
    """Markdown files in PRPs/ without YAML headers should NOT be protected."""
    from ce.vacuum_strategies.base import BaseStrategy

    strategy = ObsoleteDocStrategy(temp_project_with_prps)

    # Check garbage doc in PRPs/ is NOT protected
    garbage_doc = temp_project_with_prps / "PRPs" / "executed" / "random-notes.md"
    assert not strategy.is_protected(garbage_doc), "Docs without YAML headers should NOT be protected"
