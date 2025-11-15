---
prp_id: "34.2.2"
feature_name: "Classification Module (Phase B)"
status: pending
created: "2025-11-05T00:00:00Z"
updated: "2025-11-05T00:00:00Z"
complexity: medium
estimated_hours: 1.5
dependencies: ["34.1.1"]
files_modified: ["tools/ce/blending/classification.py"]
stage: "stage-2-parallel"
execution_order: 3
merge_order: 3
conflict_potential: "NONE"
worktree_path: "../ctx-eng-plus-prp-34-2-2"
branch_name: "prp-34-2-2-classification-module"
batch_context: "Phase B of 4-phase pipeline. Uses Haiku for fast, cheap validation."
---

# Classification Module (Phase B)

## 1. TL;DR

**Objective**: Implement CE pattern validator using Claude 4.5 Haiku for fast classification with confidence scoring

**What**: Create classification module that validates PRPs, examples, and memories with confidence scoring, gracefully handles PRPs without YAML headers, and filters garbage files

**Why**: Phase B of the Bucket Initialization pipeline needs fast, cheap validation of collected files before processing. Haiku provides 90% cost reduction vs Sonnet while maintaining accuracy for classification tasks.

**Effort**: 1.5 hours

**Dependencies**: PRP-34.1.1 (Bucket Collection Module)

**Files Modified**:
- `tools/ce/blending/classification.py` (new file)

## 2. Context

### Background

The Bucket Initialization workflow collects files from 5 source locations (.serena/memories/, examples/, PRPs/, CLAUDE.md, .claude/). Phase B (Classification) validates these files to determine:

1. **File Type**: Is this a valid PRP, example, memory, or garbage?
2. **Confidence**: How certain are we about this classification (0.0-1.0)?
3. **Issues**: What validation issues were found?

**Key Requirements**:
- **Fast**: Classification must be sub-second for most files (Haiku < 200ms)
- **Cheap**: 90% cost reduction vs Sonnet (Haiku $0.25/MTok vs Sonnet $3/MTok)
- **Graceful**: Handle older PRPs without YAML headers (check PRP ID in content)
- **Garbage Filtering**: Reject *REPORT*.md, *INITIAL*.md, summary files, analysis docs

### Constraints and Considerations

**PRP Validation Without YAML**:
- Older PRPs may not have YAML frontmatter
- Must check for PRP ID pattern in content: `PRP-\d+` or `prp_id: "?[\d.]+"?`
- YAML header is optional but preferred
- Standard sections (TL;DR, Context, Implementation, Validation) are optional

**Confidence Scoring**:
- **0.9-1.0**: High confidence (deterministic checks pass)
- **0.6-0.9**: Medium confidence (some checks pass, Haiku classifies)
- **0.0-0.6**: Low confidence (reject as invalid)

**Garbage Patterns to Filter**:
```
*REPORT*.md
*INITIAL*.md
*summary*.md
*analysis*.md
*PLAN*.md
*TODO*.md
```

**Haiku API Usage**:
- Model: `claude-4-5-haiku-20250929`
- Max tokens: 1024 (classification response)
- Temperature: 0.0 (deterministic)
- System prompt: Classification instructions with examples
- Response format: JSON with `{valid: bool, confidence: float, issues: List[str]}`

### Documentation References

**Anthropic API Documentation**:
- Messages API: https://docs.anthropic.com/en/api/messages
- Model pricing: https://docs.anthropic.com/en/docs/about-claude/models
- Best practices: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering

**CE Framework Standards**:
- Memory type system: `.serena/memories/README.md`
- PRP structure: `examples/templates/PRP-0-CONTEXT-ENGINEERING.md`
- YAML headers: `CLAUDE.md` (Framework Initialization section)

## 3. Implementation Steps

### Phase 1: Setup Module Structure (15 min)

**Step 1.1**: Create classification module file
```bash
touch tools/ce/blending/classification.py
```

**Step 1.2**: Add module docstring and imports
```python
"""
Classification Module (Phase B) - Bucket Initialization Pipeline

Validates collected files using Claude 4.5 Haiku for fast, cheap classification.

Functions:
- validate_prp(file_path: str) -> ClassificationResult
- validate_example(file_path: str) -> ClassificationResult
- validate_memory(file_path: str) -> ClassificationResult
- classify_with_haiku(file_path: str, file_type: str) -> ClassificationResult
- is_garbage(file_path: str) -> bool

Classification Result:
{
  "valid": bool,
  "confidence": float,  # 0.0-1.0
  "issues": List[str],
  "file_type": str,     # "prp", "example", "memory", "garbage"
}
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import anthropic
import os
```

