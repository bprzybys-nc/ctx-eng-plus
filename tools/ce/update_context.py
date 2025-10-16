"""Context sync operations for maintaining CE/Serena alignment with codebase.

This module provides the /update-context command functionality for syncing
knowledge systems with actual implementations.
"""

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import frontmatter

logger = logging.getLogger(__name__)

# Pattern detection rules from examples/
PATTERN_FILES = {
    "error_handling": "examples/patterns/error-handling.py",
    "no_fishy_fallbacks": "examples/patterns/no-fishy-fallbacks.py",
    "naming_conventions": "examples/patterns/naming.py"
}

PATTERN_CHECKS = {
    "error_handling": [
        ("bare_except", r"except:\s*$", "Use specific exception types"),
        ("missing_troubleshooting", r'raise \w+Error\([^🔧]+\)$', "Add 🔧 Troubleshooting guidance")
    ],
    "naming_conventions": [
        ("version_suffix", r"def \w+_v\d+", "Use descriptive names, not versions"),
    ],
    "kiss_violations": [
        ("deep_nesting", r"^                    (if |for |while |try:|elif |with )", "Reduce nesting depth (max 4 levels)")
    ]
}


def read_prp_header(file_path: Path) -> Tuple[Dict[str, Any], str]:
    """Read PRP YAML header using frontmatter library.

    Args:
        file_path: Path to PRP markdown file

    Returns:
        Tuple of (metadata dict, content string)

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If YAML header is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"PRP file not found: {file_path}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Verify file path is correct\n"
            f"   - Check if file was moved or renamed\n"
            f"   - Use: ls {file_path.parent} to list directory"
        )

    try:
        post = frontmatter.load(file_path)
        return post.metadata, post.content
    except Exception as e:
        raise ValueError(
            f"Failed to parse YAML header in {file_path}: {e}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Check YAML syntax with: head -n 20 {file_path}\n"
            f"   - Ensure --- delimiters are present\n"
            f"   - Validate YAML structure"
        ) from e


def update_context_sync_flags(
    file_path: Path,
    ce_updated: bool,
    serena_updated: bool
) -> None:
    """Update context_sync flags in PRP YAML header.

    Args:
        file_path: Path to PRP markdown file
        ce_updated: Whether CE content was updated
        serena_updated: Whether Serena was updated

    Raises:
        ValueError: If YAML update fails
    """
    metadata, content = read_prp_header(file_path)

    # Initialize context_sync if missing
    if "context_sync" not in metadata:
        metadata["context_sync"] = {}

    # Update flags
    metadata["context_sync"]["ce_updated"] = ce_updated
    metadata["context_sync"]["serena_updated"] = serena_updated
    metadata["context_sync"]["last_sync"] = datetime.now(timezone.utc).isoformat()

    # Update attribution
    metadata["updated_by"] = "update-context-command"
    metadata["updated"] = datetime.now(timezone.utc).isoformat()

    # Write back
    try:
        post = frontmatter.Post(content, **metadata)
        with open(file_path, 'w') as f:
            f.write(frontmatter.dumps(post))
        logger.info(f"Updated context_sync flags: {file_path}")
    except Exception as e:
        raise ValueError(
            f"Failed to write YAML header to {file_path}: {e}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Check file permissions: ls -la {file_path}\n"
            f"   - Ensure disk space available: df -h\n"
            f"   - Verify file not locked by another process"
        ) from e


def get_prp_status(file_path: Path) -> str:
    """Extract status field from PRP YAML header.

    Args:
        file_path: Path to PRP markdown file

    Returns:
        Status string (e.g., 'new', 'executed', 'archived')
    """
    metadata, _ = read_prp_header(file_path)
    return metadata.get("status", "unknown")


def discover_prps(target_prp: Optional[str] = None) -> List[Path]:
    """Scan PRPs/ directory recursively for markdown files.

    Args:
        target_prp: Optional specific PRP file path for targeted sync

    Returns:
        List of PRP file paths

    Raises:
        FileNotFoundError: If target_prp specified but not found
    """
    # Determine project root - if we're in tools/, go up one level
    current_dir = Path.cwd()
    if current_dir.name == "tools":
        project_root = current_dir.parent
    else:
        project_root = current_dir

    if target_prp:
        # Targeted sync - single PRP
        prp_path = project_root / target_prp
        if not prp_path.exists():
            raise FileNotFoundError(
                f"Target PRP not found: {target_prp}\n"
                f"🔧 Troubleshooting:\n"
                f"   - Check path is relative to project root\n"
                f"   - Use: ls PRPs/executed/ to list available PRPs\n"
                f"   - Verify file extension is .md"
            )
        return [prp_path]

    # Universal sync - all PRPs
    prps_dir = project_root / "PRPs"
    if not prps_dir.exists():
        logger.warning(f"PRPs directory not found: {prps_dir}")
        return []

    # Scan feature-requests and executed directories
    prp_files = []
    for subdir in ["feature-requests", "executed", "archived"]:
        subdir_path = prps_dir / subdir
        if subdir_path.exists():
            prp_files.extend(subdir_path.glob("*.md"))

    logger.info(f"Discovered {len(prp_files)} PRP files")
    return prp_files


def extract_expected_functions(content: str) -> List[str]:
    """Extract function/class names from PRP content using regex.

    Looks for:
    - `function_name()` backtick references
    - `class ClassName` backtick references
    - def function_name() in code blocks
    - class ClassName: in code blocks

    Args:
        content: PRP markdown content

    Returns:
        List of function/class names
    """
    functions = set()

    # Pattern 1: Backtick references `function_name()`
    backtick_refs = re.findall(r'`(\w+)\(\)`', content)
    functions.update(backtick_refs)

    # Pattern 2: Backtick class references `class ClassName`
    class_refs = re.findall(r'`class (\w+)`', content)
    functions.update(class_refs)

    # Pattern 3: Function definitions in code blocks
    func_defs = re.findall(r'^\s*def (\w+)\(', content, re.MULTILINE)
    functions.update(func_defs)

    # Pattern 4: Class definitions in code blocks
    class_defs = re.findall(r'^\s*class (\w+)[\(:]', content, re.MULTILINE)
    functions.update(class_defs)

    return sorted(list(functions))


def verify_implementation_with_serena(expected_functions: List[str]) -> bool:
    """Use Serena MCP find_symbol to verify implementations exist.

    Args:
        expected_functions: List of function/class names to verify

    Returns:
        True if ALL functions found, False otherwise
    """
    if not expected_functions:
        # No functions to verify - mark as updated
        return True

    try:
        # Try to use Serena MCP
        # For now, graceful degradation - log warning and return False
        logger.warning(
            "Serena MCP verification not yet implemented\n"
            "🔧 Troubleshooting: Set serena_updated=false until MCP integration complete"
        )
        return False
    except Exception as e:
        logger.warning(f"Serena MCP unavailable: {e}")
        return False


def should_transition_to_executed(file_path: Path) -> bool:
    """Check if PRP should transition from feature-requests to executed.

    Rules:
    - Current status must be "new" or "in_progress"
    - ce_updated must be True (implementation verified)
    - File must be in feature-requests/ directory

    Args:
        file_path: Path to PRP file

    Returns:
        True if should transition to executed
    """
    metadata, _ = read_prp_header(file_path)

    # Check file location
    if "feature-requests" not in str(file_path):
        return False

    # Check status
    status = metadata.get("status", "unknown")
    if status not in ["new", "in_progress"]:
        return False

    # Check ce_updated flag
    context_sync = metadata.get("context_sync", {})
    ce_updated = context_sync.get("ce_updated", False)

    return ce_updated


def move_prp_to_executed(file_path: Path) -> Path:
    """Move PRP from feature-requests/ to executed/.

    Uses pathlib rename for atomic operation.

    Args:
        file_path: Current path to PRP file

    Returns:
        New path in executed/ directory

    Raises:
        RuntimeError: If move fails
    """
    # Calculate new path
    current_dir = Path.cwd()
    if current_dir.name == "tools":
        project_root = current_dir.parent
    else:
        project_root = current_dir
    executed_dir = project_root / "PRPs" / "executed"

    # Create executed directory if needed
    executed_dir.mkdir(parents=True, exist_ok=True)

    new_path = executed_dir / file_path.name

    try:
        # Atomic move
        file_path.rename(new_path)
        logger.info(f"Moved PRP: {file_path.name} → executed/")
        return new_path
    except Exception as e:
        raise RuntimeError(
            f"Failed to move PRP to executed: {e}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Check permissions: ls -la {file_path}\n"
            f"   - Ensure target doesn't exist: ls {new_path}\n"
            f"   - Verify disk space: df -h"
        ) from e


def move_prp_to_archived(file_path: Path) -> Path:
    """Move PRP to archived/ directory.

    Args:
        file_path: Current path to PRP file

    Returns:
        New path in archived/ directory

    Raises:
        RuntimeError: If move fails
    """
    current_dir = Path.cwd()
    if current_dir.name == "tools":
        project_root = current_dir.parent
    else:
        project_root = current_dir
    archived_dir = project_root / "PRPs" / "archived"

    # Create archived directory if needed
    archived_dir.mkdir(parents=True, exist_ok=True)

    new_path = archived_dir / file_path.name

    try:
        file_path.rename(new_path)
        logger.info(f"Archived PRP: {file_path.name} → archived/")
        return new_path
    except Exception as e:
        raise RuntimeError(
            f"Failed to archive PRP: {e}\n"
            f"🔧 Troubleshooting: Check permissions and disk space"
        ) from e


def detect_archived_prps() -> List[Path]:
    """Identify superseded/deprecated PRPs for archival.

    Looks for:
    - status == "archived" in YAML
    - "superseded_by" field in metadata

    Returns:
        List of PRP paths that should be archived
    """
    archived_candidates = []
    all_prps = discover_prps()

    for prp_path in all_prps:
        # Skip if already in archived/
        if "archived" in str(prp_path):
            continue

        try:
            metadata, _ = read_prp_header(prp_path)

            # Check status
            if metadata.get("status") == "archived":
                archived_candidates.append(prp_path)
                continue

            # Check superseded_by field
            if "superseded_by" in metadata:
                archived_candidates.append(prp_path)

        except Exception as e:
            logger.warning(f"Skipping {prp_path.name} - invalid YAML: {e}")
            continue

    return archived_candidates


def load_pattern_checks() -> Dict[str, List[Tuple[str, str, str]]]:
    """Load pattern checks from PATTERN_CHECKS.

    Returns:
        {
            "error_handling": [
                ("bare_except", "regex", "fix description"),
                ...
            ]
        }
    """
    return PATTERN_CHECKS


def verify_codebase_matches_examples() -> Dict[str, Any]:
    """Check if codebase follows patterns documented in examples/.

    Returns:
        {
            "violations": [
                "File tools/ce/foo.py uses bare except (violates examples/patterns/error-handling.py)",
                ...
            ],
            "drift_score": 15.3  # Percentage of files violating patterns
        }

    Refactored to reduce nesting depth from 5 to 4 levels.
    """
    from .pattern_detectors import check_file_for_violations

    current_dir = Path.cwd()
    if current_dir.name == "tools":
        project_root = current_dir.parent
    else:
        project_root = current_dir
    examples_dir = project_root / "examples"

    # Skip if examples/ doesn't exist
    if not examples_dir.exists():
        logger.info("examples/ directory not found - skipping drift detection")
        return {"violations": [], "drift_score": 0.0}

    violations = []
    pattern_checks = load_pattern_checks()

    # Scan tools/ce/ for violations
    tools_ce_dir = project_root / "tools" / "ce"
    if not tools_ce_dir.exists():
        return {"violations": [], "drift_score": 0.0}

    python_files = list(tools_ce_dir.glob("*.py"))
    files_with_violations = set()

    # Process each file (delegated to reduce nesting)
    for py_file in python_files:
        file_violations, has_violations = check_file_for_violations(
            py_file, pattern_checks, project_root
        )
        violations.extend(file_violations)
        if has_violations:
            files_with_violations.add(py_file)

    # Calculate drift score
    drift_score = 0.0
    if python_files:
        drift_score = (len(files_with_violations) / len(python_files)) * 100

    return {
        "violations": violations,
        "drift_score": drift_score
    }


def detect_missing_examples_for_prps() -> List[Dict[str, Any]]:
    """Detect executed PRPs missing corresponding examples/ documentation.

    Returns:
        [
            {
                "prp_id": "PRP-13",
                "feature_name": "Production Hardening",
                "complexity": "high",
                "missing_example": "error_recovery",
                "suggested_path": "examples/patterns/error-recovery.py",
                "rationale": "Complex error recovery logic should be documented"
            },
            ...
        ]

    Refactored to reduce nesting depth from 5 to 4 levels.
    """
    from .pattern_detectors import check_prp_for_missing_examples

    current_dir = Path.cwd()
    if current_dir.name == "tools":
        project_root = current_dir.parent
    else:
        project_root = current_dir
    examples_dir = project_root / "examples"
    missing_examples = []

    # Define keyword patterns
    keywords_to_examples = {
        "error recovery": ("error_recovery", "examples/patterns/error-recovery.py",
                           "Complex error recovery logic should be documented"),
        "strategy pattern": ("strategy_pattern_testing", "examples/patterns/strategy-testing.py",
                             "Strategy pattern with mocks is reusable pattern"),
        "pipeline": ("pipeline_testing", "examples/patterns/pipeline-testing.py",
                     "Pipeline orchestration pattern should be documented")
    }

    # Get all executed PRPs
    executed_prps = (project_root / "PRPs" / "executed").glob("*.md")

    # Check each PRP (delegated to reduce nesting)
    for prp_path in executed_prps:
        prp_missing = check_prp_for_missing_examples(
            prp_path, project_root, keywords_to_examples
        )
        missing_examples.extend(prp_missing)

    return missing_examples


def generate_drift_report(violations: List[str], drift_score: float,
                          missing_examples: List[Dict[str, Any]]) -> str:
    """Generate formalized structured drift report with solution proposals.

    Args:
        violations: List of violation messages
        drift_score: Percentage of files violating patterns
        missing_examples: List of PRPs missing examples

    Returns:
        Markdown formatted drift report
    """
    now = datetime.now(timezone.utc).isoformat()

    # Classify drift score
    drift_level = "✅ OK" if drift_score < 5 else ("⚠️  WARNING" if drift_score < 15 else "🚨 CRITICAL")

    report = f"""## Context Drift Report - Examples/ Patterns

