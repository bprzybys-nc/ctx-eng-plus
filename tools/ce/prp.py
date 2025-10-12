"""PRP YAML validation module."""
from typing import Dict, Any, List, Optional
import yaml
import re
from pathlib import Path

# Required fields schema
REQUIRED_FIELDS = [
    "name", "description", "prp_id", "status", "priority",
    "confidence", "effort_hours", "risk", "dependencies",
    "parent_prp", "context_memories", "meeting_evidence",
    "context_sync", "version", "created_date", "last_updated"
]

# Valid enum values
VALID_STATUS = ["ready", "in_progress", "executed", "validated", "archived"]
VALID_PRIORITY = ["HIGH", "MEDIUM", "LOW"]
VALID_RISK = ["LOW", "MEDIUM", "HIGH"]


def validate_prp_yaml(file_path: str) -> Dict[str, Any]:
    """Validate PRP YAML header against schema.

    Args:
        file_path: Path to PRP markdown file

    Returns:
        Dict with: success (bool), errors (list), warnings (list), header (dict)

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parse fails
    """
    errors = []
    warnings = []

    # Check file exists
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"PRP file not found: {file_path}\n"
            f"🔧 Troubleshooting: Verify file path is correct"
        )

    # Read file
    content = path.read_text()

    # Check YAML delimiters
    if not content.startswith("---\n"):
        errors.append("Missing YAML front matter: file must start with '---'")
        return {"success": False, "errors": errors, "warnings": warnings, "header": None}

    # Extract YAML header
    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append("Missing closing '---' delimiter for YAML header")
        return {"success": False, "errors": errors, "warnings": warnings, "header": None}

    yaml_content = parts[1].strip()

    # Parse YAML
    try:
        header = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        errors.append(f"YAML parse error: {str(e)}")
        return {"success": False, "errors": errors, "warnings": warnings, "header": None}

    # Validate schema
    return validate_schema(header, errors, warnings)


def validate_schema(header: Dict[str, Any], errors: List[str], warnings: List[str]) -> Dict[str, Any]:
    """Validate YAML header against schema."""

    # Check required fields
    missing_fields = [f for f in REQUIRED_FIELDS if f not in header]
    if missing_fields:
        errors.append(f"Missing required fields: {', '.join(missing_fields)}")

    # Validate PRP ID format
    if "prp_id" in header:
        error = validate_prp_id_format(header["prp_id"])
        if error:
            errors.append(error)

    # Validate date formats
    for date_field in ["created_date", "last_updated"]:
        if date_field in header:
            error = validate_date_format(header[date_field], date_field)
            if error:
                errors.append(error)

    # Validate status enum
    if "status" in header and header["status"] not in VALID_STATUS:
        errors.append(
            f"Invalid status: '{header['status']}' (must be one of: {', '.join(VALID_STATUS)})"
        )

    # Validate priority enum
    if "priority" in header and header["priority"] not in VALID_PRIORITY:
        errors.append(
            f"Invalid priority: '{header['priority']}' (must be one of: {', '.join(VALID_PRIORITY)})"
        )

    # Validate risk enum
    if "risk" in header and header["risk"] not in VALID_RISK:
        errors.append(
            f"Invalid risk: '{header['risk']}' (must be one of: {', '.join(VALID_RISK)})"
        )

    # Validate confidence format (X/10)
    if "confidence" in header:
        conf_str = str(header["confidence"])
        if not re.match(r'^\d{1,2}/10$', conf_str):
            errors.append(f"Invalid confidence format: '{conf_str}' (expected: X/10 where X is 1-10)")

    # Validate effort_hours is numeric
    if "effort_hours" in header:
        try:
            float(header["effort_hours"])
        except (ValueError, TypeError):
            errors.append(f"Invalid effort_hours: '{header['effort_hours']}' (must be numeric)")

    # Validate dependencies is list
    if "dependencies" in header and not isinstance(header["dependencies"], list):
        errors.append(f"Invalid dependencies: must be a list, got {type(header['dependencies']).__name__}")

    # Validate context_memories is list
    if "context_memories" in header and not isinstance(header["context_memories"], list):
        errors.append(f"Invalid context_memories: must be a list, got {type(header['context_memories']).__name__}")

    # Warnings for optional fields
    if not header.get("task_id"):
        warnings.append("Optional field 'task_id' is empty (consider linking to issue tracker)")

    success = len(errors) == 0
    return {
        "success": success,
        "errors": errors,
        "warnings": warnings,
        "header": header
    }


def validate_prp_id_format(prp_id: str) -> Optional[str]:
    """Validate PRP ID format (PRP-X.Y or PRP-X.Y.Z).

    Returns:
        Error message if invalid, None if valid
    """
    # Pattern: PRP-X.Y or PRP-X.Y.Z (no leading zeros)
    pattern = r'^PRP-([1-9]\d*)(\.(0|[1-9]\d*))?(\.(0|[1-9]\d*))?$'
    if not re.match(pattern, prp_id):
        return f"Invalid PRP ID format: '{prp_id}' (expected: PRP-X.Y or PRP-X.Y.Z, no leading zeros)"
    return None


def validate_date_format(date_str: str, field_name: str) -> Optional[str]:
    """Validate ISO 8601 date format.

    Returns:
        Error message if invalid, None if valid
    """
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    if not re.match(pattern, date_str):
        return f"Invalid date format for '{field_name}': '{date_str}' (expected: YYYY-MM-DDTHH:MM:SSZ)"
    return None


def format_validation_result(result: Dict[str, Any]) -> str:
    """Format validation result for human-readable output."""
    if result["success"]:
        output = "✅ YAML validation passed\n\n"
        output += f"PRP ID: {result['header']['prp_id']}\n"
        output += f"Name: {result['header']['name']}\n"
        output += f"Status: {result['header']['status']}\n"
        output += f"Effort: {result['header']['effort_hours']}h\n"

        if result["warnings"]:
            output += "\n⚠️  Warnings:\n"
            for warning in result["warnings"]:
                output += f"  - {warning}\n"
    else:
        output = "❌ YAML validation failed\n\n"
        output += "Errors:\n"
        for error in result["errors"]:
            output += f"  ❌ {error}\n"

        if result["warnings"]:
            output += "\nWarnings:\n"
            for warning in result["warnings"]:
                output += f"  ⚠️  {warning}\n"

        output += "\n🔧 Troubleshooting: Review docs/prp-yaml-schema.md for schema reference"

    return output
