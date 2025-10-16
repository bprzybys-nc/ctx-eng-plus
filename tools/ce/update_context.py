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


def transform_drift_to_initial(
    violations: List[str],
    drift_score: float,
    missing_examples: List[Dict[str, Any]]
) -> str:
    """Transform drift report → INITIAL.md blueprint format.

    Args:
        violations: List of violation messages with format:
                   "File {path} has {issue} (violates {pattern}): {fix}"
        drift_score: Percentage score (0-100)
        missing_examples: List of PRPs missing examples with metadata:
                         [{"prp_id": "PRP-10", "feature_name": "...",
                           "suggested_path": "...", "rationale": "..."}]

    Returns:
        INITIAL.md formatted string with:
        - Feature: Drift summary with breakdown
        - Context: Root causes and impact
        - Examples: Top 5 violations + up to 3 missing examples
        - Acceptance Criteria: Standard remediation checklist
        - Technical Notes: File count, effort estimate, complexity

    Raises:
        ValueError: If violations empty and missing_examples empty
                   If drift_score invalid (not 0-100)

    Edge Cases:
        - Empty violations + empty missing: Raises ValueError
        - drift_score outside 0-100: Raises ValueError
        - More than 5 violations: Shows top 5 only
        - More than 3 missing examples: Shows top 3 only
        - No file paths extractable: files_affected = 0

    Example:
        >>> violations = ["File tools/ce/foo.py has bare_except: Use specific"]
        >>> missing = [{"prp_id": "PRP-10", "suggested_path": "ex.py",
        ...            "feature_name": "Feature", "rationale": "Important"}]
        >>> result = transform_drift_to_initial(violations, 12.5, missing)
        >>> assert "# Drift Remediation" in result
        >>> assert "12.5%" in result
        >>> assert "PRP-10" in result
    """
    # Validation
    if not violations and not missing_examples:
        raise ValueError(
            "Cannot generate INITIAL.md: no violations and no missing examples\n"
            "🔧 Troubleshooting: Drift detection returned empty results"
        )

    if not (0 <= drift_score <= 100):
        raise ValueError(
            f"Invalid drift_score: {drift_score} (must be 0-100)\n"
            "🔧 Troubleshooting: Check drift calculation returns percentage"
        )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Count violations by category (extract pattern from violation string)
    # Pattern format: "(violates examples/patterns/{category}.py)"
    error_handling = len([v for v in violations if "error-handling.py" in v or "error_handling.py" in v])
    naming = len([v for v in violations if "naming.py" in v])
    kiss = len([v for v in violations if "kiss.py" in v or "nesting" in v.lower()])

    # Categorize drift level
    if drift_score < 5:
        drift_level = "✅ OK"
    elif drift_score < 15:
        drift_level = "⚠️ WARNING"
    else:
        drift_level = "🚨 CRITICAL"

    # Calculate effort estimate (15 min per violation + 30 min per missing example)
    effort_hours = (len(violations) * 0.25) + (len(missing_examples) * 0.5)
    effort_hours = max(1, round(effort_hours))  # Minimum 1 hour

    # Calculate complexity
    total_items = len(violations) + len(missing_examples)
    if total_items < 5:
        complexity = "LOW"
    elif total_items < 15:
        complexity = "MEDIUM"
    else:
        complexity = "HIGH"

    # Extract unique file paths for count
    # Expected format: "File {path} has {issue} (violates {pattern}): {fix}"
    files_affected = set()
    for v in violations:
        if "File " in v and " has " in v:
            # Extract file path: "File tools/ce/foo.py has ..."
            try:
                file_part = v.split(" has ")[0].replace("File ", "").strip()
                if file_part:  # Only add non-empty paths
                    files_affected.add(file_part)
            except (IndexError, AttributeError):
                # Malformed violation string, skip gracefully
                continue

    # Build INITIAL.md content
    initial = f"""# Drift Remediation - {now}

## Feature

Address {len(violations)} drift violations detected in codebase scan on {now}.

**Drift Score**: {drift_score:.1f}% ({drift_level})

**Violations Breakdown**:
- Error Handling: {error_handling}
- Naming Conventions: {naming}
- KISS Violations: {kiss}
- Missing Examples: {len(missing_examples)}

## Context

Context Engineering drift detection found violations between documented patterns (CLAUDE.md, examples/) and actual implementation.

**Root Causes**:
1. New code written without pattern awareness
2. Missing examples for critical PRPs
3. Pattern evolution without documentation updates

**Impact**:
- Code quality inconsistency
- Reduced onboarding effectiveness
- Pattern erosion over time

## Examples

"""

    # Add top 5 violations
    for i, violation in enumerate(violations[:5], 1):
        initial += f"### Violation {i}\n\n"
        initial += f"{violation}\n\n"

    # Add missing examples (up to 3)
    if missing_examples:
        initial += "### Missing Examples\n\n"
        for missing in missing_examples[:3]:
            initial += f"**{missing['prp_id']}**: {missing['feature_name']}\n"
            initial += f"- **Missing**: `{missing['suggested_path']}`\n"
            initial += f"- **Rationale**: {missing['rationale']}\n\n"

    # Add Acceptance Criteria
    initial += """## Acceptance Criteria

- [ ] All HIGH priority violations resolved
- [ ] Missing examples created for critical PRPs
- [ ] L4 validation passes (ce validate --level 4)
- [ ] Drift score < 5% after remediation
- [ ] Pattern documentation updated if intentional drift

"""

    # Add Technical Notes with high-level summary
    initial += f"""## Technical Notes

**Files Affected**: {len(files_affected)}
**Estimated Effort**: {effort_hours}h based on violation count
**Complexity**: {complexity}
**Total Items**: {len(violations)} violations + {len(missing_examples)} missing examples

**Priority Focus**:
- Address HIGH priority violations first
- Create missing examples for critical PRPs
- Run L4 validation after each fix
"""

    return initial


