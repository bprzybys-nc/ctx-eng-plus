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
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import anthropic
import os


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
            model="claude-haiku-4-5",
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


def main():
    """CLI interface for classification module."""
    import sys

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
