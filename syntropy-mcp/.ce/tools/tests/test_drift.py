"""Tests for drift history tracking."""

import pytest
from pathlib import Path
from ce.drift import (
    parse_drift_justification,
    get_drift_history,
    drift_summary,
    show_drift_decision,
    compare_drift_decisions
)


def test_parse_drift_justification_valid(tmp_path):
    """Test parsing valid DRIFT_JUSTIFICATION from PRP."""
    prp_file = tmp_path / "PRP-TEST.md"
    prp_file.write_text("""---
name: "Test PRP"
prp_id: "PRP-TEST"
drift_decision:
  score: 35.5
  action: "accepted"
  justification: "Test reason"
  timestamp: "2025-10-12T15:00:00Z"
  category_breakdown:
    code_structure: 40.0
    naming_conventions: 30.0
  reviewer: "human"
---

# Test PRP
""")

    result = parse_drift_justification(str(prp_file))

    assert result is not None
    assert result["prp_id"] == "PRP-TEST"
    assert result["prp_name"] == "Test PRP"
    assert result["drift_decision"]["score"] == 35.5
    assert result["drift_decision"]["action"] == "accepted"


def test_parse_drift_justification_no_decision(tmp_path):
    """Test parsing PRP without drift decision."""
    prp_file = tmp_path / "PRP-NODRIFT.md"
    prp_file.write_text("""---
name: "Test PRP"
prp_id: "PRP-NODRIFT"
---

# Test PRP
""")

    result = parse_drift_justification(str(prp_file))
    assert result is None


def test_get_drift_history_filter_by_prp():
    """Test filtering drift history by PRP ID."""
    # Uses real PRPs in PRPs/ directory
    history = get_drift_history(prp_id="PRP-001")

    # Should return empty if PRP-001 has no drift decision
    # Or should return list with PRP-001 decisions only
    assert isinstance(history, list)
    for h in history:
        assert h["prp_id"] == "PRP-001"


def test_get_drift_history_limit():
    """Test limiting drift history results."""
    history_all = get_drift_history()
    history_limited = get_drift_history(last_n=3)

    assert isinstance(history_limited, list)
    assert len(history_limited) <= 3
    assert len(history_limited) <= len(history_all)


def test_drift_summary_structure():
    """Test drift summary returns correct structure."""
    summary = drift_summary()

    assert isinstance(summary, dict)
    assert "total_prps" in summary
    assert "prps_with_drift" in summary
    assert "decisions" in summary
    assert "avg_drift_score" in summary
    assert "score_distribution" in summary
    assert "category_breakdown" in summary
    assert "reviewer_breakdown" in summary


def test_show_drift_decision_not_found():
    """Test showing drift decision for non-existent PRP."""
    with pytest.raises(ValueError) as exc:
        show_drift_decision("PRP-NONEXISTENT")

    assert "No drift decision found" in str(exc.value)


def test_compare_drift_decisions_structure(tmp_path, monkeypatch):
    """Test drift comparison returns correct structure."""
    # Create two test PRPs with drift decisions
    prp_dir = tmp_path / "PRPs" / "executed"
    prp_dir.mkdir(parents=True)

    prp1 = prp_dir / "PRP-001.md"
    prp1.write_text("""---
name: "Test PRP 1"
prp_id: "PRP-001"
drift_decision:
  score: 35.0
  action: "accepted"
  justification: "Test 1"
  timestamp: "2025-10-12T15:00:00Z"
  category_breakdown:
    code_structure: 40.0
  reviewer: "human"
---

# Test
""")

    prp2 = prp_dir / "PRP-002.md"
    prp2.write_text("""---
name: "Test PRP 2"
prp_id: "PRP-002"
drift_decision:
  score: 25.0
  action: "rejected"
  justification: "Test 2"
  timestamp: "2025-10-12T16:00:00Z"
  category_breakdown:
    code_structure: 20.0
  reviewer: "human"
---

# Test
""")

    # Temporarily change to tmp directory for testing
    import os
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        comparison = compare_drift_decisions("PRP-001", "PRP-002")

        assert "prp_1" in comparison
        assert "prp_2" in comparison
        assert "comparison" in comparison

        comp = comparison["comparison"]
        assert "score_diff" in comp
        assert comp["score_diff"] == 10.0
        assert "same_action" in comp
        assert comp["same_action"] is False
    finally:
        os.chdir(original_dir)