def detect_drift_violations() -> Dict[str, Any]:
    """Run drift detection and return structured results.

    Returns:
        {
            "drift_score": 12.5,
            "violations": ["file.py:42 - Error", ...],
            "missing_examples": [{"prp_id": "PRP-10", ...}],
            "has_drift": True
        }

    Raises:
        RuntimeError: If detection fails with troubleshooting guidance

    Example:
        >>> result = detect_drift_violations()
        >>> assert "drift_score" in result
        >>> assert isinstance(result["violations"], list)
    """
    logger.info("Running drift detection...")
    try:
        # Call existing detection functions
        drift_result = verify_codebase_matches_examples()
        missing_examples = detect_missing_examples_for_prps()

        drift_score = drift_result["drift_score"]
        violations = drift_result["violations"]
        has_drift = drift_score >= 5 or len(missing_examples) > 0

        return {
            "drift_score": drift_score,
            "violations": violations,
            "missing_examples": missing_examples,
            "has_drift": has_drift
        }
    except Exception as e:
        raise RuntimeError(
            f"Drift detection failed: {e}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Ensure examples/ directory exists\n"
            f"   - Check PRPs have valid YAML headers\n"
            f"   - Verify tools/ce/ directory is accessible\n"
            f"   - Run: cd tools && uv run ce validate --level 1"
        ) from e


