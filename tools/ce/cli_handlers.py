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
from .blend import run_blend as blend_run_blend
from .blending.cleanup import cleanup_legacy_dirs

# Conditional import for init_project (implemented in PRP-36.2.2)
try:
    from .init_project import ProjectInitializer
    _HAS_INIT_PROJECT = True
except ImportError:
    _HAS_INIT_PROJECT = False


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
        # Set environment variable for sequential thinking
        import os
        if hasattr(args, 'use_thinking'):
            os.environ['CE_USE_SEQUENTIAL_THINKING'] = 'true' if args.use_thinking else 'false'

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

def _get_analysis_result(args, cache_ttl: int):
    """Get analysis result from cache or fresh analysis.
    
    Args:
        args: Command arguments
        cache_ttl: Cache TTL in minutes
    
    Returns:
        Analysis result dict
    """
    from .update_context import (
        analyze_context_drift,
        get_cached_analysis,
        is_cache_valid,
    )
    
    # Skip cache if forced
    if getattr(args, 'force', False):
        return analyze_context_drift()
    
    # Try to use cache
    cached = get_cached_analysis()
    if cached and is_cache_valid(cached, ttl_minutes=cache_ttl):
        return cached
    
    # Cache miss or invalid - run fresh analysis
    return analyze_context_drift()


def _print_analysis_output(result, args, cache_ttl: int) -> None:
    """Print analysis output in human or JSON format.
    
    Args:
        result: Analysis result
        args: Command arguments
        cache_ttl: Cache TTL in minutes
    """
    if args.json:
        print(format_output(result, True))
        return
    
    # Calculate cache age for display
    from datetime import datetime, timezone
    cache_age_str = ""
    if not getattr(args, 'force', False):
        try:
            generated_at = datetime.fromisoformat(
                result["generated_at"].replace("+00:00", "+00:00")
            )
            if generated_at.tzinfo is None:
                generated_at = generated_at.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            age_minutes = int((now - generated_at).total_seconds() / 60)
            cache_age_str = f" ({age_minutes}m old, TTL: {cache_ttl}m)"
        except Exception:
            cache_age_str = f" (TTL: {cache_ttl}m)"
    
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
    
    if cache_age_str and not getattr(args, 'force', False):
        print(f"✅ Using cached analysis{cache_age_str}")
        print(f"   Use --force to re-analyze")
    
    print(f"{indicator} Analysis complete ({duration}s)")
    print(f"   Drift Score: {drift_score:.1f}% ({drift_level.upper()})")
    print(f"   Violations: {violations}")
    if missing > 0:
        print(f"   Missing Examples: {missing}")
    print(f"   Report: {result['report_path']}")


def cmd_analyze_context(args) -> int:
    """Execute analyze-context command.
    
    Fast drift check without metadata updates - optimized for CI/CD.
    
    Returns:
        Exit code: 0 (ok), 1 (warning), 2 (critical)
    """
    from .update_context import get_cache_ttl
    
    try:
        # Get cache TTL (CLI flag > config > default)
        cache_ttl = get_cache_ttl(getattr(args, 'cache_ttl', None))
        
        # Get analysis result (cached or fresh)
        result = _get_analysis_result(args, cache_ttl)
        
        # Print output
        _print_analysis_output(result, args, cache_ttl)
        
        # Return exit code based on drift level
        exit_codes = {"ok": 0, "warning": 1, "critical": 2}
        return exit_codes[result["drift_level"]]
    
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


# === UPDATE-CONTEXT COMMAND ===

