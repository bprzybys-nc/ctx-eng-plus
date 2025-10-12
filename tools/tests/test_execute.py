"""Tests for PRP execution orchestration (execute.py)."""

import pytest
import tempfile
from pathlib import Path

from ce.execute import (
    parse_blueprint,
    extract_field,
    parse_file_list,
    extract_function_signatures,
    extract_phase_metadata
)
from ce.exceptions import BlueprintParseError


# ============================================================================
# Phase 1: Blueprint Parser Tests
# ============================================================================

def test_parse_blueprint():
    """Test parsing PRP blueprint into phases."""
    # Create a minimal valid PRP
    prp_content = """---
name: "Test PRP"
prp_id: "PRP-999"
---

# Test PRP

## 🔧 Implementation Blueprint

### Phase 1: Core Logic (3 hours)

**Goal**: Implement core authentication logic

**Approach**: Class-based design with async methods

**Files to Modify**:
- `src/auth.py` - Add authentication logic
- `tests/test_auth.py` - Add unit tests

**Files to Create**:
- `src/models/user.py` - User model class

**Key Functions**:
```python
def authenticate(username: str, password: str) -> User:
    \"\"\"Authenticate user with credentials.\"\"\"
    pass

async def validate_token(token: str) -> bool:
    \"\"\"Validate JWT token.\"\"\"
    pass
```

**Validation Command**: `pytest tests/test_auth.py -v`

**Checkpoint**: `git add src/ tests/ && git commit -m "feat: auth logic"`

### Phase 2: Integration (2 hours)

**Goal**: Integrate with API

**Approach**: REST API client

**Files to Modify**:
- `src/api.py` - Add API client

**Files to Create**:
- `src/api/client.py` - HTTP client

**Key Functions**:
```python
class APIClient:
    \"\"\"HTTP client for authentication API.\"\"\"
    pass
```

**Validation Command**: `pytest tests/test_api.py -v`

**Checkpoint**: `git add src/api/ && git commit -m "feat: api integration"`
"""

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(prp_content)
        prp_path = f.name

    try:
        phases = parse_blueprint(prp_path)

        # Validate phase count
        assert len(phases) == 2, f"Expected 2 phases, got {len(phases)}"

        # Validate Phase 1
        phase1 = phases[0]
        assert phase1["phase_number"] == 1
        assert phase1["phase_name"] == "Core Logic"
        assert phase1["hours"] == 3.0
        assert "authentication logic" in phase1["goal"].lower()
        assert "class-based" in phase1["approach"].lower()
        assert len(phase1["files_to_modify"]) == 2
        assert len(phase1["files_to_create"]) == 1
        assert phase1["files_to_modify"][0]["path"] == "src/auth.py"
        assert phase1["files_to_create"][0]["path"] == "src/models/user.py"
        assert len(phase1["functions"]) == 2
        assert "authenticate" in phase1["functions"][0]["signature"]
        assert "validate_token" in phase1["functions"][1]["signature"]
        assert phase1["validation_command"] == "pytest tests/test_auth.py -v"
        assert "git add" in phase1["checkpoint_command"]

        # Validate Phase 2
        phase2 = phases[1]
        assert phase2["phase_number"] == 2
        assert phase2["phase_name"] == "Integration"
        assert phase2["hours"] == 2.0
        assert "api" in phase2["goal"].lower()

    finally:
        Path(prp_path).unlink()


def test_parse_blueprint_missing_file():
    """Test parse_blueprint with non-existent file."""
    with pytest.raises(FileNotFoundError) as exc:
        parse_blueprint("/nonexistent/prp.md")

    assert "PRP file not found" in str(exc.value)
    assert "Troubleshooting" in str(exc.value)


