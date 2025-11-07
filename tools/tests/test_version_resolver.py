"""
Comprehensive tests for VersionResolver version conflict detection.

Tests cover:
- Compatible version intersections
- Incompatible version conflicts
- Edge cases (empty specs, single package, etc.)
"""

import pytest
from ce.toml_formats.version_resolver import VersionResolver


class TestVersionIntersection:
    """Test version intersection with various specifier combinations."""

    def test_compatible_versions_simple(self):
        """Test compatible version ranges."""
        framework_deps = ["pyyaml>=6.0,<7.0"]
        target_deps = ["pyyaml>=6.2"]

        result = VersionResolver.merge_dependencies(framework_deps, target_deps)

        assert len(result) == 1
        assert "pyyaml" in result[0]
        assert ">=6.0" in result[0] or ">=6.2" in result[0]
        assert "<7.0" in result[0]

    def test_incompatible_versions_no_overlap(self):
        """Test incompatible versions with no overlap (>=6.0 vs ~=5.4)."""
        framework_deps = ["pyyaml>=6.0"]
        target_deps = ["pyyaml~=5.4"]

        with pytest.raises(ValueError, match="Dependency conflict"):
            VersionResolver.merge_dependencies(framework_deps, target_deps)

    def test_incompatible_versions_gap(self):
        """Test incompatible versions with gap (<2.0 vs >=3.0)."""
        framework_deps = ["django>=3.0"]
        target_deps = ["django<2.0"]

        with pytest.raises(ValueError, match="Dependency conflict"):
            VersionResolver.merge_dependencies(framework_deps, target_deps)

    def test_incompatible_versions_exact_mismatch(self):
        """Test incompatible exact versions."""
        framework_deps = ["package==1.0.0"]
        target_deps = ["package==2.0.0"]

        with pytest.raises(ValueError, match="Dependency conflict"):
            VersionResolver.merge_dependencies(framework_deps, target_deps)

    def test_compatible_versions_overlapping_ranges(self):
        """Test overlapping compatible ranges."""
        framework_deps = ["requests>=2.0,<3.0"]
        target_deps = ["requests>=2.5,<2.9"]

        result = VersionResolver.merge_dependencies(framework_deps, target_deps)

        assert len(result) == 1
        assert "requests" in result[0]
        # Should have intersection of both ranges

    def test_compatible_exact_within_range(self):
        """Test exact version within range."""
        framework_deps = ["click>=7.0,<9.0"]
        target_deps = ["click==8.0.0"]

        result = VersionResolver.merge_dependencies(framework_deps, target_deps)

        assert len(result) == 1
        assert "click" in result[0]


