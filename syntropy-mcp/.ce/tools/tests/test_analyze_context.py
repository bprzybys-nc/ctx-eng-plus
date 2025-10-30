"""Tests for analyze-context command functionality.

Tests cache helpers, analyze_context_drift(), and CLI handler.
"""

import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from ce.update_context import (
    get_cache_ttl,
    get_cached_analysis,
    is_cache_valid,
    analyze_context_drift
)


class TestGetCacheTtl:
    """Test get_cache_ttl() function with 3-tier priority."""

    def test_priority_1_cli_flag(self, tmp_path, monkeypatch):
        """CLI flag overrides config and default."""
        monkeypatch.setattr("pathlib.Path.cwd", lambda: tmp_path / "tools")

        # CLI flag takes precedence
        ttl = get_cache_ttl(cli_ttl=15)
        assert ttl == 15

    def test_priority_2_config_file(self, tmp_path, monkeypatch):
        """Config file used when no CLI flag."""
        # Setup: create config file
        project_root = tmp_path
        tools_dir = project_root / "tools"
        tools_dir.mkdir()
        ce_dir = project_root / ".ce"
        ce_dir.mkdir()
        config_path = ce_dir / "config.yml"
        config_path.write_text("cache:\n  analysis_ttl_minutes: 10\n")

        monkeypatch.setattr("pathlib.Path.cwd", lambda: tools_dir)

        # Config value used
        ttl = get_cache_ttl()
        assert ttl == 10

    def test_priority_3_default(self, tmp_path, monkeypatch):
        """Default 5 minutes when no CLI flag or config."""
        monkeypatch.setattr("pathlib.Path.cwd", lambda: tmp_path / "tools")

        # Default used
        ttl = get_cache_ttl()
        assert ttl == 5

    def test_invalid_config_fallback_to_default(self, tmp_path, monkeypatch):
        """Invalid config falls back to default."""
        # Setup: create invalid config
        project_root = tmp_path
        tools_dir = project_root / "tools"
        tools_dir.mkdir()
        ce_dir = project_root / ".ce"
        ce_dir.mkdir()
        config_path = ce_dir / "config.yml"
        config_path.write_text("invalid: yaml: content\n")

        monkeypatch.setattr("pathlib.Path.cwd", lambda: tools_dir)

        # Falls back to default
        ttl = get_cache_ttl()
        assert ttl == 5


class TestGetCachedAnalysis:
    """Test get_cached_analysis() report parsing."""

    def test_parse_valid_report(self, tmp_path, monkeypatch):
        """Parse valid drift report successfully."""
        # Setup: create drift report
        project_root = tmp_path
        tools_dir = project_root / "tools"
        tools_dir.mkdir()
        ce_dir = project_root / ".ce"
        ce_dir.mkdir()
        report_path = ce_dir / "drift-report.md"

        report_content = """## Context Drift Report - Examples/ Patterns

**Drift Score**: 12.5% (⚠️ WARNING)
**Generated**: 2025-10-17T10:00:00+00:00
**Violations Found**: 5
**Missing Examples**: 2
"""
        report_path.write_text(report_content)

        monkeypatch.setattr("pathlib.Path.cwd", lambda: tools_dir)

        # Parse report
        cached = get_cached_analysis()

        assert cached is not None
        assert cached["drift_score"] == 12.5
        assert cached["drift_level"] == "warning"
        assert cached["violation_count"] == 5
        assert cached["generated_at"] == "2025-10-17T10:00:00+00:00"
        assert cached["cached"] is True

    def test_no_report_file_returns_none(self, tmp_path, monkeypatch):
        """Returns None when report file doesn't exist."""
        monkeypatch.setattr("pathlib.Path.cwd", lambda: tmp_path / "tools")

        cached = get_cached_analysis()
        assert cached is None

    def test_malformed_report_returns_none(self, tmp_path, monkeypatch):
        """Returns None for malformed report."""
        # Setup: create malformed report
        project_root = tmp_path
        tools_dir = project_root / "tools"
        tools_dir.mkdir()
        ce_dir = project_root / ".ce"
        ce_dir.mkdir()
        report_path = ce_dir / "drift-report.md"
        report_path.write_text("This is not a valid drift report\n")

        monkeypatch.setattr("pathlib.Path.cwd", lambda: tools_dir)

        cached = get_cached_analysis()
        assert cached is None

    def test_drift_level_classification(self, tmp_path, monkeypatch):
        """Test drift level classification logic."""
        project_root = tmp_path
        tools_dir = project_root / "tools"
        tools_dir.mkdir()
        ce_dir = project_root / ".ce"
        ce_dir.mkdir()
        report_path = ce_dir / "drift-report.md"

        monkeypatch.setattr("pathlib.Path.cwd", lambda: tools_dir)

        # Test OK level (< 5%)
        report_path.write_text("""**Drift Score**: 3.5% (✅ OK)
**Generated**: 2025-10-17T10:00:00+00:00
**Violations Found**: 2
""")
        cached = get_cached_analysis()
        assert cached["drift_level"] == "ok"

        # Test WARNING level (5-15%)
        report_path.write_text("""**Drift Score**: 12.5% (⚠️ WARNING)
**Generated**: 2025-10-17T10:00:00+00:00
**Violations Found**: 5
""")
        cached = get_cached_analysis()
        assert cached["drift_level"] == "warning"

        # Test CRITICAL level (>= 15%)
        report_path.write_text("""**Drift Score**: 19.75% (🚨 CRITICAL)
**Generated**: 2025-10-17T10:00:00+00:00
**Violations Found**: 10
""")
        cached = get_cached_analysis()
        assert cached["drift_level"] == "critical"


