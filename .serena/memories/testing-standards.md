# Testing Standards

## Testing Philosophy
**Real Functionality Testing - ZERO TOLERANCE FOR FAKE RESULTS**

The point of test/validation logic is to test REAL functionality using REAL values printing REAL results.

## Real Testing Required
```python
# ✅ GOOD - Tests real function
def test_git_status():
    status = git_status()  # Real call
    assert "clean" in status
    assert isinstance(status["staged"], list)

# ❌ BAD - Mocked result
def test_git_status():
    status = {"clean": True}  # FAKE!
    assert status["clean"]
```

## Exception Testing
```python
# ✅ GOOD - Real exception handling
try:
    result = real_function()
    print(f"✅ Real result: {result}")
except Exception as e:
    print(f"❌ Function FAILED: {e}")
    print("🔧 Troubleshooting: Check configuration...")
    raise  # MANDATORY - Always throw real exceptions

# ❌ FORBIDDEN - Fake success
print("✅ Test passed")  # While actual test failed
result = {"success": True}  # Fake fallback when real function fails
```

## Test Running
```bash
# Navigate to tools directory
cd tools

# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_core.py -v

# Run specific test
uv run pytest tests/test_core.py::test_run_cmd_success -v

# Quick test run (fail fast, minimal output)
uv run pytest tests/ -x --tb=short -q
```

## Test Organization
```
tests/
├── test_cli.py         # CLI interface tests
├── test_core.py        # Core functionality tests
├── test_validate.py    # Validation gate tests
└── test_context.py     # Context management tests
```

## Pytest Configuration
Located in `tools/pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = "-v --tb=short"
```

## TDD Approach (Pragmatic)
1. **Write test first** - Define expected behavior
2. **Watch it fail** - Ensure test validates logic
3. **Write minimal code** - Just enough to make test pass
4. **Refactor** - Improve while keeping tests green
5. **CRITICAL**: Tests must invoke actual functionality - no mocks unless explicit

## Key Principles
- Tests must use real methods
- No hardcoded success messages
- No fake metrics or percentages
- Let real failures throw with troubleshooting messages
- **Exception is exception and MUST be thrown**