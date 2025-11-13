#!/usr/bin/env python3
"""
Analyze trends across multiple batches.

Usage:
    python trend-analysis.py --recent 5
    python trend-analysis.py --all

Output: Trend report with bottlenecks and recommendations
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict
from statistics import mean, median, stdev


class TrendAnalyzer:
    """Analyze trends across batches."""

    def __init__(self, metrics_dir: Path):
        self.metrics_dir = metrics_dir

    def load_metrics(self, limit: int = None) -> List[Dict]:
        """Load metrics files."""
        files = sorted(self.metrics_dir.glob("batch-*.json"), reverse=True)
        if limit:
            files = files[:limit]

        metrics = []
        for file_path in files:
            try:
                metrics.append(json.loads(file_path.read_text()))
            except Exception as e:
                print(f"Warning: Could not load {file_path}: {e}")

        return metrics

    def analyze_durations(self, metrics: List[Dict]) -> Dict:
        """Analyze operation durations."""
        by_operation = {}

        for metric in metrics:
            op = metric.get("operation", "unknown")
            duration = metric.get("duration_seconds", 0)

            by_operation.setdefault(op, []).append(duration)

        results = {}
        for op, durations in by_operation.items():
            results[op] = {
                "mean": mean(durations) if durations else 0,
                "median": median(durations) if durations else 0,
                "min": min(durations) if durations else 0,
                "max": max(durations) if durations else 0,
                "count": len(durations),
                "stdev": stdev(durations) if len(durations) > 1 else 0
            }

        return results

    def analyze_success_rates(self, metrics: List[Dict]) -> Dict:
        """Analyze success rates."""
        by_operation = {}

        for metric in metrics:
            op = metric.get("operation", "unknown")
            metric_data = metric.get("metrics", {})
            total = metric_data.get("total_items", 0)
            success = metric_data.get("success_count", 0)
            failure = metric_data.get("failure_count", 0)

            by_operation.setdefault(op, {"total": 0, "success": 0, "failure": 0})
            by_operation[op]["total"] += total
            by_operation[op]["success"] += success
            by_operation[op]["failure"] += failure

        return {
            op: {
                "success_rate": counts["success"] / counts["total"] if counts["total"] > 0 else 0,
                "total": counts["total"],
                "success": counts["success"],
                "failure": counts["failure"]
            }
            for op, counts in by_operation.items()
        }

    def analyze_token_usage(self, metrics: List[Dict]) -> Dict:
        """Analyze token usage patterns."""
        by_operation = {}

        for metric in metrics:
            op = metric.get("operation", "unknown")
            token_data = metric.get("metrics", {}).get("token_usage", {})
            total_tokens = token_data.get("total_tokens", 0)
            cost = token_data.get("estimated_cost", 0)

            if total_tokens > 0 or cost > 0:
                by_operation.setdefault(op, {"tokens": [], "costs": []})
                if total_tokens > 0:
                    by_operation[op]["tokens"].append(total_tokens)
                if cost > 0:
                    by_operation[op]["costs"].append(cost)

        results = {}
        for op, data in by_operation.items():
            results[op] = {
                "mean_tokens": mean(data["tokens"]) if data["tokens"] else 0,
                "total_tokens": sum(data["tokens"]),
                "mean_cost": mean(data["costs"]) if data["costs"] else 0,
                "total_cost": sum(data["costs"]),
                "count": len(data["tokens"])
            }

        return results

    def identify_bottlenecks(self, metrics: List[Dict]) -> List[Dict]:
        """Identify performance bottlenecks."""
        bottlenecks = []

        # Check for long-running operations
        duration_analysis = self.analyze_durations(metrics)
        for op, stats in duration_analysis.items():
            if stats["mean"] > 600:  # 10 minutes
                improvement = stats["max"] - stats["min"]
                bottlenecks.append({
                    "type": "long_duration",
                    "operation": op,
                    "mean_duration": stats["mean"],
                    "improvement_potential": improvement,
                    "severity": "high" if improvement > 300 else "medium",
                    "recommendation": f"Investigate {op} performance (mean {stats['mean']:.0f}s, range {stats['min']:.0f}s-{stats['max']:.0f}s)"
                })

        # Check for high failure rates
        success_analysis = self.analyze_success_rates(metrics)
        for op, stats in success_analysis.items():
            if stats["success_rate"] < 0.9:
                improvement_potential = 1.0 - stats["success_rate"]
                bottlenecks.append({
                    "type": "high_failure_rate",
                    "operation": op,
                    "success_rate": stats["success_rate"],
                    "improvement_potential": improvement_potential * 100,
                    "severity": "critical" if stats["success_rate"] < 0.8 else "high",
                    "recommendation": f"Investigate {op} failures ({stats['failure']} of {stats['total']}, {stats['success_rate']:.1%} success)"
                })

        # Check for high token usage
        token_analysis = self.analyze_token_usage(metrics)
        for op, stats in token_analysis.items():
            if stats["mean_tokens"] > 100000:
                bottlenecks.append({
                    "type": "high_token_usage",
                    "operation": op,
                    "mean_tokens": stats["mean_tokens"],
                    "total_cost": stats["total_cost"],
                    "severity": "medium",
                    "recommendation": f"Consider LLM caching for {op} (mean {stats['mean_tokens']:.0f} tokens, cost ${stats['total_cost']:.2f})"
                })

        return sorted(bottlenecks, key=lambda x: x["severity"] != "critical", reverse=False)

    def generate_report(self, metrics: List[Dict]) -> str:
        """Generate trend analysis report."""
        report = []
        report.append("# Batch Operations Trend Analysis")
        report.append(f"\nAnalyzed {len(metrics)} batch operations")
        report.append(f"Generated: {json.dumps(metrics[0]['timestamp']) if metrics else 'N/A'}\n")

        # Duration analysis
        report.append("## Operation Durations")
        duration_analysis = self.analyze_durations(metrics)
        if duration_analysis:
            for op, stats in sorted(duration_analysis.items()):
                report.append(f"\n### {op.capitalize()}")
                report.append(f"- Mean: {stats['mean']:.0f}s ({stats['mean']/60:.1f} min)")
                report.append(f"- Median: {stats['median']:.0f}s")
                report.append(f"- Range: {stats['min']:.0f}s - {stats['max']:.0f}s")
                report.append(f"- Std Dev: {stats['stdev']:.0f}s")
                report.append(f"- Count: {stats['count']}")
        else:
            report.append("\nNo duration data available.")

        # Success rate analysis
        report.append("\n## Success Rates")
        success_analysis = self.analyze_success_rates(metrics)
        if success_analysis:
            for op, stats in sorted(success_analysis.items()):
                report.append(f"\n### {op.capitalize()}")
                report.append(f"- Success Rate: {stats['success_rate']:.1%}")
                report.append(f"- Total Items: {stats['total']}")
                report.append(f"- Successful: {stats['success']}")
                report.append(f"- Failed: {stats['failure']}")
        else:
            report.append("\nNo success rate data available.")

        # Token usage analysis
        report.append("\n## Token Usage")
        token_analysis = self.analyze_token_usage(metrics)
        if token_analysis:
            for op, stats in sorted(token_analysis.items()):
                report.append(f"\n### {op.capitalize()}")
                report.append(f"- Mean Tokens: {stats['mean_tokens']:.0f}")
                report.append(f"- Total Tokens: {stats['total_tokens']:.0f}")
                report.append(f"- Mean Cost: ${stats['mean_cost']:.3f}")
                report.append(f"- Total Cost: ${stats['total_cost']:.2f}")
                report.append(f"- Count: {stats['count']}")
        else:
            report.append("\nNo token usage data available.")

        # Bottlenecks
        report.append("\n## Identified Bottlenecks")
        bottlenecks = self.identify_bottlenecks(metrics)
        if bottlenecks:
            for i, bottleneck in enumerate(bottlenecks, 1):
                report.append(f"\n### Bottleneck {i}: {bottleneck['type'].replace('_', ' ').title()}")
                report.append(f"- Operation: {bottleneck['operation']}")
                report.append(f"- Severity: {bottleneck['severity'].upper()}")
                report.append(f"- Recommendation: {bottleneck['recommendation']}")
        else:
            report.append("\nNo bottlenecks identified.")

        return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(description="Analyze batch operation trends")
    parser.add_argument("--recent", type=int, help="Analyze N most recent batches")
    parser.add_argument("--all", action="store_true", help="Analyze all batches")
    args = parser.parse_args()

    metrics_dir = Path(".ce/completed-batches")
    if not metrics_dir.exists():
        print("No metrics found. Run analyze-batch.py first.")
        return

    analyzer = TrendAnalyzer(metrics_dir)
    limit = args.recent if args.recent else None
    metrics = analyzer.load_metrics(limit)

    if not metrics:
        print("No metrics found.")
        return

    report = analyzer.generate_report(metrics)
    print(report)

    # Save report
    output_file = Path(".ce/trend-analysis-report.md")
    output_file.write_text(report)
    print(f"\nReport saved to: {output_file}")


if __name__ == "__main__":
    main()
