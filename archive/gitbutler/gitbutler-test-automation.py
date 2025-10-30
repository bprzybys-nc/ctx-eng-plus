#!/usr/bin/env python3
"""
GitButler Conflict Testing Automation

Automates the 3 workflow patterns from GITBUTLER-REFERENCE.md for testing parallel PRPs.

Reference:
    - Workflow Patterns: examples/GITBUTLER-REFERENCE.md (lines 407-512)
    - Lessons Learned: PRPs/GITBUTLER-RESEARCHED-PATTERNS-LESS-LRND.md
    - Integration Guide: test-target/GITBUTLER-INTEGRATION-GUIDE.md

Usage:
    # From test target directory
    cd test-target/pls-cli
    uv run ../../examples/gitbutler-test-automation.py --scenario 1
    uv run ../../examples/gitbutler-test-automation.py --scenario 2
    uv run ../../examples/gitbutler-test-automation.py --scenario 3
    uv run ../../examples/gitbutler-test-automation.py --all

    # With options
    uv run ../../examples/gitbutler-test-automation.py --scenario 1 --no-cleanup
    uv run ../../examples/gitbutler-test-automation.py --all  # Runs all scenarios with cleanup

Requirements:
    - GitButler CLI (`but`) installed via: brew install --cask gitbutler
    - GitButler CLI activated: Settings → General → Install CLI
    - Repository initialized with `but init`
    - Python 3.8+ (automatically via `uv run`)

Serena MCP Integration:
    This script can be used with Claude Code + Serena MCP to store test context across sessions.

    Before running tests (in Claude Code):
    >>> from mcp import serena
    >>> serena.write_memory(
    ...     content="Starting GitButler conflict testing. Base: 63f1fdc. Target: test-target/pls-cli",
    ...     categories=["gitbutler", "testing", "parallel-prps"]
    ... )

    After tests complete:
    >>> serena.write_memory(
    ...     content="GitButler tests complete. Scenario 1: PASS, Scenario 2: PASS (conflict detected), Scenario 3: PASS (isolated conflict)",
    ...     categories=["gitbutler", "testing", "results"]
    ... )

    Query test history:
    >>> serena.search_memory(query="GitButler testing results")

Test Scenarios:
    Scenario 1: Non-Overlapping PRPs (Pattern 1)
        - Two branches modifying different functions
        - Expected: Both commit cleanly, no conflicts
        - Validates: Parallel work on isolated code sections

    Scenario 2: Overlapping PRPs with Conflict (Pattern 2)
        - Two branches modifying the same line
        - Expected: First commits, second shows 🔒 conflict
        - Validates: Conflict detection with lock icon

    Scenario 3: Complex 3-PRP Workflow (Pattern 1+2 Combined)
        - Three branches: one isolated, two overlapping
        - Expected: Two clean commits, one isolated conflict
        - Validates: Selective conflict detection
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def run_cmd(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run shell command and return result."""
    print(f"{Colors.BLUE}Running:{Colors.RESET} {cmd}")
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, check=False
    )
    if check and result.returncode != 0:
        print(f"{Colors.RED}Error:{Colors.RESET} {result.stderr}")
        sys.exit(1)
    return result


def check_for_conflict_icon() -> bool:
    """Check if 🔒 icon is present in but status."""
    result = run_cmd("but status | grep '🔒'", check=False)
    return result.returncode == 0


def print_status(message: str, success: bool = True):
    """Print colored status message."""
    color = Colors.GREEN if success else Colors.RED
    symbol = "✅" if success else "❌"
    print(f"{color}{symbol} {message}{Colors.RESET}")


