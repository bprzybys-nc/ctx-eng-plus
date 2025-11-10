#!/usr/bin/env python3
"""
Analyze completed batch operation and generate metrics.

Usage:
    python analyze-batch.py --batch 47 --operation generate
    python analyze-batch.py --batch 47 --operation execute
    python analyze-batch.py --batch 47 --all

Output: JSON metrics file in .ce/completed-batches/
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class BatchAnalyzer:
    """Analyze batch operations and extract metrics."""

    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        self.project_root = Path.cwd()
        self.prp_dir = self.project_root / "PRPs" / "feature-requests"
        self.executed_dir = self.project_root / "PRPs" / "executed"

    def analyze_generation(self) -> Dict:
        """Analyze batch generation metrics."""
        # Find all PRPs for batch in feature-requests
        prps = list(self.prp_dir.glob(f"PRP-{self.batch_id}.*.md"))

        # Extract metadata
        stages = {}
        for prp_path in prps:
            content = prp_path.read_text()
            # Parse YAML frontmatter
            stage = self._extract_yaml_field(content, "stage")
            stages.setdefault(stage, []).append(prp_path.stem)

        # Get git log for timing
        git_log = self._get_git_log(f"PRP-{self.batch_id}")
        first_commit = git_log[-1] if git_log else None
        last_commit = git_log[0] if git_log else None

        duration = self._calculate_duration(first_commit, last_commit)

        return {
            "batch_id": self.batch_id,
            "operation": "generate",
            "timestamp": first_commit["timestamp"] if first_commit else datetime.now().isoformat(),
            "duration_seconds": duration,
            "metrics": {
                "total_items": len(prps),
                "stages": len(stages),
                "success_count": len(prps),
                "failure_count": 0,
                "partial_count": 0,
                "stage_durations": [
                    {
                        "stage": stage,
                        "duration_seconds": 0,  # TODO: Extract from logs
                        "items": items
                    }
                    for stage, items in sorted(stages.items())
                ]
            }
        }

    def analyze_execution(self) -> Dict:
        """Analyze batch execution metrics."""
        # Find all PRPs for batch (may be in either location)
        prps_feature = list(self.prp_dir.glob(f"PRP-{self.batch_id}.*.md"))
        prps_executed = list(self.executed_dir.glob(f"PRP-{self.batch_id}.*.md"))
        prps = prps_feature + prps_executed

        if not prps:
            print(f"Warning: No PRPs found for batch {self.batch_id}")
            prps = []

        # Check status
        completed = []
        partial = []
        failed = []

        for prp_path in prps:
            content = prp_path.read_text()
            status = self._extract_yaml_field(content, "status")
            if status == "completed":
                completed.append(prp_path.stem)
            elif status == "in_progress":
                partial.append(prp_path.stem)
            else:
                failed.append(prp_path.stem)

        # Get git log for timing
        git_log = self._get_git_log(f"PRP-{self.batch_id}")
        first_commit = git_log[-1] if git_log else None
        last_commit = git_log[0] if git_log else None

        duration = self._calculate_duration(first_commit, last_commit)

        return {
            "batch_id": self.batch_id,
            "operation": "execute",
            "timestamp": first_commit["timestamp"] if first_commit else datetime.now().isoformat(),
            "duration_seconds": duration,
            "metrics": {
                "total_items": len(prps),
                "success_count": len(completed),
                "failure_count": len(failed),
                "partial_count": len(partial),
                "errors": [
                    {"item_id": prp, "error_type": "execution_failure", "error_message": "Unknown"}
                    for prp in failed
                ]
            }
        }

    def analyze_review(self) -> Dict:
        """Analyze batch review metrics."""
        # Find review report if it exists
        review_file = self.project_root / f".ce/orchestration/batches/batch-{self.batch_id}.result.json"

        metrics = {
            "batch_id": self.batch_id,
            "operation": "review",
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_items": 0,
                "success_count": 0
            },
            "optimization_metrics": {
                "shared_context_size": 0,
                "token_savings": 0
            }
        }

        if review_file.exists():
            try:
                review_data = json.loads(review_file.read_text())
                metrics["timestamp"] = review_data.get("timestamp", metrics["timestamp"])
                metrics["metrics"]["total_items"] = len(review_data.get("results", []))
                metrics["metrics"]["success_count"] = len([
                    r for r in review_data.get("results", [])
                    if r.get("status") == "completed"
                ])
            except Exception as e:
                print(f"Warning: Could not parse review file: {e}")

        return metrics

    def analyze_update_context(self) -> Dict:
        """Analyze context update metrics."""
        # Find context update logs if they exist
        return {
            "batch_id": self.batch_id,
            "operation": "update-context",
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_items": 0,
                "success_count": 0
            },
            "optimization_metrics": {
                "drift_scores": []
            }
        }

    def _extract_yaml_field(self, content: str, field: str) -> Optional[str]:
        """Extract field from YAML frontmatter."""
        lines = content.split('\n')
        for line in lines[1:]:  # Skip first ---
            if line.startswith(field + ':'):
                return line.split(':', 1)[1].strip()
            if line.startswith('---'):
                break
        return None

    def _get_git_log(self, pattern: str) -> List[Dict]:
        """Get git log entries matching pattern."""
        try:
            result = subprocess.run(
                ["git", "log", "--grep", pattern, "--format=%H|%ai|%s"],
                capture_output=True,
                text=True,
                timeout=10
            )

            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|', 2)
                if len(parts) != 3:
                    continue
                commit_hash, timestamp, message = parts
                commits.append({
                    "hash": commit_hash,
                    "timestamp": timestamp,
                    "message": message
                })

            return commits
        except subprocess.TimeoutExpired:
            print(f"Warning: git log timeout for pattern {pattern}")
            return []
        except Exception as e:
            print(f"Warning: Could not get git log: {e}")
            return []

    def _calculate_duration(self, first_commit: Optional[Dict], last_commit: Optional[Dict]) -> float:
        """Calculate duration between commits."""
        if not first_commit or not last_commit:
            return 0.0

        try:
            from dateutil import parser
            start = parser.parse(first_commit["timestamp"])
            end = parser.parse(last_commit["timestamp"])
            return (end - start).total_seconds()
        except ImportError:
            print("Warning: dateutil not installed, cannot calculate duration")
            return 0.0
        except Exception as e:
            print(f"Warning: Could not calculate duration: {e}")
            return 0.0

    def save_metrics(self, metrics: Dict):
        """Save metrics to file."""
        output_dir = self.project_root / ".ce" / "completed-batches"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"batch-{self.batch_id}-{metrics['operation']}.json"
        output_file.write_text(json.dumps(metrics, indent=2))

        print(f"Metrics saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Analyze batch operation metrics")
    parser.add_argument("--batch", required=True, help="Batch ID")
    parser.add_argument("--operation", choices=["generate", "execute", "review", "update-context", "all"])
    args = parser.parse_args()

    analyzer = BatchAnalyzer(args.batch)

    operations = {
        "generate": analyzer.analyze_generation,
        "execute": analyzer.analyze_execution,
        "review": analyzer.analyze_review,
        "update-context": analyzer.analyze_update_context,
    }

    if args.operation == "all":
        for op_name, op_func in operations.items():
            try:
                metrics = op_func()
                analyzer.save_metrics(metrics)
            except Exception as e:
                print(f"Error analyzing {op_name}: {e}", file=sys.stderr)
    elif args.operation:
        try:
            metrics = operations[args.operation]()
            analyzer.save_metrics(metrics)
        except Exception as e:
            print(f"Error analyzing {args.operation}: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