def generate_drift_blueprint(drift_result: Dict, missing_examples: List) -> Path:
    """Generate DEDRIFT-INITIAL.md blueprint in tmp/ce/.

    Args:
        drift_result: Detection results from detect_drift_violations()
        missing_examples: List of PRPs missing examples

    Returns:
        Path to generated blueprint file

    Raises:
        RuntimeError: If blueprint generation fails

    Example:
        >>> drift = detect_drift_violations()
        >>> missing = drift["missing_examples"]
        >>> path = generate_drift_blueprint(drift, missing)
        >>> assert path.exists()
        >>> assert "DEDRIFT-INITIAL.md" in path.name
    """
    logger.info("Generating remediation blueprint...")
    try:
        # Use PRP-15.1 transform function
        blueprint = transform_drift_to_initial(
            drift_result["violations"],
            drift_result["drift_score"],
            missing_examples
        )

        # Determine project root
        current_dir = Path.cwd()
        if current_dir.name == "tools":
            project_root = current_dir.parent
        else:
            project_root = current_dir

        # Create tmp/ce/ directory
        tmp_ce_dir = project_root / "tmp" / "ce"
        tmp_ce_dir.mkdir(parents=True, exist_ok=True)

        # Write blueprint
        blueprint_path = tmp_ce_dir / "DEDRIFT-INITIAL.md"
        blueprint_path.write_text(blueprint)

        logger.info(f"Blueprint generated: {blueprint_path}")
        return blueprint_path

    except Exception as e:
        raise RuntimeError(
            f"Blueprint generation failed: {e}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Check tmp/ce/ directory permissions\n"
            f"   - Verify transform_drift_to_initial() is available (PRP-15.1)\n"
            f"   - Check disk space: df -h\n"
            f"   - Run: ls -la tmp/"
        ) from e


def display_drift_summary(drift_score: float, violations: List[str],
                          missing_examples: List[Dict], blueprint_path: Path):
    """Display drift summary with direct output (no box-drawing).

    Args:
        drift_score: Percentage score (0-100)
        violations: List of violation messages
        missing_examples: List of PRPs missing examples
        blueprint_path: Path to generated blueprint

    Example:
        >>> display_drift_summary(12.5, violations, missing, path)
        # Prints direct output with Unicode separators
    """
    print("\n" + "━" * 60)
    print("📊 Drift Summary")
    print("━" * 60)

    # Drift level indicator
    level = "⚠️ WARNING" if drift_score < 15 else "🚨 CRITICAL"
    print(f"Drift Score: {drift_score:.1f}% ({level})")
    print(f"Total Violations: {len(violations) + len(missing_examples)}")
    print()

    # Breakdown by category
    # Pattern format: "(violates examples/patterns/{category}.py)"
    print("Breakdown:")
    if violations:
        # Categorize violations using pattern file detection (consistent with PRP-15.1)
        error_count = len([v for v in violations if "error-handling.py" in v or "error_handling.py" in v])
        naming_count = len([v for v in violations if "naming.py" in v])
        kiss_count = len([v for v in violations if "kiss.py" in v or "nesting" in v.lower()])

        if error_count > 0:
            print(f"  • Error Handling: {error_count} violation{'s' if error_count != 1 else ''}")
        if naming_count > 0:
            print(f"  • Naming Conventions: {naming_count} violation{'s' if naming_count != 1 else ''}")
        if kiss_count > 0:
            print(f"  • KISS Violations: {kiss_count} violation{'s' if kiss_count != 1 else ''}")

    if missing_examples:
        print(f"  • Missing Examples: {len(missing_examples)} PRP{'s' if len(missing_examples) != 1 else ''}")

    print()
    print(f"Blueprint: {blueprint_path}")
    print("━" * 60)
    print()


