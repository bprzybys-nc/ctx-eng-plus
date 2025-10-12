# Level 4 Pattern Conformance Validation - Example

This example demonstrates how to use L4 validation to detect architectural drift between PRP specifications and implementation code.

## Scenario: API Client Implementation

### 1. PRP with EXAMPLES

```markdown
---
name: "API Client Implementation"
prp_id: "PRP-42"
---

# PRP-42: API Client Implementation

## EXAMPLES

```python
# Pattern: async/await, try-except, snake_case naming
async def fetch_user_data(user_id: int) -> dict:
    """Fetch user data from API."""
    try:
        response = await http_client.get(f"/users/{user_id}")
        return response.json()
    except HTTPError as e:
        logger.error(f"Failed to fetch user {user_id}: {e}")
        raise

class APIClient:
    """API client using snake_case and PascalCase."""

    def __init__(self, base_url: str):
        self.base_url = base_url
```
```

## IMPLEMENTATION BLUEPRINT
- Create: `src/api_client.py`
```

### 2. Implementation (Low Drift - 5%)

**File**: `src/api_client.py`

```python
# ✅ GOOD: Matches patterns from EXAMPLES
import logging
from typing import Dict

logger = logging.getLogger(__name__)

async def fetch_user_data(user_id: int) -> Dict:
    """Fetch user data from API."""
    try:
        response = await http_client.get(f"/users/{user_id}")
        return response.json()
    except HTTPError as e:
        logger.error(f"Failed to fetch user {user_id}: {e}")
        raise

class APIClient:
    """API client implementation."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self._session = None  # Added feature
```

**L4 Validation Result**:
```bash
$ ce validate --level 4 --prp PRPs/PRP-42.md

✅ L4 VALIDATION PASSED
Drift Score: 5.0%
Action: auto_accept
Duration: 0.8s
```

### 3. Implementation (Medium Drift - 18%)

**File**: `src/api_client.py`

```python
# ⚠️  MEDIUM: Some deviations from patterns
import logging

logger = logging.getLogger(__name__)

# Changed to synchronous (deviation from async/await pattern)
def fetch_user_data(user_id: int) -> dict:
    """Fetch user data from API."""
    try:
        response = http_client.get(f"/users/{user_id}")
        return response.json()
    except HTTPError as e:
        logger.error(f"Failed to fetch user {user_id}: {e}")
        raise

class APIClient:
    """API client implementation."""

    def __init__(self, base_url: str):
        self.base_url = base_url
```

**L4 Validation Result**:
```bash
$ ce validate --level 4 --prp PRPs/PRP-42.md

⚠️  MODERATE DRIFT DETECTED - SUGGESTIONS:
   ⚠️  Convert to async/await pattern (expected in EXAMPLES)

✅ L4 VALIDATION PASSED (with warnings)
Drift Score: 18.0%
Action: auto_fix
Duration: 0.9s
```

### 4. Implementation (High Drift - 45%)

**File**: `src/api_client.py`

```python
# ❌ BAD: Major deviations from patterns
import logging

logger = logging.getLogger(__name__)

# Multiple issues:
# - Synchronous instead of async/await
# - camelCase instead of snake_case
# - No try-except error handling
# - Different structure

def fetchUserData(userId):  # camelCase (drift from snake_case)
    response = http_client.get(f"/users/{userId}")  # No error handling
    return response.json()

class ApiClient:  # Should be APIClient (PascalCase convention)
    def __init__(self, baseUrl):  # camelCase (drift)
        self.baseUrl = baseUrl
```

**L4 Validation Result**:
```bash
$ ce validate --level 4 --prp PRPs/PRP-42.md

================================================================================
🚨 HIGH DRIFT DETECTED: 45.0%
================================================================================

PRP: PRPs/PRP-42.md
Implementation: src/api_client.py

DRIFT BREAKDOWN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Category              Expected       Detected      Drift
────────────────────────────────────────────────────────────────────────────────
code_structure        async/await    synchronous   50.0%
error_handling        try-except     none          100.0%
naming_conventions    snake_case     camelCase     80.0%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AFFECTED PATTERNS:
• code_structure: Expected 'async/await', Detected ['synchronous']
• error_handling: Expected 'try-except', Detected None
• naming_conventions: Expected 'snake_case', Detected ['camelCase']

OPTIONS:
[A] Accept drift (add DRIFT_JUSTIFICATION to PRP)
[R] Reject and halt (requires manual refactoring)
[U] Update EXAMPLES in PRP (update specification)
[Q] Quit without saving

Your choice (A/R/U/Q): R

❌ L4 validation REJECTED - Manual refactoring required
```

## Using the Shared Module

### Pattern Analysis

```python
from ce.code_analyzer import analyze_code_patterns

code = """
async def fetch_data(id: int) -> dict:
    try:
        result = await api.get(id)
        return result
    except Exception as e:
        logger.error(e)
        raise
"""

patterns = analyze_code_patterns(code, "python")
print(patterns)
# Output:
# {
#   "code_structure": ["async/await", "functional"],
#   "error_handling": ["try-except"],
#   "naming_conventions": ["snake_case"],
#   "data_flow": [],
#   "test_patterns": [],
#   "import_patterns": []
# }
```

### Language Detection

```python
from ce.code_analyzer import determine_language

lang = determine_language(".ts")   # Returns: "typescript"
lang = determine_language(".py")   # Returns: "python"
lang = determine_language(".js")   # Returns: "javascript"
```

### Symbol Counting

```python
from ce.code_analyzer import count_code_symbols

code = """
def foo(): pass
def bar(): pass
class Baz: pass
"""

count = count_code_symbols(code, "python")
print(count)  # Output: 3
```

## Drift Decision Persistence

When user accepts high drift, decision is saved to PRP YAML header:

```yaml
---
name: "API Client Implementation"
prp_id: "PRP-42"
drift_decision:
  score: 45.0
  action: "accepted"
  justification: "Legacy synchronous API required for compatibility with existing infrastructure"
  timestamp: "2025-10-12T18:45:00Z"
  category_breakdown:
    code_structure: 50.0
    error_handling: 100.0
    naming_conventions: 80.0
  reviewer: "human"
---
```

## Best Practices

1. **Keep EXAMPLES aligned**: Update PRP EXAMPLES when patterns change intentionally
2. **Document drift justifications**: Always provide clear reasons for accepting high drift
3. **Run L4 early**: Detect drift during development, not at PR review
4. **Use auto-detection**: Let L4 find implementation files from PRP or git
5. **Review suggestions**: Act on auto-fix suggestions for 10-30% drift

## Integration with CI/CD

```bash
# In CI pipeline
ce validate --level all --json > validation-results.json

# Check confidence score
CONFIDENCE=$(jq '.confidence_score' validation-results.json)
if [ "$CONFIDENCE" -lt 9 ]; then
  echo "❌ Confidence score too low: $CONFIDENCE/10"
  exit 1
fi
```

## Summary

- **Low drift (0-10%)**: Auto-accept, continue
- **Medium drift (10-30%)**: Display suggestions, continue
- **High drift (30%+)**: Require human decision
- **All tests passing**: Confidence score can reach 10/10

Level 4 validation ensures implementations stay aligned with architectural specifications while allowing justified deviations when needed.
