#!/usr/bin/env python3
"""
TOML Merger - Intelligent pyproject.toml merging with version unification.

Supports PEP 621, Poetry, and Setuptools formats.
Uses version intersection strategy (not "higher wins").
"""

from pathlib import Path
from typing import Dict, Optional

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python 3.10

import tomli_w

from .toml_formats.pep621_handler import PEP621Handler
from .toml_formats.poetry_handler import PoetryHandler
from .toml_formats.setuptools_handler import SetuptoolsHandler
from .toml_formats.version_resolver import VersionResolver


class TomlMerger:
    """
    Orchestrates TOML merging using format-specific handlers.

    Strategy pattern delegation:
    - PEP621Handler: PEP 621 format
    - PoetryHandler: Poetry format
    - SetuptoolsHandler: Setuptools format
    - VersionResolver: Version intersection logic
    """

    def __init__(self, framework_toml: Path, target_toml: Optional[Path] = None):
        self.framework_toml = Path(framework_toml)
        self.target_toml = Path(target_toml) if target_toml else None

        # Load framework TOML
        with open(self.framework_toml, "rb") as f:
            self.framework_data = tomllib.load(f)

        # Load target TOML if exists
        self.target_data = None
        if self.target_toml and self.target_toml.exists():
            with open(self.target_toml, "rb") as f:
                self.target_data = tomllib.load(f)

    def merge(self) -> Dict:
        """
        Merge framework and target TOMLs with version intersection.

        Returns:
            Merged TOML data (dict)

        Raises:
            ValueError: If version conflict detected
        """
        # No target TOML → use framework directly
        if not self.target_data:
            return self.framework_data.copy()

        # Detect target format and convert to PEP 621
        if PoetryHandler.detect(self.target_data):
            target_pep621 = PoetryHandler.convert_to_pep621(self.target_data)
        elif SetuptoolsHandler.detect(self.target_data):
            target_pep621 = SetuptoolsHandler.convert_to_pep621(self.target_data)
        elif PEP621Handler.detect(self.target_data):
            target_pep621 = self.target_data.copy()
        else:
            # Unknown format → use framework
            return self.framework_data.copy()

        # Start with framework data
        merged = self.framework_data.copy()

        # Merge production dependencies
        if "project" in target_pep621 and "dependencies" in target_pep621["project"]:
            framework_deps = self.framework_data.get("project", {}).get("dependencies", [])
            target_deps = target_pep621["project"]["dependencies"]

            merged["project"]["dependencies"] = VersionResolver.merge_dependencies(
                framework_deps, target_deps
            )

        # Merge dev dependencies (dependency-groups)
        if "dependency-groups" in target_pep621:
            if "dependency-groups" not in merged:
                merged["dependency-groups"] = {}

            for group, deps in target_pep621["dependency-groups"].items():
                framework_deps = merged["dependency-groups"].get(group, [])
                merged["dependency-groups"][group] = VersionResolver.merge_dependencies(
                    framework_deps, deps
                )

        # Preserve target's metadata
        merged = PEP621Handler.preserve_metadata(target_pep621, merged)

        return merged

    def write(self, output_path: Path):
        """
        Write merged TOML to file.

        Args:
            output_path: Path to write merged TOML
        """
        merged_data = self.merge()

        with open(output_path, "wb") as f:
            tomli_w.dump(merged_data, f)


def merge_toml_files(framework_toml: Path, target_toml: Optional[Path], output_path: Path):
    """
    Convenience function to merge TOML files.

    Args:
        framework_toml: Path to framework pyproject.toml
        target_toml: Path to target pyproject.toml (optional)
        output_path: Path to write merged TOML

    Raises:
        ValueError: If version conflict detected
    """
    merger = TomlMerger(framework_toml, target_toml)
    merger.write(output_path)
