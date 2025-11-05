"""Context Engineering CLI - Main entry point.

This module provides the CLI interface with argparse configuration.
All command handlers are delegated to cli_handlers module for better organization.
"""

import argparse
import sys

from . import __version__
from .cli_handlers import (
    cmd_validate,
    cmd_git,
    cmd_context,
    cmd_drift,
    cmd_run_py,
    cmd_prp_validate,
    cmd_prp_generate,
    cmd_prp_execute,
    cmd_prp_analyze,
    cmd_pipeline_validate,
    cmd_pipeline_render,
    cmd_metrics,
    cmd_analyze_context,
    cmd_update_context,
    cmd_vacuum,
    cmd_blend,
)


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
        choices=["sync", "health", "prune", "pre-sync", "post-sync", "auto-sync"],
        help="Context action to perform"
    )
    # Common flags
    context_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    # For health action
    context_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose health report with component breakdown (for health)"
    )
    # For prune action
    context_parser.add_argument(
        "--age",
        type=int,
        help="Age in days for pruning (default: 7, for prune)"
    )
    context_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode (for prune)"
    )
    # For pre-sync action
    context_parser.add_argument(
        "--force",
        action="store_true",
        help="Skip drift abort check (for pre-sync, dangerous)"
    )
    # For post-sync action
    context_parser.add_argument(
        "--prp-id",
        help="PRP identifier (for post-sync)"
    )
    context_parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Skip cleanup protocol (for post-sync)"
    )
    # For auto-sync action
    auto_sync_group = context_parser.add_mutually_exclusive_group()
    auto_sync_group.add_argument(
        "--enable",
        action="store_true",
        help="Enable auto-sync mode (for auto-sync)"
    )
    auto_sync_group.add_argument(
        "--disable",
        action="store_true",
        help="Disable auto-sync mode (for auto-sync)"
    )
    auto_sync_group.add_argument(
        "--status",
        action="store_true",
        help="Check auto-sync status (for auto-sync)"
    )

    # === DRIFT COMMAND ===
    drift_parser = subparsers.add_parser(
        "drift",
        help="Drift history tracking and analysis"
    )
    drift_parser.add_argument(
        "action",
        choices=["history", "show", "summary", "compare"],
        help="Drift action to perform"
    )
    drift_parser.add_argument(
        "--last",
        type=int,
        help="Show last N decisions (for history)"
    )
    drift_parser.add_argument(
        "--prp-id",
        help="Filter by PRP ID (for history/show)"
    )
    drift_parser.add_argument(
        "--prp-id2",
        help="Second PRP ID (for compare)"
    )
    drift_parser.add_argument(
        "--action-filter",
        choices=["accepted", "rejected", "examples_updated"],
        help="Filter by action type (for history)"
    )
    drift_parser.add_argument(
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
    prp_generate_parser.add_argument(
        "--join-prp",
        help="Update existing PRP's Linear issue (PRP number, ID like 'PRP-12', or file path)"
    )
    prp_generate_parser.add_argument(
        "--use-thinking",
        action="store_true",
        default=True,
        help="Use sequential thinking for analysis (default: True)"
    )
    prp_generate_parser.add_argument(
        "--no-thinking",
        dest="use_thinking",
        action="store_false",
        help="Disable sequential thinking (use heuristics)"
    )

    # prp execute subcommand
    prp_execute_parser = prp_subparsers.add_parser(
        "execute", help="Execute PRP implementation"
    )
    prp_execute_parser.add_argument(
        "prp_id", help="PRP identifier (e.g., PRP-4)"
    )
    prp_execute_parser.add_argument(
        "--start-phase", type=int, help="Start from specific phase"
    )
    prp_execute_parser.add_argument(
        "--end-phase", type=int, help="End at specific phase"
    )
    prp_execute_parser.add_argument(
        "--skip-validation", action="store_true", help="Skip validation loops"
    )
    prp_execute_parser.add_argument(
        "--dry-run", action="store_true", help="Parse blueprint only, don't execute"
    )
    prp_execute_parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    # prp analyze subcommand
    prp_analyze_parser = prp_subparsers.add_parser(
        "analyze", help="Analyze PRP size and complexity"
    )
    prp_analyze_parser.add_argument(
        "file", help="Path to PRP markdown file"
    )
    prp_analyze_parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    # === PIPELINE COMMAND ===
    pipeline_parser = subparsers.add_parser(
        "pipeline", help="CI/CD pipeline management commands"
    )
    pipeline_subparsers = pipeline_parser.add_subparsers(dest="pipeline_command", required=True)

    # pipeline validate subcommand
    pipeline_validate_parser = pipeline_subparsers.add_parser(
        "validate", help="Validate abstract pipeline definition"
    )
    pipeline_validate_parser.add_argument(
        "pipeline_file", help="Path to abstract pipeline YAML file"
    )

    # pipeline render subcommand
    pipeline_render_parser = pipeline_subparsers.add_parser(
        "render", help="Render abstract pipeline to platform-specific format"
    )
    pipeline_render_parser.add_argument(
        "pipeline_file", help="Path to abstract pipeline YAML file"
    )
    pipeline_render_parser.add_argument(
        "--executor", type=str, choices=["github-actions", "mock"],
        default="github-actions", help="Platform executor to use"
    )
    pipeline_render_parser.add_argument(
        "-o", "--output", help="Output file path"
    )

    # === METRICS COMMAND ===
    metrics_parser = subparsers.add_parser(
        "metrics",
        help="Display system metrics and success rates"
    )
    metrics_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    metrics_parser.add_argument(
        "--file",
        default="metrics.json",
        help="Path to metrics file (default: metrics.json)"
    )

    # === ANALYZE-CONTEXT COMMAND ===
    analyze_context_parser = subparsers.add_parser(
        "analyze-context",
        aliases=["analyse-context"],
        help="Analyze context drift without updating metadata (fast check for CI/CD)"
    )
    analyze_context_parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON for scripting"
    )
    analyze_context_parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-analysis, bypass cache"
    )
    analyze_context_parser.add_argument(
        "--cache-ttl",
        type=int,
        help="Cache TTL in minutes (default: from config or 5)"
    )

    # === UPDATE-CONTEXT COMMAND ===
    update_context_parser = subparsers.add_parser(
        "update-context",
        help="Sync CE/Serena with codebase changes"
    )
    update_context_parser.add_argument(
        "--prp",
        help="Target specific PRP file (path relative to project root)"
    )
    update_context_parser.add_argument(
        "--remediate",
        action="store_true",
        help="Auto-remediate drift violations (YOLO mode - skips approval)"
    )
    update_context_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    # === VACUUM COMMAND ===
    vacuum_parser = subparsers.add_parser(
        "vacuum",
        help="Clean up project noise (temp files, obsolete docs, unreferenced code)"
    )
    vacuum_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Generate report only (default)"
    )
    vacuum_parser.add_argument(
        "--execute",
        action="store_true",
        help="Delete HIGH confidence items (temp files, backups)"
    )
    vacuum_parser.add_argument(
        "--force",
        action="store_true",
        help="Delete HIGH + MEDIUM confidence items"
    )
    vacuum_parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically delete HIGH + MEDIUM confidence items (same as --force)"
    )
    vacuum_parser.add_argument(
        "--nuclear",
        action="store_true",
        help="Delete ALL items including LOW confidence (requires confirmation)"
    )
    vacuum_parser.add_argument(
        "--min-confidence",
        type=int,
        default=0,
        help="Minimum confidence threshold 0-100 (default: 0)"
    )
    vacuum_parser.add_argument(
        "--exclude-strategy",
        action="append",
        dest="exclude_strategies",
        help="Skip specific strategy (can be used multiple times)"
    )

    # === BLEND COMMAND ===
    blend_parser = subparsers.add_parser(
        "blend",
        help="CE Framework Blending Tool - Migrate and blend framework files"
    )
    # Operation modes
    mode_group = blend_parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--all', action='store_true', help='Run all 4 phases')
    mode_group.add_argument('--phase', choices=['detect', 'classify', 'blend', 'cleanup'], help='Run specific phase')
    mode_group.add_argument('--cleanup-only', action='store_true', help='Run cleanup only')
    mode_group.add_argument('--rollback', action='store_true', help='Restore backups')
    # Domain selection (optional)
    blend_parser.add_argument('--domain', help='Blend specific domain only (settings, claude_md, memories, examples, prps, commands)')
    # Behavior flags
    blend_parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    blend_parser.add_argument('--interactive', action='store_true', help='Ask before each phase')
    blend_parser.add_argument('--skip-cleanup', action='store_true', help='Skip Phase D (keep legacy dirs)')
    blend_parser.add_argument('--fast', action='store_true', help='Fast mode (Haiku only, skip expensive ops)')
    blend_parser.add_argument('--quality', action='store_true', help='Quality mode (Sonnet for all LLM calls)')
    blend_parser.add_argument('--scan', action='store_true', help='Scan mode (detect + classify only, no blending)')
    # Configuration
    blend_parser.add_argument('--config', default='.ce/blend-config.yml', help='Path to blend config (default: .ce/blend-config.yml)')
    blend_parser.add_argument('--target-dir', default='.', help='Target project directory (default: current)')
    # Debugging
    blend_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

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
    elif args.command == "drift":
        return cmd_drift(args)
    elif args.command == "run_py":
        return cmd_run_py(args)
    elif args.command == "prp":
        if args.prp_command == "validate":
            return cmd_prp_validate(args)
        elif args.prp_command == "generate":
            return cmd_prp_generate(args)
        elif args.prp_command == "execute":
            return cmd_prp_execute(args)
        elif args.prp_command == "analyze":
            return cmd_prp_analyze(args)
    elif args.command == "pipeline":
        if args.pipeline_command == "validate":
            return cmd_pipeline_validate(args)
        elif args.pipeline_command == "render":
            return cmd_pipeline_render(args)
    elif args.command == "metrics":
        return cmd_metrics(args)
    elif args.command in ["analyze-context", "analyse-context"]:
        return cmd_analyze_context(args)
    elif args.command == "update-context":
        return cmd_update_context(args)
    elif args.command == "vacuum":
        return cmd_vacuum(args)
    elif args.command == "blend":
        return cmd_blend(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
