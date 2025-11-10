---
prp_id: PRP-47.7.1
title: Phase 2 Preparation - Metrics & Monitoring
status: planning
type: infrastructure
complexity: low
estimated_hours: 4
priority: high
dependencies: [PRP-47.1.1, PRP-47.2.1, PRP-47.3.1, PRP-47.3.2, PRP-47.4.1, PRP-47.5.1, PRP-47.5.2, PRP-47.6.1]
batch_id: 47
stage: 8
---

# PRP-47.7.1: Phase 2 Preparation - Metrics & Monitoring

## Problem

Phase 1 delivered the MVP unified batch command framework with:
- 67% code reduction (1130 lines → 360 lines)
- Parallel execution (60% time reduction)
- Token optimization (70%+ reduction in batch-peer-review)

Phase 2 will implement data-driven improvements based on production usage. To make informed decisions, we need:

- **Metrics collection**: Duration, tokens, cost, errors per batch
- **Trend analysis**: Identify bottlenecks and patterns
- **Decision framework**: Prioritize improvements by impact
- **Monitoring infrastructure**: Track batch operations in production

Without metrics and monitoring:
- Optimization guesses (not data-driven)
- Unknown bottlenecks (where to focus Phase 2 effort)
- No ROI measurement (can't prove improvements)
- Regression risk (changes might make things worse)

## Solution

Setup production monitoring infrastructure for Phase 2:

1. **Batch Metrics Schema**: Standard format for collecting batch data
2. **analyze-batch.py Script**: Extract metrics from completed batches
3. **trend-analysis.py Script**: Identify patterns and bottlenecks
4. **Archival System**: Store completed batch data (.ce/completed-batches/)
5. **Decision Framework**: Criteria for prioritizing Phase 2 work

The monitoring infrastructure will:
- Automatically capture metrics after each batch operation
- Generate trend reports (weekly/monthly)
- Highlight bottlenecks and optimization opportunities
- Inform Phase 2 feature prioritization

## Implementation

### Phase 1: Metrics Schema Definition (1 hour)

**Create**: `.ce/schemas/batch-metrics.json`

**Content**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Batch Metrics",
  "description": "Standard metrics schema for batch operations",
  "type": "object",
  "required": ["batch_id", "operation", "timestamp", "metrics"],
  "properties": {
    "batch_id": {
      "type": "string",
      "description": "Batch identifier (e.g., '47')"
    },
    "operation": {
      "type": "string",
      "enum": ["generate", "execute", "review", "update-context"],
      "description": "Batch operation type"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Operation start time (ISO 8601)"
    },
    "duration_seconds": {
      "type": "number",
      "description": "Total operation duration in seconds"
    },
    "metrics": {
      "type": "object",
      "properties": {
        "total_items": {
          "type": "integer",
          "description": "Total number of items (PRPs, phases)"
        },
        "stages": {
          "type": "integer",
          "description": "Number of stages (for parallel execution)"
        },
        "success_count": {
          "type": "integer",
          "description": "Successfully completed items"
        },
        "failure_count": {
          "type": "integer",
          "description": "Failed items"
        },
        "partial_count": {
          "type": "integer",
          "description": "Partially completed items"
        },
        "token_usage": {
          "type": "object",
          "properties": {
            "input_tokens": {"type": "integer"},
            "output_tokens": {"type": "integer"},
            "total_tokens": {"type": "integer"},
            "estimated_cost": {"type": "number", "description": "USD"}
          }
        },
        "stage_durations": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "stage": {"type": "integer"},
              "duration_seconds": {"type": "number"},
              "items": {"type": "array", "items": {"type": "string"}}
            }
          }
        },
        "errors": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "item_id": {"type": "string"},
              "error_type": {"type": "string"},
              "error_message": {"type": "string"}
            }
          }
        }
      }
    },
    "optimization_metrics": {
      "type": "object",
      "description": "Operation-specific optimization metrics",
      "properties": {
        "shared_context_size": {
          "type": "integer",
          "description": "Shared context size in tokens (review only)"
        },
        "token_savings": {
          "type": "integer",
          "description": "Tokens saved by optimization"
        },
        "parallel_efficiency": {
          "type": "number",
          "description": "Parallel speedup vs sequential (1.0 = no speedup)"
        },
        "drift_scores": {
          "type": "array",
          "description": "Drift scores for context updates",
          "items": {
            "type": "object",
            "properties": {
              "prp_id": {"type": "string"},
              "drift": {"type": "number"}
            }
          }
        }
      }
    }
  }
}
```

**Lines**: ~100 lines

### Phase 2: analyze-batch.py Script (1.5 hours)

**Create**: `.ce/scripts/analyze-batch.py`

**Content**:
```python
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
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class BatchAnalyzer:
    """Analyze batch operations and extract metrics."""

    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        self.project_root = Path.cwd()
        self.prp_dir = self.project_root / "PRPs/feature-requests"

    def analyze_generation(self) -> Dict:
        """Analyze batch generation metrics."""
        # Find all PRPs for batch
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
        # Find all PRPs for batch
        prps = list(self.prp_dir.glob(f"PRP-{self.batch_id}.*.md"))

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
        # TODO: Extract from review report
        return {
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
        result = subprocess.run(
            ["git", "log", "--grep", pattern, "--format=%H|%ai|%s"],
            capture_output=True,
            text=True
        )

        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            commit_hash, timestamp, message = line.split('|', 2)
            commits.append({
                "hash": commit_hash,
                "timestamp": timestamp,
                "message": message
            })

        return commits

    def _calculate_duration(self, first_commit: Optional[Dict], last_commit: Optional[Dict]) -> float:
        """Calculate duration between commits."""
        if not first_commit or not last_commit:
            return 0.0

        from dateutil import parser
        start = parser.parse(first_commit["timestamp"])
        end = parser.parse(last_commit["timestamp"])
        return (end - start).total_seconds()

    def save_metrics(self, metrics: Dict):
        """Save metrics to file."""
        output_dir = self.project_root / ".ce/completed-batches"
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

    if args.operation == "all" or args.operation == "generate":
        metrics = analyzer.analyze_generation()
        analyzer.save_metrics(metrics)

    if args.operation == "all" or args.operation == "execute":
        metrics = analyzer.analyze_execution()
        analyzer.save_metrics(metrics)

    if args.operation == "all" or args.operation == "review":
        metrics = analyzer.analyze_review()
        analyzer.save_metrics(metrics)


if __name__ == "__main__":
    main()
```

**Lines**: ~200 lines

### Phase 3: trend-analysis.py Script (1 hour)

**Create**: `.ce/scripts/trend-analysis.py`

**Content**:
```python
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
from statistics import mean, median


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
            metrics.append(json.loads(file_path.read_text()))

        return metrics

    def analyze_durations(self, metrics: List[Dict]) -> Dict:
        """Analyze operation durations."""
        by_operation = {}

        for metric in metrics:
            op = metric["operation"]
            duration = metric.get("duration_seconds", 0)

            by_operation.setdefault(op, []).append(duration)

        return {
            op: {
                "mean": mean(durations),
                "median": median(durations),
                "min": min(durations),
                "max": max(durations),
                "count": len(durations)
            }
            for op, durations in by_operation.items()
        }

    def analyze_success_rates(self, metrics: List[Dict]) -> Dict:
        """Analyze success rates."""
        by_operation = {}

        for metric in metrics:
            op = metric["operation"]
            total = metric["metrics"]["total_items"]
            success = metric["metrics"]["success_count"]
            failure = metric["metrics"].get("failure_count", 0)

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

    def identify_bottlenecks(self, metrics: List[Dict]) -> List[Dict]:
        """Identify performance bottlenecks."""
        bottlenecks = []

        # Check for long-running operations
        duration_analysis = self.analyze_durations(metrics)
        for op, stats in duration_analysis.items():
            if stats["mean"] > 600:  # 10 minutes
                bottlenecks.append({
                    "type": "long_duration",
                    "operation": op,
                    "mean_duration": stats["mean"],
                    "recommendation": f"Investigate {op} performance (mean {stats['mean']:.0f}s)"
                })

        # Check for high failure rates
        success_analysis = self.analyze_success_rates(metrics)
        for op, stats in success_analysis.items():
            if stats["success_rate"] < 0.9:
                bottlenecks.append({
                    "type": "high_failure_rate",
                    "operation": op,
                    "success_rate": stats["success_rate"],
                    "recommendation": f"Investigate {op} failures ({stats['failure']} of {stats['total']})"
                })

        return bottlenecks

    def generate_report(self, metrics: List[Dict]) -> str:
        """Generate trend analysis report."""
        report = []
        report.append("# Batch Operations Trend Analysis")
        report.append(f"\nAnalyzed {len(metrics)} batch operations\n")

        # Duration analysis
        report.append("## Operation Durations")
        duration_analysis = self.analyze_durations(metrics)
        for op, stats in duration_analysis.items():
            report.append(f"\n### {op.capitalize()}")
            report.append(f"- Mean: {stats['mean']:.0f}s ({stats['mean']/60:.1f} min)")
            report.append(f"- Median: {stats['median']:.0f}s")
            report.append(f"- Range: {stats['min']:.0f}s - {stats['max']:.0f}s")
            report.append(f"- Count: {stats['count']}")

        # Success rate analysis
        report.append("\n## Success Rates")
        success_analysis = self.analyze_success_rates(metrics)
        for op, stats in success_analysis.items():
            report.append(f"\n### {op.capitalize()}")
            report.append(f"- Success Rate: {stats['success_rate']:.1%}")
            report.append(f"- Total Items: {stats['total']}")
            report.append(f"- Successful: {stats['success']}")
            report.append(f"- Failed: {stats['failure']}")

        # Bottlenecks
        report.append("\n## Identified Bottlenecks")
        bottlenecks = self.identify_bottlenecks(metrics)
        if bottlenecks:
            for bottleneck in bottlenecks:
                report.append(f"\n### {bottleneck['type']}")
                report.append(f"- Operation: {bottleneck['operation']}")
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
```

**Lines**: ~180 lines

### Phase 4: Decision Framework Documentation (30 minutes)

**Create**: `PRPs/feature-requests/PRP-47-PHASE2-DECISION-FRAMEWORK.md`

**Content**:
```markdown
# Phase 2 Decision Framework

## Overview
Data-driven approach to prioritizing Phase 2 improvements based on production metrics.

## Prioritization Criteria

### 1. Impact (High/Medium/Low)
**High Impact**: >50% improvement potential or critical bottleneck
**Medium Impact**: 20-50% improvement potential
**Low Impact**: <20% improvement potential

**Measured by**:
- Duration reduction (seconds saved per batch)
- Token reduction (tokens saved per batch)
- Success rate improvement (% increase)

### 2. Effort (1-5 scale)
**1 point**: <4 hours (quick fix)
**2 points**: 4-8 hours (small feature)
**3 points**: 8-16 hours (medium feature)
**4 points**: 16-32 hours (large feature)
**5 points**: >32 hours (major rework)

### 3. Priority Score
Priority Score = Impact × (6 - Effort)

**High Priority**: Score ≥ 10
**Medium Priority**: Score 5-9
**Low Priority**: Score < 5

## Phase 2 Candidate Features

### Candidate 1: LLM Caching
**Impact**: High (50%+ token reduction for repeated calls)
**Effort**: 2 (8 hours)
**Priority Score**: High × 4 = 12

**Metrics Trigger**: Token usage >100k per batch

### Candidate 2: Subagent Result Caching
**Impact**: Medium (30% duration reduction for repeated operations)
**Effort**: 3 (12 hours)
**Priority Score**: Medium × 3 = 9

**Metrics Trigger**: Repeated operations (same input/output)

### Candidate 3: Advanced Error Recovery
**Impact**: High (improve success rate from 85% to 95%+)
**Effort**: 3 (16 hours)
**Priority Score**: High × 3 = 12

**Metrics Trigger**: Success rate <90%

### Candidate 4: Streaming Progress Updates
**Impact**: Low (UX improvement, no performance gain)
**Effort**: 2 (8 hours)
**Priority Score**: Low × 4 = 4

**Metrics Trigger**: User feedback requests

### Candidate 5: Multi-Model Orchestration
**Impact**: High (cost reduction 80%+ by using Haiku more)
**Effort**: 4 (24 hours)
**Priority Score**: High × 2 = 8

**Metrics Trigger**: Cost >$1 per batch

## Decision Process

### Step 1: Collect Metrics (Weeks 4-6)
Run production batches with metrics collection:
- Minimum 10 batches across all operations
- Mix of small (2-3 PRPs) and large (8-10 PRPs) batches
- Capture all metrics (duration, tokens, success rate, errors)

### Step 2: Analyze Trends (Week 6)
Run trend-analysis.py:
```bash
python .ce/scripts/trend-analysis.py --all
```

Review report:
- Identify bottlenecks (long duration, high failure rate)
- Calculate improvement potential (max-mean duration, success rate gap)
- Prioritize by impact

### Step 3: Score Candidates (Week 7)
For each bottleneck or improvement opportunity:
1. Match to candidate feature (or create new candidate)
2. Estimate impact (based on metrics)
3. Estimate effort (based on complexity)
4. Calculate priority score
5. Sort by priority score

### Step 4: Plan Phase 2 (Week 7)
Select top 3-5 high-priority features:
- Total effort <80 hours (2 weeks of work)
- Mix of quick wins (effort 1-2) and high-impact features
- Create PRPs for selected features
- Execute as Phase 2 batch

## Example Decision

**Metrics from Week 4-6**:
- batch-exe-prp: Mean duration 1800s (30 min), 85% success rate
- batch-gen-prp: Mean token usage 150k, cost $0.75 per batch
- batch-peer-review: Mean duration 300s (5 min), 95% success rate

**Analysis**:
- Bottleneck 1: batch-exe-prp duration (30 min mean, 10 min min)
  - Improvement potential: 20 min (66%)
  - Match to: Subagent Result Caching (Candidate 2)

- Bottleneck 2: batch-exe-prp success rate (85%)
  - Improvement potential: 10% (to 95%)
  - Match to: Advanced Error Recovery (Candidate 3)

- Opportunity: batch-gen-prp cost ($0.75 per batch)
  - Improvement potential: $0.60 (80%)
  - Match to: Multi-Model Orchestration (Candidate 5)

**Priority Scores**:
1. Advanced Error Recovery: 12 (high impact, medium effort)
2. Subagent Result Caching: 9 (medium impact, medium effort)
3. Multi-Model Orchestration: 8 (high impact, high effort)

**Phase 2 Plan**: Execute Candidates 3, 2 in order (total 28 hours)

## Metrics Collection Checklist

- [ ] analyze-batch.py script working
- [ ] trend-analysis.py script working
- [ ] Run 10+ production batches (mix of sizes)
- [ ] Collect metrics for all operations (gen, exe, review, context-update)
- [ ] Generate trend analysis report
- [ ] Review report with team
- [ ] Score candidate features
- [ ] Create Phase 2 plan
```

**Lines**: ~150 lines

### Phase 5: Integration & Testing (1 hour)

**Test metrics collection**:
```bash
# Test analyze-batch.py
cd .ce/scripts
python analyze-batch.py --batch 47 --operation generate
python analyze-batch.py --batch 47 --all

# Verify output
ls -la ../.ce/completed-batches/
cat ../.ce/completed-batches/batch-47-generate.json

# Test trend-analysis.py
python trend-analysis.py --recent 2
cat ../.ce/trend-analysis-report.md
```

**Create integration into batch commands**:
```markdown
### Post-Batch Metrics Collection

Add to each batch command's Phase 6 (Aggregation):

After operation completes:
1. Collect metrics (duration, token usage, success rate)
2. Call analyze-batch.py: `python .ce/scripts/analyze-batch.py --batch {{batch_id}} --operation {{op}}`
3. Store metrics in .ce/completed-batches/
4. Log: "Metrics saved for batch {{batch_id}}"
```

## Validation

### Pre-Implementation Checks
- [ ] All Phase 1 PRPs completed (PRP-47.1.1 through PRP-47.6.1)
- [ ] Python dateutil installed: `uv add python-dateutil`
- [ ] Create .ce/schemas/ and .ce/scripts/ directories

### Post-Implementation Checks
- [ ] analyze-batch.py generates correct metrics JSON
- [ ] trend-analysis.py identifies patterns from 2+ batches
- [ ] Metrics schema covers all needed data
- [ ] Scripts have error handling
- [ ] Documentation explains Phase 2 decision framework

### Integration Checks
- [ ] Scripts integrate with batch commands
- [ ] Metrics automatically collected after each batch
- [ ] Trend reports generated weekly

## Acceptance Criteria

1. **Metrics Collection**
   - analyze-batch.py works for all 4 operations (gen, exe, review, context-update)
   - Metrics saved in standard JSON format
   - Schema validation passes

2. **Trend Analysis**
   - trend-analysis.py identifies bottlenecks correctly
   - Report includes duration, success rate, recommendations
   - Handles edge cases (no metrics, single batch)

3. **Decision Framework**
   - Phase 2 candidate features documented
   - Prioritization criteria defined
   - Decision process clear (4 steps)

4. **Production Ready**
   - Scripts integrated into batch commands
   - Error handling robust
   - Documentation complete

## Testing Strategy

### Unit Tests
```python
# Test metrics schema validation
def test_metrics_schema_valid():
    schema = json.loads(Path(".ce/schemas/batch-metrics.json").read_text())
    # Test with sample metrics
    assert validate(sample_metrics, schema)

# Test duration calculation
def test_calculate_duration():
    analyzer = BatchAnalyzer("47")
    duration = analyzer._calculate_duration(first_commit, last_commit)
    assert duration > 0
```

### Integration Tests
```bash
# Test with real batch
python .ce/scripts/analyze-batch.py --batch 47 --all
python .ce/scripts/trend-analysis.py --recent 1

# Verify outputs
test -f .ce/completed-batches/batch-47-generate.json
test -f .ce/trend-analysis-report.md
```

### Manual Testing
```bash
# Collect metrics for PRP-47 batch
cd .ce/scripts
python analyze-batch.py --batch 47 --all

# Generate trend report
python trend-analysis.py --all

# Review report
cat ../.ce/trend-analysis-report.md
```

## Risks & Mitigations

### Risk: Metrics collection fails silently
**Impact**: No data for Phase 2 decisions
**Mitigation**: Add logging, error handling, verify metrics files after each batch

### Risk: Git log parsing unreliable
**Impact**: Inaccurate duration metrics
**Mitigation**: Test with various commit patterns, add fallback to timestamp files

### Risk: Trend analysis identifies wrong bottlenecks
**Impact**: Phase 2 optimizes wrong areas
**Mitigation**: Manual review of metrics, validate with user feedback

### Risk: Decision framework too rigid
**Impact**: Miss important improvements
**Mitigation**: Allow flexibility for critical bugs or user requests

### Risk: Metrics overhead slows batches
**Impact**: Performance regression
**Mitigation**: Run metrics collection async, minimize git log queries

## Dependencies

- **All Phase 1 PRPs**: This PRP depends on completed Phase 1 (orchestrator framework deployed)

## Related PRPs

- **Phase 1 Completion**: PRP-47.6.1 (documentation and deployment)
- **Future**: Phase 2 PRPs (to be created based on metrics)

## Files Modified

- `.ce/schemas/batch-metrics.json` (create)
- `.ce/scripts/analyze-batch.py` (create)
- `.ce/scripts/trend-analysis.py` (create)
- `PRPs/feature-requests/PRP-47-PHASE2-DECISION-FRAMEWORK.md` (create)

## Notes

- This PRP bridges Phase 1 and Phase 2
- Metrics collection starts immediately after Phase 1 deployment
- Phase 2 features TBD based on production data (Weeks 4-7)
- Decision framework flexible (adjust based on learnings)
- Scripts use stdlib + dateutil (minimal dependencies)
- Time estimate includes testing with real batches
