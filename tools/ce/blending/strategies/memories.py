"""Memories blending strategy with Haiku similarity + Sonnet merging."""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ce.blending.llm_client import BlendingLLM
from ce.blending.strategies.base import BlendStrategy

logger = logging.getLogger(__name__)


# Critical memories - always use framework version (no blending)
CRITICAL_MEMORIES = {
    "code-style-conventions.md",
    "suggested-commands.md",
    "task-completion-checklist.md",
    "testing-standards.md",
    "tool-usage-syntropy.md",
    "use-syntropy-tools-not-bash.md",
}


@dataclass
class BlendResult:
    """Result of blending operation."""
    success: bool
    files_processed: int
    skipped: List[str]
    merged: List[str]
    copied: List[str]
    errors: List[str]


class MemoriesBlendStrategy(BlendStrategy):
    """
    Blend Serena memories with Haiku similarity + Sonnet merge.

    Philosophy: Copy ours + import complementary target memories.

    Strategy:
    1. Haiku similarity check (fast, cheap)
    2. If >90% similar: Use framework version (skip target)
    3. If contradicting: Use framework version (or ask user)
    4. If complementary: Sonnet merge
    5. YAML header blending: framework type wins, merge tags, earlier created, later updated
    6. Critical memories: always framework (no blending)
    7. Target-only memories: preserve with type: user header
    """

    def __init__(self, llm_client: Optional[BlendingLLM] = None):
        """
        Initialize strategy with LLM client.

        Args:
            llm_client: LLM client for similarity/merge (creates default if None)
        """
        self.llm_client = llm_client or BlendingLLM()

    def can_handle(self, domain: str) -> bool:
        """Check if strategy can handle this domain."""
        return domain == "memories"

    def blend(
        self,
        framework_content: Any,
        target_content: Optional[Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Blend framework and target memories directories.

        Args:
            framework_content: Path to framework .serena/memories/
            target_content: Path to target .serena/memories/ (may be None)
            context: Dict with output_path (Path to output .serena/memories/)

        Returns:
            BlendResult with operation summary

        Raises:
            RuntimeError: If LLM call fails or critical error occurs
            ValueError: If framework_content is not a Path or doesn't exist
        """
        if not isinstance(framework_content, Path):
            raise ValueError(f"framework_content must be Path, got {type(framework_content)}\n🔧 Troubleshooting: Check inputs and system state")

        if not framework_content.exists():
            raise ValueError(f"Framework memories path does not exist: {framework_content}\n🔧 Troubleshooting: Check inputs and system state")

        framework_path = framework_content
        target_path = target_content if target_content else None
        output_path = context.get("output_path")

        if not output_path:
            raise ValueError("context must contain 'output_path'\n🔧 Troubleshooting: Check inputs and system state")

        output_path.mkdir(parents=True, exist_ok=True)

        skipped = []
        merged = []
        copied = []
        errors = []

        # Get all framework memories
        framework_files = self._list_memory_files(framework_path)
        target_files = self._list_memory_files(target_path) if target_path else []

        logger.info(f"Framework memories: {len(framework_files)}")
        logger.info(f"Target memories: {len(target_files)}")

        # Process framework memories
        for fw_file in framework_files:
            try:
                result = self._process_memory(
                    fw_file=framework_path / fw_file,
                    target_file=target_path / fw_file if target_path and fw_file in target_files else None,
                    output_file=output_path / fw_file
                )

                if result["action"] == "skip":
                    skipped.append(fw_file)
                elif result["action"] == "merge":
                    merged.append(fw_file)
                elif result["action"] == "copy":
                    copied.append(fw_file)

            except Exception as e:
                error_msg = f"{fw_file}: {str(e)}"
                logger.error(f"Failed to process {fw_file}: {e}")
                errors.append(error_msg)

        # Process target-only memories (preserve with type: user)
        if target_path:
            target_only = set(target_files) - set(framework_files)
            for target_file in target_only:
                try:
                    self._preserve_target_memory(
                        target_file=target_path / target_file,
                        output_file=output_path / target_file
                    )
                    copied.append(f"{target_file} (target-only)")

                except Exception as e:
                    error_msg = f"{target_file}: {str(e)}"
                    logger.error(f"Failed to preserve {target_file}: {e}")
                    errors.append(error_msg)

        total_processed = len(skipped) + len(merged) + len(copied)
        success = len(errors) == 0

        return BlendResult(
            success=success,
            files_processed=total_processed,
            skipped=skipped,
            merged=merged,
            copied=copied,
            errors=errors
        )

    def validate(self, blended_content: Any, context: Dict[str, Any]) -> bool:
        """
        Validate blended memories result.

        Args:
            blended_content: BlendResult from blend()
            context: Additional context

        Returns:
            True if valid (success=True, no errors), False otherwise
        """
        if not isinstance(blended_content, BlendResult):
            return False

        return blended_content.success and len(blended_content.errors) == 0

    def _process_memory(
        self,
        fw_file: Path,
        target_file: Optional[Path],
        output_file: Path
    ) -> Dict[str, str]:
        """
        Process single memory file.

        Returns:
            Dict with "action": "skip"|"merge"|"copy"
        """
        # Critical memory: always use framework
        if fw_file.name in CRITICAL_MEMORIES:
            logger.info(f"Critical memory: {fw_file.name} (using framework)")
            self._copy_file(fw_file, output_file)
            return {"action": "copy"}

        # No target file: copy framework
        if target_file is None or not target_file.exists():
            logger.info(f"No target version: {fw_file.name} (using framework)")
            self._copy_file(fw_file, output_file)
            return {"action": "copy"}

        # Both exist: check similarity with Haiku
        fw_content = fw_file.read_text()
        target_content = target_file.read_text()

        similarity_result = self.llm_client.check_similarity(
            text1=fw_content,
            text2=target_content,
            threshold=0.9
        )

        similarity_score = similarity_result["score"]
        logger.info(f"Similarity for {fw_file.name}: {similarity_score:.0%}")

        # >90% similar: skip target, use framework
        if similarity_result["similar"]:
            logger.info(f"High similarity ({similarity_score:.0%}): using framework")
            self._copy_file(fw_file, output_file)
            return {"action": "skip"}

        # Check if contradicting (using Haiku)
        is_contradicting = self._check_contradiction(fw_content, target_content)

        if is_contradicting:
            logger.warning(f"Contradicting content: {fw_file.name} (using framework)")
            self._copy_file(fw_file, output_file)
            return {"action": "skip"}

        # Complementary: merge with Sonnet
        logger.info(f"Complementary content: merging with Sonnet")
        merged_content = self._merge_with_sonnet(fw_content, target_content, fw_file.name)

        # Blend YAML headers
        fw_header, fw_body = self._parse_memory(fw_content)
        target_header, target_body = self._parse_memory(target_content)
        blended_header = self._blend_headers(fw_header, target_header)

        # Write merged file
        final_content = self._format_memory(blended_header, merged_content)
        output_file.write_text(final_content)

        return {"action": "merge"}

    def _check_contradiction(self, fw_content: str, target_content: str) -> bool:
        """
        Check if contents contradict using simple heuristic.

        Since BlendingLLM doesn't have check_contradiction method,
        we use a simple heuristic: if similarity is very low (<0.3),
        assume potential contradiction.

        Args:
            fw_content: Framework content
            target_content: Target content

        Returns:
            True if contradicting, False otherwise
        """
        # Simple heuristic: very low similarity suggests contradiction
        # In production, this could call Haiku with specific contradiction prompt
        similarity = self.llm_client.check_similarity(
            text1=fw_content,
            text2=target_content,
            threshold=0.3
        )

        # If similarity < 0.3, consider it potentially contradicting
        return similarity["score"] < 0.3

    def _merge_with_sonnet(
        self,
        fw_content: str,
        target_content: str,
        filename: str
    ) -> str:
        """
        Merge complementary content using Sonnet.

        Args:
            fw_content: Framework memory content (with YAML)
            target_content: Target memory content (with YAML)
            filename: Memory filename for context

        Returns:
            Merged content (body only, no YAML)
        """
        # Extract bodies (remove YAML)
        _, fw_body = self._parse_memory(fw_content)
        _, target_body = self._parse_memory(target_content)

        # Use BlendingLLM.blend_content() for merging
        result = self.llm_client.blend_content(
            framework_content=fw_body,
            target_content=target_body,
            rules_content=None,
            domain=f"memory:{filename}"
        )

        return result["blended"]

    def _blend_headers(
        self,
        fw_header: Dict[str, Any],
        target_header: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Blend YAML headers.

        Rules:
        - type: framework wins
        - category: framework wins
        - tags: merge both lists (deduplicate)
        - created: use earlier date
        - updated: use later date

        Args:
            fw_header: Framework YAML header
            target_header: Target YAML header

        Returns:
            Blended YAML header
        """
        blended = fw_header.copy()

        # Merge tags
        fw_tags = set(fw_header.get("tags", []))
        target_tags = set(target_header.get("tags", []))
        blended["tags"] = sorted(fw_tags | target_tags)

        # Use earlier created date
        fw_created = fw_header.get("created", "")
        target_created = target_header.get("created", "")
        if target_created and target_created < fw_created:
            blended["created"] = target_created

        # Use later updated date
        fw_updated = fw_header.get("updated", "")
        target_updated = target_header.get("updated", "")
        if target_updated and target_updated > fw_updated:
            blended["updated"] = target_updated

        return blended

    def _preserve_target_memory(
        self,
        target_file: Path,
        output_file: Path
    ) -> None:
        """
        Preserve target-only memory with type: user header.

        Args:
            target_file: Path to target memory file
            output_file: Path to output file
        """
        content = target_file.read_text()
        header, body = self._parse_memory(content)

        # Set type: user
        header["type"] = "user"
        header["source"] = "target-project"

        # Write with updated header
        final_content = self._format_memory(header, body)
        output_file.write_text(final_content)

        logger.info(f"Preserved target-only: {target_file.name} (type: user)")

    def _parse_memory(self, content: str) -> tuple[Dict[str, Any], str]:
        """
        Parse memory file into YAML header and body.

        Args:
            content: Full memory file content

        Returns:
            Tuple of (header dict, body string)

        Raises:
            ValueError: If YAML parse fails or invalid structure
        """
        if not content.startswith("---\n"):
            raise ValueError("Memory file must start with YAML frontmatter (---)\n🔧 Troubleshooting: Check inputs and system state")

        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValueError("Missing closing --- delimiter for YAML header\n🔧 Troubleshooting: Check inputs and system state")

        yaml_content = parts[1].strip()
        body = parts[2].strip()

        try:
            header = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML parse error: {e}\n🔧 Troubleshooting: Check inputs and system state")

        return header, body

    def _format_memory(self, header: Dict[str, Any], body: str) -> str:
        """
        Format memory with YAML header and body.

        Args:
            header: YAML header dict
            body: Memory body content

        Returns:
            Formatted memory file content
        """
        yaml_str = yaml.dump(header, default_flow_style=False, sort_keys=False)
        return f"---\n{yaml_str}---\n\n{body}\n"

    def _copy_file(self, src: Path, dst: Path) -> None:
        """
        Copy file from src to dst.

        Args:
            src: Source file path
            dst: Destination file path
        """
        dst.write_text(src.read_text())

    def _list_memory_files(self, path: Path) -> List[str]:
        """
        List all .md files in memory directory.

        Args:
            path: Path to memory directory

        Returns:
            List of filenames (not paths)
        """
        if not path or not path.exists():
            return []

        return [f.name for f in path.glob("*.md") if f.is_file() and not f.is_symlink()]
