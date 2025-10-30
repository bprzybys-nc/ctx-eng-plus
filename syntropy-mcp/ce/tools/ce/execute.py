"""PRP execution orchestration with phase-by-phase implementation and self-healing.

Testing Strategy:
    This module achieves 54% line coverage (263/487 statements), focusing on comprehensive
    testing of core utility functions rather than integration orchestration.

    Coverage Breakdown:
        ✅ Core Utilities (100% coverage):
           - parse_validation_error(): 7 tests covering all error types
             (ImportError, AssertionError, SyntaxError, TypeError, NameError)
           - apply_self_healing_fix(): 4 tests with real file operations
           - check_escalation_triggers(): 7 tests for all 5 trigger conditions
           - _add_import_statement(): 2 tests for import positioning
           - escalate_to_human(): 2 tests for exception raising

        ⚠️  Integration Orchestration (0% coverage):
           - run_validation_loop() (lines 727-902): 176 lines
           - execute_prp() (lines 359-497): 139 lines

           Rationale: These functions require complex mocking (10+ patches per test)
           due to dynamic imports, state management across retry loops, and multiple
           external dependencies. Better suited for E2E testing with real validation
           scenarios rather than unit tests.

    Quality Assurance:
        - All tests follow "Real Functionality Testing" policy (no hardcoded success)
        - Self-healing tests use real file operations (tempfile, not mocks)
        - Error parsing tests use realistic error output samples
        - Escalation trigger tests verify all 5 escalation conditions
        - 33/33 tests passing with pytest

    Future Testing:
        - Integration tests for run_validation_loop() with real test projects
        - E2E tests for execute_prp() with full PRP execution scenarios
        - Performance tests for validation retry loops
"""

import re
from typing import Dict, Any, List, Optional

from .exceptions import EscalationRequired
from .blueprint_parser import parse_blueprint
from .validation_loop import (
    run_validation_loop,
    calculate_confidence_score,
    parse_validation_error,
    check_escalation_triggers,
    apply_self_healing_fix,
    escalate_to_human
)


# ============================================================================
# Phase 1: Blueprint parsing moved to blueprint_parser.py (imported above)
# ============================================================================


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

        # Step 6.5: Post-execution sync (if auto-sync enabled)
        from .context import is_auto_sync_enabled, post_execution_sync
        if is_auto_sync_enabled():
            try:
                print(f"\n{'='*80}")
                print("Running post-execution sync...")
                print(f"{'='*80}\n")
                sync_result = post_execution_sync(prp_id, skip_cleanup=False)
                print(f"✅ Post-sync complete: drift={sync_result['drift_score']:.1f}%")
                print(f"   Cleanup: {sync_result['cleanup_completed']}")
                print(f"   Memories archived: {sync_result['memories_archived']}")
                print(f"   Final checkpoint: {sync_result.get('final_checkpoint', 'N/A')}")
            except Exception as e:
                # Non-blocking - log warning but allow execution to complete
                print(f"⚠️  Post-execution sync failed: {e}")
                print(f"🔧 Troubleshooting: Run 'ce context post-sync {prp_id}' manually")

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
        except Exception as cleanup_error:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to end PRP context during cleanup: {cleanup_error}")
        raise


