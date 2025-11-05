"""CLAUDE.md blending strategy with Sonnet-based section merging.

Philosophy: Copy framework sections (authoritative) + import target [PROJECT]
sections where non-contradictory. RULES.md enforced as invariants.
"""

import logging
from typing import Dict, List, Any, Optional

from .base import BlendStrategy

logger = logging.getLogger(__name__)

# Section categories
FRAMEWORK_SECTIONS = {
    "Core Principles", "Framework Initialization", "Tool Naming Convention",
    "Testing Standards", "Code Quality", "Context Commands",
    "Batch PRP Generation", "PRP Sizing", "Testing Patterns",
    "Documentation Standards", "Efficient Doc Review", "Git Worktree"
}

HYBRID_SECTIONS = {
    "Quick Commands", "Allowed Tools Summary", "Command Permissions",
    "Resources", "Troubleshooting"
}


class ClaudeMdBlendStrategy(BlendStrategy):
    """
    Blend framework and target CLAUDE.md files with Sonnet-based merging.

    Uses H2 section parsing to categorize content:
    - Framework sections: Copied as-is (authoritative)
    - Hybrid sections: Sonnet merge (framework + target)
    - Target-only sections: Imported if non-contradictory

    Usage:
        >>> strategy = ClaudeMdBlendStrategy()
        >>> blended = strategy.blend(framework_md, target_md, context)
    """

    def can_handle(self, domain: str) -> bool:
        """
        Return True for 'claude_md' domain.

        Args:
            domain: Domain identifier (e.g., 'claude_md', 'settings', 'commands')

        Returns:
            True if domain == 'claude_md', False otherwise
        """
        return domain == "claude_md"

    def parse_sections(self, content: str) -> Dict[str, str]:
        """
        Split CLAUDE.md into H2 sections.

        Args:
            content: CLAUDE.md file content

        Returns:
            Dict mapping section names to section content (including H2 header)
        """
        if not content.strip():
            return {}

        sections = {}
        current_section = None
        current_lines = []

        for line in content.split('\n'):
            if line.startswith('## '):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_lines).strip()

                # Start new section
                current_section = line[3:].strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_lines).strip()

        return sections

    def categorize_section(self, section_name: str) -> str:
        """
        Categorize section as framework, hybrid, or project.

        Args:
            section_name: Section name (from H2 header)

        Returns:
            "framework", "hybrid", or "project"
        """
        if section_name in FRAMEWORK_SECTIONS:
            return "framework"
        elif section_name in HYBRID_SECTIONS:
            return "hybrid"
        else:
            return "project"

    def blend(
        self,
        framework_content: str,
        target_content: Optional[str],
        context: Dict[str, Any]
    ) -> str:
        """
        Blend framework and target CLAUDE.md files.

        Algorithm:
        1. Parse both into H2 sections
        2. Framework sections → Copy as-is (authoritative)
        3. Hybrid sections → Sonnet merge (framework + target)
        4. Target-only sections → Import if non-contradictory
        5. Reassemble in logical order

        Args:
            framework_content: Framework CLAUDE.md content
            target_content: Target project CLAUDE.md content (may be empty)
            context: Dict with llm_client and optional rules_content

        Returns:
            Blended CLAUDE.md content

        Raises:
            ValueError: If LLM client not provided or blending fails
        """
        if not context or "llm_client" not in context:
            raise ValueError(
                "LLM client required in context\n"
                "🔧 Troubleshooting:\n"
                "  1. Pass context={'llm_client': BlendingLLM()} to blend()\n"
                "  2. See PRP-34.2.6 for BlendingLLM setup"
            )

        llm = context["llm_client"]
        rules = context.get("rules_content", "")

        logger.info("Blending CLAUDE.md with Sonnet...")

        # Parse sections
        framework_sections = self.parse_sections(framework_content)
        target_sections = self.parse_sections(target_content) if target_content and target_content.strip() else {}

        blended_sections = {}

        # 1. Framework sections - copy as-is (authoritative)
        for section_name in FRAMEWORK_SECTIONS:
            if section_name in framework_sections:
                blended_sections[section_name] = framework_sections[section_name]
                logger.debug(f"  Framework section: {section_name} (copied)")

        # 2. Hybrid sections - Sonnet merge
        for section_name in HYBRID_SECTIONS:
            if section_name in framework_sections:
                target_section = target_sections.get(section_name, "")

                # Build merge prompt
                logger.debug(f"  Hybrid section: {section_name} (merging)")
                result = llm.blend_content(
                    framework_content=framework_sections[section_name],
                    target_content=target_section,
                    rules_content=rules,
                    domain=f"claude_md_{section_name.replace(' ', '_').lower()}"
                )

                blended_sections[section_name] = result["blended"]

        # 3. Target-only sections - import if project-specific
        for section_name in target_sections:
            if section_name not in framework_sections:
                category = self.categorize_section(section_name)

                if category == "project":
                    # Project-specific section - import as-is
                    blended_sections[section_name] = target_sections[section_name]
                    logger.debug(f"  Target section: {section_name} (imported)")
                else:
                    # Unknown section - validate with Sonnet
                    logger.debug(f"  Target section: {section_name} (validating)")
                    result = llm.blend_content(
                        framework_content=rules if rules else "# Framework Rules\n\nNo rules provided.",
                        target_content=target_sections[section_name],
                        rules_content=rules,
                        domain=f"validate_{section_name.replace(' ', '_').lower()}"
                    )

                    # Import if high confidence (non-contradictory)
                    if result["confidence"] > 0.7:
                        blended_sections[section_name] = target_sections[section_name]
                        logger.debug(f"    → Imported (confidence: {result['confidence']:.2f})")
                    else:
                        logger.warning(f"    → Skipped (confidence: {result['confidence']:.2f})")

        # 4. Reassemble in logical order
        return self._reassemble_sections(blended_sections, framework_sections)

    def _reassemble_sections(
        self,
        blended_sections: Dict[str, str],
        framework_sections: Dict[str, str]
    ) -> str:
        """
        Reassemble sections in logical order.

        Order:
        1. Framework sections (in original order)
        2. Hybrid sections (in original order)
        3. Project sections (alphabetical)

        Args:
            blended_sections: Dict of section_name → blended_content
            framework_sections: Original framework sections (for ordering)

        Returns:
            Reassembled CLAUDE.md content
        """
        output_lines = []

        # Get framework section order
        framework_order = list(framework_sections.keys())

        # Add sections in order
        for section_name in framework_order:
            if section_name in blended_sections:
                output_lines.append(blended_sections[section_name])
                output_lines.append("")  # Blank line between sections

        # Add remaining sections (alphabetically)
        remaining = sorted(set(blended_sections.keys()) - set(framework_order))
        for section_name in remaining:
            output_lines.append(blended_sections[section_name])
            output_lines.append("")

        # Remove trailing blank lines
        while output_lines and not output_lines[-1].strip():
            output_lines.pop()

        return '\n'.join(output_lines)

    def validate(self, blended_content: str, context: Dict[str, Any]) -> bool:
        """
        Validate blended CLAUDE.md.

        Checks:
        1. Valid markdown (has H2 sections)
        2. Contains required framework sections
        3. No duplicate H2 section names

        Args:
            blended_content: Blended CLAUDE.md content
            context: Additional context (not used currently)

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        if not blended_content.strip():
            raise ValueError("Blended content is empty")

        # Parse sections
        sections = self.parse_sections(blended_content)

        if not sections:
            raise ValueError("No H2 sections found in blended content")

        # Check required framework sections present
        required = {"Core Principles", "Framework Initialization", "Testing Standards"}
        missing = required - set(sections.keys())
        if missing:
            raise ValueError(
                f"Missing required framework sections: {missing}\n"
                f"🔧 Troubleshooting:\n"
                f"  1. Check framework CLAUDE.md has these sections\n"
                f"  2. Verify blend() preserves framework sections"
            )

        # Check no duplicate section names
        section_names = [
            line[3:].strip()
            for line in blended_content.split('\n')
            if line.startswith('## ')
        ]

        duplicates = [s for s in section_names if section_names.count(s) > 1]
        if duplicates:
            raise ValueError(
                f"Duplicate H2 sections found: {set(duplicates)}\n"
                f"🔧 Troubleshooting:\n"
                f"  1. Check target CLAUDE.md for duplicate sections\n"
                f"  2. Verify blend() deduplicates correctly"
            )

        logger.info(f"✓ Validated CLAUDE.md ({len(sections)} sections)")
        return True