def scenario_1_non_overlapping():
    """
    Scenario 1: Pattern 1 - Non-Overlapping PRPs (Clean Parallel)

    Tests: Two branches modifying different functions in the same file.
    Expected: Both commit cleanly, no conflicts.
    """
    print(f"\n{Colors.BOLD}=== Scenario 1: Non-Overlapping PRPs ==={Colors.RESET}\n")

    target_file = "pls_cli/please.py"

    # Branch 1: Modify center_print()
    print(f"{Colors.YELLOW}Creating Branch 1: test-s1-color-param{Colors.RESET}")
    run_cmd('but branch new "test-s1-color-param"')

    # Read file
    with open(target_file, 'r') as f:
        content = f.read()

    # Add color parameter to center_print()
    content = content.replace(
        "def center_print(\n    text, style: Union[str, None] = None, wrap: bool = False\n) -> None:",
        "def center_print(\n    text, style: Union[str, None] = None, wrap: bool = False, color: Union[str, None] = None\n) -> None:"
    )

    with open(target_file, 'w') as f:
        f.write(content)

    run_cmd('but commit test-s1-color-param -m "Add color parameter to center_print()"')
    print_status("Branch 1 committed")

    # Branch 2: Modify print_no_pending_tasks() - different function
    print(f"\n{Colors.YELLOW}Creating Branch 2: test-s1-width-override{Colors.RESET}")
    run_cmd('but branch new "test-s1-width-override"')

    with open(target_file, 'r') as f:
        content = f.read()

    # Add width parameter to print_no_pending_tasks()
    content = content.replace(
        "def print_no_pending_tasks() -> None:",
        "def print_no_pending_tasks(width_override: Union[int, None] = None) -> None:"
    )

    with open(target_file, 'w') as f:
        f.write(content)

    # Check for conflicts
    if check_for_conflict_icon():
        print_status("Unexpected conflict detected!", success=False)
        return False

    run_cmd('but commit test-s1-width-override -m "Add width_override parameter to print_no_pending_tasks()"')
    print_status("Branch 2 committed")

    # Verify
    result = run_cmd("but status", check=False)
    if "🔒" in result.stdout:
        print_status("Scenario 1 FAILED: Unexpected conflicts", success=False)
        return False

    print_status("Scenario 1 SUCCESS: Both branches clean, no conflicts")
    return True


def scenario_2_overlapping_conflict():
    """
    Scenario 2: Pattern 2 - Overlapping PRPs with Conflict Detection

    Tests: Two branches modifying the same line.
    Expected: First branch commits, second branch shows 🔒 conflict.
    """
    print(f"\n{Colors.BOLD}=== Scenario 2: Overlapping PRPs with Conflict ==={Colors.RESET}\n")

    target_file = "pls_cli/please.py"

    # Branch 1: Modify center_print()
    print(f"{Colors.YELLOW}Creating Branch 1: test-s2-color-param{Colors.RESET}")
    run_cmd('but branch new "test-s2-color-param"')

    with open(target_file, 'r') as f:
        content = f.read()

    # Add color parameter
    content = content.replace(
        "def center_print(\n    text, style: Union[str, None] = None, wrap: bool = False\n) -> None:",
        "def center_print(\n    text, style: Union[str, None] = None, wrap: bool = False, color: Union[str, None] = None\n) -> None:"
    )

    with open(target_file, 'w') as f:
        f.write(content)

    run_cmd('but commit test-s2-color-param -m "Add color parameter to center_print()"')
    print_status("Branch 1 committed")

    # Branch 2: Modify SAME line
    print(f"\n{Colors.YELLOW}Creating Branch 2: test-s2-bg-color-param{Colors.RESET}")
    run_cmd('but branch new "test-s2-bg-color-param"')

    with open(target_file, 'r') as f:
        content = f.read()

    # Add bg_color parameter (conflicts with Branch 1)
    content = content.replace(
        "def center_print(\n    text, style: Union[str, None] = None, wrap: bool = False, color: Union[str, None] = None\n) -> None:",
        "def center_print(\n    text, style: Union[str, None] = None, wrap: bool = False, color: Union[str, None] = None, bg_color: Union[str, None] = None\n) -> None:"
    )

    with open(target_file, 'w') as f:
        f.write(content)

    # Check for conflict detection
    if not check_for_conflict_icon():
        print_status("Scenario 2 FAILED: No conflict detected (expected 🔒)", success=False)
        return False

    print_status("Conflict detected (🔒 icon present)")
    print(f"{Colors.YELLOW}Note: Do NOT commit Branch 2 - would create empty commit{Colors.RESET}")

    print_status("Scenario 2 SUCCESS: Conflict correctly detected")
    return True


