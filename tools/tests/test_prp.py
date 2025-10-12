"""Tests for PRP validation module."""
import pytest
import tempfile
from pathlib import Path
from ce.prp import (
    validate_prp_yaml,
    validate_prp_id_format,
    validate_date_format,
    validate_schema,
    format_validation_result
)


@pytest.fixture
def valid_prp_yaml():
    """Valid PRP YAML content."""
    return """---
name: "Test Feature"
description: "Test description"
prp_id: "PRP-1.2"
task_id: "TEST-123"
status: "ready"
priority: "MEDIUM"
confidence: "8/10"
effort_hours: 3.0
risk: "LOW"
dependencies: []
parent_prp: "PRP-1"
context_memories: []
meeting_evidence: []
context_sync:
  ce_updated: false
  serena_updated: false
version: 1
created_date: "2025-01-15T21:30:00Z"
last_updated: "2025-01-15T21:30:00Z"
---

# Test PRP

Content here.
"""


@pytest.fixture
def invalid_yaml_missing_fields():
    """YAML with missing required fields."""
    return """---
name: "Test Feature"
prp_id: "PRP-1.2"
---

# Test PRP
"""


@pytest.fixture
def invalid_prp_id_format():
    """YAML with invalid PRP ID format."""
    return """---
name: "Test Feature"
description: "Test description"
prp_id: "PRP-001"
task_id: ""
status: "ready"
priority: "MEDIUM"
confidence: "8/10"
effort_hours: 3.0
risk: "LOW"
dependencies: []
parent_prp: null
context_memories: []
meeting_evidence: []
context_sync:
  ce_updated: false
  serena_updated: false
version: 1
created_date: "2025-01-15T21:30:00Z"
last_updated: "2025-01-15T21:30:00Z"
---

# Test PRP
"""


@pytest.fixture
def invalid_date_format():
    """YAML with invalid date format."""
    return """---
name: "Test Feature"
description: "Test description"
prp_id: "PRP-1.2"
task_id: ""
status: "ready"
priority: "MEDIUM"
confidence: "8/10"
effort_hours: 3.0
risk: "LOW"
dependencies: []
parent_prp: null
context_memories: []
meeting_evidence: []
context_sync:
  ce_updated: false
  serena_updated: false
version: 1
created_date: "2025-01-15"
last_updated: "2025-01-15T21:30:00Z"
---

# Test PRP
"""


def test_validate_prp_yaml_valid(valid_prp_yaml):
    """Test validation with valid YAML."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(valid_prp_yaml)
        f.flush()

        result = validate_prp_yaml(f.name)

        assert result["success"] is True
        assert len(result["errors"]) == 0
        assert result["header"]["prp_id"] == "PRP-1.2"
        assert result["header"]["name"] == "Test Feature"

        Path(f.name).unlink()


def test_validate_prp_yaml_missing_fields(invalid_yaml_missing_fields):
    """Test validation with missing required fields."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(invalid_yaml_missing_fields)
        f.flush()

        result = validate_prp_yaml(f.name)

        assert result["success"] is False
        assert len(result["errors"]) > 0
        assert any("Missing required fields" in err for err in result["errors"])

        Path(f.name).unlink()


def test_validate_prp_id_format_valid():
    """Test PRP ID format validation with valid IDs."""
    assert validate_prp_id_format("PRP-1") is None
    assert validate_prp_id_format("PRP-1.2") is None
    assert validate_prp_id_format("PRP-1.2.3") is None
    assert validate_prp_id_format("PRP-100") is None


def test_validate_prp_id_format_invalid():
    """Test PRP ID format validation with invalid IDs."""
    assert validate_prp_id_format("PRP-001") is not None
    assert validate_prp_id_format("PRP-X") is not None
    assert validate_prp_id_format("prp-1") is not None
    assert validate_prp_id_format("1.2") is not None


def test_validate_date_format_valid():
    """Test date format validation with valid dates."""
    assert validate_date_format("2025-01-15T21:30:00Z", "test_field") is None
    assert validate_date_format("2025-12-31T23:59:59Z", "test_field") is None


def test_validate_date_format_invalid():
    """Test date format validation with invalid dates."""
    assert validate_date_format("2025-01-15", "test_field") is not None
    assert validate_date_format("2025-01-15 21:30:00", "test_field") is not None
    assert validate_date_format("invalid", "test_field") is not None