**Drift Score**: {drift_score:.1f}% ({drift_level})
**Generated**: {now}
**Violations Found**: {len(violations)}
**Missing Examples**: {len(missing_examples)}

### Part 1: Code Violating Documented Patterns

"""

    if violations:
        # Group violations by category
        error_handling_violations = [v for v in violations if "error_handling" in v or "bare_except" in v]
        naming_violations = [v for v in violations if "naming" in v or "version_suffix" in v]
        kiss_violations = [v for v in violations if "kiss" in v or "nesting" in v]

        if error_handling_violations:
            report += f"#### Error Handling ({len(error_handling_violations)} violations)\n\n"
            for i, v in enumerate(error_handling_violations, 1):
                report += f"{i}. {v}\n"
            report += "\n"

        if naming_violations:
            report += f"#### Naming Conventions ({len(naming_violations)} violations)\n\n"
            for i, v in enumerate(naming_violations, 1):
                report += f"{i}. {v}\n"
            report += "\n"

        if kiss_violations:
            report += f"#### KISS Violations ({len(kiss_violations)} violations)\n\n"
            for i, v in enumerate(kiss_violations, 1):
                report += f"{i}. {v}\n"
            report += "\n"
    else:
        report += "No violations detected - codebase follows documented patterns.\n\n"

    report += """### Part 2: Missing Pattern Documentation