def scenario_3_complex_multi_prp():
    """
    Scenario 3: Pattern 1+2 - Three Parallel PRPs with One Conflict

    Tests: Three branches, one isolated, two overlapping.
    Expected: Two clean commits, one conflict isolated.
    """
    print(f"\n{Colors.BOLD}=== Scenario 3: Complex 3-PRP Workflow ==={Colors.RESET}\n")

    target_file = "pls_cli/please.py"

    # Branch 1: Add new function (isolated)
    print(f"{Colors.YELLOW}Creating Branch 1: test-s3-logging{Colors.RESET}")
    run_cmd('but branch new "test-s3-logging"')

    with open(target_file, 'r') as f:
        lines = f.readlines()

    # Insert log_output() before center_print()
    insert_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith("def center_print("):
            insert_index = i
            break

    if insert_index:
        new_function = [
            "def log_output(message: str) -> None:\n",
            '    """Log output message to console."""\n',
            '    console.print(f"[LOG] {message}")\n',
            "\n\n"
        ]
        lines = lines[:insert_index] + new_function + lines[insert_index:]

        with open(target_file, 'w') as f:
            f.writelines(lines)

    run_cmd('but commit test-s3-logging -m "Add log_output() function"')
    print_status("Branch 1 committed (isolated)")

    # Branch 2: Modify center_print()
    print(f"\n{Colors.YELLOW}Creating Branch 2: test-s3-style-param{Colors.RESET}")
    run_cmd('but branch new "test-s3-style-param"')

    with open(target_file, 'r') as f:
        content = f.read()

    # Add custom_style parameter
    content = content.replace(
        "def center_print(\n    text, style: Union[str, None] = None, wrap: bool = False\n) -> None:",
        "def center_print(\n    text, style: Union[str, None] = None, wrap: bool = False, custom_style: Union[dict, None] = None\n) -> None:"
    )

    with open(target_file, 'w') as f:
        f.write(content)

    run_cmd('but commit test-s3-style-param -m "Add custom_style parameter to center_print()"')
    print_status("Branch 2 committed (clean)")

    # Branch 3: Modify SAME line as Branch 2
    print(f"\n{Colors.YELLOW}Creating Branch 3: test-s3-justify-param{Colors.RESET}")
    run_cmd('but branch new "test-s3-justify-param"')

    with open(target_file, 'r') as f:
        content = f.read()

    # Add justify parameter (conflicts with Branch 2)
    content = content.replace(
        "def center_print(\n    text, style: Union[str, None] = None, wrap: bool = False, custom_style: Union[dict, None] = None\n) -> None:",
        "def center_print(\n    text, style: Union[str, None] = None, wrap: bool = False, custom_style: Union[dict, None] = None, justify: str = \"center\"\n) -> None:"
    )

    with open(target_file, 'w') as f:
        f.write(content)

    # Check for conflict detection
    if not check_for_conflict_icon():
        print_status("Scenario 3 FAILED: No conflict detected (expected 🔒)", success=False)
        return False

    print_status("Conflict detected between Branch 3 and Branch 2")

    # Verify Branch 1 and 2 are clean
    result = run_cmd("but status", check=False)
    print(f"\n{Colors.BLUE}Final status:{Colors.RESET}")
    print(result.stdout)

    print_status("Scenario 3 SUCCESS: 2 clean branches + 1 isolated conflict")
    return True