def test_parse_drift_justification_malformed_yaml(tmp_path):
    """Test error handling for malformed YAML."""
    prp_file = tmp_path / "PRP-BAD.md"
    prp_file.write_text("""---
name: "Test"
prp_id: PRP-BAD
  invalid: yaml:
---

# Test
""")

    with pytest.raises(ValueError) as exc:
        parse_drift_justification(str(prp_file))

    assert "Failed to parse PRP YAML" in str(exc.value)


def test_parse_drift_justification_file_not_found():
    """Test error handling for missing file."""
    with pytest.raises(FileNotFoundError) as exc:
        parse_drift_justification("/nonexistent/PRP-FAKE.md")

    assert "PRP file not found" in str(exc.value)


def test_get_drift_history_action_filter(tmp_path, monkeypatch):
    """Test filtering drift history by action type."""
    prp_dir = tmp_path / "PRPs" / "executed"
    prp_dir.mkdir(parents=True)

    # Create PRPs with different actions
    for i, action in enumerate(["accepted", "rejected", "accepted"]):
        prp = prp_dir / f"PRP-{i:03d}.md"
        prp.write_text(f"""---
name: "Test PRP {i}"
prp_id: "PRP-{i:03d}"
drift_decision:
  score: 20.0
  action: "{action}"
  justification: "Test"
  timestamp: "2025-10-12T15:00:00Z"
  reviewer: "human"
---

# Test
""")

    import os
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        accepted = get_drift_history(action_filter="accepted")
        rejected = get_drift_history(action_filter="rejected")

        assert len(accepted) == 2
        assert len(rejected) == 1
        assert all(h["drift_decision"]["action"] == "accepted" for h in accepted)
        assert all(h["drift_decision"]["action"] == "rejected" for h in rejected)
    finally:
        os.chdir(original_dir)


def test_drift_summary_empty():
    """Test drift summary with no PRPs."""
    # This should return empty structure gracefully
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        original_dir = os.getcwd()
        os.chdir(tmp_dir)

        try:
            summary = drift_summary()

            assert summary["total_prps"] == 0
            assert summary["prps_with_drift"] == 0
            assert summary["avg_drift_score"] == 0.0
        finally:
            os.chdir(original_dir)


def test_get_drift_history_sorting(tmp_path, monkeypatch):
    """Test drift history sorted by timestamp (newest first)."""
    prp_dir = tmp_path / "PRPs" / "executed"
    prp_dir.mkdir(parents=True)

    # Create PRPs with different timestamps
    timestamps = ["2025-10-12T10:00:00Z", "2025-10-12T15:00:00Z", "2025-10-12T12:00:00Z"]
    for i, ts in enumerate(timestamps):
        prp = prp_dir / f"PRP-{i:03d}.md"
        prp.write_text(f"""---
name: "Test PRP {i}"
prp_id: "PRP-{i:03d}"
drift_decision:
  score: 20.0
  action: "accepted"
  justification: "Test"
  timestamp: "{ts}"
  reviewer: "human"
---

# Test
""")

    import os
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        history = get_drift_history()

        # Should be sorted newest first
        assert len(history) == 3
        assert history[0]["drift_decision"]["timestamp"] == "2025-10-12T15:00:00Z"
        assert history[1]["drift_decision"]["timestamp"] == "2025-10-12T12:00:00Z"
        assert history[2]["drift_decision"]["timestamp"] == "2025-10-12T10:00:00Z"
    finally:
        os.chdir(original_dir)


def test_drift_summary_calculations(tmp_path, monkeypatch):
    """Test drift summary calculates correct statistics."""
    prp_dir = tmp_path / "PRPs" / "executed"
    prp_dir.mkdir(parents=True)

    # Create PRPs with known values
    scores = [5.0, 15.0, 35.0]  # low, medium, high
    for i, score in enumerate(scores):
        prp = prp_dir / f"PRP-{i:03d}.md"
        prp.write_text(f"""---
name: "Test PRP {i}"
prp_id: "PRP-{i:03d}"
drift_decision:
  score: {score}
  action: "accepted"
  justification: "Test"
  timestamp: "2025-10-12T15:00:00Z"
  category_breakdown:
    code_structure: {score}
  reviewer: "human"
---

# Test
""")

    import os
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        summary = drift_summary()

        assert summary["total_prps"] == 3
        assert summary["avg_drift_score"] == round((5.0 + 15.0 + 35.0) / 3, 2)
        assert summary["score_distribution"]["low"] == 1
        assert summary["score_distribution"]["medium"] == 1
        assert summary["score_distribution"]["high"] == 1
    finally:
        os.chdir(original_dir)