def test_parse_blueprint_missing_section():
    """Test parse_blueprint with missing IMPLEMENTATION BLUEPRINT section."""
    prp_content = """---
name: "Test PRP"
---

# Test PRP

## Some Other Section

Content here.
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(prp_content)
        prp_path = f.name

    try:
        with pytest.raises(BlueprintParseError) as exc:
            parse_blueprint(prp_path)

        assert "Implementation Blueprint" in str(exc.value)
    finally:
        Path(prp_path).unlink()


def test_parse_blueprint_no_phases():
    """Test parse_blueprint with blueprint section but no phases."""
    prp_content = """---
name: "Test PRP"
---

## 🔧 Implementation Blueprint

Some text but no phases.
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(prp_content)
        prp_path = f.name

    try:
        with pytest.raises(BlueprintParseError) as exc:
            parse_blueprint(prp_path)

        assert "No phases found" in str(exc.value)
    finally:
        Path(prp_path).unlink()


def test_extract_field():
    """Test extracting a single field from text."""
    text = """
Some content.

**Goal**: Implement authentication logic

**Approach**: Use JWT tokens
"""

    # Test required field
    goal = extract_field(text, r"\*\*Goal\*\*:\s*(.+?)(?=\n\n|\*\*|$)", "test.md")
    assert goal == "Implement authentication logic"

    # Test optional field (not present)
    result = extract_field(text, r"\*\*Missing\*\*:\s*(.+?)(?=\n\n|\*\*|$)", "test.md", required=False)
    assert result is None

    # Test required field (not present) - should raise
    with pytest.raises(BlueprintParseError):
        extract_field(text, r"\*\*Missing\*\*:\s*(.+?)(?=\n\n|\*\*|$)", "test.md", required=True)


def test_parse_file_list():
    """Test parsing file list from phase text."""
    text = """
**Files to Modify**:
- `src/auth.py` - Add authentication logic
- `src/models/user.py` - Update user model
- `tests/test_auth.py` - Add unit tests

**Files to Create**:
- `src/api/client.py` - HTTP client class
"""

    files_to_modify = parse_file_list(text, "Files to Modify")
    assert len(files_to_modify) == 3
    assert files_to_modify[0]["path"] == "src/auth.py"
    assert "authentication" in files_to_modify[0]["description"]
    assert files_to_modify[2]["path"] == "tests/test_auth.py"

    files_to_create = parse_file_list(text, "Files to Create")
    assert len(files_to_create) == 1
    assert files_to_create[0]["path"] == "src/api/client.py"
    assert "HTTP client" in files_to_create[0]["description"]

    # Test missing section
    missing = parse_file_list(text, "Files to Delete")
    assert missing == []


def test_extract_function_signatures():
    """Test extracting function signatures from code blocks."""
    text = """
**Key Functions**:
```python
def authenticate(username: str, password: str) -> User:
    \"\"\"Authenticate user with credentials.\"\"\"
    pass

async def validate_token(token: str) -> bool:
    \"\"\"Validate JWT token.\"\"\"
    pass

class AuthHandler:
    \"\"\"Handle authentication requests.\"\"\"
    pass
```
"""

    functions = extract_function_signatures(text)

    assert len(functions) == 3

    # Check authenticate function
    assert "authenticate" in functions[0]["signature"]
    assert "username" in functions[0]["signature"]
    assert "Authenticate user" in functions[0]["docstring"]

    # Check validate_token function
    assert "validate_token" in functions[1]["signature"]
    assert "async" in functions[1]["signature"]
    assert "JWT" in functions[1]["docstring"]

    # Check class
    assert "class AuthHandler" in functions[2]["signature"]


def test_extract_phase_metadata():
    """Test extracting metadata from phase heading."""
    text = "### Phase 1: Core Logic Implementation (4 hours)"

    metadata = extract_phase_metadata(text)

    assert metadata["phase_number"] == 1
    assert metadata["phase_name"] == "Core Logic Implementation"
    assert metadata["hours"] == 4.0

    # Test with decimal hours
    text2 = "### Phase 2: Testing (2.5 hours)"
    metadata2 = extract_phase_metadata(text2)
    assert metadata2["hours"] == 2.5


