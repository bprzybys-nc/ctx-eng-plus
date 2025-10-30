"""CI/CD Pipeline abstraction and validation.

Provides platform-agnostic pipeline definition and validation.
"""

from typing import Dict, Any, List
import yaml
import jsonschema


PIPELINE_SCHEMA = {
    "type": "object",
    "required": ["name", "stages"],
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "stages": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "nodes"],
                "properties": {
                    "name": {"type": "string"},
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name", "command"],
                            "properties": {
                                "name": {"type": "string"},
                                "command": {"type": "string"},
                                "strategy": {"type": "string", "enum": ["real", "mock"]},
                                "timeout": {"type": "integer"}
                            }
                        }
                    },
                    "parallel": {"type": "boolean"},
                    "depends_on": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    }
}


def load_abstract_pipeline(file_path: str) -> Dict[str, Any]:
    """Load abstract pipeline definition from YAML file.

    Args:
        file_path: Path to abstract pipeline YAML file

    Returns:
        Dict containing pipeline definition

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parse fails

    Note: No fishy fallbacks - let exceptions propagate for troubleshooting.
    """
    try:
        with open(file_path, 'r') as f:
            pipeline = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Pipeline file not found: {file_path}\n"
            f"🔧 Troubleshooting: Check the file path is correct"
        )
    except yaml.YAMLError as e:
        raise RuntimeError(
            f"Failed to parse pipeline YAML: {e}\n"
            f"🔧 Troubleshooting: Validate YAML syntax at the reported line"
        )

    return pipeline


def validate_pipeline(pipeline: Dict[str, Any]) -> Dict[str, Any]:
    """Validate pipeline against schema.

    Args:
        pipeline: Pipeline definition dict

    Returns:
        Dict with: success (bool), errors (List[str])

    Example:
        result = validate_pipeline(pipeline)
        if not result["success"]:
            raise RuntimeError(f"Invalid pipeline: {result['errors']}")
    """
    errors = []

    # Schema validation
    try:
        jsonschema.validate(instance=pipeline, schema=PIPELINE_SCHEMA)
    except jsonschema.ValidationError as e:
        errors.append(f"Schema validation failed: {e.message}")
        errors.append(f"🔧 Troubleshooting: Check required fields: name, stages")
        return {"success": False, "errors": errors}

    # Semantic validation - check depends_on references
    stage_names = [s["name"] for s in pipeline["stages"]]
    for stage in pipeline["stages"]:
        if "depends_on" in stage:
            for dep in stage["depends_on"]:
                if dep not in stage_names:
                    errors.append(
                        f"Stage '{stage['name']}' depends on unknown stage '{dep}'\n"
                        f"🔧 Troubleshooting: Available stages: {stage_names}"
                    )

    return {
        "success": len(errors) == 0,
        "errors": errors
    }