class TestDifferentPackages:
    """Test merging dependencies with different packages."""

    def test_no_conflict_different_packages(self):
        """Test no conflict when packages are different."""
        framework_deps = ["pyyaml>=6.0"]
        target_deps = ["click>=8.0"]

        result = VersionResolver.merge_dependencies(framework_deps, target_deps)

        assert len(result) == 2
        assert any("pyyaml" in dep for dep in result)
        assert any("click" in dep for dep in result)

    def test_framework_only_dependency(self):
        """Test framework-only dependency preserved."""
        framework_deps = ["anthropic>=0.40.0"]
        target_deps = []

        result = VersionResolver.merge_dependencies(framework_deps, target_deps)

        assert len(result) == 1
        assert "anthropic>=0.40.0" in result

    def test_target_only_dependency(self):
        """Test target-only dependency preserved."""
        framework_deps = []
        target_deps = ["requests>=2.31.0"]

        result = VersionResolver.merge_dependencies(framework_deps, target_deps)

        assert len(result) == 1
        assert "requests>=2.31.0" in result

    def test_multiple_packages_mixed(self):
        """Test multiple packages with mixed conflicts."""
        framework_deps = ["pyyaml>=6.0", "click>=8.0"]
        target_deps = ["pyyaml>=6.2", "requests>=2.31.0"]

        result = VersionResolver.merge_dependencies(framework_deps, target_deps)

        assert len(result) == 3
        assert any("pyyaml" in dep for dep in result)
        assert any("click" in dep for dep in result)
        assert any("requests" in dep for dep in result)


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_both_lists(self):
        """Test with both lists empty."""
        result = VersionResolver.merge_dependencies([], [])
        assert result == []

    def test_package_without_version_spec(self):
        """Test package without version specifier."""
        framework_deps = ["pyyaml"]
        target_deps = ["pyyaml>=6.0"]

        result = VersionResolver.merge_dependencies(framework_deps, target_deps)

        assert len(result) == 1
        assert "pyyaml" in result[0]

    def test_both_packages_without_version(self):
        """Test both packages without version specifiers."""
        framework_deps = ["pyyaml"]
        target_deps = ["pyyaml"]

        result = VersionResolver.merge_dependencies(framework_deps, target_deps)

        assert len(result) == 1
        assert result[0] == "pyyaml"

    def test_package_with_extras(self):
        """Test package with extras notation."""
        framework_deps = ["requests[security]>=2.0"]
        target_deps = ["requests>=2.5"]

        result = VersionResolver.merge_dependencies(framework_deps, target_deps)

        # Should handle extras correctly
        assert len(result) == 1
        assert "requests" in result[0]

    def test_poetry_tilde_operator(self):
        """Test Poetry tilde operator (~=)."""
        framework_deps = ["package~=1.4"]  # 1.4 <= version < 2.0
        target_deps = ["package>=1.5"]

        result = VersionResolver.merge_dependencies(framework_deps, target_deps)

        assert len(result) == 1
        assert "package" in result[0]

    def test_poetry_tilde_incompatible(self):
        """Test incompatible Poetry tilde operator."""
        framework_deps = ["package~=2.0"]  # 2.0 <= version < 3.0
        target_deps = ["package<2.0"]

        with pytest.raises(ValueError, match="Dependency conflict"):
            VersionResolver.merge_dependencies(framework_deps, target_deps)


class TestErrorMessages:
    """Test error message quality and troubleshooting guidance."""

    def test_error_message_contains_package_name(self):
        """Test error message includes package name."""
        framework_deps = ["pyyaml>=6.0"]
        target_deps = ["pyyaml~=5.4"]

        with pytest.raises(ValueError) as exc_info:
            VersionResolver.merge_dependencies(framework_deps, target_deps)

        error_msg = str(exc_info.value)
        assert "pyyaml" in error_msg

    def test_error_message_contains_specs(self):
        """Test error message includes both specs."""
        framework_deps = ["django>=3.0"]
        target_deps = ["django<2.0"]

        with pytest.raises(ValueError) as exc_info:
            VersionResolver.merge_dependencies(framework_deps, target_deps)

        error_msg = str(exc_info.value)
        assert ">=3.0" in error_msg
        assert "<2.0" in error_msg

    def test_error_message_contains_resolution(self):
        """Test error message includes resolution guidance."""
        framework_deps = ["package>=6.0"]
        target_deps = ["package~=5.4"]

        with pytest.raises(ValueError) as exc_info:
            VersionResolver.merge_dependencies(framework_deps, target_deps)

        error_msg = str(exc_info.value)
        assert "Resolution:" in error_msg or "🔧" in error_msg


class TestRealWorldScenarios:
    """Test real-world dependency scenarios."""

    def test_anthropic_pyyaml_compatible(self):
        """Test real framework deps (anthropic + pyyaml)."""
        framework_deps = ["anthropic>=0.40.0", "pyyaml>=6.0"]
        target_deps = ["pyyaml>=6.0.1", "click>=8.0"]

        result = VersionResolver.merge_dependencies(framework_deps, target_deps)

        assert len(result) == 3
        assert any("anthropic" in dep for dep in result)
        assert any("pyyaml" in dep for dep in result)
        assert any("click" in dep for dep in result)

    def test_django_old_project_conflict(self):
        """Test Django version conflict (old project vs new framework)."""
        framework_deps = ["django>=4.2"]
        target_deps = ["django>=2.2,<3.0"]

        with pytest.raises(ValueError, match="Dependency conflict"):
            VersionResolver.merge_dependencies(framework_deps, target_deps)

    def test_python_requires_compatible(self):
        """Test python version compatibility."""
        framework_deps = ["package>=1.0"]  # Requires python>=3.10
        target_deps = ["package>=1.2"]  # Also python>=3.10

        result = VersionResolver.merge_dependencies(framework_deps, target_deps)

        assert len(result) == 1
        assert "package" in result[0]