**Step 1.3**: Define ClassificationResult dataclass
```python
@dataclass
class ClassificationResult:
    """Result of file classification."""
    valid: bool
    confidence: float
    issues: List[str]
    file_type: str  # "prp", "example", "memory", "garbage"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "valid": self.valid,
            "confidence": self.confidence,
            "issues": self.issues,
            "file_type": self.file_type
        }
```

### Phase 2: Implement Deterministic Validators (30 min)

**Step 2.1**: Implement garbage filter
```python
def is_garbage(file_path: str) -> bool:
    """
    Check if file matches garbage patterns.

    Garbage patterns:
    - *REPORT*.md
    - *INITIAL*.md
    - *summary*.md
    - *analysis*.md
    - *PLAN*.md
    - *TODO*.md

    Args:
        file_path: Path to file

    Returns:
        True if file is garbage, False otherwise
    """
    filename = Path(file_path).name.lower()
    garbage_patterns = [
        "report", "initial", "summary",
        "analysis", "plan", "todo"
    ]

    return any(pattern in filename for pattern in garbage_patterns)
```

**Step 2.2**: Implement PRP validator
```python
def validate_prp(file_path: str) -> ClassificationResult:
    """
    Validate PRP file.

    Validation checks (in priority order):
    1. File is not garbage (required)
    2. PRP ID exists in content or YAML (required)
    3. YAML header exists (optional, +0.2 confidence)
    4. Standard sections exist (optional, +0.1 confidence)

    Args:
        file_path: Path to PRP file

    Returns:
        ClassificationResult with validation outcome
    """
    issues = []
    confidence = 0.6  # Base confidence

    # Check garbage first
    if is_garbage(file_path):
        return ClassificationResult(
            valid=False,
            confidence=1.0,
            issues=["File matches garbage pattern"],
            file_type="garbage"
        )

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return ClassificationResult(
            valid=False,
            confidence=1.0,
            issues=[f"Failed to read file: {e}"],
            file_type="unknown"
        )

    # Check for PRP ID in content (required)
    prp_id_pattern = r'(?:PRP-\d+(?:\.\d+)*|prp_id:\s*["\']?[\d.]+["\']?)'
    if not re.search(prp_id_pattern, content, re.IGNORECASE):
        issues.append("No PRP ID found in content or YAML")
        return ClassificationResult(
            valid=False,
            confidence=0.9,
            issues=issues,
            file_type="unknown"
        )

    # Check for YAML header (optional, +0.2 confidence)
    if re.match(r'^---\s*\n', content):
        confidence += 0.2
    else:
        issues.append("No YAML header (optional but recommended)")

    # Check for standard sections (optional, +0.1 confidence)
    standard_sections = ["TL;DR", "Context", "Implementation", "Validation"]
    found_sections = sum(1 for section in standard_sections if section in content)
    if found_sections >= 3:
        confidence += 0.1
    else:
        issues.append(f"Found {found_sections}/4 standard sections (optional)")

    # Cap confidence at 0.9 for deterministic validation
    confidence = min(confidence, 0.9)

    return ClassificationResult(
        valid=True,
        confidence=confidence,
        issues=issues,
        file_type="prp"
    )
```

**Step 2.3**: Implement example validator
```python
def validate_example(file_path: str) -> ClassificationResult:
    """
    Validate example file.

    Validation checks:
    1. File is not garbage (required)
    2. H1 title exists (required)
    3. H2 sections exist (optional, +0.2 confidence)
    4. Code blocks exist (optional, +0.2 confidence)
    5. Substantial content (>500 chars, optional, +0.1 confidence)

    Args:
        file_path: Path to example file

    Returns:
        ClassificationResult with validation outcome
    """
    issues = []
    confidence = 0.5  # Base confidence

    # Check garbage first
    if is_garbage(file_path):
        return ClassificationResult(
            valid=False,
            confidence=1.0,
            issues=["File matches garbage pattern"],
            file_type="garbage"
        )

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return ClassificationResult(
            valid=False,
            confidence=1.0,
            issues=[f"Failed to read file: {e}"],
            file_type="unknown"
        )

    # Check for H1 title (required)
    if not re.search(r'^#\s+.+', content, re.MULTILINE):
        issues.append("No H1 title found")
        return ClassificationResult(
            valid=False,
            confidence=0.9,
            issues=issues,
            file_type="unknown"
        )

    # Check for H2 sections (optional, +0.2 confidence)
    h2_sections = re.findall(r'^##\s+.+', content, re.MULTILINE)
    if len(h2_sections) >= 2:
        confidence += 0.2
    else:
        issues.append(f"Found {len(h2_sections)} H2 sections (recommended: ≥2)")

    # Check for code blocks (optional, +0.2 confidence)
    code_blocks = re.findall(r'```.*?```', content, re.DOTALL)
    if len(code_blocks) >= 1:
        confidence += 0.2
    else:
        issues.append("No code blocks found (recommended for examples)")

    # Check substantial content (optional, +0.1 confidence)
    if len(content) > 500:
        confidence += 0.1
    else:
        issues.append(f"Short content ({len(content)} chars, recommended: >500)")

    return ClassificationResult(
        valid=True,
        confidence=confidence,
        issues=issues,
        file_type="example"
    )
```

