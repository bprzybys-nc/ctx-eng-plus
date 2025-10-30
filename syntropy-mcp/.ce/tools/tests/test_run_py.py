"""Tests for run_py function."""

import pytest
from pathlib import Path
from ce.core import run_py


def test_run_py_adhoc_oneliner():
    """Test ad-hoc Python code execution (1 LOC)."""
    result = run_py(code="print('test')")

    assert result["success"] is True
    assert "test" in result["stdout"]
    assert result["exit_code"] == 0


def test_run_py_adhoc_3loc():
    """Test ad-hoc Python code execution (3 LOC max)."""
    code = """x = [1, 2, 3]
y = sum(x)
print(y)"""

    result = run_py(code=code)

    assert result["success"] is True
    assert "6" in result["stdout"]
    assert result["exit_code"] == 0


def test_run_py_adhoc_exceeds_limit():
    """Test that code > 3 LOC raises ValueError."""
    code = """x = 1
y = 2
z = 3
w = 4
print(x + y + z + w)"""

    with pytest.raises(ValueError, match="exceeds 3 LOC limit"):
        run_py(code=code)


def test_run_py_file_in_tmp(tmp_path):
    """Test execution of Python file in tmp/ folder."""
    # Create tmp/ directory
    tmp_dir = tmp_path / "tmp"
    tmp_dir.mkdir()

    # Create test script
    script = tmp_dir / "test_script.py"
    script.write_text("print('from file')")

    result = run_py(file=str(script))

    assert result["success"] is True
    assert "from file" in result["stdout"]


def test_run_py_file_not_in_tmp(tmp_path):
    """Test that files outside tmp/ raise ValueError."""
    script = tmp_path / "test_script.py"
    script.write_text("print('test')")

    with pytest.raises(ValueError, match="must be in tmp/ folder"):
        run_py(file=str(script))


def test_run_py_file_not_found():
    """Test that missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="not found"):
        run_py(file="tmp/nonexistent.py")


def test_run_py_no_params():
    """Test that missing all params raises ValueError."""
    with pytest.raises(ValueError, match="Either 'code', 'file', or 'auto' must be provided"):
        run_py()


def test_run_py_both_params():
    """Test that providing both code and file raises ValueError."""
    with pytest.raises(ValueError, match="Cannot provide both"):
        run_py(code="print('test')", file="tmp/test.py")


def test_run_py_with_args(tmp_path):
    """Test passing arguments to Python script."""
    tmp_dir = tmp_path / "tmp"
    tmp_dir.mkdir()

    script = tmp_dir / "args_test.py"
    script.write_text("import sys; print(' '.join(sys.argv[1:]))")

    result = run_py(file=str(script), args="arg1 arg2 arg3")

    assert result["success"] is True
    assert "arg1 arg2 arg3" in result["stdout"]


def test_run_py_python_error():
    """Test that Python errors are captured."""
    result = run_py(code="raise ValueError('test error')")

    assert result["success"] is False
    assert result["exit_code"] != 0
    assert "test error" in result["stderr"]


def test_run_py_auto_code():
    """Test auto-detect mode with code."""
    result = run_py(auto="print('auto mode')")

    assert result["success"] is True
    assert "auto mode" in result["stdout"]


def test_run_py_auto_file(tmp_path):
    """Test auto-detect mode with file path."""
    tmp_dir = tmp_path / "tmp"
    tmp_dir.mkdir()

    script = tmp_dir / "auto_test.py"
    script.write_text("print('from auto file')")

    result = run_py(auto=str(script))

    assert result["success"] is True
    assert "from auto file" in result["stdout"]


def test_run_py_auto_with_explicit():
    """Test that auto cannot be used with code or file."""
    with pytest.raises(ValueError, match="Cannot use 'auto' with 'code' or 'file'"):
        run_py(auto="print('test')", code="print('test')")
