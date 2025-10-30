"""Tests for drift_analyzer.py - Pattern drift calculation for L4 validation."""

import pytest
import tempfile
from pathlib import Path
from ce.drift_analyzer import (
    analyze_implementation,
    calculate_drift_score,
    get_auto_fix_suggestions
)


def test_analyze_implementation_python_file(tmp_path):
    """Test analyzing Python implementation file."""
    # Create sample implementation
    impl_file = tmp_path / "sample.py"
    impl_file.write_text("""
async def process_data(data):
    try:
        result = await validate(data)
        return result
    except ValidationError as e:
        return None

class DataProcessor:
    def handle_request(self):
        pass
""")

    result = analyze_implementation(
        prp_path="dummy.md",
        implementation_paths=[str(impl_file)]
    )

    assert "detected_patterns" in result
    assert "async/await" in result["detected_patterns"]["code_structure"]
    assert "try-except" in result["detected_patterns"]["error_handling"]
    assert "snake_case" in result["detected_patterns"]["naming_conventions"]
    assert "class-based" in result["detected_patterns"]["code_structure"]
    assert len(result["files_analyzed"]) == 1
    assert result["symbol_count"] > 0
    assert result["serena_available"] is False


def test_analyze_implementation_multiple_files(tmp_path):
    """Test analyzing multiple implementation files."""
    file1 = tmp_path / "file1.py"
    file1.write_text("def test_example(): pass")

    file2 = tmp_path / "file2.py"
    file2.write_text("class Example: pass")

    result = analyze_implementation(
        prp_path="dummy.md",
        implementation_paths=[str(file1), str(file2)]
    )

    assert len(result["files_analyzed"]) == 2
    assert "functional" in result["detected_patterns"]["code_structure"]
    assert "class-based" in result["detected_patterns"]["code_structure"]


def test_analyze_implementation_no_files():
    """Test error when no implementation files found."""
    with pytest.raises(RuntimeError, match="No implementation files found"):
        analyze_implementation(
            prp_path="dummy.md",
            implementation_paths=["/nonexistent/file.py"]
        )


def test_calculate_drift_score_no_drift():
    """Test drift calculation with perfect match."""
    expected = {
        "code_structure": ["async/await", "class-based"],
        "error_handling": ["try-except"],
        "naming_conventions": ["snake_case"]
    }

    detected = {
        "code_structure": ["async/await", "class-based"],
        "error_handling": ["try-except"],
        "naming_conventions": ["snake_case"]
    }

    result = calculate_drift_score(expected, detected)

    assert result["drift_score"] == 0.0
    assert result["threshold_action"] == "auto_accept"
    assert len(result["mismatches"]) == 0


def test_calculate_drift_score_low_drift():
    """Test drift calculation with <10% drift (auto-accept)."""
    # To get <10% drift, we need very high match rate
    # Example: 10 patterns, 1 missing = 10% drift
    expected = {
        "code_structure": ["async/await", "class-based", "functional"],
        "error_handling": ["try-except"],
        "naming_conventions": ["snake_case"] * 6  # Use list multiplication for multiple items
    }

    detected = {
        "code_structure": ["async/await", "class-based", "functional"],
        "error_handling": ["try-except"],
        "naming_conventions": ["snake_case"] * 5  # Missing 1 out of 6
    }

    result = calculate_drift_score(expected, detected)

    # Drift: naming_conventions = 1/6 = 16.7%, others = 0%
    # Average = (0 + 0 + 16.7) / 3 = 5.6%
    assert result["drift_score"] < 10.0
    assert result["threshold_action"] == "auto_accept"


def test_calculate_drift_score_medium_drift():
    """Test drift calculation with 10-30% drift (auto-fix)."""
    # To get 10-30% drift, need strategic pattern distribution
    # Example: 4 categories, 1-2 patterns each, 20-25% missing
    expected = {
        "code_structure": ["async/await", "class-based", "functional", "decorators"],
        "error_handling": ["try-except", "early-return"],
        "naming_conventions": ["snake_case", "PascalCase"],
        "import_patterns": ["relative", "absolute"]
    }

    detected = {
        "code_structure": ["async/await", "class-based", "functional"],  # 1/4 missing = 25%
        "error_handling": ["try-except", "early-return"],   # 0/2 missing = 0%
        "naming_conventions": ["snake_case", "PascalCase"],  # 0/2 missing = 0%
        "import_patterns": ["relative"]  # 1/2 missing = 50%
    }

    result = calculate_drift_score(expected, detected)

    # Average: (25 + 0 + 0 + 50) / 4 = 18.75%
    assert 10.0 <= result["drift_score"] < 30.0
    assert result["threshold_action"] == "auto_fix"
    assert len(result["mismatches"]) > 0


def test_calculate_drift_score_high_drift():
    """Test drift calculation with >30% drift (escalate)."""
    expected = {
        "code_structure": ["async/await", "class-based"],
        "error_handling": ["try-except", "early-return"],
        "naming_conventions": ["snake_case", "PascalCase"],
        "test_patterns": ["pytest"]
    }

    detected = {
        "code_structure": ["callbacks"],
        "error_handling": [],
        "naming_conventions": ["camelCase"],
        "test_patterns": []
    }

    result = calculate_drift_score(expected, detected)

    assert result["drift_score"] >= 30.0
    assert result["threshold_action"] == "escalate"
    assert len(result["mismatches"]) > 0


