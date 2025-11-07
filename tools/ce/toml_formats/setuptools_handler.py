"""Setuptools format handler."""

from typing import Dict


class SetuptoolsHandler:
    """Handles Setuptools format TOML files."""

    @staticmethod
    def detect(toml_data: Dict) -> bool:
        """
        Check if TOML uses Setuptools format.

        Setuptools format: Has build-system but no [project] or [tool.poetry]
        """
        has_build_system = "build-system" in toml_data
        has_project = "project" in toml_data
        has_poetry = "tool" in toml_data and "poetry" in toml_data.get("tool", {})

        return has_build_system and not has_project and not has_poetry

    @staticmethod
    def convert_to_pep621(setuptools_data: Dict) -> Dict:
        """
        Convert Setuptools format to PEP 621 format.

        Args:
            setuptools_data: Setuptools-formatted TOML data

        Returns:
            PEP 621-formatted TOML data with minimal structure
        """
        pep621 = {"project": {}}

        # Preserve build-system if present
        if "build-system" in setuptools_data:
            pep621["build-system"] = setuptools_data["build-system"]

        # Setuptools typically doesn't have dependencies in pyproject.toml
        # Dependencies are usually in setup.py or setup.cfg
        # Return minimal structure
        return pep621
