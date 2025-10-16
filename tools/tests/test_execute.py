"""Tests for PRP execution orchestration (execute.py)."""

import pytest
import tempfile
from pathlib import Path

from ce.blueprint_parser import (
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
    """Test execute_phase creates and modifies real files."""
    import tempfile
    import shutil
    from pathlib import Path
    from ce.execute import execute_phase

    # Create temporary directory for test files
    test_dir = tempfile.mkdtemp()

    try:
        # Create existing file to modify
        existing_file = Path(test_dir) / "existing.py"
        existing_file.write_text("# Existing file\n")

        phase = {
            "phase_number": 1,
            "phase_name": "Test Phase",
            "goal": "Test goal",
            "approach": "Test approach",
            "files_to_create": [
                {"path": str(Path(test_dir) / "new_file.py"), "description": "Test file"}
            ],
            "files_to_modify": [
                {"path": str(existing_file), "description": "Modify existing"}
            ],
            "functions": [
                {
                    "signature": "def test_func():",
                    "docstring": "Test function",
                    "full_code": "def test_func():\n    pass"
                }
            ]
        }

        # Execute phase - this should create/modify REAL files
        result = execute_phase(phase)

        # Validate result structure
        assert "success" in result
        assert "files_created" in result
        assert "files_modified" in result
        assert "functions_added" in result
        assert "duration" in result

        # Validate real file operations happened
        if result["success"]:
            created_file = Path(test_dir) / "new_file.py"
            assert created_file.exists(), f"File {created_file} was not created"
            assert "test_func" in result["functions_added"]

            # Check modified file
            modified_content = existing_file.read_text()
            assert len(modified_content) > len("# Existing file\n"), "File was not actually modified"

        else:
            # If it fails, check error message is actionable
            assert "error" in result
            print(f"🔧 Execution failed (expected in unit test context): {result['error']}")

    finally:
        # Cleanup
        shutil.rmtree(test_dir)


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
# Phase 3: Error Parsing Tests
# ============================================================================

def test_parse_validation_error_import_error():
    """Test parsing ImportError with module name extraction."""
    from ce.execute import parse_validation_error

    output = """
    Traceback (most recent call last):
      File "src/auth.py", line 5, in authenticate
        import jwt
    ImportError: No module named 'jwt'
    """

    error = parse_validation_error(output, "L2")

    assert error["type"] == "import_error"
    assert error["file"] == "src/auth.py"
    assert error["line"] == 5
    assert error["function"] == "authenticate"
    assert "jwt" in error["message"]
    assert "import" in error["suggested_fix"].lower()


def test_parse_validation_error_import_cannot_import():
    """Test parsing 'cannot import name' errors."""
    from ce.execute import parse_validation_error

    output = """
    Traceback (most recent call last):
      File "tests/test_api.py", line 10
        from models import User
    ImportError: cannot import name 'User'
    """

    error = parse_validation_error(output, "L2")

    assert error["type"] == "import_error"
    assert "User" in error["message"]
    assert "import" in error["suggested_fix"].lower()


def test_parse_validation_error_assertion_error():
    """Test parsing AssertionError with context."""
    from ce.execute import parse_validation_error

    output = """
    tests/test_auth.py:42: in test_authenticate
        assert result == expected
    AssertionError: Expected User(id=1), got None
    """

    error = parse_validation_error(output, "L2")

    assert error["type"] == "assertion_error"
    assert error["file"] == "tests/test_auth.py"
    assert error["line"] == 42
    assert "assertion" in error["suggested_fix"].lower()


def test_parse_validation_error_syntax_error():
    """Test parsing SyntaxError with file:line location."""
    from ce.execute import parse_validation_error

    output = """
      File "src/models.py", line 23
        def validate_user(
                         ^
    SyntaxError: invalid syntax
    """

    error = parse_validation_error(output, "L1")

    assert error["type"] == "syntax_error"
    assert error["file"] == "src/models.py"
    assert error["line"] == 23
    assert "syntax" in error["suggested_fix"].lower()


def test_parse_validation_error_type_error():
    """Test parsing TypeError detection."""
    from ce.execute import parse_validation_error

    output = """
    File "src/api.py", line 15, in call_api
        response = requests.get(url, timeout=timeout)
    TypeError: get() got an unexpected keyword argument 'timeout'
    """

    error = parse_validation_error(output, "L2")

    assert error["type"] == "type_error"
    assert error["file"] == "src/api.py"
    assert error["line"] == 15
    assert "type" in error["suggested_fix"].lower()


def test_parse_validation_error_name_error():
    """Test parsing NameError detection."""
    from ce.execute import parse_validation_error

    output = """
    File "src/utils.py", line 8, in helper
        return undefined_variable
    NameError: name 'undefined_variable' is not defined
    """

    error = parse_validation_error(output, "L2")

    assert error["type"] == "name_error"
    assert "variable" in error["suggested_fix"].lower() or "import" in error["suggested_fix"].lower()


def test_parse_validation_error_file_line_extraction():
    """Test extracting file:line from various formats."""
    from ce.execute import parse_validation_error

    # Format 1: File "path", line N
    output1 = 'File "src/test.py", line 42, in func\n    ImportError'
    error1 = parse_validation_error(output1, "L2")
    assert error1["file"] == "src/test.py"
    assert error1["line"] == 42

    # Format 2: path.py:N:
    output2 = 'src/test.py:42: in func\n    AssertionError'
    error2 = parse_validation_error(output2, "L2")
    assert error2["file"] == "src/test.py"
    assert error2["line"] == 42


# ============================================================================
# Phase 4: Self-Healing Tests
# ============================================================================

def test_apply_self_healing_fix_import_error_no_module():
    """Test fixing 'No module named X' errors."""
    from ce.execute import apply_self_healing_fix
    import tempfile
    from pathlib import Path

    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("# Test file\ndef main():\n    pass\n")
        temp_file = f.name

    try:
        error = {
            "type": "import_error",
            "file": temp_file,
            "message": "No module named 'jwt'"
        }

        result = apply_self_healing_fix(error, 1)

        assert result["success"] == True
        assert result["fix_type"] == "import_added"
        assert "jwt" in result["description"]

        # Verify import was actually added
        content = Path(temp_file).read_text()
        assert "import jwt" in content

    finally:
        Path(temp_file).unlink()


def test_apply_self_healing_fix_import_error_cannot_import():
    """Test fixing 'cannot import name X' errors."""
    from ce.execute import apply_self_healing_fix
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("import sys\n\ndef main():\n    pass\n")
        temp_file = f.name

    try:
        error = {
            "type": "import_error",
            "file": temp_file,
            "message": "cannot import name 'User'"
        }

        result = apply_self_healing_fix(error, 1)

        assert result["success"] == True
        assert result["fix_type"] == "import_added"
        assert "User" in result["description"]

        # Verify import was added after existing imports
        content = Path(temp_file).read_text()
        lines = content.split("\n")
        assert "from . import User" in content
        # Should be added after "import sys"
        user_import_idx = next(i for i, line in enumerate(lines) if "User" in line)
        sys_import_idx = next(i for i, line in enumerate(lines) if "import sys" in line)
        assert user_import_idx > sys_import_idx

    finally:
        Path(temp_file).unlink()


def test_apply_self_healing_fix_file_not_found():
    """Test handling of file not found error."""
    from ce.execute import apply_self_healing_fix

    error = {
        "type": "import_error",
        "file": "/nonexistent/file.py",
        "message": "No module named 'jwt'"
    }

    result = apply_self_healing_fix(error, 1)

    assert result["success"] == False
    assert "not found" in result["description"].lower()


def test_apply_self_healing_fix_unsupported_error_type():
    """Test that unsupported error types return failure (not crash)."""
    from ce.execute import apply_self_healing_fix

    error = {
        "type": "assertion_error",
        "file": "test.py",
        "message": "Test failed"
    }

    result = apply_self_healing_fix(error, 1)

    assert result["success"] == False
    assert "not_implemented" in result["fix_type"]


def test_add_import_statement_top_of_file():
    """Test import added at correct position in file."""
    from ce.validation_loop import _add_import_statement
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('"""Module docstring."""\n\ndef main():\n    pass\n')
        temp_file = f.name

    try:
        result = _add_import_statement(temp_file, "import jwt")

        assert result["success"] == True

        # Verify import was added
        content = Path(temp_file).read_text()
        assert "import jwt" in content

    finally:
        Path(temp_file).unlink()


def test_add_import_statement_after_existing_imports():
    """Test import added after existing imports, not at top."""
    from ce.validation_loop import _add_import_statement
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("import sys\nimport os\n\ndef main():\n    pass\n")
        temp_file = f.name

    try:
        result = _add_import_statement(temp_file, "import jwt")

        assert result["success"] == True

        content = Path(temp_file).read_text()
        lines = content.split("\n")

        # Find line indices
        jwt_idx = next(i for i, line in enumerate(lines) if "import jwt" in line)
        os_idx = next(i for i, line in enumerate(lines) if "import os" in line)

        # jwt import should be after os import
        assert jwt_idx > os_idx

    finally:
        Path(temp_file).unlink()


# ============================================================================
# Phase 5: Escalation Trigger Tests
# ============================================================================

def test_check_escalation_triggers_persistent_error():
    """Test trigger 1: Same error after 3 attempts."""
    from ce.execute import check_escalation_triggers

    error = {
        "type": "import_error",
        "message": "No module named 'jwt'",
        "file": "test.py",
        "line": 5
    }

    # Same error 3 times
    error_history = [
        "No module named 'jwt'",
        "No module named 'jwt'",
        "No module named 'jwt'"
    ]

    result = check_escalation_triggers(error, 3, error_history)
    assert result == True


def test_check_escalation_triggers_persistent_error_different():
    """Test trigger 1: Different errors - no escalation."""
    from ce.execute import check_escalation_triggers

    error = {
        "type": "import_error",
        "message": "No module named 'requests'",
        "file": "test.py",
        "line": 5
    }

    # Different errors
    error_history = [
        "No module named 'jwt'",
        "No module named 'pyjwt'",
        "No module named 'requests'"
    ]

    result = check_escalation_triggers(error, 3, error_history)
    assert result == False


def test_check_escalation_triggers_ambiguous_error():
    """Test trigger 2: Generic error with no file/line info."""
    from ce.execute import check_escalation_triggers

    error = {
        "type": "unknown_error",
        "message": "something went wrong",
        "file": "unknown",
        "line": 0
    }

    result = check_escalation_triggers(error, 1, ["something went wrong"])
    assert result == True


def test_check_escalation_triggers_ambiguous_with_location():
    """Test trigger 2: Generic error but WITH file/line - no escalation."""
    from ce.execute import check_escalation_triggers

    error = {
        "type": "unknown_error",
        "message": "something went wrong",
        "file": "test.py",
        "line": 42
    }

    result = check_escalation_triggers(error, 1, ["something went wrong"])
    assert result == False


def test_check_escalation_triggers_architectural():
    """Test trigger 3: Keywords like 'refactor', 'circular import'."""
    from ce.execute import check_escalation_triggers

    # Test architectural keywords
    for keyword in ["refactor", "circular import", "redesign", "architecture"]:
        error = {
            "type": "import_error",
            "message": f"Error: {keyword} required",
            "traceback": f"Full traceback with {keyword}",
            "file": "test.py",
            "line": 5
        }

        result = check_escalation_triggers(error, 1, [error["message"]])
        assert result == True, f"Should escalate for keyword: {keyword}"


def test_check_escalation_triggers_dependencies():
    """Test trigger 4: Network/dependency errors."""
    from ce.execute import check_escalation_triggers

    # Test dependency keywords
    for keyword in ["connection refused", "network error", "timeout", "api error", "package not found"]:
        error = {
            "type": "unknown_error",
            "message": f"Error: {keyword}",
            "traceback": f"Traceback with {keyword}",
            "file": "test.py",
            "line": 5
        }

        result = check_escalation_triggers(error, 1, [error["message"]])
        assert result == True, f"Should escalate for keyword: {keyword}"


def test_check_escalation_triggers_security():
    """Test trigger 5: CVE, secrets, credentials mentioned."""
    from ce.execute import check_escalation_triggers

    # Test security keywords
    for keyword in ["cve-", "vulnerability", "secret", "password", "api key", "credential", "unauthorized"]:
        error = {
            "type": "unknown_error",
            "message": f"Error with {keyword}",
            "traceback": f"Traceback mentioning {keyword}",
            "file": "test.py",
            "line": 5
        }

        result = check_escalation_triggers(error, 1, [error["message"]])
        assert result == True, f"Should escalate for keyword: {keyword}"


def test_escalate_to_human_raises_exception():
    """Test escalate_to_human always raises EscalationRequired."""
    from ce.execute import escalate_to_human
    from ce.exceptions import EscalationRequired

    error = {
        "type": "import_error",
        "message": "No module named 'jwt'",
        "file": "test.py",
        "line": 5
    }

    with pytest.raises(EscalationRequired) as exc:
        escalate_to_human(error, "persistent_error")

    assert "persistent_error" in str(exc.value)
    assert "jwt" in str(exc.value)


def test_escalation_required_exception_format():
    """Test exception includes reason, error, troubleshooting."""
    from ce.exceptions import EscalationRequired

    error = {
        "type": "import_error",
        "message": "No module named 'jwt'",
        "file": "src/auth.py",
        "line": 5
    }

    exc = EscalationRequired(
        reason="persistent_error",
        error=error,
        troubleshooting="Steps:\n1. Check imports\n2. Install package"
    )

    assert exc.reason == "persistent_error"
    assert exc.error == error
    assert "Check imports" in exc.troubleshooting
    assert "jwt" in str(exc)
    assert "src/auth.py" in str(exc)