def _should_rebuild_packages() -> bool:
    """
    Check if repomix packages should be rebuilt.

    Checks:
    - .serena/memories/ modified (git status)
    - examples/ modified (git status)

    Returns:
        True if rebuild needed, False otherwise
    """
    import subprocess
    from pathlib import Path

    try:
        # Check if in git repo
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return False

        # Check for modifications in framework directories
        result = subprocess.run(
            ["git", "status", "--porcelain", ".serena/memories/", "examples/"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # If any modifications detected, rebuild
        return bool(result.stdout.strip())

    except Exception:
        # If check fails, don't rebuild (non-fatal)
        return False


def _rebuild_repomix_packages() -> bool:
    """
    Rebuild repomix packages by running build-and-distribute.sh.

    Returns:
        True if rebuild successful, False otherwise
    """
    import subprocess
    from pathlib import Path
    import shutil

    try:
        project_root = Path.cwd()
        build_script = project_root / ".ce" / "build-and-distribute.sh"

        if not build_script.exists():
            return False

        # Run build script
        result = subprocess.run(
            [str(build_script)],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            return False

        # Copy packages from ce-32/builds/ to .ce/
        builds_dir = project_root / "ce-32" / "builds"
        ce_dir = project_root / ".ce"

        if builds_dir.exists():
            for xml_file in builds_dir.glob("*.xml"):
                shutil.copy2(xml_file, ce_dir / xml_file.name)

        return True

    except Exception as e:
        print(f"   Rebuild error: {str(e)}")
        return False


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

        # Step 1.5: Auto-rebuild repomix packages if framework files updated
        if not args.json and _should_rebuild_packages():
            print("\n📦 Framework files updated - rebuilding packages...")
            rebuild_success = _rebuild_repomix_packages()
            if rebuild_success:
                print("✅ Packages rebuilt successfully")
            else:
                print("⚠️  Package rebuild failed (non-fatal)")

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


def cmd_vacuum(args):
    """Handle vacuum command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 = success, 1 = candidates found, 2 = error)
    """
    from pathlib import Path
    from .vacuum import VacuumCommand

    try:
        # Find project root (where .ce/ directory exists)
        current = Path.cwd()
        project_root = None

        for parent in [current] + list(current.parents):
            if (parent / ".ce").exists():
                project_root = parent
                break

        if not project_root:
            print("❌ Error: Not in a Context Engineering project (.ce/ not found)\n🔧 Troubleshooting: Check inputs and system state", file=sys.stderr)
            return 2

        # Resolve scan path if provided
        scan_path = None
        if hasattr(args, 'path') and args.path:
            scan_path = project_root / args.path
            if not scan_path.exists():
                print(f"❌ Error: Path does not exist: {args.path}\n🔧 Troubleshooting: Verify file path exists", file=sys.stderr)
                return 2
            if not scan_path.is_dir():
                print(f"❌ Error: Path is not a directory: {args.path}\n🔧 Troubleshooting: Check inputs and system state", file=sys.stderr)
                return 2

        # Run vacuum command
        vacuum = VacuumCommand(project_root)
        return vacuum.run(
            dry_run=not (args.execute or args.force or args.auto or args.nuclear),
            min_confidence=args.min_confidence,
            exclude_strategies=args.exclude_strategies or [],
            execute=args.execute,
            force=args.force,
            auto=args.auto,
            nuclear=args.nuclear,
            scan_path=scan_path,
        )

    except KeyboardInterrupt:
        print("\n❌ Vacuum cancelled by user", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"❌ Vacuum failed: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2


# === BLEND COMMAND ===

def cmd_blend(args) -> int:
    """Execute blend command."""
    return blend_run_blend(args)


# === CLEANUP COMMAND ===

def cmd_cleanup(args) -> int:
    """Execute cleanup command."""
    from pathlib import Path
    from .blending.cleanup import cleanup_legacy_dirs

    try:
        # Determine dry_run mode
        dry_run = not args.execute

        target_project = Path.cwd()

        status = cleanup_legacy_dirs(
            target_project=target_project,
            dry_run=dry_run
        )

        # Exit with success if all cleanups succeeded
        if all(status.values()):
            return 0
        else:
            return 1

    except ValueError as e:
        # Migration incomplete
        print(f"❌ {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"❌ Cleanup failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


# === INIT-PROJECT COMMAND ===

def cmd_init_project(args) -> int:
    """Execute init-project command.

    Orchestrates CE framework installation on target projects using ProjectInitializer.

    Args:
        args: Parsed command-line arguments with:
            - target_dir: Path to target project
            - dry_run: If True, show actions without executing
            - blend_only: If True, run only blend phase
            - phase: Which phase to run (extract, blend, initialize, verify, all)

    Returns:
        Exit code: 0 (success), 1 (user error), 2 (initialization error)
    """
    from pathlib import Path

    try:
        # Parse and resolve target directory to absolute path
        target_dir = Path(args.target_dir).resolve()

        # Validate target directory exists
        if not target_dir.exists():
            print(f"❌ Target directory not found: {target_dir}", file=sys.stderr)
            print(f"🔧 Troubleshooting: Verify path and ensure directory exists", file=sys.stderr)
            return 1

        # Create ProjectInitializer instance
        dry_run = getattr(args, 'dry_run', False)
        initializer = ProjectInitializer(target_dir, dry_run=dry_run)

        # Handle --blend-only flag (takes precedence over --phase)
        if getattr(args, 'blend_only', False):
            result = initializer.blend()

            if args.json:
                print(format_output({"blend": result}, True))
            else:
                print(result.get("message", "Blend phase completed"))
                if result.get("stdout"):
                    print(result["stdout"])
                if result.get("stderr"):
                    print(result["stderr"], file=sys.stderr)

            return 0 if result.get("success", False) else 2

        # Handle --phase flag or run all phases
        phase = getattr(args, 'phase', 'all')
        results = initializer.run(phase=phase)

        # Output results
        if getattr(args, 'json', False):
            print(format_output(results, True))
        else:
            for phase_name, result in results.items():
                print(f"\n{'='*60}")
                print(f"Phase: {phase_name}")
                print(f"{'='*60}")
                print(result.get("message", "No message"))

                # Print stdout/stderr if present
                if result.get("stdout"):
                    print(result["stdout"])
                if result.get("stderr"):
                    print(result["stderr"], file=sys.stderr)

        # Determine exit code based on all phases
        all_success = all(r.get("success", True) for r in results.values())
        return 0 if all_success else 2

    except ValueError as e:
        # Invalid phase or other user errors
        print(f"❌ {str(e)}", file=sys.stderr)
        print(f"🔧 Troubleshooting: Check command arguments and try again", file=sys.stderr)
        return 1
    except Exception as e:
        # Initialization errors from ProjectInitializer
        print(f"❌ Initialization failed: {str(e)}", file=sys.stderr)
        print(f"🔧 Troubleshooting: Check error details above and verify framework files exist", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2
