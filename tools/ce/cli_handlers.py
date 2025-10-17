"""CLI command handlers with delegation pattern.

Extracted from __main__.py to reduce nesting depth and improve maintainability.
Each handler follows KISS principle with max 4 nesting levels.
"""

import sys
import json
from typing import Any, Dict

from .core import git_status, git_checkpoint, git_diff, run_py
from .validate import validate_level_1, validate_level_2, validate_level_3, validate_level_4, validate_all
from .context import (
    sync, health, prune,
    pre_generation_sync, post_execution_sync,
    context_health_verbose, drift_report_markdown,
    enable_auto_sync, disable_auto_sync, get_auto_sync_status
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
from .update_context import sync_context


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


# === VALIDATE COMMAND ===

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
            if not args.prp:
                print("❌ Level 4 validation requires --prp argument", file=sys.stderr)
                return 1

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


# === GIT COMMAND ===

def cmd_git(args) -> int:
    """Execute git command."""
    try:
        if args.action == "status":
            result = git_status()
            print(format_output(result, args.json))
            return 0

        if args.action == "checkpoint":
            message = args.message or "Context Engineering checkpoint"
            checkpoint_id = git_checkpoint(message)
            result = {"checkpoint_id": checkpoint_id, "message": message}
            print(format_output(result, args.json))
            return 0

        if args.action == "diff":
            since = args.since or "HEAD~5"
            files = git_diff(since=since, name_only=True)
            result = {"changed_files": files, "count": len(files), "since": since}
            print(format_output(result, args.json))
            return 0

        print(f"Unknown git action: {args.action}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"❌ Git operation failed: {str(e)}", file=sys.stderr)
        return 1


# === CONTEXT COMMAND (delegated) ===

def _handle_context_sync(args) -> int:
    """Handle context sync action."""
    result = sync()
    print(format_output(result, args.json))
    return 0


def _handle_context_health(args) -> int:
    """Handle context health action."""
    verbose = getattr(args, 'verbose', False)

    if verbose:
        result = context_health_verbose()
        if args.json:
            print(format_output(result, True))
        else:
            print(drift_report_markdown())
        return 0 if result["threshold"] != "critical" else 1

    result = health()
    print(format_output(result, args.json))

    if not args.json:
        print()
        if result["healthy"]:
            print("✅ Context is healthy")
        else:
            print("⚠️  Context needs attention:")
            for rec in result["recommendations"]:
                print(f"  • {rec}")

    return 0 if result["healthy"] else 1


def _handle_context_prune(args) -> int:
    """Handle context prune action."""
    age = args.age or 7
    dry_run = args.dry_run or False
    result = prune(age_days=age, dry_run=dry_run)
    print(format_output(result, args.json))
    return 0


def _handle_context_pre_sync(args) -> int:
    """Handle context pre-sync action."""
    force = getattr(args, 'force', False)
    result = pre_generation_sync(force=force)
    if args.json:
        print(format_output(result, True))
    else:
        print(f"✅ Pre-generation sync complete")
        print(f"   Drift score: {result['drift_score']:.1f}%")
        print(f"   Git clean: {result['git_clean']}")
    return 0


def _handle_context_post_sync(args) -> int:
    """Handle context post-sync action."""
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


def _handle_context_auto_sync(args) -> int:
    """Handle context auto-sync action."""
    subaction = getattr(args, 'subaction', None)

    if subaction == "enable" or getattr(args, 'enable', False):
        result = enable_auto_sync()
        if args.json:
            print(format_output(result, True))
        else:
            print(f"✅ {result['mode'].title()}: Auto-sync enabled")
            print(f"   Steps 2.5 and 6.5 will run automatically")
        return 0

    if subaction == "disable" or getattr(args, 'disable', False):
        result = disable_auto_sync()
        if args.json:
            print(format_output(result, True))
        else:
            print(f"✅ {result['mode'].title()}: Auto-sync disabled")
            print(f"   Manual sync required")
        return 0

    if subaction == "status" or getattr(args, 'status', False):
        result = get_auto_sync_status()
        if args.json:
            print(format_output(result, True))
        else:
            status_emoji = "✅" if result["enabled"] else "❌"
            print(f"{status_emoji} {result['message']}")
        return 0

    print("❌ auto-sync requires --enable, --disable, or --status", file=sys.stderr)
    return 1


def cmd_context(args) -> int:
    """Execute context command with delegation."""
    handlers = {
        "sync": _handle_context_sync,
        "health": _handle_context_health,
        "prune": _handle_context_prune,
        "pre-sync": _handle_context_pre_sync,
        "post-sync": _handle_context_post_sync,
        "auto-sync": _handle_context_auto_sync,
    }

    handler = handlers.get(args.action)
    if not handler:
        print(f"Unknown context action: {args.action}", file=sys.stderr)
        return 1

    try:
        return handler(args)
    except Exception as e:
        print(f"❌ Context operation failed: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


# === DRIFT COMMAND (delegated) ===

def _handle_drift_history(args) -> int:
    """Handle drift history action."""
    history = get_drift_history(
        last_n=args.last,
        prp_id=args.prp_id,
        action_filter=args.action_filter
    )

    if args.json:
        print(format_output({"history": history}, True))
        return 0

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


def _handle_drift_show(args) -> int:
    """Handle drift show action."""
    if not args.prp_id:
        print("❌ show requires PRP ID argument", file=sys.stderr)
        return 1

    decision = show_drift_decision(args.prp_id)

    if args.json:
        print(format_output(decision, True))
        return 0

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


def _handle_drift_summary(args) -> int:
    """Handle drift summary action."""
    summary = drift_summary()

    if args.json:
        print(format_output(summary, True))
        return 0

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


def _handle_drift_compare(args) -> int:
    """Handle drift compare action."""
    if not args.prp_id or not args.prp_id2:
        print("❌ compare requires two PRP IDs", file=sys.stderr)
        return 1

    comparison = compare_drift_decisions(args.prp_id, args.prp_id2)

    if args.json:
        print(format_output(comparison, True))
        return 0

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


def cmd_drift(args) -> int:
    """Execute drift history command with delegation."""
    handlers = {
        "history": _handle_drift_history,
        "show": _handle_drift_show,
        "summary": _handle_drift_summary,
        "compare": _handle_drift_compare,
    }

    handler = handlers.get(args.action)
    if not handler:
        print(f"Unknown drift action: {args.action}", file=sys.stderr)
        return 1

    try:
        return handler(args)
    except ValueError as e:
        print(f"❌ {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Drift operation failed: {str(e)}", file=sys.stderr)
        return 1


# === RUN_PY COMMAND ===

def cmd_run_py(args) -> int:
    """Execute run_py command."""
    try:
        auto_input = getattr(args, 'input', None)

        result = run_py(
            code=args.code if hasattr(args, 'code') else None,
            file=args.file if hasattr(args, 'file') else None,
            auto=auto_input,
            args=args.script_args or ""
        )

        if result["stdout"]:
            print(result["stdout"], end="")

        if result["stderr"]:
            print(result["stderr"], end="", file=sys.stderr)

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


# === PRP COMMANDS ===

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
        join_prp = getattr(args, 'join_prp', None)
        prp_path = generate_prp(args.initial_md, output_dir, join_prp=join_prp)

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
            return 0 if result["success"] else 1

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


# === PIPELINE COMMANDS ===

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


def cmd_pipeline_render(args) -> int:
    """Execute pipeline render command."""
    from pathlib import Path

    try:
        pipeline = load_abstract_pipeline(args.pipeline_file)

        if args.executor == "github-actions":
            executor = GitHubActionsExecutor()
        else:
            executor = MockExecutor()

        rendered = executor.render(pipeline)

        if args.output:
            Path(args.output).write_text(rendered)
            print(f"✅ Rendered to {args.output}")
        else:
            print(rendered)

        return 0

    except Exception as e:
        print(f"❌ Render error: {str(e)}", file=sys.stderr)
        return 1


# === METRICS COMMAND ===

def cmd_metrics(args) -> int:
    """Display system metrics and success rates."""
    try:
        collector = MetricsCollector(metrics_file=args.file)
        summary = collector.get_summary()

        if args.format == "json":
            print(json.dumps(summary, indent=2))
            return 0

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


# === ANALYZE-CONTEXT COMMAND ===

def cmd_analyze_context(args) -> int:
    """Execute analyze-context command.
    
    Fast drift check without metadata updates - optimized for CI/CD.
    
    Returns:
        Exit code: 0 (ok), 1 (warning), 2 (critical)
    """
    from .update_context import (
        analyze_context_drift,
        get_cached_analysis,
        is_cache_valid,
        get_cache_ttl
    )
    
    try:
        # Get cache TTL (CLI flag > config > default)
        cache_ttl = get_cache_ttl(getattr(args, 'cache_ttl', None))
        
        # Check cache if not forced
        if not getattr(args, 'force', False):
            cached = get_cached_analysis()
            if cached and is_cache_valid(cached, ttl_minutes=cache_ttl):
                result = cached
                
                if not args.json:
                    # Calculate cache age
                    from datetime import datetime, timezone
                    try:
                        generated_at = datetime.fromisoformat(
                            cached["generated_at"].replace("+00:00", "+00:00")
                        )
                        if generated_at.tzinfo is None:
                            generated_at = generated_at.replace(tzinfo=timezone.utc)
                        now = datetime.now(timezone.utc)
                        age_minutes = int((now - generated_at).total_seconds() / 60)
                        print(f"\u2705 Using cached analysis ({age_minutes}m old, TTL: {cache_ttl}m)")
                        print(f"   Use --force to re-analyze\n")
                    except Exception:
                        print(f"\u2705 Using cached analysis (TTL: {cache_ttl}m)\n")
            else:
                result = analyze_context_drift()
        else:
            result = analyze_context_drift()
        
        # Display or output JSON
        if args.json:
            print(format_output(result, True))
        else:
            # Human-readable output
            drift_score = result["drift_score"]
            drift_level = result["drift_level"]
            violations = result.get("violation_count", 0)
            missing = len(result.get("missing_examples", []))
            duration = result.get("duration_seconds", 0)
            
            # Emoji indicators
            if drift_level == "ok":
                indicator = "✅"
            elif drift_level == "warning":
                indicator = "⚠️ "
            else:  # critical
                indicator = "🚨"
            
            print("🔍 Analyzing context drift...")
            if duration > 0:
                print("   📊 Pattern conformance: scan complete")
                print("   📚 Documentation gaps: check complete")
                print()
            
            print(f"{indicator} Analysis complete ({duration}s)")
            print(f"   Drift Score: {drift_score:.1f}% ({drift_level.upper()})")
            print(f"   Violations: {violations}")
            if missing > 0:
                print(f"   Missing Examples: {missing}")
            print(f"   Report: {result['report_path']}")
        
        # Return exit code based on drift level
        exit_codes = {"ok": 0, "warning": 1, "critical": 2}
        return exit_codes[result["drift_level"]]
    
    except Exception as e:
        print(f"\u274c Analysis failed: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


# === UPDATE-CONTEXT COMMAND ===

def cmd_update_context(args) -> int:
    """Execute update-context command.

    Workflow:
        1. Standard context sync (always runs)
        2. Drift remediation workflow (always runs)
           - Vanilla mode (no --remediate): asks approval before PRP generation
           - YOLO mode (--remediate): skips approval, auto-generates PRP
    """
    try:
        # Step 1: ALWAYS run standard context sync first
        target_prp = args.prp if hasattr(args, 'prp') and args.prp else None
        result = sync_context(target_prp=target_prp)

        if args.json:
            print(format_output(result, True))
        else:
            print("✅ Context sync completed")
            print(f"   PRPs scanned: {result['prps_scanned']}")
            print(f"   PRPs updated: {result['prps_updated']}")
            print(f"   PRPs moved: {result['prps_moved']}")
            print(f"   CE updated: {result['ce_updated_count']}")
            print(f"   Serena updated: {result['serena_updated_count']}")

            if result['errors']:
                print(f"\n⚠️  Errors encountered:")
                for error in result['errors']:
                    print(f"   - {error}")

        # Step 2: ALWAYS run drift remediation workflow after sync
        from .update_context import remediate_drift_workflow

        yolo_mode = hasattr(args, 'remediate') and args.remediate
        remediate_result = remediate_drift_workflow(yolo_mode=yolo_mode)

        if args.json:
            # Combine both results in JSON output
            combined = {
                "sync": result,
                "remediation": remediate_result
            }
            print(format_output(combined, True))

        # Combine success status from both workflows
        success = result['success'] and remediate_result['success']
        return 0 if success else 1

    except Exception as e:
        print(f"❌ Update context failed: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
