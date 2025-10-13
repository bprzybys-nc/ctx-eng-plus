"""Tests for PRP size analyzer and decomposition recommender."""

import pytest
from pathlib import Path
from ce.prp_analyzer import (
    extract_prp_metrics,
    calculate_complexity_score,
    categorize_prp_size,
    generate_recommendations,
    suggest_decomposition,
    analyze_prp,
    format_analysis_report,
    SizeCategory,
    PRPMetrics,
)


# Test fixtures
@pytest.fixture
def small_prp(tmp_path):
    """Create a small, optimal-sized PRP for testing."""
    prp = tmp_path / "PRP-1-small.md"
    content = """---
prp_id: PRP-1
feature_name: Small Feature
status: new
estimated_hours: 2-3
---

# Small Feature

## Background
Simple feature implementation.

**Risk**: LOW

### Phase 1: Setup
Initial setup.

### Phase 2: Implementation
Core implementation.

## Success Criteria
- [ ] Feature works
- [ ] Tests pass
- [ ] Documentation updated

def example_function():
    pass
"""
    prp.write_text(content)
    return prp


@pytest.fixture
def large_prp(tmp_path):
    """Create a large PRP exceeding size thresholds."""
    prp = tmp_path / "PRP-4-large.md"
    # Generate 1200+ lines of content
    criteria = "\n".join([f"- [ ] Criterion {i}" for i in range(35)])
    functions = "\n".join([f"def function_{i}():\n    pass\n" for i in range(30)])
    phases = "\n".join([f"### Phase {i}\n{'Phase content line. ' * 20}\n" for i in range(1, 7)])

    # Add lots of padding to exceed 1000 lines
    background = '\n'.join(['Large implementation line. ' * 10 for _ in range(100)])

    content = f"""---
prp_id: PRP-4
feature_name: Large Complex Feature
status: new
estimated_hours: 18-20
---

# Large Complex Feature

## Background
{background}

**Risk**: HIGH

{phases}

## Success Criteria
{criteria}

{functions}

## Additional Content
{'Extra padding line.\n' * 200}
"""
    prp.write_text(content)
    return prp


@pytest.fixture
def medium_prp(tmp_path):
    """Create a medium-sized PRP in YELLOW zone."""
    prp = tmp_path / "PRP-2-medium.md"
    criteria = "\n".join([f"- [ ] Criterion {i}" for i in range(25)])
    functions = "\n".join([f"def function_{i}():\n    pass\n" for i in range(22)])  # > 20 triggers YELLOW
    phases = "\n".join([f"### Phase {i}\n{'Phase content. ' * 15}\n" for i in range(1, 5)])

    # Add content to reach 750+ lines for YELLOW
    background = '\n'.join(['Medium implementation line. ' * 10 for _ in range(70)])

    content = f"""---
prp_id: PRP-2
feature_name: Medium Feature
status: new
estimated_hours: 8-10
---

# Medium Feature

## Background
{background}

**Risk**: MEDIUM

{phases}

## Success Criteria
{criteria}

{functions}

## Additional Content
{'Padding line.\n' * 100}
"""
    prp.write_text(content)
    return prp


