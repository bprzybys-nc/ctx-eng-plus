"""PRP Size Analyzer and Decomposition Recommender.

Analyzes PRP documents for size constraints and provides decomposition
recommendations to prevent "PRP obesity".
"""

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional


class SizeCategory(Enum):
    """PRP size categories based on complexity metrics."""
    GREEN = "GREEN"    # Optimal size
    YELLOW = "YELLOW"  # Approaching limits
    RED = "RED"        # Needs decomposition


@dataclass
class PRPMetrics:
    """Metrics extracted from a PRP document."""
    name: str
    lines: int
    estimated_hours: Optional[str]
    phases: int
    risk_level: str
    functions: int
    success_criteria: int
    file_path: Path


@dataclass
class PRPAnalysis:
    """Analysis results for a PRP document."""
    metrics: PRPMetrics
    size_category: SizeCategory
    score: float  # 0-100, higher = more complex
    recommendations: List[str]
    decomposition_suggestions: List[str]


def extract_prp_metrics(prp_file: Path) -> PRPMetrics:
    """Extract size and complexity metrics from a PRP file.

    Args:
        prp_file: Path to PRP markdown file

    Returns:
        PRPMetrics object with extracted data

    Raises:
        FileNotFoundError: If PRP file doesn't exist
        RuntimeError: If metrics extraction fails
    """
    if not prp_file.exists():
        raise FileNotFoundError(
            f"PRP file not found: {prp_file}\n"
            f"🔧 Troubleshooting: Verify file path and try again"
        )

    try:
        content = prp_file.read_text()
    except Exception as e:
        raise RuntimeError(
            f"Failed to read PRP file: {e}\n"
            f"🔧 Troubleshooting: Check file permissions"
        )

    # Extract metrics
    name = prp_file.stem
    lines = len(content.split('\n'))

    # Hours - try multiple patterns
    hours_match = re.search(r'estimated_hours:\s*([0-9]+(?:-[0-9]+)?)', content)
    if not hours_match:
        hours_match = re.search(r'Effort.*?([0-9]+-?[0-9]*)\s*hour', content, re.IGNORECASE)
    hours = hours_match.group(1) if hours_match else None

    # Phases
    phases = len(re.findall(r'^### Phase [0-9]+', content, re.MULTILINE))

    # Risk
    risk_match = re.search(r'\*\*Risk\*\*:\s*(LOW|MEDIUM|HIGH)', content)
    risk = risk_match.group(1) if risk_match else 'UNKNOWN'

    # Functions (code examples in PRP)
    functions = len(re.findall(r'def \w+\(', content))

    # Success criteria
    criteria = len(re.findall(r'- \[[ x]\]', content))

    return PRPMetrics(
        name=name,
        lines=lines,
        estimated_hours=hours,
        phases=phases,
        risk_level=risk,
        functions=functions,
        success_criteria=criteria,
        file_path=prp_file
    )


def calculate_complexity_score(metrics: PRPMetrics) -> float:
    """Calculate complexity score (0-100) for a PRP.

    Score formula weights multiple factors:
    - Lines: 40% weight (normalized to 1500 lines max)
    - Functions: 25% weight (normalized to 40 functions max)
    - Criteria: 20% weight (normalized to 50 criteria max)
    - Phases: 10% weight (normalized to 15 phases max)
    - Risk: 5% weight (LOW=0, MEDIUM=50, HIGH=100)

    Args:
        metrics: PRPMetrics object

    Returns:
        Complexity score from 0-100
    """
    # Normalize each metric to 0-100 scale
    line_score = min(100, (metrics.lines / 1500) * 100)
    function_score = min(100, (metrics.functions / 40) * 100)
    criteria_score = min(100, (metrics.success_criteria / 50) * 100)
    phase_score = min(100, (metrics.phases / 15) * 100)

    # Risk mapping
    risk_map = {'LOW': 0, 'MEDIUM': 50, 'HIGH': 100, 'UNKNOWN': 25}
    risk_score = risk_map.get(metrics.risk_level, 25)

    # Weighted average
    score = (
        line_score * 0.40 +
        function_score * 0.25 +
        criteria_score * 0.20 +
        phase_score * 0.10 +
        risk_score * 0.05
    )

    return round(score, 2)


def categorize_prp_size(score: float, metrics: PRPMetrics) -> SizeCategory:
    """Determine size category based on complexity score and metrics.

    Thresholds derived from historical PRP analysis:
    - GREEN: score < 50, lines < 700, risk LOW-MEDIUM
    - YELLOW: score 50-70, lines 700-1000, risk MEDIUM
    - RED: score > 70, lines > 1000, risk HIGH

    Args:
        score: Complexity score (0-100)
        metrics: PRPMetrics object

    Returns:
        SizeCategory enum value
    """
    # Hard constraints for RED
    if metrics.lines > 1000 or metrics.risk_level == 'HIGH' or score > 70:
        return SizeCategory.RED

    # YELLOW thresholds
    if (metrics.lines > 700 or
        metrics.functions > 20 or
        metrics.success_criteria > 30 or
        score > 50):
        return SizeCategory.YELLOW

    # GREEN - optimal size
    return SizeCategory.GREEN


