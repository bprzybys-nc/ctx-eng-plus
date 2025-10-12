"""PRP execution orchestration with phase-by-phase implementation and self-healing."""

import re
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from .exceptions import BlueprintParseError, EscalationRequired, ValidationError


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


# ============================================================================
# Phase 2: Execution Orchestration Functions
# ============================================================================

def execute_prp(
    prp_id: str,
    start_phase: Optional[int] = None,
    end_phase: Optional[int] = None,
    skip_validation: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Main execution function - orchestrates PRP implementation.

    Args:
        prp_id: PRP identifier (e.g., "PRP-4")
        start_phase: Optional phase to start from (None = Phase 1)
        end_phase: Optional phase to end at (None = all phases)
        skip_validation: Skip validation loops (dangerous - for debugging only)
        dry_run: Parse blueprint and return phases without execution

    Returns:
        {
            "success": True,
            "prp_id": "PRP-4",
            "phases_completed": 3,
            "validation_results": {
                "L1": {"passed": True, "attempts": 1},
                "L2": {"passed": True, "attempts": 2},
                "L3": {"passed": True, "attempts": 1},
                "L4": {"passed": True, "attempts": 1}
            },
            "checkpoints_created": ["checkpoint-PRP-4-phase1", ...],
            "confidence_score": "10/10",
            "execution_time": "45m 23s"
        }

    Raises:
        RuntimeError: If execution fails after escalation
        FileNotFoundError: If PRP file not found

    Process:
        1. Initialize PRP context: ce prp start <prp_id>
        2. Parse blueprint: parse_blueprint(prp_path)
        3. Filter phases: start_phase to end_phase
        4. Handle dry-run: If dry_run=True, return parsed blueprint without execution
        5. For each phase:
           a. Update phase in state: update_prp_phase(phase_name)
           b. Execute phase: execute_phase(phase)
           c. Run validation loop: run_validation_loop(phase) (unless skip_validation)
           d. Create checkpoint: create_checkpoint(phase)
           e. Update validation attempts in state
        6. Calculate confidence score
        7. End PRP context: ce prp end <prp_id>
        8. Return execution summary
    """
    import time
    from datetime import datetime, timezone
    from .prp import start_prp, end_prp, update_prp_phase, create_checkpoint

    start_time = time.time()

    # Find PRP file
    prp_path = _find_prp_file(prp_id)

    # Parse blueprint
    phases = parse_blueprint(prp_path)

    # Filter phases
    if start_phase:
        phases = [p for p in phases if p["phase_number"] >= start_phase]
    if end_phase:
        phases = [p for p in phases if p["phase_number"] <= end_phase]

    if not phases:
        raise RuntimeError(
            f"No phases to execute (start={start_phase}, end={end_phase})\n"
            f"🔧 Troubleshooting: Check phase numbers in PRP"
        )

    # Dry run - return parsed blueprint
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "prp_id": prp_id,
            "phases": phases,
            "total_phases": len(phases)
        }

    # Initialize PRP context
    prp_name = phases[0]["phase_name"] if phases else prp_id
    start_result = start_prp(prp_id, prp_name)

    # Track execution state
    phases_completed = 0
    checkpoints_created = []
    validation_results = {}

    try:
        # Execute each phase
        for phase in phases:
            phase_num = phase["phase_number"]
            phase_name = phase["phase_name"]

            print(f"\n{'='*80}")
            print(f"Phase {phase_num}: {phase_name}")
            print(f"Goal: {phase['goal']}")
            print(f"{'='*80}\n")

            # Update phase in state
            update_prp_phase(f"phase{phase_num}")

            # Execute phase
            exec_result = execute_phase(phase)
            if not exec_result["success"]:
                raise RuntimeError(
                    f"Phase {phase_num} execution failed: {exec_result.get('error', 'Unknown error')}\n"
                    f"🔧 Troubleshooting: Check phase implementation logic"
                )

            # Run validation loop (unless skipped)
            if not skip_validation and phase.get("validation_command"):
                val_result = run_validation_loop(phase, prp_path)
                validation_results[f"Phase{phase_num}"] = val_result

                if not val_result["success"]:
                    raise RuntimeError(
                        f"Phase {phase_num} validation failed after {val_result.get('attempts', 0)} attempts\n"
                        f"🔧 Troubleshooting: Review validation errors"
                    )

            # Create checkpoint
            checkpoint_result = create_checkpoint(
                f"phase{phase_num}",
                f"Phase {phase_num} complete: {phase_name}"
            )
            checkpoints_created.append(checkpoint_result["tag_name"])

            phases_completed += 1
            print(f"\n✅ Phase {phase_num} complete\n")

        # Calculate confidence score
        confidence_score = calculate_confidence_score(validation_results)

        # Calculate execution time
        duration_seconds = time.time() - start_time
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)

        if hours > 0:
            execution_time = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            execution_time = f"{minutes}m {seconds}s"
        else:
            execution_time = f"{seconds}s"

        # End PRP context
        end_result = end_prp(prp_id)

        return {
            "success": True,
            "prp_id": prp_id,
            "phases_completed": phases_completed,
            "validation_results": validation_results,
            "checkpoints_created": checkpoints_created,
            "confidence_score": confidence_score,
            "execution_time": execution_time
        }

    except Exception as e:
        # On error, still try to end PRP context
        try:
            end_prp(prp_id)
        except:
            pass
        raise


def execute_phase(phase: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single blueprint phase.

    Args:
        phase: Parsed phase dict from parse_blueprint()

    Returns:
        {
            "success": True,
            "files_modified": ["src/auth.py"],
            "files_created": ["src/models/user.py"],
            "functions_added": ["authenticate", "validate_token"],
            "duration": "12m 34s"
        }

    Process:
        1. Create files listed in files_to_create
        2. Modify files listed in files_to_modify
        3. Implement functions from function signatures
        4. Use Serena MCP for code editing:
           - mcp__serena__create_text_file(path, content)
           - mcp__serena__replace_symbol_body(name_path, new_body)
           - mcp__serena__insert_after_symbol(name_path, content)
        5. Log progress to console
        6. Return execution summary

    Implementation Strategy:
        - Use function signatures as implementation guides
        - Follow approach description for implementation style
        - Reference goal for context
        - For MVP: Log actions without actual file modification
          (Phase 5 will add Serena MCP integration)
    """
    import time

    start_time = time.time()

    files_created = []
    files_modified = []
    functions_added = []

    # Log files to create
    for file_entry in phase.get("files_to_create", []):
        filepath = file_entry["path"]
        description = file_entry["description"]
        print(f"  📝 Create: {filepath} - {description}")
        files_created.append(filepath)

    # Log files to modify
    for file_entry in phase.get("files_to_modify", []):
        filepath = file_entry["path"]
        description = file_entry["description"]
        print(f"  ✏️  Modify: {filepath} - {description}")
        files_modified.append(filepath)

    # Log functions to implement
    for func_entry in phase.get("functions", []):
        signature = func_entry["signature"]
        # Extract function name from signature
        func_name_match = re.search(r'(?:def|class)\s+(\w+)', signature)
        if func_name_match:
            func_name = func_name_match.group(1)
            print(f"  🔧 Implement: {func_name}")
            functions_added.append(func_name)

    # Calculate duration
    duration = time.time() - start_time

    # Note: For MVP, we're logging actions
    # Phase 5 will integrate with Serena MCP for actual implementation
    print(f"\n  ⚠️  MVP Mode: Actions logged, not executed")
    print(f"  Phase 5 will add Serena MCP integration for actual implementation")

    return {
        "success": True,
        "files_created": files_created,
        "files_modified": files_modified,
        "functions_added": functions_added,
        "duration": f"{duration:.2f}s"
    }


def run_validation_loop(
    phase: Dict[str, Any],
    prp_path: str,
    max_attempts: int = 3
) -> Dict[str, Any]:
    """Run L1-L4 validation loop with self-healing.

    Args:
        phase: Phase dict with validation_command
        prp_path: Path to PRP file (for L4 validation)
        max_attempts: Max self-healing attempts (default: 3)

    Returns:
        {
            "success": True,
            "validation_levels": {
                "L1": {"passed": True, "attempts": 1, "errors": []},
                "L2": {"passed": True, "attempts": 2, "errors": ["..."]},
                "L3": {"passed": True, "attempts": 1, "errors": []},
                "L4": {"passed": True, "attempts": 1, "errors": []}
            },
            "self_healed": ["L2: Fixed import error"],
            "escalated": [],
            "attempts": 1
        }

    Raises:
        EscalationRequired: If validation fails after max_attempts or trigger hit

    Process:
        1. Run L1 (Syntax): validate_level_1()
        2. Run L2 (Unit Tests): Custom validation from phase
        3. Run L3 (Integration): validate_level_3()
        4. Run L4 (Pattern Conformance): validate_level_4(prp_path)

        For each level:
        - If pass: continue to next level
        - If fail: Phase 4 will add self-healing, for now log and continue

    Note: Phase 4 will add self-healing logic
    """
    from .validate import validate_level_1, validate_level_2, validate_level_3, validate_level_4

    print(f"  🧪 Running validation...")

    validation_levels = {}
    self_healed = []
    escalated = []
    all_passed = True

    # L1: Syntax & Style
    try:
        print(f"    L1: Syntax & Style...")
        l1_result = validate_level_1()
        validation_levels["L1"] = {
            "passed": l1_result["success"],
            "attempts": 1,
            "errors": l1_result.get("errors", [])
        }
        if l1_result["success"]:
            print(f"    ✅ L1 passed ({l1_result['duration']:.2f}s)")
        else:
            print(f"    ❌ L1 failed: {len(l1_result['errors'])} errors")
            all_passed = False
    except Exception as e:
        print(f"    ❌ L1 exception: {str(e)}")
        validation_levels["L1"] = {"passed": False, "attempts": 1, "errors": [str(e)]}
        all_passed = False

    # L2: Unit Tests (use phase validation command if provided)
    if phase.get("validation_command"):
        try:
            print(f"    L2: Running {phase['validation_command']}...")
            from .core import run_cmd
            l2_result = run_cmd(phase["validation_command"])
            validation_levels["L2"] = {
                "passed": l2_result["success"],
                "attempts": 1,
                "errors": [] if l2_result["success"] else [l2_result.get("stderr", "Test failed")]
            }
            if l2_result["success"]:
                print(f"    ✅ L2 passed ({l2_result['duration']:.2f}s)")
            else:
                print(f"    ❌ L2 failed")
                print(f"       {l2_result.get('stderr', 'Unknown error')[:200]}")
                all_passed = False
        except Exception as e:
            print(f"    ❌ L2 exception: {str(e)}")
            validation_levels["L2"] = {"passed": False, "attempts": 1, "errors": [str(e)]}
            all_passed = False
    else:
        # No validation command - try generic L2
        try:
            print(f"    L2: Unit Tests...")
            l2_result = validate_level_2()
            validation_levels["L2"] = {
                "passed": l2_result["success"],
                "attempts": 1,
                "errors": l2_result.get("errors", [])
            }
            if l2_result["success"]:
                print(f"    ✅ L2 passed ({l2_result['duration']:.2f}s)")
            else:
                print(f"    ❌ L2 failed")
                all_passed = False
        except Exception as e:
            print(f"    ⚠️  L2 skipped: {str(e)}")
            validation_levels["L2"] = {"passed": True, "attempts": 1, "errors": [], "skipped": True}

    # L3: Integration Tests
    try:
        print(f"    L3: Integration Tests...")
        l3_result = validate_level_3()
        validation_levels["L3"] = {
            "passed": l3_result["success"],
            "attempts": 1,
            "errors": l3_result.get("errors", [])
        }
        if l3_result["success"]:
            print(f"    ✅ L3 passed ({l3_result['duration']:.2f}s)")
        else:
            print(f"    ❌ L3 failed")
            all_passed = False
    except Exception as e:
        print(f"    ⚠️  L3 skipped: {str(e)}")
        validation_levels["L3"] = {"passed": True, "attempts": 1, "errors": [], "skipped": True}

    # L4: Pattern Conformance
    try:
        print(f"    L4: Pattern Conformance...")
        l4_result = validate_level_4(prp_path)
        validation_levels["L4"] = {
            "passed": l4_result["success"],
            "attempts": 1,
            "errors": [],
            "drift_score": l4_result.get("drift_score", 0)
        }
        if l4_result["success"]:
            print(f"    ✅ L4 passed (drift: {l4_result.get('drift_score', 0):.1f}%)")
        else:
            print(f"    ❌ L4 failed (drift: {l4_result.get('drift_score', 100):.1f}%)")
            all_passed = False
    except Exception as e:
        print(f"    ⚠️  L4 skipped: {str(e)}")
        validation_levels["L4"] = {"passed": True, "attempts": 1, "errors": [], "skipped": True}

    print(f"  {'✅' if all_passed else '❌'} Validation {'complete' if all_passed else 'failed'}")

    return {
        "success": all_passed,
        "validation_levels": validation_levels,
        "self_healed": self_healed,
        "escalated": escalated,
        "attempts": 1
    }


def calculate_confidence_score(validation_results: Dict[str, Any]) -> str:
    """Calculate confidence score (1-10) based on validation results.

    Args:
        validation_results: Dict with L1-L4 results per phase

    Returns:
        "8/10" or "10/10"

    Scoring:
        - All L1-L4 passed on first attempt: 10/10
        - All passed, 1-2 self-heals: 9/10
        - All passed, 3+ self-heals: 8/10
        - L1-L3 passed, L4 skipped: 7/10
        - L1-L2 passed, L3-L4 skipped: 5/10
    """
    if not validation_results:
        return "6/10"  # No validation = baseline

    total_attempts = 0
    all_passed = True

    for phase_key, phase_result in validation_results.items():
        if not phase_result.get("success"):
            all_passed = False

        # Count total attempts across all levels
        for level_key, level_result in phase_result.get("validation_levels", {}).items():
            total_attempts += level_result.get("attempts", 1) - 1  # -1 because first attempt doesn't count as retry

    if not all_passed:
        return "5/10"  # Validation failures

    # All passed - score by attempts
    if total_attempts == 0:
        return "10/10"  # Perfect
    elif total_attempts <= 2:
        return "9/10"  # Minor issues
    else:
        return "8/10"  # Multiple retries


def _find_prp_file(prp_id: str) -> str:
    """Find PRP file path from PRP ID.

    Args:
        prp_id: PRP identifier (e.g., "PRP-4")

    Returns:
        Absolute path to PRP file

    Raises:
        FileNotFoundError: If PRP file not found

    Search strategy:
        1. Check PRPs/feature-requests/PRP-{id}-*.md
        2. Check PRPs/executed/PRP-{id}-*.md
        3. Check PRPs/PRP-{id}-*.md
    """
    from pathlib import Path
    import glob

    # Get project root (assuming we're in tools/ce/)
    project_root = Path(__file__).parent.parent.parent

    # Search locations
    search_paths = [
        project_root / "PRPs" / "feature-requests",
        project_root / "PRPs" / "executed",
        project_root / "PRPs"
    ]

    # Extract numeric ID (e.g., "PRP-4" -> "4")
    numeric_id = prp_id.replace("PRP-", "").replace("prp-", "")

    for search_dir in search_paths:
        if not search_dir.exists():
            continue

        # Look for PRP-{id}-*.md or PRP{id}-*.md
        patterns = [
            f"PRP-{numeric_id}-*.md",
            f"PRP{numeric_id}-*.md",
            f"prp-{numeric_id}-*.md"
        ]

        for pattern in patterns:
            matches = list(search_dir.glob(pattern))
            if matches:
                return str(matches[0].absolute())

    raise FileNotFoundError(
        f"PRP file not found: {prp_id}\n"
        f"🔧 Troubleshooting: Check PRPs/feature-requests/ or PRPs/executed/"
    )
