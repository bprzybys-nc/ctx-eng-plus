"""Post-blend validation framework."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


def validate_settings_json(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate settings.local.json after blending.

    Checks:
    1. Valid JSON
    2. Has allow/deny/ask lists
    3. Each CE tool in ONE list only

    Args:
        file_path: Path to settings.local.json

    Returns:
        (is_valid, errors) tuple
    """
    errors = []

    if not file_path.exists():
        return (False, [f"Settings file not found: {file_path}"])

    try:
        with open(file_path) as f:
            settings = json.load(f)
    except json.JSONDecodeError as e:
        return (False, [f"Invalid JSON: {e}"])

    # Check required lists exist
    for list_name in ['allow', 'deny', 'ask']:
        if list_name not in settings:
            errors.append(f"Missing '{list_name}' list")

    if errors:
        return (False, errors)

    # Check single membership (each tool in ONE list only)
    allow_set = set(settings.get('allow', []))
    deny_set = set(settings.get('deny', []))
    ask_set = set(settings.get('ask', []))

    # Find tools in multiple lists
    all_tools = allow_set | deny_set | ask_set
    for tool in all_tools:
        count = 0
        if tool in allow_set:
            count += 1
        if tool in deny_set:
            count += 1
        if tool in ask_set:
            count += 1

        if count > 1:
            errors.append(f"Tool in multiple lists: {tool}")

    return (len(errors) == 0, errors)


def validate_claude_md(file_path: Path, required_sections: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate CLAUDE.md after blending.

    Checks:
    1. File exists
    2. Valid markdown
    3. All framework sections present

    Args:
        file_path: Path to CLAUDE.md
        required_sections: List of required section headers (e.g., ["## Quick Commands"])

    Returns:
        (is_valid, errors) tuple
    """
    errors = []

    if not file_path.exists():
        return (False, [f"CLAUDE.md not found: {file_path}"])

    try:
        with open(file_path) as f:
            content = f.read()
    except OSError as e:
        return (False, [f"Cannot read CLAUDE.md: {e}"])

    # Check required sections present
    for section in required_sections:
        if section not in content:
            errors.append(f"Missing section: {section}")

    # Basic markdown validation
    if len(content) < 100:
        errors.append("CLAUDE.md too short (< 100 chars)")

    return (len(errors) == 0, errors)


def validate_memories(memories_dir: Path, min_count: int = 23) -> Tuple[bool, List[str]]:
    """
    Validate Serena memories after blending.

    Checks:
    1. Directory exists
    2. At least min_count memory files
    3. All have valid YAML headers

    Args:
        memories_dir: Path to .serena/memories/
        min_count: Minimum expected memory files (default: 23 framework memories)

    Returns:
        (is_valid, errors) tuple
    """
    errors = []

    if not memories_dir.exists():
        return (False, [f"Memories directory not found: {memories_dir}"])

    # Count memory files
    memory_files = list(memories_dir.glob('*.md'))

    if len(memory_files) < min_count:
        errors.append(f"Too few memories: {len(memory_files)} (expected >= {min_count})")

    # Check YAML headers (sample first 5)
    import yaml

    for memory_file in memory_files[:5]:
        try:
            with open(memory_file) as f:
                content = f.read()

            if not content.startswith('---'):
                errors.append(f"Missing YAML header: {memory_file.name}")
                continue

            # Parse YAML frontmatter
            yaml_end = content.find('---', 3)
            if yaml_end == -1:
                errors.append(f"Invalid YAML header: {memory_file.name}")
                continue

            yaml_content = content[3:yaml_end]
            yaml_data = yaml.safe_load(yaml_content)

            if not yaml_data or 'type' not in yaml_data:
                errors.append(f"YAML missing 'type': {memory_file.name}")

        except Exception as e:
            errors.append(f"Cannot parse {memory_file.name}: {e}")

    return (len(errors) == 0, errors)


def validate_all_domains(target_dir: Path, config: Dict[str, Any]) -> Dict[str, Tuple[bool, List[str]]]:
    """
    Run validation on all domains.

    Args:
        target_dir: Target project directory
        config: Blend configuration

    Returns:
        Dict of {domain: (is_valid, errors)}
    """
    results = {}

    # Validate settings
    settings_path = target_dir / '.claude' / 'settings.local.json'
    results['settings'] = validate_settings_json(settings_path)

    # Validate CLAUDE.md
    claude_md_path = target_dir / 'CLAUDE.md'
    required_sections = [
        "## Core Principles",
        "## Quick Commands",
        "## Project Structure"
    ]
    results['claude_md'] = validate_claude_md(claude_md_path, required_sections)

    # Validate memories
    memories_dir = target_dir / '.serena' / 'memories'
    results['memories'] = validate_memories(memories_dir, min_count=23)

    return results