def generate_prp_yaml_header(violation_count: int, missing_count: int, timestamp: str) -> str:
    """Generate YAML header for DEDRIFT maintenance PRP.

    Args:
        violation_count: Number of code violations
        missing_count: Number of missing examples
        timestamp: Formatted timestamp for PRP ID (e.g., "20251015-120530")

    Returns:
        YAML header string with metadata

    Example:
        >>> header = generate_prp_yaml_header(5, 2, "20251015-120530")
        >>> assert "prp_id:" in header
        >>> assert "DEDRIFT-20251015-120530" in header
        >>> assert "effort_hours:" in header
    """
    total_items = violation_count + missing_count

    # Effort estimation: 15 min per violation + 30 min per missing example
    # NOTE: Same formula as PRP-15.1 transform function for consistency
    effort_hours = (violation_count * 0.25) + (missing_count * 0.5)
    effort_hours = max(1, round(effort_hours))  # Minimum 1 hour

    # Risk assessment based on item count
    if total_items < 5:
        risk = "LOW"
    elif total_items < 10:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    now = datetime.now().isoformat()

    return f"""---
name: "Drift Remediation - {timestamp}"
description: "Address drift violations detected in codebase scan"
prp_id: "DEDRIFT-{timestamp}"
status: "new"
created_date: "{now}Z"
last_updated: "{now}Z"
updated_by: "drift-remediation-workflow"
context_sync:
  ce_updated: false
  serena_updated: false
version: 1
priority: "MEDIUM"
effort_hours: {effort_hours}
risk: "{risk}"
---

"""


# ======================================================================
# PRP-15.3: Drift Remediation Workflow Automation
# ======================================================================

def generate_maintenance_prp(blueprint_path: Path) -> Path:
    """Generate complete maintenance PRP file from blueprint.

    Args:
        blueprint_path: Path to DEDRIFT-INITIAL.md blueprint

    Returns:
        Path to generated PRP file in PRPs/system/

    Raises:
        RuntimeError: If PRP generation fails

    Example:
        >>> blueprint = Path("tmp/ce/DEDRIFT-INITIAL.md")
        >>> prp = generate_maintenance_prp(blueprint)
        >>> assert prp.exists()
        >>> assert "DEDRIFT_PRP-" in prp.name
    """
    logger.info("Generating maintenance PRP file...")
    try:
        # Read blueprint content
        blueprint_content = blueprint_path.read_text()

        # Extract metadata from blueprint for YAML header
        # Count violations and missing examples from content
        violation_count = blueprint_content.count("### Violation")
        missing_count = blueprint_content.count("**Missing**:")

        # Generate timestamp for PRP ID
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Generate YAML header (PRP-15.2 function)
        yaml_header = generate_prp_yaml_header(violation_count, missing_count, timestamp)

        # Combine YAML + blueprint content
        prp_content = yaml_header + blueprint_content

        # Determine project root and create PRPs/system/ directory
        current_dir = Path.cwd()
        if current_dir.name == "tools":
            project_root = current_dir.parent
        else:
            project_root = current_dir

        prp_system_dir = project_root / "PRPs" / "system"
        prp_system_dir.mkdir(parents=True, exist_ok=True)

        # Write PRP file
        prp_path = prp_system_dir / f"DEDRIFT_PRP-{timestamp}.md"
        prp_path.write_text(prp_content)

        logger.info(f"Maintenance PRP generated: {prp_path}")
        return prp_path

    except Exception as e:
        raise RuntimeError(
            f"PRP generation failed: {e}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Check PRPs/system/ directory permissions\n"
            f"   - Verify blueprint file exists: {blueprint_path}\n"
            f"   - Check disk space: df -h"
        ) from e


