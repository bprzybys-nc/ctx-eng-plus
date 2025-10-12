"""Tests for PRP generation from INITIAL.md."""
import pytest
from pathlib import Path
from ce.generate import (
    parse_initial_md,
    extract_code_examples,
    extract_documentation_links,
)


@pytest.fixture
def sample_initial_path(tmp_path):
    """Create sample INITIAL.md for testing."""
    initial_content = """# Feature: User Authentication System

## FEATURE
Build user authentication with JWT tokens. Users should be able to:
- Register with email/password
- Login and receive JWT token
- Logout and invalidate token
- Reset password via email

## EXAMPLES

```python
async def authenticate_user(email: str, password: str):
    try:
        user = await db.get_user(email)
        if verify_password(password, user.password_hash):
            return {"token": generate_jwt(user.id)}
    except Exception as e:
        logger.error(f"Auth failed: {e}")
        raise
```

See src/auth.py:42-67 for OAuth implementation pattern.

The authentication flow uses async/await for database queries
and follows the repository pattern for data access.

## DOCUMENTATION

- [JWT Best Practices](https://jwt.io/introduction)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- https://docs.python.org/3/library/hashlib.html
- "pytest-asyncio" for async testing

## OTHER CONSIDERATIONS

Security:
- Hash passwords with bcrypt (min 12 rounds)
- Store JWT secret in environment variable
- Implement rate limiting (max 5 attempts per minute)

Edge Cases:
- Handle expired tokens gracefully
- Validate email format before DB query
"""
    initial_path = tmp_path / "INITIAL.md"
    initial_path.write_text(initial_content)
    return str(initial_path)


def test_parse_initial_md_complete(sample_initial_path):
    """Test parsing complete INITIAL.md with all sections."""
    result = parse_initial_md(sample_initial_path)

    # Feature name extracted
    assert result["feature_name"] == "User Authentication System"

    # FEATURE section present
    assert "JWT tokens" in result["feature"]
    assert "Register with email/password" in result["feature"]

    # EXAMPLES parsed
    assert len(result["examples"]) >= 2
    # Check for inline code example
    inline_examples = [ex for ex in result["examples"] if ex["type"] == "inline"]
    assert len(inline_examples) >= 1
    assert inline_examples[0]["language"] == "python"
    assert "authenticate_user" in inline_examples[0]["code"]

    # Check for file reference
    file_refs = [ex for ex in result["examples"] if ex["type"] == "file_ref"]
    assert len(file_refs) >= 1
    assert file_refs[0]["file"] == "src/auth.py"
    assert file_refs[0]["lines"] == "42-67"

    # DOCUMENTATION parsed
    assert len(result["documentation"]) >= 3
    doc_links = [doc for doc in result["documentation"] if doc["type"] == "link"]
    assert len(doc_links) >= 2
    assert any("jwt.io" in doc["url"] for doc in doc_links)

    # OTHER CONSIDERATIONS present
    assert "bcrypt" in result["other_considerations"]
    assert "rate limiting" in result["other_considerations"]

    # Raw content preserved
    assert "# Feature:" in result["raw_content"]


def test_parse_initial_md_missing_file():
    """Test error when INITIAL.md doesn't exist."""
    with pytest.raises(FileNotFoundError, match="INITIAL.md not found"):
        parse_initial_md("nonexistent/INITIAL.md")


def test_parse_initial_md_missing_feature_name(tmp_path):
    """Test error when feature name header is missing."""
    invalid_path = tmp_path / "invalid.md"
    invalid_path.write_text("## FEATURE\nSome feature")

    with pytest.raises(ValueError, match="Feature name not found"):
        parse_initial_md(str(invalid_path))


def test_parse_initial_md_missing_required_sections(tmp_path):
    """Test error when required sections are missing."""
    # Missing EXAMPLES
    no_examples_path = tmp_path / "no_examples.md"
    no_examples_path.write_text("""# Feature: Test

## FEATURE
Test feature
""")

    with pytest.raises(ValueError, match="Required EXAMPLES section missing"):
        parse_initial_md(str(no_examples_path))

    # Missing FEATURE
    no_feature_path = tmp_path / "no_feature.md"
    no_feature_path.write_text("""# Feature: Test

## EXAMPLES
Some code
""")

    with pytest.raises(ValueError, match="Required FEATURE section missing"):
        parse_initial_md(str(no_feature_path))


def test_extract_code_examples_inline():
    """Test extracting inline code blocks."""
    text = """
Here is an example:

```python
def hello():
    return "world"
```

And another:

```typescript
const greet = () => "hello";
```
"""
    examples = extract_code_examples(text)

    inline = [ex for ex in examples if ex["type"] == "inline"]
    assert len(inline) == 2
    assert inline[0]["language"] == "python"
    assert "def hello()" in inline[0]["code"]
    assert inline[1]["language"] == "typescript"
    assert "const greet" in inline[1]["code"]


def test_extract_code_examples_file_refs():
    """Test extracting file references."""
    text = """
See src/auth.py:42-67 for implementation.
Also check tests/test_auth.py lines 100-150.
"""
    examples = extract_code_examples(text)

    file_refs = [ex for ex in examples if ex["type"] == "file_ref"]
    assert len(file_refs) == 2
    assert file_refs[0]["file"] == "src/auth.py"
    assert file_refs[0]["lines"] == "42-67"
    assert file_refs[1]["file"] == "tests/test_auth.py"
    assert file_refs[1]["lines"] == "100-150"


def test_extract_code_examples_descriptions():
    """Test extracting natural language descriptions."""
    text = """
The authentication system uses async/await pattern
for all database operations.

File reference: src/auth.py:10-20

Error handling follows the fail-fast principle
with detailed logging at each step.
"""
    examples = extract_code_examples(text)

    descriptions = [ex for ex in examples if ex["type"] == "description"]
    assert len(descriptions) >= 1
    assert any("async/await" in desc["text"] for desc in descriptions)


def test_extract_documentation_links_markdown():
    """Test extracting Markdown-style links."""
    text = """
- [JWT Introduction](https://jwt.io/introduction)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
"""
    links = extract_documentation_links(text)

    markdown_links = [link for link in links if link["type"] == "link"]
    assert len(markdown_links) >= 2
    assert any("JWT Introduction" == link["title"] for link in markdown_links)
    assert any("jwt.io" in link["url"] for link in markdown_links)


def test_extract_documentation_links_plain_urls():
    """Test extracting plain URLs."""
    text = """
Reference: https://docs.python.org/3/library/hashlib.html
Also see: https://github.com/user/repo
"""
    links = extract_documentation_links(text)

    plain_urls = [link for link in links if "docs.python.org" in link["url"]]
    assert len(plain_urls) >= 1


def test_extract_documentation_links_libraries():
    """Test extracting library names."""
    text = """
Use "pytest" for testing and "FastAPI" for the web framework.
Also consider requests library.
"""
    links = extract_documentation_links(text)

    libraries = [link for link in links if link["type"] == "library"]
    assert len(libraries) >= 2
    assert any(lib["title"] == "pytest" for lib in libraries)
    assert any(lib["title"] == "FastAPI" for lib in libraries)


def test_extract_documentation_links_empty():
    """Test extracting from empty documentation text."""
    links = extract_documentation_links("")
    assert links == []