**Step 2.4**: Implement memory validator
```python
def validate_memory(file_path: str) -> ClassificationResult:
    """
    Validate memory file.

    Validation checks:
    1. File is not garbage (required)
    2. YAML frontmatter exists (required)
    3. Type field in YAML (regular|critical|user, required)
    4. Created/updated timestamps (optional, +0.1 confidence)
    5. Category field (optional, +0.1 confidence)

    Args:
        file_path: Path to memory file

    Returns:
        ClassificationResult with validation outcome
    """
    issues = []
    confidence = 0.6  # Base confidence

    # Check garbage first
    if is_garbage(file_path):
        return ClassificationResult(
            valid=False,
            confidence=1.0,
            issues=["File matches garbage pattern"],
            file_type="garbage"
        )

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return ClassificationResult(
            valid=False,
            confidence=1.0,
            issues=[f"Failed to read file: {e}"],
            file_type="unknown"
        )

    # Check for YAML frontmatter (required)
    if not re.match(r'^---\s*\n', content):
        issues.append("No YAML frontmatter found")
        return ClassificationResult(
            valid=False,
            confidence=0.9,
            issues=issues,
            file_type="unknown"
        )

    # Extract YAML header
    yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not yaml_match:
        issues.append("Malformed YAML frontmatter")
        return ClassificationResult(
            valid=False,
            confidence=0.9,
            issues=issues,
            file_type="unknown"
        )

    yaml_content = yaml_match.group(1)

    # Check for type field (required)
    type_match = re.search(r'type:\s*(regular|critical|user)', yaml_content)
    if not type_match:
        issues.append("No valid type field (must be: regular, critical, or user)")
        return ClassificationResult(
            valid=False,
            confidence=0.9,
            issues=issues,
            file_type="unknown"
        )

    confidence += 0.2  # Valid type field

    # Check for created/updated timestamps (optional, +0.1 confidence)
    if re.search(r'created:\s*["\']?\d{4}-\d{2}-\d{2}', yaml_content):
        confidence += 0.05
    else:
        issues.append("No created timestamp (optional)")

    if re.search(r'updated:\s*["\']?\d{4}-\d{2}-\d{2}', yaml_content):
        confidence += 0.05
    else:
        issues.append("No updated timestamp (optional)")

    # Check for category field (optional, +0.1 confidence)
    if re.search(r'category:\s*\w+', yaml_content):
        confidence += 0.1
    else:
        issues.append("No category field (optional)")

    return ClassificationResult(
        valid=True,
        confidence=confidence,
        issues=issues,
        file_type="memory"
    )
```

### Phase 3: Implement Haiku Classifier (30 min)