def remediate_drift_workflow(yolo_mode: bool = False) -> Dict[str, Any]:
    """Execute drift remediation workflow.

    Args:
        yolo_mode: If True, skip approval gate (--remediate flag)

    Returns:
        {
            "success": bool,
            "prp_path": Optional[Path],
            "blueprint_path": Optional[Path],
            "errors": List[str]
        }

    Workflow:
        1. Detect drift violations (PRP-15.2)
        2. Transform to INITIAL.md format (PRP-15.1)
        3. Generate blueprint file (PRP-15.2)
        4. Display drift summary (PRP-15.2)
        5. Ask approval (vanilla) OR skip approval (YOLO)
        6. Generate maintenance PRP (PRP-15.3)
        7. Display /execute-prp command for manual execution

    Raises:
        None - all errors captured in errors list

    Example (Vanilla Mode):
        >>> result = remediate_drift_workflow(yolo_mode=False)
        # Prompts: "Proceed with remediation? (yes/no):"
        # If yes: Generates PRP, displays command
        # If no: Workflow stops, blueprint saved

    Example (YOLO Mode):
        >>> result = remediate_drift_workflow(yolo_mode=True)
        # Skips approval prompt
        # Auto-generates PRP, displays command
    """
    mode_label = "YOLO mode (no approval)" if yolo_mode else "Interactive mode"
    logger.info(f"Starting drift remediation workflow ({mode_label})...")
    errors = []

    # Step 1: Detect drift (PRP-15.2 function)
    try:
        drift = detect_drift_violations()
    except RuntimeError as e:
        return {
            "success": False,
            "prp_path": None,
            "blueprint_path": None,
            "errors": [str(e)]
        }

    # Early exit if no drift
    if not drift["has_drift"]:
        print(f"\n✅ No drift detected (score: {drift['drift_score']:.1f}%)")
        print("Context is healthy - no remediation needed.\n")
        return {
            "success": True,
            "prp_path": None,
            "blueprint_path": None,
            "errors": []
        }

    # Step 2: Generate blueprint (PRP-15.2 function)
    try:
        blueprint_path = generate_drift_blueprint(drift, drift["missing_examples"])
    except RuntimeError as e:
        return {
            "success": False,
            "prp_path": None,
            "blueprint_path": None,
            "errors": [str(e)]
        }

    # Step 3: Display summary (PRP-15.2 function)
    display_drift_summary(
        drift["drift_score"],
        drift["violations"],
        drift["missing_examples"],
        blueprint_path
    )

    # Step 4: Approval gate (vanilla only)
    if not yolo_mode:
        print(f"\nReview INITIAL.md: {blueprint_path}")
        approval = input("Proceed with remediation? (yes/no): ").strip().lower()

        if approval not in ["yes", "y"]:
            print("⚠️ Remediation skipped by user")
            print(f"Blueprint saved: {blueprint_path}\n")
            return {
                "success": True,
                "prp_path": None,
                "blueprint_path": blueprint_path,
                "errors": []
            }

        logger.info("User approved remediation - proceeding...")

    # Step 5: Generate maintenance PRP (PRP-15.3 function)
    logger.info("Generating maintenance PRP...")
    try:
        prp_path = generate_maintenance_prp(blueprint_path)
    except Exception as e:
        errors.append(f"PRP generation failed: {e}")
        return {
            "success": False,
            "prp_path": None,
            "blueprint_path": blueprint_path,
            "errors": errors
        }

    # Step 6: Display next step (manual execution)
    logger.info("PRP ready for execution...")

    print("\n" + "━" * 60)
    print("🔧 Next Step: Execute PRP")
    print("━" * 60)
    print(f"Run: /execute-prp {prp_path}")
    print("━" * 60)
    print()

    # Workflow complete - PRP ready for manual execution
    print(f"✅ PRP Generated: {prp_path}")
    print(f"📄 Blueprint: {blueprint_path}\n")

    return {
        "success": True,
        "prp_path": prp_path,
        "blueprint_path": blueprint_path,
        "errors": []
    }


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

    Raises:
        None - gracefully degrades if Serena unavailable

    Example:
        >>> funcs = ["generate_maintenance_prp", "remediate_drift_workflow"]
        >>> result = verify_implementation_with_serena(funcs)
        >>> assert isinstance(result, bool)
    """
    if not expected_functions:
        # No functions to verify - mark as updated
        logger.debug("No implementations to verify")
        return True

    try:
        # Import Serena MCP module directly
        import mcp__serena as serena

        verified_count = 0
        missing = []

        for func_name in expected_functions:
            try:
                # Query Serena for symbol
                # Note: Serena MCP returns list directly
                # Based on actual usage in this codebase
                result = serena.find_symbol(
                    name_path=func_name,
                    relative_path="tools/ce/",  # Search in ce module
                    include_body=False
                )

                # Check if implementation found
                # Result structure: list of symbol dicts
                if result and isinstance(result, list) and len(result) > 0:
                    verified_count += 1
                    logger.debug(f"✓ Verified: {func_name}")
                else:
                    missing.append(func_name)
                    logger.warning(f"✗ Missing: {func_name}")

            except Exception as e:
                # Symbol query failed, mark as missing
                logger.debug(f"Symbol query failed for {func_name}: {e}")
                missing.append(func_name)
                continue

        # Mark as verified only if ALL functions found
        all_verified = len(missing) == 0

        if all_verified:
            logger.info(f"Serena verification complete: {verified_count}/{len(expected_functions)} implementations found")
        else:
            logger.warning(
                f"Serena verification incomplete: {verified_count}/{len(expected_functions)} found\n"
                f"Missing: {', '.join(missing)}"
            )

        return all_verified

    except (ImportError, ModuleNotFoundError):
        # Serena MCP not available - graceful degradation
        logger.warning(
            "Serena MCP not available - skipping verification\n"
            "🔧 Troubleshooting: Ensure Serena MCP server is configured and running"
        )
        return False
    except Exception as e:
        # Unexpected error - log and degrade gracefully
        logger.error(
            f"Serena verification failed: {e}\n"
            "🔧 Troubleshooting: Check Serena MCP connection and logs"
        )
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
3. **🔧 CRITICAL - Validate Each Fix**:
   - After fixing each violation, run: ce update-context
   - Verify violation removed from drift report
   - If still present: Analyze why fix didn't work, try different approach
4. Validate: ce validate --level 4
5. Update patterns if codebase evolution is intentional
6. Re-run /update-context to verify drift resolved

**Anti-Pattern**: Batch-apply all fixes without validation (violations may persist)
**Correct Pattern**: Fix → Validate → Next fix (iterative verification)
"""

    return report