def test_calculate_drift_score_category_breakdown():
    """Test category score breakdown."""
    expected = {
        "code_structure": ["async/await", "class-based"],  # 2 patterns
        "naming_conventions": ["snake_case"]  # 1 pattern
    }

    detected = {
        "code_structure": ["async/await"],  # 1/2 match = 50% drift
        "naming_conventions": ["snake_case"]  # 1/1 match = 0% drift
    }

    result = calculate_drift_score(expected, detected)

    assert "category_scores" in result
    assert result["category_scores"]["code_structure"] == 50.0
    assert result["category_scores"]["naming_conventions"] == 0.0
    # Overall: (50 + 0) / 2 = 25% drift
    assert result["drift_score"] == 25.0


def test_calculate_drift_score_empty_expected():
    """Test drift calculation with no expected patterns."""
    expected = {}
    detected = {
        "code_structure": ["async/await"]
    }

    result = calculate_drift_score(expected, detected)

    assert result["drift_score"] == 0.0
    assert result["threshold_action"] == "auto_accept"


def test_get_auto_fix_suggestions_naming():
    """Test auto-fix suggestions for naming conventions."""
    mismatches = [
        {
            "category": "naming_conventions",
            "expected": "snake_case",
            "detected": ["camelCase"],
            "severity": "medium",
            "affected_symbols": []
        }
    ]

    suggestions = get_auto_fix_suggestions(mismatches)

    assert len(suggestions) > 0
    assert any("snake_case" in s for s in suggestions)


def test_get_auto_fix_suggestions_error_handling():
    """Test auto-fix suggestions for error handling."""
    mismatches = [
        {
            "category": "error_handling",
            "expected": "try-except",
            "detected": [],
            "severity": "high",
            "affected_symbols": []
        }
    ]

    suggestions = get_auto_fix_suggestions(mismatches)

    assert len(suggestions) > 0
    assert any("try-except" in s for s in suggestions)


def test_get_auto_fix_suggestions_async_patterns():
    """Test auto-fix suggestions for async patterns."""
    mismatches = [
        {
            "category": "code_structure",
            "expected": "async/await",
            "detected": ["callbacks"],
            "severity": "high",
            "affected_symbols": []
        }
    ]

    suggestions = get_auto_fix_suggestions(mismatches)

    assert len(suggestions) > 0
    assert any("async/await" in s for s in suggestions)


def test_get_auto_fix_suggestions_empty():
    """Test auto-fix suggestions with no mismatches."""
    mismatches = []

    suggestions = get_auto_fix_suggestions(mismatches)

    assert len(suggestions) > 0  # Should return at least info message


def test_analyze_typescript_file(tmp_path):
    """Test analyzing TypeScript implementation."""
    impl_file = tmp_path / "sample.ts"
    impl_file.write_text("""
async function processData(data: any): Promise<void> {
    try {
        const result = await validate(data);
        return result;
    } catch (error) {
        console.error(error);
    }
}

class DataProcessor {
    handleRequest() {
        // camelCase naming
    }
}
""")

    result = analyze_implementation(
        prp_path="dummy.md",
        implementation_paths=[str(impl_file)]
    )

    assert "async/await" in result["detected_patterns"]["code_structure"]
    assert "try-catch" in result["detected_patterns"]["error_handling"]
    assert "camelCase" in result["detected_patterns"]["naming_conventions"]


def test_drift_score_formula():
    """Test drift score formula: Σ(category_mismatch) / categories * 100."""
    # Test case verifying formula calculation
    # Formula: mismatch_ratio = missing_count / expected_count per category
    expected = {
        "code_structure": ["async/await", "class-based"],  # 2 patterns
        "error_handling": ["try-except"],  # 1 pattern
        "naming_conventions": ["snake_case", "PascalCase", "camelCase", "_private", "CONSTANT"]  # 5 patterns
    }

    detected = {
        "code_structure": ["async/await"],  # 1/2 missing = 50% drift
        "error_handling": ["try-except"],   # 0/1 missing = 0% drift
        "naming_conventions": ["snake_case", "PascalCase"]  # 3/5 missing = 60% drift
    }

    # Expected: (50% + 0% + 60%) / 3 = 36.7%
    result = calculate_drift_score(expected, detected)

    # Allow small floating point variance
    assert 35.0 <= result["drift_score"] <= 40.0
    assert result["threshold_action"] == "escalate"


def test_mismatch_severity_levels():
    """Test severity determination for different patterns."""
    # High severity: error handling
    result = calculate_drift_score(
        {"error_handling": ["try-except"]},
        {"error_handling": []}
    )
    high_severity_mismatch = [m for m in result["mismatches"] if m["severity"] == "high"]
    assert len(high_severity_mismatch) > 0

    # Medium severity: naming conventions
    result = calculate_drift_score(
        {"naming_conventions": ["snake_case"]},
        {"naming_conventions": ["camelCase"]}
    )
    medium_severity_mismatch = [m for m in result["mismatches"] if m["severity"] == "medium"]
    assert len(medium_severity_mismatch) > 0


def test_analyze_implementation_with_syntax_error(tmp_path):
    """Test fallback when Python file has syntax error."""
    impl_file = tmp_path / "bad_syntax.py"
    impl_file.write_text("""
def incomplete_function(
    # Missing closing paren and function body
""")

    # Should fall back to regex analysis without crashing
    result = analyze_implementation(
        prp_path="dummy.md",
        implementation_paths=[str(impl_file)]
    )

    assert result["files_analyzed"] == [str(impl_file)]
    # Fallback should still detect some patterns
    assert "detected_patterns" in result


def test_drift_score_edge_case_all_unexpected():
    """Test drift when detected patterns are all unexpected (not in expected)."""
    expected = {
        "code_structure": ["async/await"]
    }

    detected = {
        "code_structure": ["callbacks", "promises", "class-based"]  # None match
    }

    result = calculate_drift_score(expected, detected)

    # Missing async/await = 100% drift in this category
    assert result["category_scores"]["code_structure"] == 100.0
    assert result["threshold_action"] == "escalate"