**Step 3.1**: Create Haiku classification function
```python
def classify_with_haiku(file_path: str, file_type: str) -> ClassificationResult:
    """
    Classify file using Claude 4.5 Haiku for uncertain cases.

    Used when deterministic validation has confidence < 0.9.

    Args:
        file_path: Path to file
        file_type: Expected file type ("prp", "example", "memory")

    Returns:
        ClassificationResult from Haiku analysis
    """
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return ClassificationResult(
            valid=False,
            confidence=1.0,
            issues=[f"Failed to read file: {e}"],
            file_type="unknown"
        )

    # Prepare system prompt based on file type
    system_prompts = {
        "prp": """You are a PRP (Product Requirements Prompt) validator.

Analyze the file and determine:
1. Is this a valid PRP? (contains PRP ID, describes a feature/task)
2. Confidence level (0.0-1.0)
3. Any issues found

Respond in JSON format:
{
  "valid": true/false,
  "confidence": 0.0-1.0,
  "issues": ["issue1", "issue2", ...]
}

Valid PRP indicators:
- Contains PRP ID (PRP-X or prp_id: X)
- Describes a feature or task
- Has implementation steps or acceptance criteria

Invalid indicators:
- Garbage file (REPORT, INITIAL, summary, analysis)
- No clear feature description
- Empty or minimal content""",

        "example": """You are an example file validator.

Analyze the file and determine:
1. Is this a valid example? (demonstrates code patterns, has explanations)
2. Confidence level (0.0-1.0)
3. Any issues found

Respond in JSON format:
{
  "valid": true/false,
  "confidence": 0.0-1.0,
  "issues": ["issue1", "issue2", ...]
}

Valid example indicators:
- Contains code blocks
- Has explanatory text
- Demonstrates patterns or best practices

Invalid indicators:
- Garbage file (REPORT, INITIAL, summary)
- No code or minimal content
- Just a file listing""",

        "memory": """You are a Serena memory validator.

Analyze the file and determine:
1. Is this a valid memory? (has YAML frontmatter with type field)
2. Confidence level (0.0-1.0)
3. Any issues found

Respond in JSON format:
{
  "valid": true/false,
  "confidence": 0.0-1.0,
  "issues": ["issue1", "issue2", ...]
}

Valid memory indicators:
- Has YAML frontmatter with --- delimiters
- Contains type field (regular, critical, or user)
- Has meaningful content

Invalid indicators:
- No YAML frontmatter
- No type field
- Garbage file (REPORT, INITIAL)"""
    }

    system_prompt = system_prompts.get(file_type, system_prompts["prp"])

    # Call Haiku API
    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        message = client.messages.create(
            model="claude-4-5-haiku-20250929",
            max_tokens=1024,
            temperature=0.0,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Classify this file:\n\n{content[:4000]}"  # Limit to 4000 chars
                }
            ]
        )

        # Parse JSON response
        response_text = message.content[0].text

        # Extract JSON from response (may have markdown code blocks)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            return ClassificationResult(
                valid=False,
                confidence=0.5,
                issues=["Haiku returned invalid JSON"],
                file_type="unknown"
            )

        import json
        result = json.loads(json_match.group(0))

        return ClassificationResult(
            valid=result.get("valid", False),
            confidence=result.get("confidence", 0.5),
            issues=result.get("issues", []),
            file_type=file_type if result.get("valid") else "unknown"
        )

    except anthropic.APIError as e:
        return ClassificationResult(
            valid=False,
            confidence=0.5,
            issues=[f"Haiku API error: {e}"],
            file_type="unknown"
        )
    except Exception as e:
        return ClassificationResult(
            valid=False,
            confidence=0.5,
            issues=[f"Classification error: {e}"],
            file_type="unknown"
        )
```

### Phase 4: Main Classification Interface (15 min)

**Step 4.1**: Create main classification function
```python
def classify_file(file_path: str, expected_type: Optional[str] = None) -> ClassificationResult:
    """
    Classify a file using deterministic validation + Haiku fallback.

    Process:
    1. Run deterministic validator based on expected_type or file location
    2. If confidence < 0.9, call classify_with_haiku()
    3. Return final classification result

    Args:
        file_path: Path to file
        expected_type: Expected file type ("prp", "example", "memory"), or None to infer

    Returns:
        ClassificationResult with final classification
    """
    # Infer expected type from file path if not provided
    if expected_type is None:
        path_lower = file_path.lower()
        if "prp" in path_lower:
            expected_type = "prp"
        elif "example" in path_lower:
            expected_type = "example"
        elif "memor" in path_lower or "serena" in path_lower:
            expected_type = "memory"
        else:
            expected_type = "prp"  # Default to PRP

    # Run deterministic validator
    validators = {
        "prp": validate_prp,
        "example": validate_example,
        "memory": validate_memory
    }

    validator = validators.get(expected_type, validate_prp)
    result = validator(file_path)

    # If garbage, return immediately
    if result.file_type == "garbage":
        return result

    # If confidence < 0.9, use Haiku for additional validation
    if result.confidence < 0.9:
        haiku_result = classify_with_haiku(file_path, expected_type)

        # Combine results (use Haiku's validation, average confidence)
        return ClassificationResult(
            valid=haiku_result.valid,
            confidence=(result.confidence + haiku_result.confidence) / 2,
            issues=result.issues + haiku_result.issues,
            file_type=haiku_result.file_type if haiku_result.valid else "unknown"
        )

    return result
```