def get_cache_ttl(cli_ttl: Optional[int] = None) -> int:
    """Get cache TTL from CLI arg, config, or default.

    Priority:
        1. CLI flag (--cache-ttl)
        2. .ce/config.yml value
        3. Hardcoded default (5 minutes)

    Args:
        cli_ttl: TTL from command-line --cache-ttl flag

    Returns:
        TTL in minutes

    Example:
        >>> ttl = get_cache_ttl()
        >>> assert ttl >= 1
        >>> ttl = get_cache_ttl(cli_ttl=10)
        >>> assert ttl == 10
    """
    # Priority 1: CLI flag
    if cli_ttl is not None:
        return cli_ttl

    # Priority 2: Config file
    current_dir = Path.cwd()
    if current_dir.name == "tools":
        project_root = current_dir.parent
    else:
        project_root = current_dir

    config_path = project_root / ".ce" / "config.yml"
    if config_path.exists():
        try:
            import yaml
            config = yaml.safe_load(config_path.read_text())
            ttl = config.get("cache", {}).get("analysis_ttl_minutes")
            if ttl is not None:
                return int(ttl)
        except Exception:
            pass  # Fall back to default

    # Priority 3: Default
    return 5


def get_cached_analysis() -> Optional[Dict[str, Any]]:
    """Read cached drift analysis from report file.

    Parses .ce/drift-report.md to extract cached analysis results.

    Returns:
        Cached analysis dict or None if not found

    Example:
        >>> cached = get_cached_analysis()
        >>> if cached:
        ...     assert "drift_score" in cached
        ...     assert "generated_at" in cached
    """
    current_dir = Path.cwd()
    if current_dir.name == "tools":
        project_root = current_dir.parent
    else:
        project_root = current_dir

    report_path = project_root / ".ce" / "drift-report.md"
    if not report_path.exists():
        return None

    try:
        content = report_path.read_text()

        # Extract timestamp from report
        # Format: **Generated**: 2025-10-16T20:03:32.185604+00:00
        timestamp_match = re.search(
            r'\*\*Generated\*\*: (.+?)$',
            content,
            re.MULTILINE
        )
        if not timestamp_match:
            return None

        generated_at = timestamp_match.group(1).strip()

        # Extract drift score
        score_match = re.search(r'\*\*Drift Score\*\*: ([\d.]+)%', content)
        if not score_match:
            return None

        drift_score = float(score_match.group(1))

        # Extract violation count
        violations_match = re.search(r'\*\*Violations Found\*\*: (\d+)', content)
        violation_count = int(violations_match.group(1)) if violations_match else 0

        # Classify drift level
        if drift_score < 5:
            drift_level = "ok"
        elif drift_score < 15:
            drift_level = "warning"
        else:
            drift_level = "critical"

        return {
            "drift_score": drift_score,
            "drift_level": drift_level,
            "violation_count": violation_count,
            "report_path": str(report_path),
            "generated_at": generated_at,
            "cached": True
        }

    except Exception as e:
        logger.debug(f"Failed to read cache: {e}")
        return None