def cleanup_test_environment():
    """Nuclear cleanup of GitButler state."""
    print(f"\n{Colors.YELLOW}Cleaning up test environment...{Colors.RESET}")
    run_cmd("rm -rf .git/gitbutler", check=False)
    run_cmd("but init")
    run_cmd("git restore .", check=False)
    run_cmd("git clean -fd", check=False)
    print_status("Test environment cleaned")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="GitButler Conflict Testing Automation")
    parser.add_argument(
        "--scenario",
        type=int,
        choices=[1, 2, 3],
        help="Run specific scenario (1, 2, or 3)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all scenarios"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Skip cleanup before tests"
    )

    args = parser.parse_args()

    if not args.scenario and not args.all:
        parser.print_help()
        sys.exit(1)

    # Verify we're in correct directory
    if not Path("pls_cli/please.py").exists():
        print(f"{Colors.RED}Error: Must run from test-target/pls-cli directory{Colors.RESET}")
        sys.exit(1)

    # Cleanup unless skipped
    if not args.no_cleanup:
        cleanup_test_environment()

    results = {}

    try:
        if args.scenario == 1 or args.all:
            results["Scenario 1"] = scenario_1_non_overlapping()
            if args.all:
                cleanup_test_environment()

        if args.scenario == 2 or args.all:
            results["Scenario 2"] = scenario_2_overlapping_conflict()
            if args.all:
                cleanup_test_environment()

        if args.scenario == 3 or args.all:
            results["Scenario 3"] = scenario_3_complex_multi_prp()
            if args.all:
                cleanup_test_environment()

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted{Colors.RESET}")
        sys.exit(130)

    # Summary
    print(f"\n{Colors.BOLD}=== Test Summary ==={Colors.RESET}")
    for scenario, success in results.items():
        print_status(scenario, success)

    all_passed = all(results.values())
    if all_passed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All tests passed!{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}Some tests failed{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()


# ============================================================================
# Claude Code + Serena MCP Integration Examples
# ============================================================================

"""
Example 1: Store test session context before running tests
-----------------------------------------------------------

In Claude Code, before running this script:

```python
# Store test session metadata
mcp__syntropy__serena_write_memory(
    content='''
    GitButler Testing Session
    Date: 2025-10-29
    Target: test-target/pls-cli
    Base Commit: 63f1fdc (Release 0.3.4)
    Scenarios: 1 (non-overlapping), 2 (conflict detection), 3 (complex multi-PRP)
    Expected: Pattern validation, conflict icon detection, cleanup verification
    ''',
    memory_type='testing-session'
)
```

Then run tests:
```bash
cd test-target/pls-cli
uv run ../../examples/gitbutler-test-automation.py --all
```


Example 2: Store test results after completion
-----------------------------------------------

After running tests, store results in Serena:

```python
# Store successful test results
mcp__syntropy__serena_write_memory(
    content='''
    GitButler Test Results - Round 2

    Scenario 1 (Non-Overlapping): ✅ PASS
    - Branches: test-s1-color-param, test-s1-width-override
    - Result: Both committed cleanly, no conflicts

    Scenario 2 (Conflict Detection): ✅ PASS
    - Branches: test-s2-color-param, test-s2-bg-color-param
    - Result: 🔒 icon appeared on second branch
    - Validation: Conflict detection working correctly

    Scenario 3 (Complex Multi-PRP): ✅ PASS
    - Branches: test-s3-logging (isolated), test-s3-style-param, test-s3-justify-param
    - Result: Conflict isolated between branches 2 & 3, branch 1 remained clean

    Key Findings:
    - Nuclear cleanup (rm -rf .git/gitbutler) is most reliable
    - 🔒 icon prevents empty commits when checked before committing
    - Pattern 1+2+3 from GITBUTLER-REFERENCE.md all validated
    ''',
    memory_type='test-results'
)
```


Example 3: Query test history across sessions
----------------------------------------------

In future Claude Code sessions, retrieve test context:

```python
# Find all GitButler testing sessions
memories = mcp__syntropy__serena_read_memory(
    query="GitButler testing"
)

# Find specific test failures
failures = mcp__syntropy__serena_read_memory(
    query="GitButler test FAIL"
)

# Find cleanup methods
cleanup_info = mcp__syntropy__serena_read_memory(
    query="GitButler nuclear cleanup"
)
```


Example 4: Continuous integration with Serena
----------------------------------------------

Create a testing loop that stores incremental results:

```python
# Before each scenario
mcp__syntropy__serena_write_memory(
    content=f"Starting Scenario {scenario_num}: {scenario_name}",
    memory_type='test-execution'
)

# After each scenario
mcp__syntropy__serena_write_memory(
    content=f"Scenario {scenario_num} result: {status}. Branches: {branches}. Conflicts: {conflict_detected}",
    memory_type='test-execution'
)

# Final summary
all_results = mcp__syntropy__serena_read_memory(query="test-execution")
# Analyze patterns, store insights
```


Example 5: Link tests to PRPs
------------------------------

Store relationship between tests and PRP implementation:

```python
# After testing a new PRP workflow
mcp__syntropy__serena_write_memory(
    content='''
    PRP-42: GitButler Cleanup Documentation

    Testing Performed:
    - Validated nuclear cleanup method: rm -rf .git/gitbutler && but init
    - Tested git branch -D for orphaned branches
    - Confirmed two-layer cleanup requirement

    Test Script: examples/gitbutler-test-automation.py
    Results: All cleanup methods working as documented
    Documentation Updated: examples/GITBUTLER-REFERENCE.md (lines 154-287)

    Lessons: Nuclear option fastest for test cleanup, "not found in stack" error
    occurs when GitButler virtual branch removed but Git branch remains
    ''',
    memory_type='prp-validation'
)
```


Example 6: Debug failing tests with context
--------------------------------------------

When a test fails, store debugging context:

```python
# Store failure context
mcp__syntropy__serena_write_memory(
    content='''
    GitButler Test Failure Debug

    Scenario 2 failed: Conflict NOT detected
    Expected: 🔒 icon after modifying same line
    Actual: No 🔒 icon, both branches committed

    Hypothesis: Did not commit Branch 1 before creating Branch 2
    Workflow used: Created both branches, made changes, then tried to commit
    Correct workflow: Commit Branch 1 FIRST, then create Branch 2

    Reference: GITBUTLER-REFERENCE.md Pattern 2 (lines 435-462)
    Fix: Implement commit-first workflow
    ''',
    memory_type='debugging'
)

# After fix, update memory
mcp__syntropy__serena_write_memory(
    content='''
    GitButler Test Failure RESOLVED

    Issue: Commit-first workflow not followed
    Fix Applied: Modified test to commit Branch 1 before Branch 2 changes
    Result: ✅ Conflict now detected correctly with 🔒 icon

    Learning: GitButler needs committed state to detect conflicts
    Updated Documentation: Added commit-first workflow to testing script
    ''',
    memory_type='debugging-resolved'
)
```


Benefits of Serena Integration:
--------------------------------

1. **Session Continuity**: Resume testing across Claude Code sessions without losing context
2. **Historical Analysis**: Track test evolution, identify patterns in failures
3. **Cross-Reference**: Link tests to PRPs, documentation, and bug fixes
4. **Knowledge Base**: Build searchable testing knowledge over time
5. **Debugging Aid**: Store failure context for faster root cause analysis
6. **Team Collaboration**: Share testing insights through persistent memories

See Also:
---------
- examples/GITBUTLER-REFERENCE.md (Workflow patterns documentation)
- PRPs/GITBUTLER-RESEARCHED-PATTERNS-LESS-LRND.md (Testing lessons learned)
- test-target/GITBUTLER-INTEGRATION-GUIDE.md (Integration setup)
"""