**Step 4.2**: Add CLI interface function
```python
def main():
    """CLI interface for classification module."""
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python classification.py <file-path> [expected-type]")
        print("Expected types: prp, example, memory")
        sys.exit(1)

    file_path = sys.argv[1]
    expected_type = sys.argv[2] if len(sys.argv) > 2 else None

    result = classify_file(file_path, expected_type)

    print(json.dumps(result.to_dict(), indent=2))

    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
```

## 4. Validation Gates

### Gate 1: Garbage Filter Works

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
python -m ce.blending.classification /tmp/test-REPORT.md
```

**Expected Output**:
```json
{
  "valid": false,
  "confidence": 1.0,
  "issues": ["File matches garbage pattern"],
  "file_type": "garbage"
}
```

**Exit Code**: 1 (invalid)

### Gate 2: PRP Without YAML Validates

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools

# Create test PRP without YAML
cat > /tmp/test-prp.md << 'EOF'
# PRP-99: Test Feature

## Implementation
Build the thing.

## Validation
Test the thing.
EOF

python -m ce.blending.classification /tmp/test-prp.md prp
```

**Expected Output**:
```json
{
  "valid": true,
  "confidence": 0.6-0.9,
  "issues": ["No YAML header (optional but recommended)", ...],
  "file_type": "prp"
}
```

**Exit Code**: 0 (valid)

### Gate 3: Memory Validates Type Field

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools

# Create test memory
cat > /tmp/test-memory.md << 'EOF'
---
type: regular
category: documentation
created: "2025-11-05T00:00:00Z"
---

# Test Memory

This is a test memory.
EOF

python -m ce.blending.classification /tmp/test-memory.md memory
```

**Expected Output**:
```json
{
  "valid": true,
  "confidence": 0.8-1.0,
  "issues": [],
  "file_type": "memory"
}
```

**Exit Code**: 0 (valid)

### Gate 4: Haiku Classification Returns Valid JSON

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools

# Create ambiguous file (low confidence from deterministic validator)
cat > /tmp/test-ambiguous.md << 'EOF'
# Some Document

This could be a PRP or an example, unclear.

## Section 1
Some content here.
EOF

# Should trigger Haiku classification
python -m ce.blending.classification /tmp/test-ambiguous.md
```

**Expected Output**:
- Valid JSON with `valid`, `confidence`, `issues`, `file_type` fields
- Confidence combined from deterministic + Haiku
- Exit code 0 or 1 depending on Haiku's classification

### Gate 5: Haiku API Errors Handled Gracefully

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools

# Test with invalid API key
ANTHROPIC_API_KEY=invalid python -m ce.blending.classification /tmp/test-ambiguous.md
```

**Expected Output**:
```json
{
  "valid": false,
  "confidence": 0.5,
  "issues": ["Haiku API error: ..."],
  "file_type": "unknown"
}
```

**Exit Code**: 1 (error handled, not crash)

## 5. Testing Strategy

### Test Framework
pytest

### Test Command
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/ce/blending/test_classification.py -v
```

### Test Coverage

**Unit Tests** (15 tests):
1. `test_is_garbage_filters_report_files()`
2. `test_is_garbage_filters_initial_files()`
3. `test_is_garbage_passes_normal_files()`
4. `test_validate_prp_with_yaml_header()`
5. `test_validate_prp_without_yaml_header()`
6. `test_validate_prp_no_prp_id()`
7. `test_validate_prp_garbage_file()`
8. `test_validate_example_with_code_blocks()`
9. `test_validate_example_no_h1_title()`
10. `test_validate_example_garbage_file()`
11. `test_validate_memory_with_valid_yaml()`
12. `test_validate_memory_no_yaml()`
13. `test_validate_memory_invalid_type()`
14. `test_classify_with_haiku_prp()` (mocked Haiku response)
15. `test_classify_with_haiku_api_error()` (error handling)

**Integration Tests** (5 tests):
1. `test_classify_file_prp_high_confidence()` (no Haiku call)
2. `test_classify_file_prp_low_confidence()` (triggers Haiku)
3. `test_classify_file_infers_type_from_path()`
4. `test_classify_file_garbage_immediate_return()`
5. `test_main_cli_interface()` (CLI arguments)

