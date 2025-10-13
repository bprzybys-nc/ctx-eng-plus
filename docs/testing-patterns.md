# Testing Patterns with Strategy Pattern

## Overview

Context Engineering uses strategy pattern for composable testing with three distinct patterns:
- **Unit tests**: Single node in isolation, all dependencies mocked
- **Integration tests**: Real nodes with some dependencies mocked
- **E2E tests**: Full pipeline with all external dependencies mocked

## Quick Start

### Unit Test Pattern

Test single strategy in isolation:

```python
from ce.testing.mocks import MockSerenaStrategy

def test_mock_serena():
    strategy = MockSerenaStrategy(canned_results=[
        {"file": "test.py", "match": "def test(): pass"}
    ])
    result = strategy.execute({"pattern": "def test"})

    assert result["success"] is True
    assert len(result["results"]) == 1
```

### Integration Test Pattern

Test subgraph with real + mock strategies:

```python
from ce.testing.builder import PipelineBuilder
from ce.testing.real_strategies import RealParserStrategy
from ce.testing.mocks import MockSerenaStrategy

def test_parse_and_research():
    pipeline = (
        PipelineBuilder(mode="integration")
        .add_node("parse", RealParserStrategy())
        .add_node("research", MockSerenaStrategy(canned_results=[...]))
        .add_edge("parse", "research")
        .build()
    )
    result = pipeline.execute({"prp_path": "test.md"})
```

### E2E Test Pattern

Test full pipeline with mocked external dependencies:

```python
from ce.testing.builder import PipelineBuilder
from ce.testing.real_strategies import RealParserStrategy
from ce.testing.mocks import MockSerenaStrategy, MockContext7Strategy, MockLLMStrategy

def test_full_generation():
    pipeline = (
        PipelineBuilder(mode="e2e")
        .add_node("parse", RealParserStrategy())
        .add_node("research", MockSerenaStrategy(canned_results=[...]))
        .add_node("docs", MockContext7Strategy(cached_docs="..."))
        .add_node("generate", MockLLMStrategy(template="..."))
        .add_edge("parse", "research")
        .add_edge("research", "docs")
        .add_edge("docs", "generate")
        .build()
    )
    result = pipeline.execute({"prp_path": "INITIAL.md"})
```

## Migration Guide

### Before (Ad-hoc Mocking)

```python
from unittest.mock import MagicMock, patch

def test_old_way():
    mock_serena = MagicMock()
    mock_serena.search = Mock(return_value=[...])

    with patch('ce.serena', mock_serena):
        result = function_under_test()
```

### After (Strategy Pattern)

```python
from ce.testing.mocks import MockSerenaStrategy

def test_new_way():
    strategy = MockSerenaStrategy(canned_results=[...])
    result = strategy.execute({"pattern": "test"})
```

## Observable Mocking

Pipeline builder logs mocked nodes during build:

```
🎭 MOCKED NODES: research, docs, generate
```

Clear indication of what's real vs mocked in your tests.

## Available Strategies

### Mock Strategies

**MockSerenaStrategy**: Codebase search operations
```python
strategy = MockSerenaStrategy(canned_results=[
    {"file": "test.py", "match": "def test(): pass"}
])
```

**MockContext7Strategy**: Documentation fetching
```python
strategy = MockContext7Strategy(cached_docs="pytest fixtures...")
```

**MockLLMStrategy**: Text generation with templates
```python
strategy = MockLLMStrategy(template="# {title}\n\n{content}")
```

### Real Strategies

**RealParserStrategy**: PRP blueprint parsing
```python
from ce.testing.real_strategies import RealParserStrategy

strategy = RealParserStrategy()
result = strategy.execute({"prp_path": "PRPs/PRP-1.md"})
```

**RealCommandStrategy**: Shell command execution
```python
from ce.testing.real_strategies import RealCommandStrategy

strategy = RealCommandStrategy()
result = strategy.execute({"cmd": "pytest tests/ -v"})
```

## Creating Custom Strategies

### Real Strategy

```python
from ce.testing.strategy import BaseRealStrategy

class MyRealStrategy(BaseRealStrategy):
    def execute(self, input_data):
        # Call actual service/function
        result = my_real_function(input_data["param"])
        return {"success": True, "data": result}
```

### Mock Strategy

```python
from ce.testing.strategy import BaseMockStrategy

class MyMockStrategy(BaseMockStrategy):
    def __init__(self, canned_data):
        self.data = canned_data

    def execute(self, input_data):
        # Return canned data
        return {"success": True, "data": self.data}
```

## Best Practices

### 1. Use Observable Mocking

Always build pipelines to see which nodes are mocked:

```python
pipeline = builder.build()  # Prints: 🎭 MOCKED NODES: ...
```

### 2. Keep Strategies Focused

Each strategy should have a single responsibility:

```python
# ✅ GOOD - Single responsibility
class ParseStrategy:
    def execute(self, input_data):
        return parse_blueprint(input_data["prp_path"])

# ❌ BAD - Multiple responsibilities
class ParseAndValidateStrategy:
    def execute(self, input_data):
        phases = parse_blueprint(input_data["prp_path"])
        validate_phases(phases)  # Too much!
        return phases
```

### 3. Test Data Flow

Ensure data flows correctly between nodes:

```python
def test_data_flow():
    pipeline = (
        PipelineBuilder(mode="integration")
        .add_node("step1", Strategy1())  # Returns {"value": 5}
        .add_node("step2", Strategy2())  # Uses input_data["value"]
        .add_edge("step1", "step2")
        .build()
    )

    result = pipeline.execute({"initial": "data"})
    # step2 should receive output from step1
```

### 4. Use Appropriate Test Mode

- **Unit**: Testing single strategy logic
- **Integration**: Testing 2-3 connected strategies
- **E2E**: Testing full pipeline end-to-end

### 5. Mock External Dependencies Only

Keep internal logic real, mock external APIs:

```python
# ✅ GOOD - Real internal logic, mocked external APIs
PipelineBuilder(mode="e2e")
.add_node("parse", RealParserStrategy())  # Internal - real
.add_node("search", MockSerenaStrategy())  # External - mock
.add_node("llm", MockLLMStrategy())  # External - mock
```

## Running Tests

```bash
# All testing framework tests
cd tools && uv run pytest tests/test_strategy.py tests/test_mocks.py tests/test_builder.py -v

# Composition pattern examples
cd tools && uv run pytest tests/test_pipeline_composition.py -v

# Real strategy tests
cd tools && uv run pytest tests/test_real_strategies.py -v
```

## Token Savings

Mocked LLM strategies save ~5000 tokens per call:

```python
result = mock_llm.execute({"context": {...}})
assert result["tokens_saved"] == 5000  # Per LLM call avoided
```

For E2E tests with multiple LLM calls, this adds up to significant savings in CI/CD.

## Examples

See [test_pipeline_composition.py](../tools/tests/test_pipeline_composition.py) for comprehensive examples of all three patterns.

## Further Reading

- **Strategy Pattern**: Gang of Four Design Patterns
- **Builder Pattern**: Fluent API for object construction
- **Protocol (PEP 544)**: Structural subtyping in Python
- **pytest fixtures**: Test setup and teardown patterns