**Critical PRPs Without Examples**:

"""

    if missing_examples:
        for i, missing in enumerate(missing_examples, 1):
            report += f"""{i}. **{missing['prp_id']}**: {missing['feature_name']}
   **Complexity**: {missing['complexity']}
   **Missing Example**: {missing['missing_example']}
   **Suggested Path**: {missing['suggested_path']}
   **Rationale**: {missing['rationale']}
   **Action**: Create example showing this pattern

"""
    else:
        report += "All critical PRPs have corresponding examples/ documentation.\n\n"

    report += """### Proposed Solutions Summary

1. **Code Violations** (manual review):
"""
    if violations:
        for v in violations[:3]:  # Show first 3
            report += f"   - Review and fix: {v}\n"
        if len(violations) > 3:
            report += f"   - Review {len(violations) - 3} other files listed in Part 1\n"
    else:
        report += "   - No violations to fix\n"

    report += """
2. **Missing Examples** (documentation needed):
"""
    if missing_examples:
        for missing in missing_examples[:3]:  # Show first 3
            report += f"   - Create {missing['suggested_path']} (from {missing['prp_id']})\n"
        if len(missing_examples) > 3:
            report += f"   - Create {len(missing_examples) - 3} other examples listed in Part 2\n"
    else:
        report += "   - No missing examples\n"

    report += """