class TestIsCacheValid:
    """Test is_cache_valid() TTL checking."""

    def test_fresh_cache_is_valid(self):
        """Cache within TTL is valid."""
        now = datetime.now(timezone.utc)
        recent = now - timedelta(minutes=2)

        cached = {"generated_at": recent.isoformat()}

        assert is_cache_valid(cached, ttl_minutes=5) is True

    def test_stale_cache_is_invalid(self):
        """Cache beyond TTL is invalid."""
        now = datetime.now(timezone.utc)
        old = now - timedelta(minutes=10)

        cached = {"generated_at": old.isoformat()}

        assert is_cache_valid(cached, ttl_minutes=5) is False

    def test_edge_case_exact_ttl(self):
        """Cache exactly at TTL is invalid."""
        now = datetime.now(timezone.utc)
        exact_ttl = now - timedelta(minutes=5)

        cached = {"generated_at": exact_ttl.isoformat()}

        # Should be invalid (age >= TTL)
        assert is_cache_valid(cached, ttl_minutes=5) is False

    def test_malformed_timestamp_returns_false(self):
        """Malformed timestamp returns False."""
        cached = {"generated_at": "invalid-timestamp"}

        assert is_cache_valid(cached, ttl_minutes=5) is False

    def test_missing_timestamp_returns_false(self):
        """Missing timestamp returns False."""
        cached = {}

        assert is_cache_valid(cached, ttl_minutes=5) is False


