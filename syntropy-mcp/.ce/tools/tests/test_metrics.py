"""Tests for metrics collection module."""

import pytest
import json
from pathlib import Path
from ce.metrics import MetricsCollector


class TestMetricsCollector:
    """Test metrics collector class."""

    def test_initialization_creates_empty_structure(self, tmp_path):
        """Test that new collector creates empty metrics structure."""
        metrics_file = tmp_path / "metrics.json"
        collector = MetricsCollector(metrics_file=str(metrics_file))

        assert collector.metrics["prp_executions"] == []
        assert collector.metrics["validation_results"] == []
        assert collector.metrics["performance_stats"] == {}

    def test_load_existing_metrics(self, tmp_path):
        """Test loading existing metrics from file."""
        metrics_file = tmp_path / "metrics.json"

        # Create existing metrics
        existing_data = {
            "prp_executions": [{"prp_id": "PRP-001", "success": True}],
            "validation_results": [],
            "performance_stats": {}
        }
        metrics_file.write_text(json.dumps(existing_data))

        # Load metrics
        collector = MetricsCollector(metrics_file=str(metrics_file))

        assert len(collector.metrics["prp_executions"]) == 1
        assert collector.metrics["prp_executions"][0]["prp_id"] == "PRP-001"

    def test_corrupted_file_creates_new_structure(self, tmp_path):
        """Test that corrupted metrics file is replaced."""
        metrics_file = tmp_path / "metrics.json"
        metrics_file.write_text("invalid json {{{")

        collector = MetricsCollector(metrics_file=str(metrics_file))

        # Should create fresh structure
        assert collector.metrics["prp_executions"] == []

    def test_record_prp_execution(self, tmp_path):
        """Test recording PRP execution metrics."""
        metrics_file = tmp_path / "metrics.json"
        collector = MetricsCollector(metrics_file=str(metrics_file))

        collector.record_prp_execution(
            prp_id="PRP-003",
            success=True,
            duration=1200.5,
            first_pass=True,
            validation_level=4
        )

        assert len(collector.metrics["prp_executions"]) == 1
        execution = collector.metrics["prp_executions"][0]
        assert execution["prp_id"] == "PRP-003"
        assert execution["success"] is True
        assert execution["duration"] == 1200.5
        assert execution["first_pass"] is True
        assert execution["validation_level"] == 4
        assert "timestamp" in execution

    def test_record_validation_result(self, tmp_path):
        """Test recording validation gate results."""
        metrics_file = tmp_path / "metrics.json"
        collector = MetricsCollector(metrics_file=str(metrics_file))

        collector.record_validation_result(
            prp_id="PRP-003",
            validation_level=2,
            passed=True,
            duration=5.5
        )

        assert len(collector.metrics["validation_results"]) == 1
        validation = collector.metrics["validation_results"][0]
        assert validation["prp_id"] == "PRP-003"
        assert validation["validation_level"] == 2
        assert validation["passed"] is True
        assert validation["duration"] == 5.5
        assert "timestamp" in validation

    def test_calculate_success_rates_empty(self, tmp_path):
        """Test success rate calculation with no data."""
        metrics_file = tmp_path / "metrics.json"
        collector = MetricsCollector(metrics_file=str(metrics_file))

        rates = collector.calculate_success_rates()

        assert rates["first_pass_rate"] == 0.0
        assert rates["second_pass_rate"] == 0.0
        assert rates["overall_rate"] == 0.0
        assert rates["total_executions"] == 0

    def test_calculate_success_rates_with_data(self, tmp_path):
        """Test success rate calculation with execution data."""
        metrics_file = tmp_path / "metrics.json"
        collector = MetricsCollector(metrics_file=str(metrics_file))

        # Add test data: 10 executions, 8 first-pass, 9 eventually successful
        for i in range(10):
            collector.record_prp_execution(
                prp_id=f"PRP-{i:03d}",
                success=(i < 9),  # 9 successes
                duration=100.0,
                first_pass=(i < 8),  # 8 first-pass
                validation_level=4
            )

        rates = collector.calculate_success_rates()

        assert rates["first_pass_rate"] == 80.0  # 8/10
        assert rates["second_pass_rate"] == 90.0  # 9/10
        assert rates["overall_rate"] == 90.0
        assert rates["total_executions"] == 10

    def test_calculate_validation_stats_empty(self, tmp_path):
        """Test validation stats with no data."""
        metrics_file = tmp_path / "metrics.json"
        collector = MetricsCollector(metrics_file=str(metrics_file))

        stats = collector.calculate_validation_stats()

        assert stats == {}

    def test_calculate_validation_stats_with_data(self, tmp_path):
        """Test validation stats calculation."""
        metrics_file = tmp_path / "metrics.json"
        collector = MetricsCollector(metrics_file=str(metrics_file))

        # Add L1 validations (5 total, 4 passed)
        for i in range(5):
            collector.record_validation_result(
                prp_id=f"PRP-{i:03d}",
                validation_level=1,
                passed=(i < 4),
                duration=5.0
            )

        # Add L2 validations (3 total, 3 passed)
        for i in range(3):
            collector.record_validation_result(
                prp_id=f"PRP-{i:03d}",
                validation_level=2,
                passed=True,
                duration=10.0
            )

        stats = collector.calculate_validation_stats()

        assert stats["L1_pass_rate"] == 80.0  # 4/5
        assert stats["L1_total"] == 5
        assert stats["L2_pass_rate"] == 100.0  # 3/3
        assert stats["L2_total"] == 3

    def test_get_average_duration_empty(self, tmp_path):
        """Test average duration with no executions."""
        metrics_file = tmp_path / "metrics.json"
        collector = MetricsCollector(metrics_file=str(metrics_file))

        avg = collector.get_average_duration()

        assert avg == 0.0

    def test_get_average_duration_with_data(self, tmp_path):
        """Test average duration calculation."""
        metrics_file = tmp_path / "metrics.json"
        collector = MetricsCollector(metrics_file=str(metrics_file))

        # Add executions with durations: 100, 200, 300
        collector.record_prp_execution("PRP-001", True, 100.0, True, 4)
        collector.record_prp_execution("PRP-002", True, 200.0, True, 4)
        collector.record_prp_execution("PRP-003", True, 300.0, True, 4)

        avg = collector.get_average_duration()

        assert avg == 200.0  # (100 + 200 + 300) / 3

    def test_save_metrics(self, tmp_path):
        """Test saving metrics to file."""
        metrics_file = tmp_path / "metrics.json"
        collector = MetricsCollector(metrics_file=str(metrics_file))

        collector.record_prp_execution("PRP-001", True, 100.0, True, 4)
        collector.save()

        # File should exist and contain valid JSON
        assert metrics_file.exists()
        saved_data = json.loads(metrics_file.read_text())
        assert len(saved_data["prp_executions"]) == 1

    def test_save_creates_parent_directory(self, tmp_path):
        """Test that save creates parent directory if needed."""
        metrics_file = tmp_path / "subdir" / "metrics.json"
        collector = MetricsCollector(metrics_file=str(metrics_file))

        collector.record_prp_execution("PRP-001", True, 100.0, True, 4)
        collector.save()

        assert metrics_file.exists()
        assert metrics_file.parent.exists()

    def test_get_summary(self, tmp_path):
        """Test comprehensive metrics summary."""
        metrics_file = tmp_path / "metrics.json"
        collector = MetricsCollector(metrics_file=str(metrics_file))

        # Add test data
        collector.record_prp_execution("PRP-001", True, 100.0, True, 4)
        collector.record_prp_execution("PRP-002", True, 200.0, True, 4)
        collector.record_validation_result("PRP-001", 1, True, 5.0)

        summary = collector.get_summary()

        # Check structure
        assert "success_rates" in summary
        assert "validation_stats" in summary
        assert "performance" in summary

        # Check success rates
        assert summary["success_rates"]["total_executions"] == 2
        assert summary["success_rates"]["first_pass_rate"] == 100.0

        # Check validation stats
        assert summary["validation_stats"]["L1_pass_rate"] == 100.0

        # Check performance
        assert summary["performance"]["avg_duration"] == 150.0
        assert summary["performance"]["total_prps"] == 2
        assert summary["performance"]["total_validations"] == 1


