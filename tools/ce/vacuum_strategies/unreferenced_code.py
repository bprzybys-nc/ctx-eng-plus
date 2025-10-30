"""Strategy for finding unreferenced code files using Serena."""

from pathlib import Path
from typing import List, Set
import subprocess
import json

from .base import BaseStrategy, CleanupCandidate


class UnreferencedCodeStrategy(BaseStrategy):
    """Find Python files with no external references using Serena MCP."""

    def __init__(self, project_root: Path):
        """Initialize strategy and activate Serena project.

        Args:
            project_root: Path to project root directory
        """
        super().__init__(project_root)
        self.serena_available = False

    def find_candidates(self) -> List[CleanupCandidate]:
        """Find unreferenced code files.

        Returns:
            List of CleanupCandidate objects with LOW confidence (40%)
        """
        candidates = []

        # Check if Serena is available via mcp CLI
        if not self._check_serena_available():
            return candidates

        # Get all Python files
        py_files = list(self.project_root.glob("**/*.py"))

        # Get all import statements to find which files are referenced
        referenced_modules = self._get_all_imports()

        for py_file in py_files:
            if not py_file.exists() or py_file.is_dir():
                continue

            # Skip if protected
            if self.is_protected(py_file):
                continue

            # Check if this file is imported anywhere
            relative_path = py_file.relative_to(self.project_root)
            module_name = str(relative_path).replace("/", ".").replace(".py", "")

            # Also check stem (e.g., "core" from "ce/core.py")
            stem = py_file.stem

            is_referenced = False
            for ref_module in referenced_modules:
                if module_name in ref_module or stem in ref_module:
                    is_referenced = True
                    break

            if not is_referenced:
                # Recently active files get lower confidence
                confidence = 40
                if self.is_recently_active(py_file, days=30):
                    confidence = 30

                candidate = CleanupCandidate(
                    path=py_file,
                    reason="No imports found (potentially unreferenced)",
                    confidence=confidence,  # LOW confidence
                    size_bytes=self.get_file_size(py_file),
                    last_modified=self.get_last_modified(py_file),
                    git_history=self.get_git_history(py_file),
                    references=list(referenced_modules) if referenced_modules else [],
                )
                candidates.append(candidate)

        return candidates

    def _check_serena_available(self) -> bool:
        """Check if Serena MCP is available.

        Returns:
            True if Serena is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["mcp", "list"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            self.serena_available = "serena" in result.stdout.lower()
            return self.serena_available
        except Exception:
            return False

    def _get_all_imports(self) -> Set[str]:
        """Get all import statements in the project.

        Uses grep to find all import statements efficiently.

        Returns:
            Set of imported module names
        """
        imports = set()

        try:
            # Find all "from X import" and "import X" statements
            result = subprocess.run(
                ["grep", "-rh", "--include=*.py", "-E", r"^(from|import)\s+", str(self.project_root)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    line = line.strip()
                    if not line:
                        continue

                    # Parse "from foo.bar import baz" -> "foo.bar"
                    if line.startswith("from "):
                        parts = line.split()
                        if len(parts) >= 2:
                            imports.add(parts[1])

                    # Parse "import foo.bar" -> "foo.bar"
                    elif line.startswith("import "):
                        parts = line.split()
                        if len(parts) >= 2:
                            # Handle "import foo, bar, baz"
                            for module in parts[1:]:
                                module = module.strip(",")
                                if module and not module.startswith("#"):
                                    imports.add(module)

        except Exception:
            pass

        return imports
