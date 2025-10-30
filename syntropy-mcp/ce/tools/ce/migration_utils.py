"""Configuration migration utilities.

Migrates from old linear-defaults.yml to new config.yml profile section.
"""

from pathlib import Path
from typing import Dict, Any
import yaml
import shutil


def migrate_linear_defaults_to_config() -> Dict[str, Any]:
    """Migrate linear-defaults.yml content into config.yml profile section.

    Returns:
        Dict with migration status and actions taken

    Raises:
        FileNotFoundError: If config.yml template not found
        RuntimeError: If migration fails
    """
    # Find project root (go up from tools/)
    project_root = Path(__file__).parent.parent.parent
    old_linear_path = project_root / ".ce" / "linear-defaults.yml"
    old_serena_path = project_root / ".serena" / "project.yml"
    new_config_path = project_root / ".ce" / "config.yml"
    linear_backup_path = project_root / ".ce" / "linear-defaults.yml.backup"

    result = {
        "success": False,
        "actions": [],
        "warnings": []
    }

    # Check if old configs exist
    has_linear = old_linear_path.exists()
    has_serena = old_serena_path.exists()

    if not has_linear and not has_serena:
        result["warnings"].append(
            "No legacy config files found (linear-defaults.yml, .serena/project.yml)"
        )
        result["success"] = True  # Not an error - might already be migrated
        return result

    # Check if new config exists
    if not new_config_path.exists():
        raise FileNotFoundError(
            f"Config template not found: {new_config_path}\n"
            "🔧 Troubleshooting: Run init-project to create .ce/config.yml"
        )

    try:
        # Read current config.yml
        with open(new_config_path) as f:
            current_config = yaml.safe_load(f)

        # Ensure profile section exists
        if "profile" not in current_config:
            current_config["profile"] = {}

        # Migrate Linear config if exists
        if has_linear:
            with open(old_linear_path) as f:
                linear_config = yaml.safe_load(f)

            result["actions"].append(f"Read Linear config from {old_linear_path}")

            current_config["profile"]["linear"] = {
                "project": linear_config.get("project", "<missing>"),
                "assignee": linear_config.get("assignee", "<missing>"),
                "team": linear_config.get("team", "<missing>"),
                "default_labels": linear_config.get("default_labels", ["feature"])
            }

            result["actions"].append("Migrated Linear config to profile.linear")

        # Migrate project_name from Serena config if exists
        if has_serena:
            with open(old_serena_path) as f:
                serena_config = yaml.safe_load(f)

            result["actions"].append(f"Read Serena config from {old_serena_path}")

            project_name = serena_config.get("project_name", "<missing>")
            if project_name and project_name != "<missing>":
                current_config["profile"]["project_name"] = project_name
                result["actions"].append(f"Migrated project_name: {project_name}")

        # Backup old Linear file BEFORE modifying config.yml (safety)
        if has_linear:
            shutil.copy2(old_linear_path, linear_backup_path)
            result["actions"].append(f"Backed up to {linear_backup_path}")

        # Write updated config.yml
        with open(new_config_path, 'w') as f:
            yaml.safe_dump(current_config, f, default_flow_style=False, sort_keys=False)

        result["actions"].append(f"Updated {new_config_path}")

        # Delete old Linear file after successful migration
        if has_linear:
            old_linear_path.unlink()
            result["actions"].append(f"Removed {old_linear_path}")

        # Note: Keep .serena/project.yml for Serena MCP compatibility
        if has_serena:
            result["warnings"].append(
                "Kept .serena/project.yml for Serena MCP (config.yml takes precedence)"
            )

        result["success"] = True
        result["warnings"].append(
            "Migration complete. Review config.yml and test commands."
        )

    except Exception as e:
        raise RuntimeError(
            f"Migration failed: {e}\n"
            "🔧 Troubleshooting:\n"
            "   1. Check YAML syntax in both files\n"
            "   2. Ensure you have write permissions\n"
            "   3. Restore from .backup if needed"
        ) from e

    return result


def print_migration_report(result: Dict[str, Any]) -> None:
    """Print human-readable migration report.

    Args:
        result: Migration result dict from migrate_linear_defaults_to_config()
    """
    if result["success"]:
        print("✅ Migration Successful\n")
    else:
        print("❌ Migration Failed\n")

    if result["actions"]:
        print("Actions Taken:")
        for action in result["actions"]:
            print(f"  • {action}")
        print()

    if result["warnings"]:
        print("Warnings:")
        for warning in result["warnings"]:
            print(f"  ⚠️  {warning}")
        print()

    if result["success"]:
        print("Next Steps:")
        print("  1. Review .ce/config.yml profile section")
        print("  2. Verify Linear config is correct")
        print("  3. Test commands: ce git status, ce validate --level all")
