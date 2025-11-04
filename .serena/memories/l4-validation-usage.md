---
type: regular
category: documentation
tags: [validation, testing, l4]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---

# Level 4 Pattern Conformance Validation - Usage Guide

## Overview

L4 validation detects architectural drift between PRP EXAMPLES and implementation code using semantic pattern analysis.

## Key Modules

### 1. code_analyzer.py (Shared Module)
**Single source of truth for pattern detection**

```python
from ce.code_analyzer import (
    analyze_code_patterns,
    determine_language,
    count_code_symbols
)

# Analyze code patterns
patterns = analyze_code_patterns(code="def foo(): pass", language="python")
# Returns: {"code_structure": ["functional"], "naming_conventions": ["snake_case"], ...}

# Determine language from file extension
lang = determine_language(".py")  # Returns: "python"

# Count code symbols (functions, classes, methods)
count = count_code_symbols(code="def foo(): pass\nclass Bar: pass", language="python")
# Returns: 2
```

### 2. pattern_extractor.py
**Extracts patterns from PRP EXAMPLES section**

```python
from ce.pattern_extractor import extract_patterns_from_prp

patterns = extract_patterns_from_prp("PRPs/PRP-X.md")
# Returns: {
#   "code_structure": ["async/await", "class-based"],
#   "error_handling": ["try-except"],
#   "naming_conventions": ["snake_case", "PascalCase"],
#   "test_patterns": ["pytest"],
#   "raw_examples": [{"language": "python", "code": "..."}]
# }
```

### 3. drift_analyzer.py
**Calculates drift between expected and actual patterns**

```python
from ce.drift_analyzer import (
    analyze_implementation,
    calculate_drift_score,
    get_auto_fix_suggestions
)

# Analyze implementation files
analysis = analyze_implementation(
    prp_path="PRPs/PRP-X.md",
    implementation_paths=["src/feature.py"]
)

# Calculate drift score
drift = calculate_drift_score(expected_patterns, detected_patterns)
# Returns: {
#   "drift_score": 15.0,  # 0-100%
#   "threshold_action": "auto_fix",  # auto_accept | auto_fix | escalate
#   "category_scores": {"code_structure": 10.0, ...},
#   "mismatches": [...]
# }

# Get auto-fix suggestions
suggestions = get_auto_fix_suggestions(drift["mismatches"])
```

### 4. validate.py
**L4 validation orchestration**

```python
from ce.validate import validate_level_4, calculate_confidence

# Run L4 validation
result = validate_level_4(
    prp_path="PRPs/PRP-X.md",
    implementation_paths=["src/feature.py"]  # Optional - auto-detects if None
)

# Calculate confidence score (includes L4 result)
results = {1: {...}, 2: {...}, 3: {...}, 4: result}
confidence = calculate_confidence(results)  # Returns: 1-10
```

## CLI Usage

```bash
# Run L4 validation on a PRP
ce validate --level 4 --prp PRPs/PRP-X.md --files src/feature.py

# Auto-detect implementation files from PRP or git
ce validate --level 4 --prp PRPs/PRP-X.md

# Run all validation levels
ce validate --level all
```

## Drift Thresholds

- **0-10% drift**: Auto-accept (pattern variations acceptable)
- **10-30% drift**: Auto-fix (display suggestions, continue)
- **30%+ drift**: Escalate (interactive user decision required)

## Pattern Categories

1. **code_structure**: async/await, class-based, functional, decorators
2. **error_handling**: try-except, early-return, null-checks
3. **naming_conventions**: snake_case, camelCase, PascalCase, _private
4. **data_flow**: props, state, context, closure
5. **test_patterns**: pytest, jest, unittest, fixtures
6. **import_patterns**: relative, absolute

## User Escalation (30%+ drift)

When drift ≥ 30%, L4 prompts user:

```
🚨 HIGH DRIFT DETECTED: 45.2%

OPTIONS:
[A] Accept drift (add DRIFT_JUSTIFICATION to PRP)
[R] Reject and halt (requires manual refactoring)
[U] Update EXAMPLES in PRP (update specification)
[Q] Quit without saving
```

Decisions are persisted to PRP YAML header for audit trail.

## Confidence Scoring

L4 validation adds +1 to confidence score when:
- Drift < 10% (auto-accept), OR
- Drift < 30% AND user accepted with justification

Maximum achievable: 10/10 (production-ready)

## Code Consolidation

**Before**: 780 LOC across pattern_extractor.py + drift_analyzer.py  
**After**: 697 LOC with shared code_analyzer.py module  
**Savings**: 83 LOC (11% reduction), single source of truth
