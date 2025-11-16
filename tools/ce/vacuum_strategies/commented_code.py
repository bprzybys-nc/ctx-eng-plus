"""Strategy for finding large commented code blocks."""

import re
from pathlib import Path
from typing import List

from .base import BaseStrategy, CleanupCandidate


class CommentedCodeStrategy(BaseStrategy):
    """Find large commented-out code blocks."""

    MIN_COMMENTED_LINES = 20  # Minimum consecutive commented lines to flag

    def find_candidates(self) -> List[CleanupCandidate]:
        """Find files with large commented code blocks.

        Returns:
            List of CleanupCandidate objects with LOW confidence (30%)
        """
        candidates = []

        # Find all Python files
        for py_file in self.scan_path.glob("**/*.py"):
            if not py_file.exists() or py_file.is_dir():
                continue

            # Skip if protected
            if self.is_protected(py_file):
                continue

            # Find commented code blocks
            blocks = self._find_commented_code_blocks(py_file)

            if blocks:
                total_lines = sum(block["lines"] for block in blocks)
                block_summary = ", ".join(
                    f"Line {b['start']}: {b['lines']} lines" for b in blocks
                )

                candidate = CleanupCandidate(
                    path=py_file,
                    reason=f"Contains {len(blocks)} commented code block(s) ({total_lines} lines total). {block_summary}",
                    confidence=30,  # LOW confidence - manual review only
                    size_bytes=self.get_file_size(py_file),
                    last_modified=self.get_last_modified(py_file),
                    git_history=self.get_git_history(py_file),
                )
                candidates.append(candidate)

        return candidates

    def _find_commented_code_blocks(self, py_file: Path) -> List[dict]:
        """Find large commented code blocks in Python file.

        Args:
            py_file: Path to Python file

        Returns:
            List of dicts with block info: {"start": line_num, "lines": count}
        """
        blocks = []

        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            return blocks

        lines = content.split("\n")
        in_block = False
        block_start = 0
        block_lines = 0

        # Code patterns that indicate commented-out code (not prose)
        code_patterns = [
            r"^\s*#\s*(def|class|if|for|while|try|except|import|from)\s",
            r"^\s*#\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=",  # assignments
            r"^\s*#\s*return\s",
        ]

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Skip docstrings and module headers
            if '"""' in line or "'''" in line:
                continue

            # Check if line is a comment with code
            is_code_comment = any(re.search(pattern, line) for pattern in code_patterns)

            if is_code_comment:
                if not in_block:
                    in_block = True
                    block_start = i
                    block_lines = 1
                else:
                    block_lines += 1
            else:
                # End of block
                if in_block and block_lines >= self.MIN_COMMENTED_LINES:
                    blocks.append({"start": block_start, "lines": block_lines})

                in_block = False
                block_lines = 0

        # Check final block
        if in_block and block_lines >= self.MIN_COMMENTED_LINES:
            blocks.append({"start": block_start, "lines": block_lines})

        return blocks