def is_cache_valid(cached: Dict[str, Any], ttl_minutes: int = 5) -> bool:
    """Check if cached analysis is still valid.

    Args:
        cached: Cached analysis dict with 'generated_at' field
        ttl_minutes: Cache time-to-live in minutes

    Returns:
        True if cache is fresh (< TTL), False otherwise

    Example:
        >>> cached = {"generated_at": "2025-10-17T10:00:00+00:00"}
        >>> is_valid = is_cache_valid(cached, ttl_minutes=5)
        >>> assert isinstance(is_valid, bool)
    """
    try:
        # Parse timestamp (handle multiple formats)
        generated_str = cached["generated_at"]

        # Replace timezone suffix for consistent parsing
        generated_str = generated_str.replace("+00:00", "+00:00")

        generated_at = datetime.fromisoformat(generated_str)

        # Ensure timezone aware
        if generated_at.tzinfo is None:
            generated_at = generated_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        age_minutes = (now - generated_at).total_seconds() / 60

        return age_minutes < ttl_minutes

    except Exception:
        return False


def analyze_context_drift() -> Dict[str, Any]:
    """Run drift analysis and generate report.

    Fast drift detection without metadata updates - optimized for CI/CD.

    Returns:
        {
            "drift_score": 17.9,
            "drift_level": "critical",  # ok, warning, critical
            "violations": ["..."],
            "violation_count": 5,
            "missing_examples": [...],
            "report_path": ".ce/drift-report.md",
            "generated_at": "2025-10-16T20:15:00Z",
            "duration_seconds": 2.3
        }

    Raises:
        RuntimeError: If analysis fails with troubleshooting guidance

    Example:
        >>> result = analyze_context_drift()
        >>> assert result["drift_level"] in ["ok", "warning", "critical"]
        >>> assert 0 <= result["drift_score"] <= 100
    """
    import time
    start_time = time.time()

    try:
        # Run drift detection (existing functions)
        drift_result = verify_codebase_matches_examples()
        missing_examples = detect_missing_examples_for_prps()

        # Generate report
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

        # Calculate duration
        duration = time.time() - start_time

        # Classify drift level
        drift_score = drift_result["drift_score"]
        if drift_score < 5:
            drift_level = "ok"
        elif drift_score < 15:
            drift_level = "warning"
        else:
            drift_level = "critical"

        return {
            "drift_score": drift_score,
            "drift_level": drift_level,
            "violations": drift_result["violations"],
            "violation_count": len(drift_result["violations"]),
            "missing_examples": missing_examples,
            "report_path": str(report_path),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(duration, 1)
        }

    except Exception as e:
        raise RuntimeError(
            f"Drift analysis failed: {e}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Ensure examples/ directory exists\n"
            f"   - Check PRPs have valid YAML headers\n"
            f"   - Verify tools/ce/ directory is accessible\n"
            f"   - Run: cd tools && uv run ce validate --level 1"
        ) from e


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
