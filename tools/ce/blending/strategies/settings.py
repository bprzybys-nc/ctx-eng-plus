"""Settings blending strategy for .claude/settings.local.json files.

Implements 3-rule blending logic from PRP-33:
1. CE deny removes from target allow
2. Merge CE entries to target lists (dedupe)
3. Ensure tool appears in ONE list only
"""

import json
from typing import Dict, List, Set, Any, Optional

from .base import BlendStrategy


class SettingsBlendStrategy(BlendStrategy):
    """Blend CE and target settings.local.json files.

    Philosophy: Copy ours (CE settings) + import target permissions where not contradictory.

    Blending Rules:
    1. CE Deny Precedence: Target allow entries in CE deny → Remove from target allow
    2. List Merging: CE entries → Add to target's respective lists (deduplicate)
    3. Single Membership: CE entries → Ensure not in other lists (CE list takes precedence)
    """

    def can_handle(self, domain: str) -> bool:
        """Return True for 'settings' domain.

        Args:
            domain: Domain identifier (e.g., 'settings', 'claude-md', 'commands')

        Returns:
            True if domain == 'settings', False otherwise
        """
        return domain == "settings"

    def blend(
        self,
        framework_content: Any,
        target_content: Optional[Any],
        context: Dict[str, Any]
    ) -> Any:
        """Blend CE and target settings with 3-rule logic.

        Args:
            framework_content: CE settings (dict or JSON string)
            target_content: Target project settings (dict, JSON string, or None)
            context: Additional context (unused for settings)

        Returns:
            Blended settings as dict

        Raises:
            ValueError: If JSON parsing fails or settings invalid
            RuntimeError: If blending logic fails
        """
        # Parse CE settings
        if isinstance(framework_content, str):
            try:
                ce_settings = json.loads(framework_content)
            except json.JSONDecodeError as e:
                raise ValueError(f"CE settings JSON invalid: {e}\n🔧 Troubleshooting: Check inputs and system state")
        elif isinstance(framework_content, dict):
            ce_settings = framework_content
        else:
            raise ValueError(f"CE settings must be dict or JSON string, got {type(framework_content)}\n🔧 Troubleshooting: Check inputs and system state")

        # Parse target settings
        if target_content is None or target_content == "":
            target_settings = {"allow": [], "deny": [], "ask": []}
        elif isinstance(target_content, str):
            if not target_content.strip():
                target_settings = {"allow": [], "deny": [], "ask": []}
            else:
                try:
                    target_settings = json.loads(target_content)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Target settings JSON invalid: {e}\n🔧 Troubleshooting: Check inputs and system state")
        elif isinstance(target_content, dict):
            target_settings = target_content
        else:
            raise ValueError(f"Target settings must be dict or JSON string, got {type(target_content)}\n🔧 Troubleshooting: Check inputs and system state")

        # Initialize default structure if missing
        for list_name in ["allow", "deny", "ask"]:
            if list_name not in target_settings:
                target_settings[list_name] = []
            if list_name not in ce_settings:
                ce_settings[list_name] = []

        # Rule 1: Remove from target's allow list entries in CE's deny list
        target_settings["allow"] = [
            entry for entry in target_settings["allow"]
            if entry not in ce_settings["deny"]
        ]

        # Rule 2: Add CE entries to target's respective lists (deduplicate)
        for list_name in ["allow", "deny", "ask"]:
            merged = set(target_settings[list_name]) | set(ce_settings[list_name])
            target_settings[list_name] = sorted(merged)

        # Rule 3: Ensure CE entries only appear in one list
        for list_name in ["allow", "deny", "ask"]:
            other_lists = [l for l in ["allow", "deny", "ask"] if l != list_name]
            for entry in ce_settings[list_name]:
                for other_list in other_lists:
                    if entry in target_settings[other_list]:
                        target_settings[other_list].remove(entry)

        return target_settings

    def validate(self, blended_content: Any, context: Dict[str, Any]) -> bool:
        """Validate blended settings.

        Checks:
        1. Contains allow, deny, ask lists
        2. All lists are actually lists
        3. No duplicates across lists

        Args:
            blended_content: Blended settings (dict or JSON string)
            context: Additional context (unused for settings)

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        # Parse if string
        if isinstance(blended_content, str):
            try:
                settings = json.loads(blended_content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Blended settings JSON invalid: {e}\n🔧 Troubleshooting: Check inputs and system state")
        elif isinstance(blended_content, dict):
            settings = blended_content
        else:
            raise ValueError(f"Blended content must be dict or JSON string, got {type(blended_content)}\n🔧 Troubleshooting: Check inputs and system state")

        # Check structure
        for list_name in ["allow", "deny", "ask"]:
            if list_name not in settings:
                raise ValueError(f"Missing '{list_name}' list in blended settings\n🔧 Troubleshooting: Check inputs and system state")
            if not isinstance(settings[list_name], list):
                raise ValueError(f"'{list_name}' must be a list, got {type(settings[list_name])}\n🔧 Troubleshooting: Check inputs and system state")

        # Check no duplicates across lists
        all_entries = (
            settings["allow"] + settings["deny"] + settings["ask"]
        )
        duplicates = [entry for entry in all_entries if all_entries.count(entry) > 1]
        if duplicates:
            raise ValueError(f"Duplicate entries across lists: {set(duplicates)}\n🔧 Troubleshooting: Check inputs and system state")

        return True
