"""PRP blueprint parsing functions.

Extracts implementation phases from PRP IMPLEMENTATION BLUEPRINT markdown sections.
Parses structured blueprint data into executable phase dictionaries.
"""

import re
from typing import Dict, Any, List, Optional
from pathlib import Path

from .exceptions import BlueprintParseError


def parse_blueprint(prp_path: str) -> List[Dict[str, Any]]:
    """Parse PRP IMPLEMENTATION BLUEPRINT into executable phases.

    Args:
        prp_path: Path to PRP markdown file

    Returns:
        [
            {
                "phase_number": 1,
                "phase_name": "Core Logic Implementation",
                "goal": "Implement main authentication flow",
                "approach": "Class-based with async methods",
                "hours": 4.0,
                "files_to_modify": [
                    {"path": "src/auth.py", "description": "Add auth logic"}
                ],
                "files_to_create": [
                    {"path": "src/models/user.py", "description": "User model"}
                ],
                "functions": [
                    {
                        "signature": "def authenticate(username: str) -> User:",
                        "docstring": "Authenticate user with credentials",
                        "full_code": "<complete function body if provided>"
                    }
                ],
                "validation_command": "pytest tests/test_auth.py -v",
                "checkpoint_command": "git add src/ && git commit -m 'feat: auth'"
            },
            # ... more phases
        ]

    Raises:
        FileNotFoundError: If PRP file doesn't exist
        BlueprintParseError: If blueprint section missing or malformed

    Process:
        1. Read PRP file
        2. Extract ## 🔧 Implementation Blueprint section
        3. Split by ### Phase N: pattern
        4. For each phase:
           a. Extract phase number, name, hours from heading
           b. Extract **Goal**: text
           c. Extract **Approach**: text
           d. Parse **Files to Modify**: list
           e. Parse **Files to Create**: list
           f. Extract **Key Functions**: code blocks
           g. Extract **Validation Command**: command
           h. Extract **Checkpoint**: git command
        5. Validate required fields present
    """
    # Check file exists
    path = Path(prp_path)
    if not path.exists():
        raise FileNotFoundError(
            f"PRP file not found: {prp_path}\n"
            f"🔧 Troubleshooting: Verify file path is correct"
        )

    # Read file
    content = path.read_text()

    # Extract IMPLEMENTATION BLUEPRINT section
    # Note: (?=\n## [^#]) ensures we stop at ## headers (not ###)
    blueprint_match = re.search(
        r"##\s+🔧\s+Implementation\s+Blueprint\s*\n(.*?)(?=\n## [^#]|\Z)",
        content,
        re.DOTALL | re.IGNORECASE
    )

    if not blueprint_match:
        raise BlueprintParseError(
            prp_path,
            "Missing '## 🔧 Implementation Blueprint' section"
        )

    blueprint_text = blueprint_match.group(1)

    # Split by phase headings: ### Phase N: Name (X hours)
    phase_pattern = r"###\s+Phase\s+(\d+):\s+([^\(]+)\(([^)]+)\)"
    phase_splits = list(re.finditer(phase_pattern, blueprint_text))

    if not phase_splits:
        raise BlueprintParseError(
            prp_path,
            "No phases found (expected '### Phase N: Name (X hours)' format)"
        )

    phases = []

    for i, match in enumerate(phase_splits):
        phase_number = int(match.group(1))
        phase_name = match.group(2).strip()
        hours_str = match.group(3).strip()

        # Parse hours (handle "X hours", "X.Y hours", etc.)
        hours_match = re.search(r"(\d+(?:\.\d+)?)", hours_str)
        hours = float(hours_match.group(1)) if hours_match else 0.0

        # Extract phase content (from this phase to next phase or end)
        start = match.end()
        end = phase_splits[i + 1].start() if i + 1 < len(phase_splits) else len(blueprint_text)
        phase_text = blueprint_text[start:end]

        # Parse phase content
        phase_data = {
            "phase_number": phase_number,
            "phase_name": phase_name,
            "hours": hours,
            "goal": extract_field(phase_text, r"\*\*Goal\*\*:\s*(.+?)(?=\n\n|\*\*|$)", prp_path),
            "approach": extract_field(phase_text, r"\*\*Approach\*\*:\s*(.+?)(?=\n\n|\*\*|$)", prp_path),
            "files_to_modify": parse_file_list(phase_text, "Files to Modify"),
            "files_to_create": parse_file_list(phase_text, "Files to Create"),
            "functions": extract_function_signatures(phase_text),
            "validation_command": extract_field(
                phase_text,
                r"\*\*Validation\s+Command\*\*:\s*`([^`]+)`",
                prp_path,
                required=False
            ),
            "checkpoint_command": extract_field(
                phase_text,
                r"\*\*Checkpoint\*\*:\s*`([^`]+)`",
                prp_path,
                required=False
            )
        }

        phases.append(phase_data)

    return phases