def test_validate_prp_yaml_invalid_status(valid_prp_yaml):
    """Test validation with invalid status enum."""
    invalid_yaml = valid_prp_yaml.replace('status: "ready"', 'status: "invalid"')

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(invalid_yaml)
        f.flush()

        result = validate_prp_yaml(f.name)

        assert result["success"] is False
        assert any("Invalid status" in err for err in result["errors"])

        Path(f.name).unlink()


def test_validate_prp_yaml_file_not_found():
    """Test validation with non-existent file."""
    with pytest.raises(FileNotFoundError):
        validate_prp_yaml("/nonexistent/file.md")


def test_validate_prp_yaml_syntax_error():
    """Test validation with YAML syntax error."""
    invalid_yaml = """---
name: "Test Feature"
  invalid_indent: value
prp_id: "PRP-1.2"
---

# Test PRP
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(invalid_yaml)
        f.flush()

        result = validate_prp_yaml(f.name)

        # Should handle YAML parse error gracefully
        assert result["success"] is False
        assert len(result["errors"]) > 0

        Path(f.name).unlink()


def test_validate_prp_yaml_missing_delimiters():
    """Test validation with missing YAML delimiters."""
    invalid_yaml = """# Test PRP

No YAML header here.
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(invalid_yaml)
        f.flush()

        result = validate_prp_yaml(f.name)

        assert result["success"] is False
        assert any("Missing YAML front matter" in err for err in result["errors"])

        Path(f.name).unlink()


def test_format_validation_result_success():
    """Test formatting successful validation result."""
    result = {
        "success": True,
        "errors": [],
        "warnings": ["Test warning"],
        "header": {
            "prp_id": "PRP-1.2",
            "name": "Test Feature",
            "status": "ready",
            "effort_hours": 3.0
        }
    }

    output = format_validation_result(result)

    assert "✅ YAML validation passed" in output
    assert "PRP-1.2" in output
    assert "Test Feature" in output
    assert "⚠️  Warnings" in output
    assert "Test warning" in output


def test_format_validation_result_failure():
    """Test formatting failed validation result."""
    result = {
        "success": False,
        "errors": ["Error 1", "Error 2"],
        "warnings": [],
        "header": None
    }

    output = format_validation_result(result)

    assert "❌ YAML validation failed" in output
    assert "Error 1" in output
    assert "Error 2" in output
    assert "🔧 Troubleshooting" in output


def test_validate_schema_invalid_confidence():
    """Test schema validation with invalid confidence format."""
    header = {
        "name": "Test",
        "description": "Test",
        "prp_id": "PRP-1",
        "task_id": "",
        "status": "ready",
        "priority": "MEDIUM",
        "confidence": "eleven/10",  # Invalid
        "effort_hours": 3.0,
        "risk": "LOW",
        "dependencies": [],
        "parent_prp": None,
        "context_memories": [],
        "meeting_evidence": [],
        "context_sync": {"ce_updated": False, "serena_updated": False},
        "version": 1,
        "created_date": "2025-01-15T21:30:00Z",
        "last_updated": "2025-01-15T21:30:00Z"
    }

    result = validate_schema(header, [], [])

    assert result["success"] is False
    assert any("Invalid confidence format" in err for err in result["errors"])


def test_validate_schema_invalid_effort_hours():
    """Test schema validation with non-numeric effort_hours."""
    header = {
        "name": "Test",
        "description": "Test",
        "prp_id": "PRP-1",
        "task_id": "",
        "status": "ready",
        "priority": "MEDIUM",
        "confidence": "8/10",
        "effort_hours": "three hours",  # Invalid
        "risk": "LOW",
        "dependencies": [],
        "parent_prp": None,
        "context_memories": [],
        "meeting_evidence": [],
        "context_sync": {"ce_updated": False, "serena_updated": False},
        "version": 1,
        "created_date": "2025-01-15T21:30:00Z",
        "last_updated": "2025-01-15T21:30:00Z"
    }

    result = validate_schema(header, [], [])

    assert result["success"] is False
    assert any("Invalid effort_hours" in err for err in result["errors"])