def generate_recommendations(metrics: PRPMetrics, score: float, category: SizeCategory) -> List[str]:
    """Generate actionable recommendations based on PRP analysis.

    Args:
        metrics: PRPMetrics object
        score: Complexity score
        category: Size category

    Returns:
        List of recommendation strings
    """
    recs = []

    if category == SizeCategory.GREEN:
        recs.append("✅ PRP size is optimal - good job!")
        if score > 40:
            recs.append("Monitor: Approaching YELLOW threshold, avoid scope creep")
        return recs

    if category == SizeCategory.YELLOW:
        recs.append("⚠️ PRP approaching size limits - consider scope reduction")

        if metrics.lines > 700:
            recs.append(f"Lines ({metrics.lines}) approaching RED threshold (1000)")

        if metrics.functions > 20:
            recs.append(f"Functions ({metrics.functions}) indicate high implementation complexity")

        if metrics.success_criteria > 30:
            recs.append(f"Success criteria ({metrics.success_criteria}) suggest multiple features")

        recs.append("Recommendation: Review if PRP can be split into sub-PRPs")
        return recs

    # RED category
    recs.append("🚨 PRP TOO LARGE - decomposition strongly recommended")

    if metrics.lines > 1000:
        recs.append(f"Lines ({metrics.lines}) exceed RED threshold - split into sub-PRPs")

    if metrics.risk_level == 'HIGH':
        recs.append("HIGH risk rating - isolate risky components into separate PRPs")

    if metrics.functions > 25:
        recs.append(f"Functions ({metrics.functions}) indicate multiple features - create sub-PRPs")

    if metrics.phases > 5:
        recs.append(f"Phases ({metrics.phases}) could be independent PRPs")

    recs.append("ACTION REQUIRED: Decompose before execution")

    return recs


def suggest_decomposition(metrics: PRPMetrics) -> List[str]:
    """Generate decomposition strategy suggestions.

    Args:
        metrics: PRPMetrics object

    Returns:
        List of decomposition suggestion strings
    """
    suggestions = []

    if metrics.phases >= 5:
        suggestions.append(
            f"Phase-based decomposition: Create {metrics.phases} sub-PRPs "
            f"(PRP-X.1 through PRP-X.{metrics.phases})"
        )
        suggestions.append("Group related phases if some are interdependent")

    if metrics.functions > 20:
        suggestions.append(
            "Feature-based decomposition: Split by functional area "
            "(e.g., parser, validator, executor)"
        )

    if metrics.risk_level == 'HIGH':
        suggestions.append(
            "Risk-based decomposition: Isolate HIGH-risk components "
            "into separate PRPs for focused attention"
        )

    if metrics.success_criteria > 30:
        suggestions.append(
            "Criteria-based decomposition: Group related success criteria "
            "into logical sub-features"
        )

    if not suggestions:
        suggestions.append("No decomposition needed - PRP size is manageable")

    return suggestions


def analyze_prp(prp_file: Path) -> PRPAnalysis:
    """Comprehensive PRP size analysis.

    Args:
        prp_file: Path to PRP markdown file

    Returns:
        PRPAnalysis object with full analysis results

    Raises:
        FileNotFoundError: If PRP file doesn't exist
        RuntimeError: If analysis fails
    """
    try:
        metrics = extract_prp_metrics(prp_file)
        score = calculate_complexity_score(metrics)
        category = categorize_prp_size(score, metrics)
        recommendations = generate_recommendations(metrics, score, category)
        decomposition = suggest_decomposition(metrics)

        return PRPAnalysis(
            metrics=metrics,
            size_category=category,
            score=score,
            recommendations=recommendations,
            decomposition_suggestions=decomposition
        )
    except Exception as e:
        raise RuntimeError(
            f"PRP analysis failed: {e}\n"
            f"🔧 Troubleshooting: Verify PRP file format and try again"
        )


def format_analysis_report(analysis: PRPAnalysis, json_output: bool = False) -> str:
    """Format analysis results as human-readable report or JSON.

    Args:
        analysis: PRPAnalysis object
        json_output: If True, return JSON string

    Returns:
        Formatted report string
    """
    if json_output:
        import json
        data = {
            'name': analysis.metrics.name,
            'size_category': analysis.size_category.value,
            'complexity_score': analysis.score,
            'metrics': {
                'lines': analysis.metrics.lines,
                'hours': analysis.metrics.estimated_hours,
                'phases': analysis.metrics.phases,
                'risk': analysis.metrics.risk_level,
                'functions': analysis.metrics.functions,
                'criteria': analysis.metrics.success_criteria
            },
            'recommendations': analysis.recommendations,
            'decomposition_suggestions': analysis.decomposition_suggestions
        }
        return json.dumps(data, indent=2)

    # Human-readable format
    m = analysis.metrics
    lines = [
        f"\n{'='*80}",
        f"PRP Size Analysis: {m.name}",
        f"{'='*80}",
        f"\nMetrics:",
        f"  Lines:            {m.lines}",
        f"  Estimated Hours:  {m.estimated_hours or 'N/A'}",
        f"  Phases:           {m.phases}",
        f"  Risk Level:       {m.risk_level}",
        f"  Functions:        {m.functions}",
        f"  Success Criteria: {m.success_criteria}",
        f"\nComplexity Score: {analysis.score}/100",
        f"Size Category:    {analysis.size_category.value}",
        f"\nRecommendations:",
    ]

    for rec in analysis.recommendations:
        lines.append(f"  • {rec}")

    lines.append("\nDecomposition Suggestions:")
    for sug in analysis.decomposition_suggestions:
        lines.append(f"  • {sug}")

    lines.append(f"\n{'='*80}\n")

    return '\n'.join(lines)