def extract_field(
    text: str,
    pattern: str,
    prp_path: str,
    required: bool = True
) -> Optional[str]:
    """Extract a field from phase text using regex.

    Args:
        text: Phase text to search
        pattern: Regex pattern with one capture group
        prp_path: PRP path for error messages
        required: Whether field is required

    Returns:
        Extracted value or None if not found and not required

    Raises:
        BlueprintParseError: If required field not found
    """
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        if required:
            raise BlueprintParseError(
                prp_path,
                f"Required field not found (pattern: {pattern})"
            )
        return None

    return match.group(1).strip()


def parse_file_list(section_text: str, marker: str) -> List[Dict[str, str]]:
    """Parse **Files to Modify**: or **Files to Create**: section.

    Args:
        section_text: Phase section text
        marker: "Files to Modify" or "Files to Create"

    Returns:
        [
            {"path": "src/auth.py", "description": "Add auth logic"},
            {"path": "tests/test_auth.py", "description": "Add tests"}
        ]

    Pattern:
        **Files to Modify**:
        - `path/to/file.py` - Description
    """
    result = []

    # Find the marker section
    marker_pattern = rf"\*\*{re.escape(marker)}\*\*:\s*\n((?:- `[^`]+` - [^\n]+\n?)*)"
    match = re.search(marker_pattern, section_text, re.MULTILINE)

    if not match:
        return []

    list_content = match.group(1)

    # Parse each list item: - `path/to/file.py` - Description
    item_pattern = r"- `([^`]+)` - (.+)"
    for item_match in re.finditer(item_pattern, list_content):
        result.append({
            "path": item_match.group(1).strip(),
            "description": item_match.group(2).strip()
        })

    return result


def extract_function_signatures(phase_text: str) -> List[Dict[str, str]]:
    """Extract function signatures from **Key Functions**: code blocks.

    Args:
        phase_text: Phase section text

    Returns:
        [
            {
                "signature": "def authenticate(username: str) -> User:",
                "docstring": "Authenticate user with credentials",
                "full_code": "<complete function body if provided>"
            }
        ]
    """
    result = []

    # Find **Key Functions**: section followed by ```python code block
    func_pattern = r"\*\*Key\s+Functions\*\*:.*?```python\s*\n(.*?)```"
    matches = re.finditer(func_pattern, phase_text, re.DOTALL | re.IGNORECASE)

    for match in matches:
        code_block = match.group(1).strip()

        # Split by function definitions
        func_defs = re.split(r'\n(?=def |async def |class )', code_block)

        for func_def in func_defs:
            func_def = func_def.strip()
            if not func_def:
                continue

            # Extract signature (first line)
            lines = func_def.split('\n')
            signature = lines[0].strip()

            # Extract docstring if present
            docstring = None
            docstring_match = re.search(r'"""(.*?)"""', func_def, re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(1).strip()

            result.append({
                "signature": signature,
                "docstring": docstring or "",
                "full_code": func_def
            })

    return result


def extract_phase_metadata(phase_text: str) -> Dict[str, Any]:
    """Extract metadata from phase heading.

    Args:
        phase_text: Full phase section text

    Returns:
        {
            "phase_number": 1,
            "phase_name": "Core Logic Implementation",
            "hours": 4.0
        }

    Pattern: ### Phase 1: Core Logic Implementation (4 hours)
    """
    # This function is superseded by the inline parsing in parse_blueprint()
    # Kept for backwards compatibility and as a utility function
    pattern = r"###\s+Phase\s+(\d+):\s+([^\(]+)\(([^)]+)\)"
    match = re.search(pattern, phase_text)

    if not match:
        return {
            "phase_number": 0,
            "phase_name": "Unknown",
            "hours": 0.0
        }

    hours_match = re.search(r"(\d+(?:\.\d+)?)", match.group(3))
    hours = float(hours_match.group(1)) if hours_match else 0.0

    return {
        "phase_number": int(match.group(1)),
        "phase_name": match.group(2).strip(),
        "hours": hours
    }