def execute_phase(phase: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single blueprint phase using Serena MCP for file operations.

    Args:
        phase: Parsed phase dict from parse_blueprint()

    Returns:
        {
            "success": True,
            "files_modified": ["src/auth.py"],
            "files_created": ["src/models/user.py"],
            "functions_added": ["authenticate", "validate_token"],
            "duration": "12m 34s",
            "error": "Error message if success=False"
        }

    Process:
        1. Create files listed in files_to_create using Serena MCP (or fallback)
        2. Modify files listed in files_to_modify using Serena MCP (or fallback)
        3. Implement functions from function signatures
        4. Log progress to console (shows method used: mcp vs filesystem)
        5. Return execution summary

    Implementation Strategy:
        - Use Serena MCP when available for symbol-aware code insertion
        - Graceful fallback to filesystem operations when MCP unavailable
        - Use function signatures as implementation guides
        - Follow approach description for implementation style
        - Reference goal for context

    MCP Integration (PRP-9):
        - mcp_adapter.py provides abstraction layer
        - File creation: create_file_with_mcp() tries MCP, falls back to filesystem
        - Code insertion: insert_code_with_mcp() uses symbol-aware MCP or naive append
        - Console output shows method used (mcp/mcp_symbol_aware/filesystem_append)
    """
    import time

    start_time = time.time()

    files_created = []
    files_modified = []
    functions_added = []

    try:
        # Create new files
        for file_entry in phase.get("files_to_create", []):
            filepath = file_entry["path"]
            description = file_entry["description"]
            print(f"  📝 Create: {filepath} - {description}")

            # Generate initial file content based on description and functions
            content = _generate_file_content(filepath, description, phase)

            # Create file using Serena MCP or fallback to filesystem
            from .mcp_adapter import create_file_with_mcp
            result = create_file_with_mcp(filepath, content)

            if not result["success"]:
                raise RuntimeError(
                    f"Failed to create {filepath}: {result.get('error')}\n"
                    f"🔧 Troubleshooting:\n"
                    f"  1. Verify parent directory exists and is writable\n"
                    f"  2. Check file path doesn't contain invalid characters\n"
                    f"  3. Ensure Serena MCP is available (fallback may fail)\n"
                    f"  4. Review phase files_to_create list for accuracy"
                )

            files_created.append(filepath)
            print(f"    ✓ Created via {result['method']}: {filepath}")

        # Modify existing files
        for file_entry in phase.get("files_to_modify", []):
            filepath = file_entry["path"]
            description = file_entry["description"]
            print(f"  ✏️  Modify: {filepath} - {description}")

            # Add functions to existing file
            _add_functions_to_file(filepath, phase.get("functions", []), phase)

            files_modified.append(filepath)

        # Track implemented functions
        for func_entry in phase.get("functions", []):
            signature = func_entry["signature"]
            func_name_match = re.search(r'(?:def|class)\s+(\w+)', signature)
            if func_name_match:
                func_name = func_name_match.group(1)
                print(f"  🔧 Implement: {func_name}")
                functions_added.append(func_name)

        duration = time.time() - start_time

        return {
            "success": True,
            "files_created": files_created,
            "files_modified": files_modified,
            "functions_added": functions_added,
            "duration": f"{duration:.2f}s"
        }

    except Exception as e:
        duration = time.time() - start_time
        raise RuntimeError(
            f"Phase execution failed after {duration:.2f}s\n"
            f"Error: {str(e)}\n"
            f"Files created: {files_created}\n"
            f"Files modified: {files_modified}\n"
            f"🔧 Troubleshooting:\n"
            f"  1. Check if file paths are valid\n"
            f"  2. Verify Serena MCP is available\n"
            f"  3. Review function signatures for syntax errors\n"
            f"  4. Check phase goal and approach for clarity"
        ) from e


def _generate_file_content(filepath: str, description: str, phase: Dict[str, Any]) -> str:
    """Generate initial content for a new file based on context.

    Args:
        filepath: Path to file being created
        description: File description from phase
        phase: Phase context with goal, approach, functions

    Returns:
        Generated file content with module docstring and function stubs
    """
    lines = []

    # Add module docstring
    lines.append(f'"""{description}."""')
    lines.append("")

    # Add relevant functions for this file
    for func_entry in phase.get("functions", []):
        full_code = func_entry.get("full_code", "")
        if full_code:
            lines.append(full_code)
            lines.append("")
            lines.append("")

    # If no functions, add placeholder comment
    if not phase.get("functions"):
        lines.append(f"# {phase['goal']}")
        lines.append(f"# Approach: {phase['approach']}")

    return "\n".join(lines)


def _add_functions_to_file(filepath: str, functions: List[Dict[str, str]], phase: Dict[str, Any]) -> None:
    """Add functions to an existing file using Serena MCP.

    Args:
        filepath: Path to file to modify
        functions: List of function dicts with signature, docstring, full_code
        phase: Phase context

    Raises:
        RuntimeError: If file modification fails
    """
    if not functions:
        return

    # Use Serena MCP for symbol-aware insertion or fallback to filesystem
    from .mcp_adapter import insert_code_with_mcp

    try:
        # Insert each function using symbol-aware insertion
        for func_entry in functions:
            full_code = func_entry.get("full_code", "")
            if full_code:
                result = insert_code_with_mcp(
                    filepath=filepath,
                    code=full_code,
                    mode="after_last_symbol"  # Insert after last function/class
                )

                if not result["success"]:
                    raise RuntimeError(
                        f"Failed to insert code: {result.get('error')}\n"
                        f"🔧 Troubleshooting:\n"
                        f"  1. Verify file exists and is writable: {filepath}\n"
                        f"  2. Check function code is syntactically valid\n"
                        f"  3. Ensure Serena MCP is available for symbol-aware insertion\n"
                        f"  4. Review phase functions list for correctness"
                    )

                method = result["method"]
                if method == "mcp_symbol_aware":
                    print(f"    ✓ Inserted via MCP (after {result.get('symbol')})")
                else:
                    print(f"    ✓ Inserted via {method}")

    except Exception as e:
        raise RuntimeError(
            f"Failed to add functions to {filepath}\n"
            f"Error: {str(e)}\n"
            f"🔧 Troubleshooting:\n"
            f"  1. Check file exists and is writable\n"
            f"  2. Verify function code is syntactically valid\n"
            f"  3. Review phase functions list"
        ) from e


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
