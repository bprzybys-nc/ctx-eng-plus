# Mock Marking Pattern

## Purpose
Ensure temporary mock implementations are visible, trackable, and easily removable during refactoring.

## Policy
**MANDATORY**: All mocked functionality in non-test code must be explicitly marked.

## Marking Requirements

### 1. Decorator
```python
@mocked  # Required for all mock functions/methods
```

### 2. Inline Comments
```python
# FIXME: Mock implementation - replace with real functionality
# MOCKED: Hardcoded return value
```

### 3. Logging Statement
```python
logger.warning("MOCK: Using hardcoded response")
```

## Examples

### ✅ Correct Mock Marking
```python
@mocked
def fetch_api_data(endpoint: str) -> dict:
    """Fetch data from API endpoint."""
    # FIXME: Mock implementation - returns fake data
    logger.warning("MOCK: fetch_api_data returning hardcoded response")
    return {"status": "success", "data": []}  # MOCKED: Fake data
```

### ❌ Incorrect - Unmarked Mock
```python
def fetch_api_data(endpoint: str) -> dict:
    """Fetch data from API endpoint."""
    return {"status": "success", "data": []}  # No indication this is fake!
```

## Replacement Process

**When replacing mock with real implementation:**

1. **Remove decorator**: Delete `@mocked`
2. **Remove comments**: Delete `FIXME`/`MOCKED` tags
3. **Update logging**: Replace warning with appropriate level
4. **Implement real logic**: Replace hardcoded returns

### Example Refactoring

**Before (Mock):**
```python
@mocked
def fetch_api_data(endpoint: str) -> dict:
    """Fetch data from API endpoint."""
    # FIXME: Mock implementation
    logger.warning("MOCK: fetch_api_data returning hardcoded response")
    return {"status": "success", "data": []}  # MOCKED: Fake data
```

**After (Real):**
```python
def fetch_api_data(endpoint: str) -> dict:
    """Fetch data from API endpoint."""
    logger.debug(f"Fetching data from {endpoint}")
    response = requests.get(f"{API_BASE}/{endpoint}")
    response.raise_for_status()
    return response.json()
```

## Rationale

- **Transparency**: Makes technical debt visible
- **Searchability**: Easy to find all mocks via `grep "@mocked"`
- **Safety**: Prevents mocks from reaching production silently
- **Refactoring**: Clear removal checklist

## Related Patterns

- **No Fishy Fallbacks**: Mocks should fail fast, not hide errors
- **Real Functionality Testing**: Tests must validate real implementations