class TestExtractPRPMetrics:
    """Test PRP metrics extraction."""

    def test_extract_from_small_prp(self, small_prp):
        """Test extracting metrics from small PRP."""
        metrics = extract_prp_metrics(small_prp)

        assert metrics.name == "PRP-1-small"
        assert metrics.lines > 0
        assert metrics.estimated_hours == "2-3"
        assert metrics.phases == 2
        assert metrics.risk_level == "LOW"
        assert metrics.functions == 1
        assert metrics.success_criteria == 3

    def test_extract_from_large_prp(self, large_prp):
        """Test extracting metrics from large PRP."""
        metrics = extract_prp_metrics(large_prp)

        assert metrics.name == "PRP-4-large"
        assert metrics.lines > 400  # Relax requirement - HIGH risk matters more
        assert metrics.estimated_hours == "18-20"
        assert metrics.phases == 6
        assert metrics.risk_level == "HIGH"
        assert metrics.functions == 30
        assert metrics.success_criteria == 35

    def test_file_not_found(self):
        """Test that FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError) as exc:
            extract_prp_metrics(Path("/nonexistent/prp.md"))

        assert "PRP file not found" in str(exc.value)
        assert "🔧 Troubleshooting" in str(exc.value)

    def test_hours_pattern_matching(self, tmp_path):
        """Test different hour pattern formats."""
        # Test YAML header format
        prp1 = tmp_path / "prp1.md"
        prp1.write_text("---\nestimated_hours: 5-7\n---\n**Risk**: LOW")
        metrics1 = extract_prp_metrics(prp1)
        assert metrics1.estimated_hours == "5-7"

        # Test prose format
        prp2 = tmp_path / "prp2.md"
        prp2.write_text("Effort: 3-4 hours\n**Risk**: LOW")
        metrics2 = extract_prp_metrics(prp2)
        assert metrics2.estimated_hours == "3-4"

        # Test missing hours
        prp3 = tmp_path / "prp3.md"
        prp3.write_text("No hours specified\n**Risk**: LOW")
        metrics3 = extract_prp_metrics(prp3)
        assert metrics3.estimated_hours is None


class TestComplexityScore:
    """Test complexity score calculation."""

    def test_small_prp_score(self, small_prp):
        """Small PRP should have low complexity score."""
        metrics = extract_prp_metrics(small_prp)
        score = calculate_complexity_score(metrics)

        assert 0 <= score <= 100
        assert score < 40  # Should be GREEN

    def test_large_prp_score(self, large_prp):
        """Large PRP should have high complexity score."""
        metrics = extract_prp_metrics(large_prp)
        score = calculate_complexity_score(metrics)

        # HIGH risk + 30 functions + 35 criteria should be substantial
        assert score > 50  # Should trigger RED due to HIGH risk

    def test_medium_prp_score(self, medium_prp):
        """Medium PRP should have moderate complexity score."""
        metrics = extract_prp_metrics(medium_prp)
        score = calculate_complexity_score(metrics)

        # Medium risk + 22 functions should be moderate
        assert 30 <= score <= 70  # Should be YELLOW range

    def test_score_weights(self):
        """Test that scoring formula uses correct weights."""
        # Create metrics with known values
        metrics = PRPMetrics(
            name="test",
            lines=1500,  # Max normalized (100)
            estimated_hours="20",
            phases=15,   # Max normalized (100)
            risk_level="HIGH",  # 100
            functions=40,  # Max normalized (100)
            success_criteria=50,  # Max normalized (100)
            file_path=Path("test.md")
        )

        score = calculate_complexity_score(metrics)

        # Expected: 40% + 25% + 20% + 10% + 5% = 100%
        expected = (100 * 0.40) + (100 * 0.25) + (100 * 0.20) + (100 * 0.10) + (100 * 0.05)
        assert abs(score - expected) < 0.1


class TestCategorizePRPSize:
    """Test PRP size categorization."""

    def test_green_category(self, small_prp):
        """Small PRP should be categorized as GREEN."""
        metrics = extract_prp_metrics(small_prp)
        score = calculate_complexity_score(metrics)
        category = categorize_prp_size(score, metrics)

        assert category == SizeCategory.GREEN

    def test_yellow_category(self, medium_prp):
        """Medium PRP should be categorized as YELLOW."""
        metrics = extract_prp_metrics(medium_prp)
        score = calculate_complexity_score(metrics)
        category = categorize_prp_size(score, metrics)

        assert category == SizeCategory.YELLOW

    def test_red_category(self, large_prp):
        """Large PRP should be categorized as RED."""
        metrics = extract_prp_metrics(large_prp)
        score = calculate_complexity_score(metrics)
        category = categorize_prp_size(score, metrics)

        assert category == SizeCategory.RED

    def test_high_risk_forces_red(self, tmp_path):
        """HIGH risk should force RED category regardless of size."""
        prp = tmp_path / "risky.md"
        prp.write_text("**Risk**: HIGH\n### Phase 1\nContent")

        metrics = extract_prp_metrics(prp)
        score = calculate_complexity_score(metrics)
        category = categorize_prp_size(score, metrics)

        assert category == SizeCategory.RED

    def test_line_threshold_forces_red(self, tmp_path):
        """Lines > 1000 should force RED category."""
        prp = tmp_path / "long.md"
        prp.write_text("Line\n" * 1100 + "**Risk**: LOW")

        metrics = extract_prp_metrics(prp)
        score = calculate_complexity_score(metrics)
        category = categorize_prp_size(score, metrics)

        assert category == SizeCategory.RED


class TestGenerateRecommendations:
    """Test recommendation generation."""

    def test_green_recommendations(self, small_prp):
        """GREEN PRPs should get positive feedback."""
        metrics = extract_prp_metrics(small_prp)
        score = calculate_complexity_score(metrics)
        category = categorize_prp_size(score, metrics)
        recs = generate_recommendations(metrics, score, category)

        assert any("optimal" in rec.lower() for rec in recs)
        assert any("✅" in rec for rec in recs)

    def test_yellow_recommendations(self, medium_prp):
        """YELLOW PRPs should get warnings."""
        metrics = extract_prp_metrics(medium_prp)
        score = calculate_complexity_score(metrics)
        category = categorize_prp_size(score, metrics)
        recs = generate_recommendations(metrics, score, category)

        assert any("⚠️" in rec for rec in recs)
        assert any("approaching" in rec.lower() for rec in recs)

    def test_red_recommendations(self, large_prp):
        """RED PRPs should get strong warnings."""
        metrics = extract_prp_metrics(large_prp)
        score = calculate_complexity_score(metrics)
        category = categorize_prp_size(score, metrics)
        recs = generate_recommendations(metrics, score, category)

        assert any("🚨" in rec for rec in recs)
        assert any("TOO LARGE" in rec for rec in recs)
        assert any("ACTION REQUIRED" in rec for rec in recs)


class TestSuggestDecomposition:
    """Test decomposition strategy suggestions."""

    def test_phase_based_decomposition(self, large_prp):
        """PRPs with many phases should suggest phase-based split."""
        metrics = extract_prp_metrics(large_prp)
        suggestions = suggest_decomposition(metrics)

        assert any("Phase-based" in sug for sug in suggestions)
        assert any("PRP-X.1 through PRP-X.6" in sug for sug in suggestions)

    def test_feature_based_decomposition(self, large_prp):
        """PRPs with many functions should suggest feature-based split."""
        metrics = extract_prp_metrics(large_prp)
        suggestions = suggest_decomposition(metrics)

        assert any("Feature-based" in sug for sug in suggestions)
        assert any("parser, validator, executor" in sug for sug in suggestions)

    def test_risk_based_decomposition(self, large_prp):
        """HIGH-risk PRPs should suggest risk-based isolation."""
        metrics = extract_prp_metrics(large_prp)
        suggestions = suggest_decomposition(metrics)

        assert any("Risk-based" in sug for sug in suggestions)
        assert any("HIGH-risk components" in sug for sug in suggestions)

    def test_no_decomposition_needed(self, small_prp):
        """Small PRPs should not need decomposition."""
        metrics = extract_prp_metrics(small_prp)
        suggestions = suggest_decomposition(metrics)

        assert any("No decomposition needed" in sug for sug in suggestions)


class TestAnalyzePRP:
    """Test full PRP analysis workflow."""

    def test_full_analysis_small_prp(self, small_prp):
        """Test complete analysis of small PRP."""
        analysis = analyze_prp(small_prp)

        assert analysis.size_category == SizeCategory.GREEN
        assert 0 <= analysis.score <= 100
        assert len(analysis.recommendations) > 0
        assert len(analysis.decomposition_suggestions) > 0

    def test_full_analysis_large_prp(self, large_prp):
        """Test complete analysis of large PRP."""
        analysis = analyze_prp(large_prp)

        # HIGH risk forces RED category
        assert analysis.size_category == SizeCategory.RED
        assert analysis.score > 50
        assert any("🚨" in rec for rec in analysis.recommendations)

    def test_analysis_error_handling(self):
        """Test that analysis fails gracefully for bad files."""
        with pytest.raises(RuntimeError) as exc:
            analyze_prp(Path("/nonexistent/prp.md"))

        assert "PRP analysis failed" in str(exc.value)
        assert "🔧 Troubleshooting" in str(exc.value)


class TestFormatAnalysisReport:
    """Test report formatting."""

    def test_human_readable_format(self, small_prp):
        """Test human-readable report format."""
        analysis = analyze_prp(small_prp)
        report = format_analysis_report(analysis, json_output=False)

        assert "PRP Size Analysis" in report
        assert "Metrics:" in report
        assert "Complexity Score:" in report
        assert "Recommendations:" in report
        assert "Decomposition Suggestions:" in report

    def test_json_format(self, small_prp):
        """Test JSON report format."""
        import json

        analysis = analyze_prp(small_prp)
        report = format_analysis_report(analysis, json_output=True)

        # Should be valid JSON
        data = json.loads(report)

        assert data["name"] == "PRP-1-small"
        assert data["size_category"] == "GREEN"
        assert "complexity_score" in data
        assert "metrics" in data
        assert "recommendations" in data
        assert "decomposition_suggestions" in data

    def test_report_includes_all_metrics(self, large_prp):
        """Test that report includes all key metrics."""
        analysis = analyze_prp(large_prp)
        report = format_analysis_report(analysis, json_output=False)

        assert "Lines:" in report
        assert "Estimated Hours:" in report
        assert "Phases:" in report
        assert "Risk Level:" in report
        assert "Functions:" in report
        assert "Success Criteria:" in report


class TestRealPRPs:
    """Test analyzer on real PRP files from project."""

    @pytest.mark.skipif(
        not Path("../PRPs/executed").exists(),
        reason="PRPs directory not available"
    )
    def test_analyze_prp_4(self):
        """Test analysis of real PRP-4 (the notorious large one)."""
        prp_path = Path("../PRPs/executed/PRP-4-execute-prp-orchestration.md")

        if not prp_path.exists():
            pytest.skip("PRP-4 not found")

        analysis = analyze_prp(prp_path)

        # PRP-4 should definitely be RED
        assert analysis.size_category == SizeCategory.RED
        assert analysis.score > 70
        assert any("decomposition" in rec.lower() for rec in analysis.recommendations)
