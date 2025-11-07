"""Poetry format handler."""

from typing import Dict


class PoetryHandler:
    """Handles Poetry format TOML files."""

    @staticmethod
    def detect(toml_data: Dict) -> bool:
        """Check if TOML uses Poetry format."""
        return "tool" in toml_data and "poetry" in toml_data.get("tool", {})

    @staticmethod
    def convert_to_pep621(poetry_data: Dict) -> Dict:
        """
        Convert Poetry format to PEP 621 format.

        Args:
            poetry_data: Poetry-formatted TOML data

        Returns:
            PEP 621-formatted TOML data
        """
        pep621 = {"project": {}, "dependency-groups": {}}
        poetry = poetry_data["tool"]["poetry"]

        # Convert basic metadata
        pep621["project"]["name"] = poetry.get("name", "")
        pep621["project"]["version"] = poetry.get("version", "0.1.0")
        pep621["project"]["description"] = poetry.get("description", "")

        # Convert dependencies
        if "dependencies" in poetry:
            pep621["project"]["dependencies"] = []
            for pkg, version in poetry["dependencies"].items():
                if pkg == "python":
                    pep621["project"]["requires-python"] = version
                else:
                    pep621["project"]["dependencies"].append(
                        PoetryHandler._convert_dep(pkg, version)
                    )

        # Convert dev-dependencies
        if "dev-dependencies" in poetry:
            pep621["dependency-groups"]["dev"] = [
                PoetryHandler._convert_dep(pkg, version)
                for pkg, version in poetry["dev-dependencies"].items()
            ]

        return pep621

    @staticmethod
    def _convert_dep(package: str, version) -> str:
        """
        Convert Poetry dependency to PEP 621 format.

        Args:
            package: Package name
            version: Poetry version specifier (string or dict)

        Returns:
            PEP 621 dependency string
        """
        if isinstance(version, dict):
            version_str = version.get("version", "")
        else:
            version_str = str(version)

        # Convert Poetry caret (^) to PEP 440
        # ^1.2.3 → >=1.2.3,<2.0.0
        if version_str.startswith("^"):
            base = version_str[1:]
            major = base.split(".")[0]
            version_str = f">={base},<{int(major)+1}.0.0"

        # Convert Poetry tilde (~) to PEP 440
        # ~1.2.3 → >=1.2.3,<1.3.0
        elif version_str.startswith("~"):
            base = version_str[1:]
            parts = base.split(".")
            if len(parts) >= 2:
                version_str = f">={base},<{parts[0]}.{int(parts[1])+1}.0"

        return f"{package}{version_str}" if version_str else package