class TestMetricsIntegration:
    """Test metrics integration scenarios."""

    def test_multiple_prp_tracking(self, tmp_path):
        """Test tracking multiple PRP executions."""
        metrics_file = tmp_path / "metrics.json"
        collector = MetricsCollector(metrics_file=str(metrics_file))

        # Simulate multiple PRP executions
        prps = [
            ("PRP-001", True, 1000.0, True, 4),
            ("PRP-002", False, 500.0, False, 2),
            ("PRP-003", True, 1500.0, True, 4),
            ("PRP-004", True, 800.0, False, 4),  # Second pass success
        ]

        for prp_data in prps:
            collector.record_prp_execution(*prp_data)

        rates = collector.calculate_success_rates()

        assert rates["total_executions"] == 4
        assert rates["first_pass_rate"] == 50.0  # 2/4 first pass
        assert rates["overall_rate"] == 75.0  # 3/4 total success

    def test_persistence_across_instances(self, tmp_path):
        """Test that metrics persist across collector instances."""
        metrics_file = tmp_path / "metrics.json"

        # First instance
        collector1 = MetricsCollector(metrics_file=str(metrics_file))
        collector1.record_prp_execution("PRP-001", True, 100.0, True, 4)
        collector1.save()

        # Second instance (load existing)
        collector2 = MetricsCollector(metrics_file=str(metrics_file))
        collector2.record_prp_execution("PRP-002", True, 200.0, True, 4)
        collector2.save()

        # Third instance (verify both records)
        collector3 = MetricsCollector(metrics_file=str(metrics_file))
        assert len(collector3.metrics["prp_executions"]) == 2
