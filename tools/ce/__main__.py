"""Context Engineering CLI - Main entry point."""

import argparse
import json
import sys
from typing import Any, Dict

from . import __version__
from .core import git_status, git_checkpoint, git_diff, run_py
from .validate import validate_level_1, validate_level_2, validate_level_3, validate_level_4, validate_all
from .context import (
    sync, health, prune,
    pre_generation_sync, post_execution_sync,
    context_health_verbose, drift_report_markdown,
    enable_auto_sync, disable_auto_sync, get_auto_sync_status,
    prune_stale_memories
)
from .generate import generate_prp
from .drift import (
    get_drift_history,
    drift_summary,
    show_drift_decision,
    compare_drift_decisions
)
from .pipeline import load_abstract_pipeline, validate_pipeline
from .executors.github_actions import GitHubActionsExecutor
from .executors.mock import MockExecutor
from .metrics import MetricsCollector


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
            # Check if verbose flag
            verbose = getattr(args, 'verbose', False)

            if verbose:
                result = context_health_verbose()
                if args.json:
                    print(format_output(result, True))
                else:
                    print(drift_report_markdown())
                return 0 if result["threshold"] != "critical" else 1
            else:
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

        elif args.action == "pre-sync":
            force = getattr(args, 'force', False)
            result = pre_generation_sync(force=force)
            if args.json:
                print(format_output(result, True))
            else:
                print(f"✅ Pre-generation sync complete")
                print(f"   Drift score: {result['drift_score']:.1f}%")
                print(f"   Git clean: {result['git_clean']}")
            return 0

        elif args.action == "post-sync":
            prp_id = getattr(args, 'prp_id', None)
            if not prp_id:
                print("❌ post-sync requires --prp-id argument", file=sys.stderr)
                return 1

            skip_cleanup = getattr(args, 'skip_cleanup', False)
            result = post_execution_sync(prp_id, skip_cleanup=skip_cleanup)
            if args.json:
                print(format_output(result, True))
            else:
                print(f"✅ Post-execution sync complete (PRP-{prp_id})")
                print(f"   Cleanup: {result['cleanup_completed']}")
                print(f"   Drift score: {result['drift_score']:.1f}%")
                if result['final_checkpoint']:
                    print(f"   Checkpoint: {result['final_checkpoint']}")
            return 0

        elif args.action == "auto-sync":
            # Check subaction
            subaction = getattr(args, 'subaction', None)

            if subaction == "enable" or getattr(args, 'enable', False):
                result = enable_auto_sync()
                if args.json:
                    print(format_output(result, True))
                else:
                    print(f"✅ {result['mode'].title()}: Auto-sync enabled")
                    print(f"   Steps 2.5 and 6.5 will run automatically")
                return 0

            elif subaction == "disable" or getattr(args, 'disable', False):
                result = disable_auto_sync()
                if args.json:
                    print(format_output(result, True))
                else:
                    print(f"✅ {result['mode'].title()}: Auto-sync disabled")
                    print(f"   Manual sync required")
                return 0

            elif subaction == "status" or getattr(args, 'status', False):
                result = get_auto_sync_status()
                if args.json:
                    print(format_output(result, True))
                else:
                    status_emoji = "✅" if result["enabled"] else "❌"
                    print(f"{status_emoji} {result['message']}")
                return 0

            else:
                print("❌ auto-sync requires --enable, --disable, or --status", file=sys.stderr)
                return 1

        else:
            print(f"Unknown context action: {args.action}", file=sys.stderr)
            return 1

    except Exception as e:
        print(f"❌ Context operation failed: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_drift(args) -> int:
    """Execute drift history command."""
    try:
        if args.action == "history":
            history = get_drift_history(
                last_n=args.last,
                prp_id=args.prp_id,
                action_filter=args.action_filter
            )

            if args.json:
                print(format_output({"history": history}, True))
            else:
                if not history:
                    print("No drift decisions found")
                    return 0

                print("\n📊 DRIFT DECISION HISTORY\n")
                print("━" * 80)
                print(f"{'PRP ID':<12} {'Score':<8} {'Action':<18} {'Reviewer':<12} {'Date':<20}")
                print("━" * 80)

                for h in history:
                    decision = h["drift_decision"]
                    prp_id = h["prp_id"]
                    score = decision["score"]
                    action = decision["action"]
                    reviewer = decision.get("reviewer", "unknown")
                    timestamp = decision.get("timestamp", "N/A")[:10]

                    print(f"{prp_id:<12} {score:<8.2f} {action:<18} {reviewer:<12} {timestamp:<20}")

                print("━" * 80)
                print(f"\nTotal: {len(history)} decisions\n")

            return 0

        elif args.action == "show":
            if not args.prp_id:
                print("❌ show requires PRP ID argument", file=sys.stderr)
                return 1

            decision = show_drift_decision(args.prp_id)

            if args.json:
                print(format_output(decision, True))
            else:
                dd = decision["drift_decision"]
                print(f"\n📋 DRIFT DECISION: {decision['prp_id']}")
                print(f"PRP: {decision['prp_name']}\n")
                print(f"Score: {dd['score']:.2f}%")
                print(f"Action: {dd['action']}")
                print(f"Reviewer: {dd.get('reviewer', 'unknown')}")
                print(f"Timestamp: {dd.get('timestamp', 'N/A')}\n")

                print("Justification:")
                print(f"  {dd['justification']}\n")

                if "category_breakdown" in dd:
                    print("Category Breakdown:")
                    for cat, score in dd["category_breakdown"].items():
                        print(f"  • {cat}: {score:.2f}%")
                    print()

            return 0

        elif args.action == "summary":
            summary = drift_summary()

            if args.json:
                print(format_output(summary, True))
            else:
                print("\n📊 DRIFT SUMMARY\n")
                print("━" * 60)
                print(f"Total PRPs: {summary['total_prps']}")
                print(f"PRPs with Drift: {summary['prps_with_drift']}")
                print(f"Average Drift Score: {summary['avg_drift_score']:.2f}%\n")

                print("Decisions:")
                for action, count in summary.get("decisions", {}).items():
                    print(f"  • {action}: {count}")
                print()

                print("Score Distribution:")
                dist = summary.get("score_distribution", {})
                print(f"  • Low (0-10%): {dist.get('low', 0)}")
                print(f"  • Medium (10-30%): {dist.get('medium', 0)}")
                print(f"  • High (30%+): {dist.get('high', 0)}")
                print()

                if summary.get("category_breakdown"):
                    print("Category Breakdown:")
                    for cat, data in summary["category_breakdown"].items():
                        print(f"  • {cat}: {data['avg']:.2f}% avg ({data['count']} PRPs)")
                    print()

                if summary.get("reviewer_breakdown"):
                    print("Reviewer Breakdown:")
                    for reviewer, count in summary["reviewer_breakdown"].items():
                        print(f"  • {reviewer}: {count}")
                    print()

            return 0

        elif args.action == "compare":
            if not args.prp_id or not args.prp_id2:
                print("❌ compare requires two PRP IDs", file=sys.stderr)
                return 1

            comparison = compare_drift_decisions(args.prp_id, args.prp_id2)

            if args.json:
                print(format_output(comparison, True))
            else:
                comp = comparison["comparison"]
                prp1 = comparison["prp_1"]
                prp2 = comparison["prp_2"]

                print(f"\n🔍 DRIFT COMPARISON: {args.prp_id} vs {args.prp_id2}\n")
                print("━" * 60)

                print(f"\n{args.prp_id}:")
                print(f"  Score: {prp1['drift_decision']['score']:.2f}%")
                print(f"  Action: {prp1['drift_decision']['action']}")

                print(f"\n{args.prp_id2}:")
                print(f"  Score: {prp2['drift_decision']['score']:.2f}%")
                print(f"  Action: {prp2['drift_decision']['action']}")

                print(f"\nDifferences:")
                print(f"  Score Difference: {comp['score_diff']:.2f}%")
                print(f"  Same Action: {'Yes' if comp['same_action'] else 'No'}")

                if comp.get("common_categories"):
                    print(f"\nCommon Categories:")
                    for cat in comp["common_categories"]:
                        print(f"  • {cat}")

                if comp.get("divergent_categories"):
                    print(f"\nDivergent Categories:")
                    for cat in comp["divergent_categories"]:
                        print(f"  • {cat}")

                print()

            return 0

        else:
            print(f"Unknown drift action: {args.action}", file=sys.stderr)
            return 1

    except ValueError as e:
        print(f"❌ {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Drift operation failed: {str(e)}", file=sys.stderr)
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


def cmd_prp_execute(args) -> int:
    """Execute prp execute command."""
    from .execute import execute_prp
    from .exceptions import EscalationRequired

    try:
        result = execute_prp(
            prp_id=args.prp_id,
            start_phase=args.start_phase,
            end_phase=args.end_phase,
            skip_validation=args.skip_validation,
            dry_run=args.dry_run
        )

        if args.json:
            print(format_output(result, True))
        else:
            if result.get("dry_run"):
                print(f"\n✅ Dry run: {len(result['phases'])} phases parsed")
                for phase in result['phases']:
                    print(f"  Phase {phase['phase_number']}: {phase['phase_name']} ({phase['hours']}h)")
            else:
                print(f"\n{'='*80}")
                print(f"✅ PRP-{args.prp_id} execution complete")
                print(f"{'='*80}")
                print(f"Phases completed: {result['phases_completed']}")
                print(f"Confidence score: {result['confidence_score']}")
                print(f"Execution time: {result['execution_time']}")
                print(f"Checkpoints created: {len(result['checkpoints_created'])}")

        return 0 if result["success"] else 1

    except EscalationRequired as e:
        print(f"\n{'='*80}", file=sys.stderr)
        print(f"🚨 ESCALATION REQUIRED", file=sys.stderr)
        print(f"{'='*80}", file=sys.stderr)
        print(f"Reason: {e.reason}", file=sys.stderr)
        print(f"\nError Details:", file=sys.stderr)
        print(f"  Type: {e.error.get('type', 'unknown')}", file=sys.stderr)
        print(f"  Location: {e.error.get('file', 'unknown')}:{e.error.get('line', '?')}", file=sys.stderr)
        print(f"  Message: {e.error.get('message', 'No message')}", file=sys.stderr)
        print(f"\n🔧 Troubleshooting:", file=sys.stderr)
        print(e.troubleshooting, file=sys.stderr)
        return 2

    except FileNotFoundError as e:
        print(f"❌ {str(e)}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"❌ Execution failed: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_prp_analyze(args) -> int:
    """Execute prp analyze command."""
    from pathlib import Path
    from .prp_analyzer import analyze_prp, format_analysis_report

    try:
        prp_path = Path(args.file)
        analysis = analyze_prp(prp_path)
        print(format_analysis_report(analysis, json_output=args.json))

        # Return exit code based on size category
        # RED = 2 (strong warning), YELLOW = 1 (warning), GREEN = 0 (ok)
        if analysis.size_category.value == "RED":
            return 2
        elif analysis.size_category.value == "YELLOW":
            return 1
        else:
            return 0

    except FileNotFoundError as e:
        print(f"❌ {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ PRP analysis failed: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_pipeline_validate(args) -> int:
    """Execute pipeline validate command."""
    try:
        pipeline = load_abstract_pipeline(args.pipeline_file)
        result = validate_pipeline(pipeline)

        if result["success"]:
            print("✅ Pipeline validation passed")
            return 0
        else:
            print("❌ Pipeline validation failed:")
            for error in result["errors"]:
                print(f"  - {error}")
            return 1

    except Exception as e:
        print(f"❌ Validation error: {str(e)}", file=sys.stderr)
        return 1


def cmd_metrics(args) -> int:
    """Display system metrics and success rates.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    try:
        collector = MetricsCollector(metrics_file=args.file)
        summary = collector.get_summary()

        if args.format == "json":
            print(json.dumps(summary, indent=2))
        else:
            # Human-readable format
            print("\n📊 Context Engineering Metrics")
            print("=" * 60)

            # Success rates
            rates = summary["success_rates"]
            print("\n🎯 Success Rates:")
            print(f"  First-pass:  {rates['first_pass_rate']:.1f}%")
            print(f"  Second-pass: {rates['second_pass_rate']:.1f}%")
            print(f"  Overall:     {rates['overall_rate']:.1f}%")
            print(f"  Total PRPs:  {rates['total_executions']}")

            # Validation stats
            val_stats = summary["validation_stats"]
            if val_stats:
                print("\n✅ Validation Pass Rates:")
                for key, value in sorted(val_stats.items()):
                    if key.endswith("_pass_rate"):
                        level = key.replace("_pass_rate", "")
                        total_key = f"{level}_total"
                        total = val_stats.get(total_key, 0)
                        print(f"  {level.upper()}: {value:.1f}% ({total} executions)")

            # Performance
            perf = summary["performance"]
            print("\n⚡ Performance:")
            print(f"  Avg duration: {perf['avg_duration']:.1f}s")
            print(f"  Total PRPs:   {perf['total_prps']}")
            print(f"  Total validations: {perf['total_validations']}")

            print("=" * 60)

        return 0

    except FileNotFoundError:
        print(f"❌ Metrics file not found: {args.file}", file=sys.stderr)
        print(f"🔧 Troubleshooting: Run PRP executions to collect metrics", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Metrics error: {str(e)}", file=sys.stderr)
        return 1


def cmd_pipeline_render(args) -> int:
    """Execute pipeline render command."""
    from pathlib import Path

    try:
        pipeline = load_abstract_pipeline(args.pipeline_file)

        # Select executor
        if args.executor == "github-actions":
            executor = GitHubActionsExecutor()
        else:
            executor = MockExecutor()

        # Render
        rendered = executor.render(pipeline)

        # Output
        if args.output:
            Path(args.output).write_text(rendered)
            print(f"✅ Rendered to {args.output}")
        else:
            print(rendered)

        return 0

    except Exception as e:
        print(f"❌ Render error: {str(e)}", file=sys.stderr)
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
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
