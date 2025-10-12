"""Tests for pattern extraction from PRP EXAMPLES sections."""

import pytest
from pathlib import Path
from ce.pattern_extractor import (
    extract_patterns_from_prp,
    parse_code_structure,
    _parse_python_patterns,
    _parse_typescript_patterns
)


@pytest.fixture
def sample_prp_with_examples(tmp_path):
    """Create a sample PRP with EXAMPLES section."""
    prp_content = """# PRP-TEST: Sample Feature

## EXAMPLES

```python
async def validate_data(data: Dict) -> ValidationResult:
    try:
        result = await schema.validate(data)
        return ValidationResult(success=True, data=result)
    except ValidationError as e:
        return ValidationResult(success=False, error=str(e))

class DataValidator:
    def __init__(self):
        self._schema = None

    @property
    def schema(self):
        return self._schema
```

```typescript
async function processData(data: Record<string, any>): Promise<Result> {
    try {
        const result = await validateSchema(data);
        return { success: true, data: result };
    } catch (error) {
        return { success: false, error: error.message };
    }
}
```
"""
    prp_file = tmp_path / "sample_prp.md"
    prp_file.write_text(prp_content)
    return str(prp_file)


@pytest.fixture
def prp_without_examples(tmp_path):
    """Create a PRP without EXAMPLES section."""
    prp_content = """# PRP-TEST: Sample Feature

## CONTEXT
Some context here.

## IMPLEMENTATION
Some implementation details.
"""
    prp_file = tmp_path / "no_examples.md"
    prp_file.write_text(prp_content)
    return str(prp_file)


def test_pattern_extraction_from_prp(sample_prp_with_examples):
    """Verify pattern extraction from PRP EXAMPLES section."""
    patterns = extract_patterns_from_prp(sample_prp_with_examples)

    # Check structure
    assert "code_structure" in patterns
    assert "error_handling" in patterns
    assert "naming_conventions" in patterns
    assert "raw_examples" in patterns

    # Check async/await detected
    assert "async/await" in patterns["code_structure"]

    # Check error handling detected
    assert "try-except" in patterns["error_handling"] or "try-catch" in patterns["error_handling"]

    # Check naming conventions
    assert "snake_case" in patterns["naming_conventions"] or "camelCase" in patterns["naming_conventions"]

    # Check raw examples
    assert len(patterns["raw_examples"]) == 2
    assert patterns["raw_examples"][0]["language"] == "python"
    assert patterns["raw_examples"][1]["language"] == "typescript"


def test_pattern_extraction_missing_examples(prp_without_examples):
    """Verify error when EXAMPLES section missing."""
    with pytest.raises(ValueError, match="No EXAMPLES section found"):
        extract_patterns_from_prp(prp_without_examples)


def test_pattern_extraction_file_not_found():
    """Verify error when PRP file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        extract_patterns_from_prp("/nonexistent/prp.md")


def test_parse_code_structure_python():
    """Test Python code structure parsing."""
    code = """
async def fetch_data():
    await api.get("/data")

class Handler:
    pass
"""
    structure = parse_code_structure(code, "python")
    assert "async/await" in structure
    assert "class-based" in structure


def test_parse_code_structure_typescript():
    """Test TypeScript code structure parsing."""
    code = """
async function fetchData(): Promise<Data> {
    return await api.get("/data");
}

class DataHandler {
    constructor() {}
}
"""
    structure = parse_code_structure(code, "typescript")
    assert "async/await" in structure
    assert "class-based" in structure


def test_python_patterns_async_await():
    """Test detection of async/await patterns in Python."""
    code = """
async def process():
    result = await some_function()
    return result
"""
    patterns = _parse_python_patterns(code)
    assert "async/await" in patterns["code_structure"]


def test_python_patterns_try_except():
    """Test detection of try-except patterns."""
    code = """
def validate():
    try:
        check_data()
    except ValueError:
        handle_error()
"""
    patterns = _parse_python_patterns(code)
    assert "try-except" in patterns["error_handling"]


def test_python_patterns_class_based():
    """Test detection of class-based patterns."""
    code = """
class DataProcessor:
    def __init__(self):
        self.data = []

    def process(self):
        pass
"""
    patterns = _parse_python_patterns(code)
    assert "class-based" in patterns["code_structure"]
    assert "PascalCase" in patterns["naming_conventions"]


def test_python_patterns_snake_case():
    """Test detection of snake_case naming."""
    code = """