# ============================================================================
# Phase 2: Execution Orchestration Tests
# ============================================================================

def test_execute_phase():
    """Test execute_phase function."""
    from ce.execute import execute_phase

    phase = {
        "phase_number": 1,
        "phase_name": "Test Phase",
        "goal": "Test goal",
        "approach": "Test approach",
        "files_to_create": [
            {"path": "src/test.py", "description": "Test file"}
        ],
        "files_to_modify": [
            {"path": "src/existing.py", "description": "Modify existing"}
        ],
        "functions": [
            {
                "signature": "def test_func():",
                "docstring": "Test function",
                "full_code": "def test_func():\n    pass"
            }
        ]
    }

    result = execute_phase(phase)

    assert result["success"] is True
    assert "src/test.py" in result["files_created"]
    assert "src/existing.py" in result["files_modified"]
    assert "test_func" in result["functions_added"]
    assert "duration" in result


def test_calculate_confidence_score():
    """Test confidence score calculation."""
    from ce.execute import calculate_confidence_score

    # Perfect score - no retries
    results_perfect = {
        "Phase1": {
            "success": True,
            "validation_levels": {
                "L1": {"passed": True, "attempts": 1},
                "L2": {"passed": True, "attempts": 1},
                "L3": {"passed": True, "attempts": 1},
                "L4": {"passed": True, "attempts": 1}
            }
        }
    }
    assert calculate_confidence_score(results_perfect) == "10/10"

    # Minor issues - 1-2 retries
    results_minor = {
        "Phase1": {
            "success": True,
            "validation_levels": {
                "L1": {"passed": True, "attempts": 1},
                "L2": {"passed": True, "attempts": 2},  # 1 retry
                "L3": {"passed": True, "attempts": 1},
                "L4": {"passed": True, "attempts": 1}
            }
        }
    }
    assert calculate_confidence_score(results_minor) == "9/10"

    # Multiple retries - 3+
    results_multiple = {
        "Phase1": {
            "success": True,
            "validation_levels": {
                "L1": {"passed": True, "attempts": 2},  # 1 retry
                "L2": {"passed": True, "attempts": 3},  # 2 retries
                "L3": {"passed": True, "attempts": 1},
                "L4": {"passed": True, "attempts": 1}
            }
        }
    }
    assert calculate_confidence_score(results_multiple) == "8/10"

    # Validation failures
    results_failed = {
        "Phase1": {
            "success": False,
            "validation_levels": {
                "L1": {"passed": False, "attempts": 1}
            }
        }
    }
    assert calculate_confidence_score(results_failed) == "5/10"

    # No validation
    assert calculate_confidence_score({}) == "6/10"


def test_find_prp_file():
    """Test PRP file finding logic."""
    from ce.execute import _find_prp_file

    # Test with PRP-4 (should find this file)
    prp_path = _find_prp_file("PRP-4")
    assert "PRP-4" in prp_path
    assert prp_path.endswith(".md")
    assert Path(prp_path).exists()

    # Test with invalid PRP
    with pytest.raises(FileNotFoundError) as exc:
        _find_prp_file("PRP-99999")

    assert "PRP file not found" in str(exc.value)
    assert "Troubleshooting" in str(exc.value)


# ============================================================================
# Phase 3: Validation Loop Tests (Placeholder)
# ============================================================================

def test_validation_loop():
    """Placeholder for validation loop tests."""
    # Will be implemented in Phase 3
    pass


# ============================================================================
# Phase 4: Self-Healing Tests (Placeholder)
# ============================================================================

def test_self_healing():
    """Placeholder for self-healing tests."""
    # Will be implemented in Phase 4
    pass


def test_escalation_triggers():
    """Placeholder for escalation trigger tests."""
    # Will be implemented in Phase 4
    pass
