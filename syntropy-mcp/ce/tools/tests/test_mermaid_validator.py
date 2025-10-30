"""Tests for mermaid diagram validator."""

import pytest
from pathlib import Path
import tempfile
import shutil

from ce.mermaid_validator import (
    validate_mermaid_diagrams,
    _has_unquoted_special_chars,
    _determine_text_color,
    lint_all_markdown_mermaid
)


class TestSpecialCharDetection:
    """Test _has_unquoted_special_chars function."""

    def test_safe_characters_allowed(self):
        """Colons, question marks, exclamation marks, slashes are safe."""
        assert not _has_unquoted_special_chars("Level 0: CLAUDE.md")
        assert not _has_unquoted_special_chars("Why? Because!")
        assert not _has_unquoted_special_chars("path/to/file")
        assert not _has_unquoted_special_chars("windows\\path")

    def test_html_tags_allowed(self):
        """HTML tags like <br/> should be allowed."""
        assert not _has_unquoted_special_chars("Line 1<br/>Line 2")
        assert not _has_unquoted_special_chars("Text with <sub>subscript</sub>")
        assert not _has_unquoted_special_chars("Text with <sup>superscript</sup>")

    def test_problematic_chars_detected(self):
        """Brackets, parentheses, pipes, quotes should be detected."""
        assert _has_unquoted_special_chars("Text with [brackets]")
        assert _has_unquoted_special_chars("Text with (parentheses)")
        assert _has_unquoted_special_chars("Text with {curly braces}")
        assert _has_unquoted_special_chars("Text with | pipe")
        assert _has_unquoted_special_chars('Text with "quotes"')
        assert _has_unquoted_special_chars("Text with 'single quotes'")

    def test_quoted_text_safe(self):
        """Quoted text should always be considered safe."""
        assert not _has_unquoted_special_chars('"Text with [brackets]"')
        assert not _has_unquoted_special_chars("'Text with (parentheses)'")

    def test_mixed_safe_and_html(self):
        """Mix of safe characters and HTML tags."""
        assert not _has_unquoted_special_chars("Level 0: CLAUDE.md<br/>Constitutional Rules")
        assert not _has_unquoted_special_chars("Question? Yes!<br/>Answer")


class TestTextColorDetermination:
    """Test _determine_text_color function."""

    def test_light_background_gets_black_text(self):
        """Light backgrounds should get black text (#000)."""
        assert _determine_text_color("#ffffff") == "#000"  # white
        assert _determine_text_color("#ffd93d") == "#000"  # light yellow
        assert _determine_text_color("#d0f0d0") == "#000"  # very light green

    def test_dark_background_gets_white_text(self):
        """Dark backgrounds should get white text (#fff)."""
        assert _determine_text_color("#000000") == "#fff"  # black
        assert _determine_text_color("#2c3e50") == "#fff"  # dark blue
        assert _determine_text_color("#34495e") == "#fff"  # dark gray

    def test_shorthand_hex_expansion(self):
        """3-digit hex colors should work correctly."""
        assert _determine_text_color("#fff") == "#000"  # white
        assert _determine_text_color("#000") == "#fff"  # black

    def test_mid_tone_colors(self):
        """Test colors around the luminance threshold."""
        # These are approximate - exact threshold is luminance 0.5
        assert _determine_text_color("#808080") in ["#000", "#fff"]  # gray


