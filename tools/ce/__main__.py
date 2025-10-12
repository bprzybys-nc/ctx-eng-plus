"""Context Engineering CLI - Main entry point."""

import argparse
import json
import sys
from typing import Any, Dict

from . import __version__
from .core import git_status, git_checkpoint, git_diff, run_py
from .validate import validate_level_1, validate_level_2, validate_level_3, validate_level_4, validate_all
from .context import sync, health, prune
from .generate import generate_prp


def format_output(data: Dict[str, Any], as_json: bool = False) -> str:
    """Format output for display.

    Args:
        data: Data to format
        as_json: If True, return JSON string

    Returns:
        Formatted string
    """
    if as_json:
        return json.dumps(data, indent=2)

    # Human-readable format
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for k, v in value.items():
                lines.append(f"  {k}: {v}")
        else:
            lines.append(f"{key}: {value}")

    return "\n".join(lines)


def cmd_validate(args) -> int:
    """Execute validate command."""
    try:
        if args.level == "1":
            result = validate_level_1()
        elif args.level == "2":
            result = validate_level_2()
        elif args.level == "3":
            result = validate_level_3()
        elif args.level == "4":
            # L4 requires --prp argument
            if not args.prp:
                print("❌ Level 4 validation requires --prp argument", file=sys.stderr)
                return 1

            # Parse --files if provided
            files = None
            if args.files:
                files = [f.strip() for f in args.files.split(",")]

            result = validate_level_4(prp_path=args.prp, implementation_paths=files)
        else:  # "all"
            result = validate_all()

        print(format_output(result, args.json))
        return 0 if result["success"] else 1

    except Exception as e:
        print(f"❌ Validation failed: {str(e)}", file=sys.stderr)
        return 1


def cmd_git(args) -> int:
    """Execute git command."""
    try:
        if args.action == "status":
            result = git_status()
            print(format_output(result, args.json))
            return 0

        elif args.action == "checkpoint":
            message = args.message or "Context Engineering checkpoint"
            checkpoint_id = git_checkpoint(message)
            result = {"checkpoint_id": checkpoint_id, "message": message}
            print(format_output(result, args.json))
            return 0

        elif args.action == "diff":
            since = args.since or "HEAD~5"
            files = git_diff(since=since, name_only=True)
            result = {"changed_files": files, "count": len(files), "since": since}
            print(format_output(result, args.json))
            return 0

        else:
            print(f"Unknown git action: {args.action}", file=sys.stderr)
            return 1

    except Exception as e:
        print(f"❌ Git operation failed: {str(e)}", file=sys.stderr)
        return 1


def cmd_context(args) -> int:
    """Execute context command."""
    try:
        if args.action == "sync":
            result = sync()
            print(format_output(result, args.json))
            return 0

        elif args.action == "health":
            result = health()
            print(format_output(result, args.json))

            # Print summary
            if not args.json:
                print()
                if result["healthy"]:
                    print("✅ Context is healthy")
                else:
                    print("⚠️  Context needs attention:")
                    for rec in result["recommendations"]:
                        print(f"  • {rec}")

            return 0 if result["healthy"] else 1

        elif args.action == "prune":
            age = args.age or 7
            dry_run = args.dry_run or False
            result = prune(age_days=age, dry_run=dry_run)
            print(format_output(result, args.json))
            return 0

        else:
            print(f"Unknown context action: {args.action}", file=sys.stderr)
            return 1

    except Exception as e:
        print(f"❌ Context operation failed: {str(e)}", file=sys.stderr)
        return 1


def cmd_run_py(args) -> int:
    """Execute run_py command."""
    try:
        # Determine input mode
        auto_input = getattr(args, 'input', None)

        result = run_py(
            code=args.code if hasattr(args, 'code') else None,
            file=args.file if hasattr(args, 'file') else None,
            auto=auto_input,
            args=args.script_args or ""
        )

        # Always show output
        if result["stdout"]:
            print(result["stdout"], end="")

        if result["stderr"]:
            print(result["stderr"], end="", file=sys.stderr)

        # Show summary if JSON requested
        if args.json:
            summary = {
                "exit_code": result["exit_code"],
                "success": result["success"],
                "duration": result["duration"]
            }
            print(json.dumps(summary, indent=2))

        return result["exit_code"]

    except Exception as e:
        print(f"❌ Python execution failed: {str(e)}", file=sys.stderr)
        return 1


def cmd_prp_validate(args) -> int:
    """Execute prp validate command."""
    from ce.prp import validate_prp_yaml, format_validation_result

    try:
        result = validate_prp_yaml(args.file)

        if args.json:
            print(format_output(result, True))
        else:
            print(format_validation_result(result))

        return 0 if result["success"] else 1
    except FileNotFoundError as e:
        print(f"❌ {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ PRP validation failed: {str(e)}", file=sys.stderr)
        return 1


