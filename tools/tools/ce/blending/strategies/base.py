"""Base classes for blending strategies."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path


class BlendStrategy(ABC):
    """
    Base class for all blending strategies.

    Each domain (settings, CLAUDE.md, memories, etc.) implements this interface
    to define how framework and target content should be blended.

    Philosophy: "Copy ours (framework), import theirs (target) where not contradictory"
    """

    @abstractmethod
    def can_handle(self, domain: str) -> bool:
        """
        Check if strategy can handle this domain.

        Args:
            domain: Domain name (settings, claude_md, memories, etc.)

        Returns:
            True if strategy can handle this domain

        Example:
            >>> strategy = SettingsBlendStrategy()
            >>> strategy.can_handle("settings")
            True
            >>> strategy.can_handle("claude_md")
            False
        """
        pass

    @abstractmethod
    def blend(
        self,
        framework_content: Any,
        target_content: Optional[Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Blend framework and target content.

        Args:
            framework_content: Framework version (always present, authoritative)
            target_content: Target version (may be None)
            context: Additional context:
                - file_path: Path to output file
                - dry_run: bool (if True, return result without writing)
                - interactive: bool (if True, ask user for conflicts)
                - backup_path: Path to backup (if created)
                - rules_content: str (framework rules, e.g., RULES.md)
                - llm_client: Anthropic client (for NL-based strategies)

        Returns:
            Blended content (type varies by domain)

        Raises:
            ValueError: If framework_content invalid
            Runtime Error: If blending fails

        Note: No fishy fallbacks - exceptions bubble up with actionable messages
        """
        pass

    @abstractmethod
    def validate(self, blended_content: Any, context: Dict[str, Any]) -> bool:
        """
        Validate blended content integrity.

        Args:
            blended_content: Result from blend()
            context: Additional context (same as blend())

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If validation detects critical errors

        Example validation checks:
        - Settings: Valid JSON, all CE tools in one list
        - CLAUDE.md: Valid markdown, all framework sections present
        - Memories: Valid YAML headers, >= 23 files
        """
        pass

    def get_domain_name(self) -> str:
        """
        Get human-readable domain name.

        Returns:
            Domain name (e.g., "Settings JSON", "CLAUDE.md")
        """
        return self.__class__.__name__.replace("BlendStrategy", "")