### Mock Strategy

**Haiku API**: Mock `anthropic.Anthropic.messages.create()` to return JSON responses without real API calls.

**File System**: Use `pytest.tmp_path` fixture for temporary test files.

## 6. Rollout Plan

### Phase 1: Development (1.5 hours)

**6.1.1**: Create worktree and branch
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
git worktree add ../ctx-eng-plus-prp-34-2-2 -b prp-34-2-2-classification-module
cd ../ctx-eng-plus-prp-34-2-2
```

**6.1.2**: Implement classification module (1 hour)
- Follow implementation steps in Phase 1-4
- Write code in `tools/ce/blending/classification.py`
- Test manually with validation gates

**6.1.3**: Write tests (30 minutes)
```bash
mkdir -p tools/tests/ce/blending
touch tools/tests/ce/blending/test_classification.py
# Write 20 tests (unit + integration)
```

**6.1.4**: Run validation gates
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/../ctx-eng-plus-prp-34-2-2/tools
# Run all 5 validation gates
# Fix any issues found
```

### Phase 2: Testing (included in Phase 1)

Tests written and run during development (TDD approach).

### Phase 3: Documentation (included in implementation)

Module docstring and function docstrings written inline during implementation.

### Phase 4: Commit and Report (5 minutes)

**6.4.1**: Commit changes
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/../ctx-eng-plus-prp-34-2-2
git add tools/ce/blending/classification.py tools/tests/ce/blending/test_classification.py
git commit -m "PRP-34.2.2: Implement classification module with Haiku validation"
```

**6.4.2**: Return JSON report
```json
{
  "prp_id": "34.2.2",
  "status": "completed",
  "worktree_path": "../ctx-eng-plus-prp-34-2-2",
  "branch_name": "prp-34-2-2-classification-module",
  "files_created": [
    "tools/ce/blending/classification.py",
    "tools/tests/ce/blending/test_classification.py"
  ],
  "validation_gates_passed": 5,
  "tests_written": 20,
  "linear_issue_id": "TBD"
}
```

---

## Research Findings

### Dependency Analysis

**PRP-34.1.1 (Bucket Collection Module)** provides:
- `BucketCollectionResult` dataclass with collected files
- File paths from 5 source locations
- No classification or validation

**This PRP (34.2.2)** consumes:
- File paths from `BucketCollectionResult.collected_files`
- Validates each file and returns `ClassificationResult`

**Downstream consumers**:
- PRP-34.2.1 (Extract Module): Uses `valid=True` files only
- PRP-34.2.3 (Blending Module): Uses classified files for merging

### Haiku Performance Characteristics

**Cost Comparison** (per 1M tokens):
- Claude 4.5 Haiku: $0.25 input / $1.25 output
- Claude 3.5 Sonnet: $3.00 input / $15.00 output
- **Savings**: 90% cost reduction

**Speed**:
- Haiku: <200ms for classification tasks
- Sonnet: 500-1000ms

**Accuracy**:
- Haiku: 85-90% for structured tasks (classification, validation)
- Sonnet: 95%+ (overkill for this use case)

**Best Use Cases for Haiku**:
- Classification and categorization
- Pattern matching and validation
- Structured output (JSON)
- Low-stakes decisions (can fallback to Sonnet if needed)

### CE Framework Memory Type System

**Memory Types** (from `.serena/memories/README.md`):
1. **regular**: Standard framework documentation (default)
2. **critical**: High-priority memories (code-style-conventions, tool-usage-syntropy)
3. **user**: User-specific memories (from target project)

**YAML Header Format**:
```yaml
---
type: regular
category: documentation
tags: [tag1, tag2]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---
```

**Validation Requirements**:
- `type` field is **required** (must be: regular, critical, or user)
- `created` and `updated` are optional but recommended
- `category` is optional but helpful for organization

### Garbage File Patterns

Based on initialization workflow analysis:

**Common Garbage Files**:
- `*REPORT*.md`: Status reports, not actionable docs
- `*INITIAL*.md`: Planning docs, replaced by PRPs
- `*summary*.md`: Summary files, not source docs
- `*analysis*.md`: Analysis docs, not implementation guides
- `*PLAN*.md`: High-level plans, not detailed PRPs
- `*TODO*.md`: TODO lists, not structured PRPs

**Why Filter Garbage**:
- Reduces noise in collection phase
- Prevents accidental processing of temporary files
- Maintains clean file type classification (prp, example, memory)