def process_user_data(user_id):
    return fetch_user(user_id)
"""
    patterns = _parse_python_patterns(code)
    assert "snake_case" in patterns["naming_conventions"]


def test_python_patterns_decorators():
    """Test detection of decorator patterns."""
    code = """
@staticmethod
def helper():
    pass

@dataclass
class Config:
    name: str
"""
    patterns = _parse_python_patterns(code)
    assert "decorator-staticmethod" in patterns["code_structure"]
    assert "dataclass" in patterns["code_structure"]


def test_python_patterns_early_return():
    """Test detection of early return guard clauses."""
    code = """
def validate(data):
    if not data:
        return False
    return True
"""
    patterns = _parse_python_patterns(code)
    assert "early-return" in patterns["error_handling"]


def test_python_patterns_private_naming():
    """Test detection of private naming convention."""
    code = """
def _internal_helper():
    pass
"""
    patterns = _parse_python_patterns(code)
    assert "_private" in patterns["naming_conventions"]


def test_typescript_patterns_async_await():
    """Test detection of async/await in TypeScript."""
    code = """
async function fetchData(): Promise<Data> {
    const result = await api.get("/data");
    return result;
}
"""
    patterns = _parse_typescript_patterns(code)
    assert "async/await" in patterns["code_structure"]


def test_typescript_patterns_promises():
    """Test detection of Promise patterns."""
    code = """
function fetchData() {
    return api.get("/data")
        .then(response => response.json())
        .catch(error => handleError(error));
}
"""
    patterns = _parse_typescript_patterns(code)
    assert "promises" in patterns["code_structure"]


def test_typescript_patterns_try_catch():
    """Test detection of try-catch patterns."""
    code = """
function process() {
    try {
        validateData();
    } catch (error) {
        handleError(error);
    }
}
"""
    patterns = _parse_typescript_patterns(code)
    assert "try-catch" in patterns["error_handling"]


def test_typescript_patterns_camel_case():
    """Test detection of camelCase naming."""
    code = """
const userData = fetchUserData(userId);
function processUserData(data) {
    return data;
}
"""
    patterns = _parse_typescript_patterns(code)
    assert "camelCase" in patterns["naming_conventions"]


def test_typescript_patterns_pascal_case():
    """Test detection of PascalCase (classes)."""
    code = """
class DataProcessor {
    constructor() {}
}
"""
    patterns = _parse_typescript_patterns(code)
    assert "PascalCase" in patterns["naming_conventions"]


def test_typescript_patterns_relative_imports():
    """Test detection of relative imports."""
    code = """
import { helper } from './utils';
import { Component } from '../components/Component';
"""
    patterns = _parse_typescript_patterns(code)
    assert "relative" in patterns["import_patterns"]


def test_typescript_patterns_absolute_imports():
    """Test detection of absolute imports."""
    code = """
import React from 'react';
import { useState } from 'react';
"""
    patterns = _parse_typescript_patterns(code)
    assert "absolute" in patterns["import_patterns"]


def test_python_syntax_error_fallback():
    """Test fallback to regex when Python AST parsing fails."""
    # Invalid Python syntax
    code = """
def broken_function(
    incomplete
"""
    patterns = _parse_python_patterns(code)
    # Should still return pattern dict (from regex fallback)
    assert isinstance(patterns, dict)
    assert "code_structure" in patterns


def test_empty_examples_section(tmp_path):
    """Test handling of empty EXAMPLES section."""
    prp_content = """# PRP-TEST

## EXAMPLES

No code blocks here, just text.
"""
    prp_file = tmp_path / "empty_examples.md"
    prp_file.write_text(prp_content)

    with pytest.raises(ValueError, match="No code blocks found"):
        extract_patterns_from_prp(str(prp_file))


def test_multiple_languages(tmp_path):
    """Test extraction from multiple language examples."""
    prp_content = """# PRP-TEST

## EXAMPLES

```python
def python_function():
    pass
```

```typescript
function tsFunction() {}
```

```go
func goFunction() {}
```
"""
    prp_file = tmp_path / "multi_lang.md"
    prp_file.write_text(prp_content)

    patterns = extract_patterns_from_prp(str(prp_file))
    assert len(patterns["raw_examples"]) == 3
    assert patterns["raw_examples"][0]["language"] == "python"
    assert patterns["raw_examples"][1]["language"] == "typescript"
    assert patterns["raw_examples"][2]["language"] == "go"