def cmd_prp_generate(args) -> int:
    """Execute prp generate command."""
    try:
        output_dir = args.output or "PRPs/feature-requests"
        prp_path = generate_prp(args.initial_md, output_dir)

        result = {
            "success": True,
            "prp_path": prp_path,
            "message": f"PRP generated: {prp_path}"
        }

        if args.json:
            print(format_output(result, True))
        else:
            print(f"✅ PRP generated: {prp_path}")

        return 0

    except FileNotFoundError as e:
        print(f"❌ {str(e)}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"❌ Invalid INITIAL.md: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ PRP generation failed: {str(e)}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Context Engineering CLI Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ce validate --level all
  ce git status
  ce git checkpoint "Phase 1 complete"
  ce context sync
  ce context health --json
  ce run_py "print('hello')"
  ce run_py "x = [1,2,3]; print(sum(x))"
  ce run_py tmp/script.py
  ce run_py --code "import sys; print(sys.version)"
  ce run_py --file tmp/script.py --args "--input data.csv"
        """
    )

    parser.add_argument("--version", action="version", version=f"ce {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # === VALIDATE COMMAND ===
    validate_parser = subparsers.add_parser(
        "validate",
        help="Run validation gates"
    )
    validate_parser.add_argument(
        "--level",
        choices=["1", "2", "3", "4", "all"],
        default="all",
        help="Validation level (1=lint/type, 2=unit tests, 3=integration, 4=pattern conformance, all=all levels)"
    )
    validate_parser.add_argument(
        "--prp",
        help="Path to PRP file (required for level 4)"
    )
    validate_parser.add_argument(
        "--files",
        help="Comma-separated list of implementation files (for level 4, optional - auto-detected if not provided)"
    )
    validate_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    # === GIT COMMAND ===
    git_parser = subparsers.add_parser(
        "git",
        help="Git operations"
    )
    git_parser.add_argument(
        "action",
        choices=["status", "checkpoint", "diff"],
        help="Git action to perform"
    )
    git_parser.add_argument(
        "--message",
        help="Checkpoint message (for checkpoint action)"
    )
    git_parser.add_argument(
        "--since",
        help="Git ref for diff (default: HEAD~5)"
    )
    git_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    # === CONTEXT COMMAND ===
    context_parser = subparsers.add_parser(
        "context",
        help="Context management"
    )
    context_parser.add_argument(
        "action",
        choices=["sync", "health", "prune"],
        help="Context action to perform"
    )
    context_parser.add_argument(
        "--age",
        type=int,
        help="Age in days for pruning (default: 7)"
    )
    context_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode (for prune)"
    )
    context_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    # === RUN_PY COMMAND ===
    runpy_parser = subparsers.add_parser(
        "run_py",
        help="Execute Python code (auto-detect or explicit mode)"
    )
    runpy_group = runpy_parser.add_mutually_exclusive_group(required=False)
    runpy_group.add_argument(
        "input",
        nargs="?",
        help="Auto-detect: code (≤3 LOC) or file path (tmp/*.py)"
    )
    runpy_parser.add_argument(
        "--code",
        help="Explicit: Ad-hoc Python code (max 3 LOC)"
    )
    runpy_parser.add_argument(
        "--file",
        help="Explicit: Path to Python file in tmp/ folder"
    )
    runpy_parser.add_argument(
        "--args",
        dest="script_args",
        help="Arguments to pass to Python script"
    )
    runpy_parser.add_argument(
        "--json",
        action="store_true",
        help="Output execution summary as JSON"
    )

    # === PRP COMMAND ===
    prp_parser = subparsers.add_parser(
        "prp", help="PRP management commands"
    )
    prp_subparsers = prp_parser.add_subparsers(dest="prp_command", required=True)

    # prp validate subcommand
    prp_validate_parser = prp_subparsers.add_parser(
        "validate", help="Validate PRP YAML header"
    )
    prp_validate_parser.add_argument(
        "file", help="Path to PRP markdown file"
    )
    prp_validate_parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    # prp generate subcommand
    prp_generate_parser = prp_subparsers.add_parser(
        "generate", help="Generate PRP from INITIAL.md"
    )
    prp_generate_parser.add_argument(
        "initial_md", help="Path to INITIAL.md file"
    )
    prp_generate_parser.add_argument(
        "-o", "--output",
        help="Output directory for PRP (default: PRPs/feature-requests)"
    )
    prp_generate_parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Execute command
    if args.command == "validate":
        return cmd_validate(args)
    elif args.command == "git":
        return cmd_git(args)
    elif args.command == "context":
        return cmd_context(args)
    elif args.command == "run_py":
        return cmd_run_py(args)
    elif args.command == "prp":
        if args.prp_command == "validate":
            return cmd_prp_validate(args)
        elif args.prp_command == "generate":
            return cmd_prp_generate(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