class TestAnalyzeContextDrift:
    """Test analyze_context_drift() main function."""

    @patch("ce.update_context.verify_codebase_matches_examples")
    @patch("ce.update_context.detect_missing_examples_for_prps")
    @patch("ce.update_context.generate_drift_report")
    def test_successful_analysis(self, mock_gen_report, mock_missing, mock_verify, tmp_path, monkeypatch):
        """Test successful drift analysis execution."""
        # Setup mocks
        mock_verify.return_value = {
            "violations": ["File foo.py has bare_except"],
            "drift_score": 12.5
        }
        mock_missing.return_value = []
        mock_gen_report.return_value = "# Drift Report\ntest content"

        # Setup project structure
        project_root = tmp_path
        tools_dir = project_root / "tools"
        tools_dir.mkdir()
        monkeypatch.setattr("pathlib.Path.cwd", lambda: tools_dir)

        # Run analysis
        result = analyze_context_drift()

        # Verify result structure
        assert result["drift_score"] == 12.5
        assert result["drift_level"] == "warning"
        assert result["violation_count"] == 1
        assert "report_path" in result
        assert "generated_at" in result
        assert "duration_seconds" in result

        # Verify report saved
        report_path = project_root / ".ce" / "drift-report.md"
        assert report_path.exists()
        assert report_path.read_text() == "# Drift Report\ntest content"

    @patch("ce.update_context.verify_codebase_matches_examples")
    def test_analysis_failure_raises_runtimeerror(self, mock_verify, tmp_path, monkeypatch):
        """Test analysis failure with troubleshooting guidance."""
        mock_verify.side_effect = Exception("Test failure")

        monkeypatch.setattr("pathlib.Path.cwd", lambda: tmp_path / "tools")

        with pytest.raises(RuntimeError) as exc_info:
            analyze_context_drift()

        # Verify troubleshooting guidance included
        assert "Drift analysis failed" in str(exc_info.value)
        assert "🔧 Troubleshooting" in str(exc_info.value)
        assert "examples/ directory exists" in str(exc_info.value)

    @patch("ce.update_context.verify_codebase_matches_examples")
    @patch("ce.update_context.detect_missing_examples_for_prps")
    @patch("ce.update_context.generate_drift_report")
    def test_drift_level_classification(self, mock_gen_report, mock_missing, mock_verify, tmp_path, monkeypatch):
        """Test drift level classification logic."""
        mock_missing.return_value = []
        mock_gen_report.return_value = "# Report"

        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        monkeypatch.setattr("pathlib.Path.cwd", lambda: tools_dir)

        # Test OK level
        mock_verify.return_value = {"violations": [], "drift_score": 3.0}
        result = analyze_context_drift()
        assert result["drift_level"] == "ok"

        # Test WARNING level
        mock_verify.return_value = {"violations": ["test"], "drift_score": 12.0}
        result = analyze_context_drift()
        assert result["drift_level"] == "warning"

        # Test CRITICAL level
        mock_verify.return_value = {"violations": ["test"], "drift_score": 20.0}
        result = analyze_context_drift()
        assert result["drift_level"] == "critical"


class TestIntegration:
    """Integration tests for cache workflow."""

    @patch("ce.update_context.verify_codebase_matches_examples")
    @patch("ce.update_context.detect_missing_examples_for_prps")
    def test_cache_reuse_workflow(self, mock_missing, mock_verify, tmp_path, monkeypatch):
        """Test analyze creates cache, second call reuses it."""
        # Setup
        mock_verify.return_value = {"violations": [], "drift_score": 3.0}
        mock_missing.return_value = []

        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        monkeypatch.setattr("pathlib.Path.cwd", lambda: tools_dir)

        # First call: creates cache
        result1 = analyze_context_drift()
        assert result1["drift_score"] == 3.0
        assert "cached" not in result1  # Fresh analysis

        # Second call: reuses cache
        cached = get_cached_analysis()
        assert cached is not None
        assert is_cache_valid(cached, ttl_minutes=5) is True
        assert cached["drift_score"] == 3.0
        assert cached["cached"] is True

    @patch("ce.update_context.verify_codebase_matches_examples")
    @patch("ce.update_context.detect_missing_examples_for_prps")
    def test_stale_cache_triggers_fresh_analysis(self, mock_missing, mock_verify, tmp_path, monkeypatch):
        """Test stale cache triggers fresh analysis."""
        # Setup
        mock_verify.return_value = {"violations": [], "drift_score": 3.0}
        mock_missing.return_value = []

        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        ce_dir = tmp_path / ".ce"
        ce_dir.mkdir()
        monkeypatch.setattr("pathlib.Path.cwd", lambda: tools_dir)

        # Create old report (10 minutes ago)
        old_timestamp = datetime.now(timezone.utc) - timedelta(minutes=10)
        report_path = ce_dir / "drift-report.md"
        report_path.write_text(f"""**Drift Score**: 5.0% (⚠️ WARNING)
**Generated**: {old_timestamp.isoformat()}
**Violations Found**: 2
""")

        # Cache should be invalid
        cached = get_cached_analysis()
        assert cached is not None
        assert is_cache_valid(cached, ttl_minutes=5) is False

        # Fresh analysis should run
        result = analyze_context_drift()
        assert result["drift_score"] == 3.0  # New value from mock