class TestMermaidValidation:
    """Test validate_mermaid_diagrams function."""

    @pytest.fixture
    def temp_md_file(self):
        """Create temporary markdown file for testing."""
        temp_dir = tempfile.mkdtemp()
        temp_file = Path(temp_dir) / "test.md"
        yield temp_file
        shutil.rmtree(temp_dir)

    def test_no_mermaid_blocks_passes(self, temp_md_file):
        """File with no mermaid blocks should pass."""
        temp_md_file.write_text("# Just a markdown file\n\nNo mermaid here.")

        result = validate_mermaid_diagrams(str(temp_md_file))

        assert result["success"] is True
        assert result["diagrams_checked"] == 0
        assert len(result["errors"]) == 0

    def test_valid_mermaid_passes(self, temp_md_file):
        """Valid mermaid diagram should pass."""
        content = """# Test

```mermaid
graph TD
    A[Start] --> B[End]
    style A fill:#ff6b6b,color:#000
    style B fill:#2c3e50,color:#fff
```
"""
        temp_md_file.write_text(content)

        result = validate_mermaid_diagrams(str(temp_md_file))

        assert result["success"] is True
        assert result["diagrams_checked"] == 1
        assert len(result["errors"]) == 0

    def test_mermaid_with_html_tags_passes(self, temp_md_file):
        """Mermaid with <br/> tags should pass validation."""
        content = """# Test

```mermaid
graph TD
    A[Line 1<br/>Line 2] --> B[End]
```
"""
        temp_md_file.write_text(content)

        result = validate_mermaid_diagrams(str(temp_md_file))

        assert result["success"] is True
        assert result["diagrams_checked"] == 1
        assert len(result["errors"]) == 0

    def test_mermaid_with_safe_chars_passes(self, temp_md_file):
        """Mermaid with colons, question marks should pass."""
        content = """# Test

```mermaid
graph TD
    A[Level 0: CLAUDE.md] --> B[Why? Because!]
```
"""
        temp_md_file.write_text(content)

        result = validate_mermaid_diagrams(str(temp_md_file))

        assert result["success"] is True
        assert result["diagrams_checked"] == 1
        assert len(result["errors"]) == 0

    def test_style_missing_color_detected(self, temp_md_file):
        """Style statement missing color should be detected."""
        content = """# Test

```mermaid
graph TD
    A[Start] --> B[End]
    style A fill:#ff6b6b
```
"""
        temp_md_file.write_text(content)

        result = validate_mermaid_diagrams(str(temp_md_file))

        assert result["success"] is False
        assert result["diagrams_checked"] == 1
        assert len(result["errors"]) > 0
        assert "missing color specification" in result["errors"][0].lower()

    def test_auto_fix_applies_changes(self, temp_md_file):
        """Auto-fix should modify file and report fixes."""
        content = """# Test

```mermaid
graph TD
    A[Start] --> B[End]
    style A fill:#ff6b6b
```
"""
        temp_md_file.write_text(content)

        result = validate_mermaid_diagrams(str(temp_md_file), auto_fix=True)

        assert result["success"] is True
        assert len(result["fixes_applied"]) > 0

        # Verify file was modified
        fixed_content = temp_md_file.read_text()
        assert "color:#" in fixed_content

    def test_multiple_diagrams_checked(self, temp_md_file):
        """Multiple mermaid blocks should all be validated."""
        content = """# Test

```mermaid
graph TD
    A[First]
```

Some text

```mermaid
graph TD
    B[Second]
```
"""
        temp_md_file.write_text(content)

        result = validate_mermaid_diagrams(str(temp_md_file))

        assert result["diagrams_checked"] == 2


class TestBulkLinting:
    """Test lint_all_markdown_mermaid function."""

    @pytest.fixture
    def temp_docs_dir(self):
        """Create temporary docs directory with markdown files."""
        temp_dir = tempfile.mkdtemp()
        docs_dir = Path(temp_dir) / "docs"
        docs_dir.mkdir()

        # Create files with mermaid
        (docs_dir / "file1.md").write_text("""
```mermaid
graph TD
    A[Valid]
```
""")

        (docs_dir / "file2.md").write_text("""
```mermaid
graph TD
    A[Start]
    style A fill:#ff0000
```
""")

        (docs_dir / "no_mermaid.md").write_text("Just text")

        yield docs_dir
        shutil.rmtree(temp_dir)

    def test_bulk_lint_multiple_files(self, temp_docs_dir):
        """Bulk linting should process multiple files."""
        result = lint_all_markdown_mermaid(str(temp_docs_dir))

        assert result["files_checked"] == 3
        assert result["diagrams_checked"] >= 2

    def test_bulk_lint_detects_issues(self, temp_docs_dir):
        """Bulk linting should detect issues across files."""
        result = lint_all_markdown_mermaid(str(temp_docs_dir))

        # file2.md has style missing color
        assert result["files_with_issues"] >= 1

    def test_bulk_auto_fix(self, temp_docs_dir):
        """Bulk auto-fix should fix issues across all files."""
        result = lint_all_markdown_mermaid(str(temp_docs_dir), auto_fix=True)

        if result["fixes_applied"]:
            # Verify files were modified
            file2 = (temp_docs_dir / "file2.md").read_text()
            assert "color:#" in file2


class TestRegressions:
    """Regression tests for previously fixed bugs."""

    @pytest.fixture
    def temp_md_file(self):
        """Create temporary markdown file for testing."""
        temp_dir = tempfile.mkdtemp()
        temp_file = Path(temp_dir) / "test.md"
        yield temp_file
        shutil.rmtree(temp_dir)

    def test_issue_html_tags_false_positive(self, temp_md_file):
        """Regression: <br/> tags should not trigger special char warning."""
        content = """# Test

```mermaid
graph TD
    L0[Level 0: CLAUDE.md<br/>Constitutional Rules]
    L1[Level 1: Codebase<br/>Absolute Truth]
```
"""
        temp_md_file.write_text(content)

        result = validate_mermaid_diagrams(str(temp_md_file))

        # Should pass without errors about special chars
        assert result["success"] is True
        special_char_errors = [e for e in result["errors"] if "unquoted special chars" in e]
        assert len(special_char_errors) == 0
