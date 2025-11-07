"""Version resolution using packaging.specifiers for version intersection."""

from typing import Dict, List
from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.version import Version


class VersionResolver:
    """
    Resolves version conflicts using intersection strategy.

    Key principle: Version intersection, NOT "higher wins".
    Example: Framework >=6.0 + Target ~=5.4 → Error (no intersection)
    Example: Framework >=6.0,<7.0 + Target >=6.2 → >=6.2,<7.0
    """

    @staticmethod
    def parse_dependencies(deps: List[str]) -> Dict[str, SpecifierSet]:
        """
        Parse dependency list into {package: SpecifierSet} dict.

        Args:
            deps: List of dependency strings (e.g., ["pyyaml>=6.0", "click"])

        Returns:
            Dict mapping package name to SpecifierSet
        """
        result = {}
        for dep in deps:
            # Handle extras: requests[security]>=2.0
            if "[" in dep:
                package = dep.split("[")[0]
                version_part = dep.split("]", 1)[1] if "]" in dep else ""
            else:
                # Split at first operator
                for op in [">=", "<=", "==", "!=", "~=", ">", "<"]:
                    if op in dep:
                        package, version_part = dep.split(op, 1)
                        version_part = op + version_part
                        break
                else:
                    # No version specifier
                    package = dep.strip()
                    version_part = ""

            package = package.strip()

            try:
                spec = SpecifierSet(version_part) if version_part else SpecifierSet()
                result[package] = spec
            except InvalidSpecifier:
                # Invalid specifier → store as empty (no constraints)
                result[package] = SpecifierSet()

        return result

    @staticmethod
    def _is_intersection_satisfiable(intersection: SpecifierSet) -> bool:
        """
        Check if SpecifierSet intersection is satisfiable by any version.

        Args:
            intersection: SpecifierSet resulting from intersection

        Returns:
            True if any version can satisfy the specifier, False otherwise
        """
        # Test a comprehensive range of versions to see if any satisfy the intersection
        # This handles cases where SpecifierSet creates invalid combinations like ">=6.0,~=5.4"

        # Generate test versions: 0.1 to 10.0 with finer granularity
        test_versions = []

        # Major versions 0-10
        for major in range(11):
            test_versions.append(f"{major}.0.0")
            # Minor versions 0-9 for each major
            for minor in range(10):
                test_versions.append(f"{major}.{minor}.0")
                # Patch versions for common minors (2, 5, 8)
                if minor in [2, 5, 8]:
                    for patch in range(5):
                        test_versions.append(f"{major}.{minor}.{patch}")

        for version_str in test_versions:
            try:
                if Version(version_str) in intersection:
                    return True
            except Exception:
                continue

        return False

    @staticmethod
    def merge_dependencies(framework_deps: List[str], target_deps: List[str]) -> List[str]:
        """
        Merge two dependency lists with version intersection.

        Args:
            framework_deps: Framework dependencies
            target_deps: Target project dependencies

        Returns:
            Merged dependency list with unified versions

        Raises:
            ValueError: If version conflict detected (no intersection)
        """
        framework_map = VersionResolver.parse_dependencies(framework_deps)
        target_map = VersionResolver.parse_dependencies(target_deps)

        merged_map = {}
        all_packages = set(framework_map.keys()) | set(target_map.keys())

        for package in all_packages:
            framework_spec = framework_map.get(package)
            target_spec = target_map.get(package)

            if framework_spec and target_spec:
                # Both have version constraints → compute intersection
                try:
                    intersection = framework_spec & target_spec

                    # Check if intersection is satisfiable
                    if not VersionResolver._is_intersection_satisfiable(intersection):
                        raise ValueError(
                            f"❌ Dependency conflict: {package}\n"
                            f"   Framework requires: {framework_spec}\n"
                            f"   Target requires: {target_spec}\n"
                            f"   No compatible version exists.\n"
                            f"🔧 Resolution:\n"
                            f"   1. Update target project to use compatible version\n"
                            f"   2. Or update framework dependencies in tools/pyproject.toml"
                        )
                    merged_map[package] = intersection
                except InvalidSpecifier as e:
                    raise ValueError(
                        f"❌ Invalid version specifier for {package}: {e}\n"
                        f"🔧 Check dependency syntax in pyproject.toml"
                    )
            elif framework_spec:
                merged_map[package] = framework_spec
            else:
                merged_map[package] = target_spec

        # Convert back to list format
        return [
            f"{pkg}{spec}" if str(spec) else pkg
            for pkg, spec in sorted(merged_map.items())
        ]
