"""PEP 621 format handler."""

from typing import Dict


class PEP621Handler:
    """Handles PEP 621 format TOML files."""

    @staticmethod
    def detect(toml_data: Dict) -> bool:
        """Check if TOML uses PEP 621 format."""
        return "project" in toml_data

    @staticmethod
    def extract_dependencies(toml_data: Dict) -> Dict[str, list]:
        """
        Extract dependencies from PEP 621 TOML.

        Returns:
            Dict with 'prod' and 'dev' keys containing dependency lists
        """
        result = {"prod": [], "dev": []}

        # Production dependencies
        if "project" in toml_data and "dependencies" in toml_data["project"]:
            result["prod"] = toml_data["project"]["dependencies"]

        # Dev dependencies (PEP 735 dependency groups)
        if "dependency-groups" in toml_data:
            if "dev" in toml_data["dependency-groups"]:
                result["dev"] = toml_data["dependency-groups"]["dev"]

        return result

    @staticmethod
    def preserve_metadata(target_data: Dict, merged_data: Dict) -> Dict:
        """
        Preserve target's extra metadata in merged TOML.

        Args:
            target_data: Original target TOML
            merged_data: Merged TOML data

        Returns:
            Merged data with preserved metadata
        """
        if "project" not in target_data or "project" not in merged_data:
            return merged_data

        # Preserve these fields from target if present
        preserve_keys = ["authors", "maintainers", "urls", "license", "keywords", "classifiers"]

        for key in preserve_keys:
            if key in target_data["project"] and key not in merged_data["project"]:
                merged_data["project"][key] = target_data["project"][key]

        return merged_data
