"""Simple blending strategies for PRPs and Commands.

This module implements Python-only blending strategies that don't require LLM:
- PRPMoveStrategy: Move user PRPs with hash deduplication, add type headers
- CommandOverwriteStrategy: Overwrite user commands with framework versions

Philosophy:
- No ID deduplication for PRPs (preserve all user PRPs)
- Framework authority for commands (backup user versions)
- Hash-based deduplication (skip identical files)
- Atomic operations with proper error handling
"""

import hashlib
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class PRPMoveStrategy:
    """
    Move user PRPs to CE structure with hash deduplication.

    Behavior:
    - Moves all PRPs from source to target/.ce/PRPs/
    - Determines status (executed vs feature-requests) from content
    - Adds 'type: user' YAML header if missing
    - Skips if identical file exists (hash-based dedupe)
    - No ID-based deduplication (all PRPs preserved)

    Usage:
        >>> strategy = PRPMoveStrategy()
        >>> result = strategy.execute({
        ...     "source_dir": Path("PRPs"),
        ...     "target_dir": Path(".ce/PRPs")
        ... })
        >>> print(result["prps_moved"])
    """

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute PRP move strategy.

        Args:
            input_data: {
                "source_dir": Path to source PRPs directory,
                "target_dir": Path to target .ce/PRPs directory
            }

        Returns:
            {
                "prps_moved": int,
                "prps_skipped": int,
                "errors": List[str]
            }
        """
        source_dir = input_data.get("source_dir")
        target_dir = input_data.get("target_dir")

        if not source_dir or not target_dir:
            raise ValueError("source_dir and target_dir are required")

        source_dir = Path(source_dir)
        target_dir = Path(target_dir)

        if not source_dir.exists():
            return {
                "prps_moved": 0,
                "prps_skipped": 0,
                "errors": [f"Source directory does not exist: {source_dir}"]
            }

        # Ensure target subdirectories exist
        (target_dir / "executed").mkdir(parents=True, exist_ok=True)
        (target_dir / "feature-requests").mkdir(parents=True, exist_ok=True)

        moved = 0
        skipped = 0
        errors = []

        # Find all markdown files in source
        for prp_file in source_dir.glob("*.md"):
            try:
                # Read content
                content = prp_file.read_text(encoding="utf-8")

                # Add user header if missing
                if not self._has_yaml_header(content):
                    content = self._add_user_header(content)

                # Determine status (executed vs feature-requests)
                status = self._parse_prp_status(content)

                # Destination path
                dest = target_dir / status / prp_file.name

                # Hash-based deduplication
                if dest.exists():
                    if self._calculate_hash(content) == self._calculate_hash(dest.read_text(encoding="utf-8")):
                        skipped += 1
                        continue

                # Write to destination
                dest.write_text(content, encoding="utf-8")
                moved += 1

            except Exception as e:
                errors.append(f"Error processing {prp_file.name}: {str(e)}")

        return {
            "success": len(errors) == 0,
            "prps_moved": moved,
            "prps_skipped": skipped,
            "errors": errors,
            "files_processed": moved
        }

    def _has_yaml_header(self, content: str) -> bool:
        """
        Check if content has YAML frontmatter header.

        Args:
            content: File content

        Returns:
            True if starts with "---"
        """
        return content.strip().startswith("---")

    def _add_user_header(self, content: str) -> str:
        """
        Add user YAML header to content.

        Args:
            content: Original file content

        Returns:
            Content with added YAML header
        """
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        header = f"""---
type: user
source: target-project
created: "{now}"
updated: "{now}"
---

"""
        return header + content

    def _parse_prp_status(self, content: str) -> str:
        """
        Determine PRP status from content.

        Looks for keywords indicating completion:
        - "completed", "merged", "deployed" → executed
        - Default → feature-requests

        Args:
            content: PRP file content

        Returns:
            "executed" or "feature-requests"
        """
        content_lower = content.lower()

        # Check for completion keywords
        completed_keywords = ["status: completed", "status: merged", "status: deployed"]

        for keyword in completed_keywords:
            if keyword in content_lower:
                return "executed"

        # Default to feature-requests
        return "feature-requests"

    def _calculate_hash(self, content: str) -> str:
        """
        Calculate SHA256 hash of content.

        Args:
            content: String content

        Returns:
            Hex digest hash string
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


class CommandOverwriteStrategy:
    """
    Overwrite user commands with framework commands.

    Behavior:
    - Backs up existing commands to .claude/commands.backup/
    - Overwrites with framework commands from source
    - Skips if identical file exists (hash-based dedupe)
    - Preserves user custom commands (not in framework)

    Usage:
        >>> strategy = CommandOverwriteStrategy()
        >>> result = strategy.execute({
        ...     "source_dir": Path(".ce/commands"),
        ...     "target_dir": Path(".claude/commands"),
        ...     "backup_dir": Path(".claude/commands.backup")
        ... })
        >>> print(result["commands_overwritten"])
    """

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute command overwrite strategy.

        Args:
            input_data: {
                "source_dir": Path to framework commands,
                "target_dir": Path to target .claude/commands,
                "backup_dir": Path to backup directory
            }

        Returns:
            {
                "commands_overwritten": int,
                "commands_backed_up": int,
                "commands_skipped": int,
                "errors": List[str]
            }
        """
        source_dir = input_data.get("source_dir")
        target_dir = input_data.get("target_dir")
        backup_dir = input_data.get("backup_dir")

        if not source_dir or not target_dir or not backup_dir:
            raise ValueError("source_dir, target_dir, and backup_dir are required")

        source_dir = Path(source_dir)
        target_dir = Path(target_dir)
        backup_dir = Path(backup_dir)

        if not source_dir.exists():
            return {
                "commands_overwritten": 0,
                "commands_backed_up": 0,
                "commands_skipped": 0,
                "errors": [f"Source directory does not exist: {source_dir}"]
            }

        # Ensure directories exist
        target_dir.mkdir(parents=True, exist_ok=True)
        backup_dir.mkdir(parents=True, exist_ok=True)

        overwritten = 0
        backed_up = 0
        skipped = 0
        errors = []

        # Process all command files in source
        for cmd_file in source_dir.glob("*.md"):
            try:
                target_file = target_dir / cmd_file.name

                # Read source content
                source_content = cmd_file.read_text(encoding="utf-8")
                source_hash = self._calculate_hash(source_content)

                # Check if target exists and needs backup
                if target_file.exists():
                    target_content = target_file.read_text(encoding="utf-8")
                    target_hash = self._calculate_hash(target_content)

                    # Hash-based deduplication
                    if source_hash == target_hash:
                        skipped += 1
                        continue

                    # Backup existing command
                    backup_file = backup_dir / cmd_file.name
                    shutil.copy2(target_file, backup_file)
                    backed_up += 1

                # Overwrite with framework command
                target_file.write_text(source_content, encoding="utf-8")
                overwritten += 1

            except Exception as e:
                errors.append(f"Error processing {cmd_file.name}: {str(e)}")

        return {
            "success": len(errors) == 0,
            "commands_overwritten": overwritten,
            "commands_backed_up": backed_up,
            "commands_skipped": skipped,
            "errors": errors,
            "files_processed": overwritten
        }

    def _calculate_hash(self, content: str) -> str:
        """
        Calculate SHA256 hash of content.

        Args:
            content: String content

        Returns:
            Hex digest hash string
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
