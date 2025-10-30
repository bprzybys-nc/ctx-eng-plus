"""Metrics collection module - track performance and success rates.

Provides lightweight metrics collection for tracking PRP execution success rates,
timing data, and validation results without heavy telemetry infrastructure.
"""

from typing import Dict, Any, List
from datetime import datetime
import json
from pathlib import Path


class MetricsCollector:
    """Collect and persist performance metrics.

    Tracks success rates, timing data, and validation results.

    Example:
        metrics = MetricsCollector()
        metrics.record_prp_execution(
            prp_id="PRP-003",
            success=True,
            duration=1200.5,
            first_pass=True,
            validation_level=4
        )
        metrics.save()

    Attributes:
        metrics_file: Path to metrics JSON file
        metrics: Dict containing all collected metrics
    """

    def __init__(self, metrics_file: str = "metrics.json"):
        """Initialize metrics collector.

        Args:
            metrics_file: Path to metrics JSON file

        Note: Creates new metrics file if it doesn't exist.
        """
        self.metrics_file = Path(metrics_file)
        self.metrics: Dict[str, Any] = self._load_metrics()

    def _load_metrics(self) -> Dict[str, Any]:
        """Load existing metrics from file.

        Returns:
            Dict with metrics data structure

        Note: Creates empty structure if file doesn't exist.
        """
        if self.metrics_file.exists():
            try:
                return json.loads(self.metrics_file.read_text())
            except json.JSONDecodeError:
                # Corrupted file - start fresh
                return self._empty_metrics()
        return self._empty_metrics()

    def _empty_metrics(self) -> Dict[str, Any]:
        """Create empty metrics structure.

        Returns:
            Dict with empty metrics data structure
        """
        return {
            "prp_executions": [],
            "validation_results": [],
            "performance_stats": {}
        }

    def record_prp_execution(
        self,
        prp_id: str,
        success: bool,
        duration: float,
        first_pass: bool,
        validation_level: int
    ):
        """Record PRP execution metrics.

        Args:
            prp_id: PRP identifier
            success: Whether execution succeeded
            duration: Execution time in seconds
            first_pass: Whether succeeded on first pass
            validation_level: Highest validation level passed (1-4)

        Note: Call save() after recording to persist metrics.
        """
        self.metrics["prp_executions"].append({
            "prp_id": prp_id,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "duration": duration,
            "first_pass": first_pass,
            "validation_level": validation_level
        })

    def record_validation_result(
        self,
        prp_id: str,
        validation_level: int,
        passed: bool,
        duration: float,
        error_message: str = None
    ):
        """Record validation gate result.

        Args:
            prp_id: PRP identifier
            validation_level: Validation level (1-4)
            passed: Whether validation passed
            duration: Validation time in seconds
            error_message: Error message if failed

        Note: Call save() after recording to persist metrics.
        """
        self.metrics["validation_results"].append({
            "prp_id": prp_id,
            "timestamp": datetime.now().isoformat(),
            "validation_level": validation_level,
            "passed": passed,
            "duration": duration,
            "error_message": error_message
        })

    def calculate_success_rates(self) -> Dict[str, float]:
        """Calculate success rate metrics.

        Returns:
            Dict with first_pass_rate, second_pass_rate, overall_rate, total_executions

        Note: Returns 0.0 rates if no executions recorded.
        """
        executions = self.metrics["prp_executions"]
        if not executions:
            return {
                "first_pass_rate": 0.0,
                "second_pass_rate": 0.0,
                "overall_rate": 0.0,
                "total_executions": 0
            }

        total = len(executions)
        first_pass = sum(1 for e in executions if e["first_pass"])
        successful = sum(1 for e in executions if e["success"])

        return {
            "first_pass_rate": (first_pass / total) * 100,
            "second_pass_rate": (successful / total) * 100,
            "overall_rate": (successful / total) * 100,
            "total_executions": total
        }

    def calculate_validation_stats(self) -> Dict[str, Any]:
        """Calculate validation gate statistics.

        Returns:
            Dict with pass rates per validation level

        Note: Returns empty dict if no validations recorded.
        """
        validations = self.metrics["validation_results"]
        if not validations:
            return {}

        # Group by level
        by_level = {}
        for v in validations:
            level = v["validation_level"]
            if level not in by_level:
                by_level[level] = {"total": 0, "passed": 0}
            by_level[level]["total"] += 1
            if v["passed"]:
                by_level[level]["passed"] += 1

        # Calculate pass rates
        stats = {}
        for level, data in by_level.items():
            stats[f"L{level}_pass_rate"] = (data["passed"] / data["total"]) * 100
            stats[f"L{level}_total"] = data["total"]

        return stats

    def get_average_duration(self) -> float:
        """Calculate average PRP execution duration.

        Returns:
            Average duration in seconds, or 0.0 if no executions

        Note: Includes both successful and failed executions.
        """
        executions = self.metrics["prp_executions"]
        if not executions:
            return 0.0

        total_duration = sum(e["duration"] for e in executions)
        return total_duration / len(executions)

    def save(self):
        """Persist metrics to file.

        Raises:
            RuntimeError: If file cannot be written

        Note: Creates parent directory if needed.
        """
        try:
            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
            self.metrics_file.write_text(json.dumps(self.metrics, indent=2))
        except Exception as e:
            raise RuntimeError(
                f"Failed to save metrics to {self.metrics_file}\n"
                f"Error: {str(e)}\n"
                f"🔧 Troubleshooting:\n"
                f"  1. Check write permissions\n"
                f"  2. Ensure parent directory exists or can be created\n"
                f"  3. Verify disk space available"
            ) from e

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary.

        Returns:
            Dict with success rates, validation stats, and performance metrics

        Example:
            {
                "success_rates": {"first_pass_rate": 85.0, ...},
                "validation_stats": {"L1_pass_rate": 95.0, ...},
                "performance": {"avg_duration": 1200.5, ...}
            }

        Note: Useful for status dashboards and reports.
        """
        return {
            "success_rates": self.calculate_success_rates(),
            "validation_stats": self.calculate_validation_stats(),
            "performance": {
                "avg_duration": self.get_average_duration(),
                "total_prps": len(self.metrics["prp_executions"]),
                "total_validations": len(self.metrics["validation_results"])
            }
        }
