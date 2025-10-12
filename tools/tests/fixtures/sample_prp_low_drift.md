---
name: "Sample PRP - Low Drift"
prp_id: "TEST-001"
status: "new"
---

# TEST-001: Sample PRP - Low Drift

## FEATURE
Simple data validation function.

## EXAMPLES

```python
def validate_data(data: dict) -> bool:
    """Validate input data using snake_case naming."""
    if not data:
        return False

    try:
        result = check_schema(data)
        return result
    except ValidationError:
        return False
```

## IMPLEMENTATION BLUEPRINT

### Phase 1
**Files to Create**:
- `tools/tests/fixtures/sample_implementation_low.py`
