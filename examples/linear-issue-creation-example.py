"""Example: Creating Linear issues with project defaults.

This example shows how to use the Linear integration utilities
to create issues with automatic project/assignee defaults.

Source: PRP-14 Linear integration
Implementation: tools/ce/linear_utils.py
"""

from pathlib import Path
import sys

# Add tools/ to path for imports
tools_path = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(tools_path))

from ce.linear_utils import (
    get_linear_defaults,
    get_default_assignee,
    get_default_project,
    create_issue_with_defaults
)


def example_1_read_defaults():
    """Example 1: Read Linear configuration defaults."""
    print("=== Example 1: Read Defaults ===")

    defaults = get_linear_defaults()
    print(f"Full config: {defaults}")

    assignee = get_default_assignee()
    print(f"Default assignee: {assignee}")

    project = get_default_project()
    print(f"Default project: {project}")
    print()


def example_2_create_issue_with_defaults():
    """Example 2: Create issue using defaults."""
    print("=== Example 2: Create Issue with Defaults ===")

    # Issue data prepared with defaults
    issue_data = create_issue_with_defaults(
        title="PRP-15: New Feature Implementation",
        description="""## Feature

Implement new feature X for Context Engineering system.

## Technical Details

- Module: tools/ce/feature.py
- Tests: tools/tests/test_feature.py
- Complexity: Medium

## Success Criteria

- Implementation complete
- Tests passing (≥80% coverage)
- Documentation updated
""",
        state="todo"
    )

    print("Issue would be created with:")
    print(f"  Team: {issue_data['team']}")
    print(f"  Project: {issue_data['project']}")
    print(f"  Assignee: {issue_data['assignee']}")
    print(f"  Labels: {issue_data['labels']}")
    print(f"  State: {issue_data['state']}")
    print()


def example_3_override_defaults():
    """Example 3: Override specific defaults when needed."""
    print("=== Example 3: Override Defaults ===")

    issue_data = create_issue_with_defaults(
        title="Special Issue for Different Person",
        description="This issue goes to someone else.",
        state="in_progress",
        override_assignee="someone.else@example.com",
        labels=["bug", "urgent"]  # Adds to default_labels
    )

    print("Issue with overrides:")
    print(f"  Assignee: {issue_data['assignee']} (overridden)")
    print(f"  Labels: {issue_data['labels']} (merged with defaults)")
    print()


def example_4_error_handling():
    """Example 4: Handle missing config gracefully."""
    print("=== Example 4: Error Handling ===")

    try:
        defaults = get_linear_defaults()
        print(f"✅ Config loaded successfully")
    except FileNotFoundError as e:
        print(f"❌ Config not found:")
        print(f"   {e}")
        print(f"   Create .ce/linear-defaults.yml to fix")
    except RuntimeError as e:
        print(f"❌ Invalid config:")
        print(f"   {e}")
    print()


if __name__ == "__main__":
    print("Linear Issue Creation Examples\n")

    example_1_read_defaults()
    example_2_create_issue_with_defaults()
    example_3_override_defaults()
    example_4_error_handling()

    print("=== Key Takeaways ===")
    print("1. Defaults are loaded from .ce/linear-defaults.yml")
    print("2. Use create_issue_with_defaults() for automatic config")
    print("3. Override specific fields when needed")
    print("4. Graceful error handling with troubleshooting guidance")