3. **Prevention**:
   - Add pre-commit hook: ce validate --level 4 (pattern conformance)
   - Run /update-context weekly to detect drift early
   - Update CLAUDE.md when new patterns emerge

### Next Steps
1. Review violations in Part 1 and fix manually
2. Create missing examples from Part 2
3. Validate: ce validate --level 4
4. Update patterns if codebase evolution is intentional
5. Re-run /update-context to verify drift resolved
"""

    return report


def sync_context(target_prp: Optional[str] = None) -> Dict[str, Any]:
    """Execute context sync workflow.

    Args:
        target_prp: Optional PRP file path for targeted sync

    Returns:
        {
            "success": True,
            "prps_scanned": 15,
            "prps_updated": 8,
            "prps_moved": 2,
            "ce_updated_count": 8,
            "serena_updated_count": 5,
            "errors": []
        }
    """
    logger.info("Starting context sync...")

    # Initialize counters
    prps_scanned = 0
    prps_updated = 0
    prps_moved = 0
    ce_updated_count = 0
    serena_updated_count = 0
    errors = []

    # Discover PRPs
    try:
        prp_files = discover_prps(target_prp)
    except Exception as e:
        logger.error(f"Failed to discover PRPs: {e}")
        return {
            "success": False,
            "prps_scanned": 0,
            "prps_updated": 0,
            "prps_moved": 0,
            "ce_updated_count": 0,
            "serena_updated_count": 0,
            "errors": [str(e)]
        }

    # Process each PRP
    for prp_path in prp_files:
        prps_scanned += 1

        try:
            # Read PRP
            metadata, content = read_prp_header(prp_path)

            # Extract expected functions
            expected_functions = extract_expected_functions(content)

            # Verify with Serena
            serena_verified = verify_implementation_with_serena(expected_functions)

            # For now, mark CE as updated if functions found
            ce_verified = len(expected_functions) > 0

            # Update context_sync flags
            update_context_sync_flags(prp_path, ce_verified, serena_verified)
            prps_updated += 1

            if ce_verified:
                ce_updated_count += 1
            if serena_verified:
                serena_updated_count += 1

            # Check status transition
            if should_transition_to_executed(prp_path):
                new_path = move_prp_to_executed(prp_path)
                prps_moved += 1
                prp_path = new_path  # Update path for drift detection

        except Exception as e:
            error_msg = f"Error processing {prp_path.name}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            continue

    # Drift detection (universal sync only)
    if not target_prp:
        logger.info("Running drift detection...")
        drift_result = verify_codebase_matches_examples()
        missing_examples = detect_missing_examples_for_prps()

        if drift_result["violations"] or missing_examples:
            report = generate_drift_report(
                drift_result["violations"],
                drift_result["drift_score"],
                missing_examples
            )

            # Save report
            current_dir = Path.cwd()
            if current_dir.name == "tools":
                project_root = current_dir.parent
            else:
                project_root = current_dir
            ce_dir = project_root / ".ce"
            ce_dir.mkdir(exist_ok=True)
            report_path = ce_dir / "drift-report.md"
            report_path.write_text(report)

            logger.warning(
                f"Examples drift detected: {drift_result['drift_score']:.1f}%\n"
                f"📊 Report saved: {report_path}\n"
                f"🔧 Review and apply fixes: cat {report_path}"
            )

    logger.info("Context sync completed")

    return {
        "success": len(errors) == 0,
        "prps_scanned": prps_scanned,
        "prps_updated": prps_updated,
        "prps_moved": prps_moved,
        "ce_updated_count": ce_updated_count,
        "serena_updated_count": serena_updated_count,
        "errors": errors
    }
