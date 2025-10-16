"""Tests for shell_utils module - 100% coverage target."""

import pytest
from pathlib import Path
from ce.shell_utils import (
    grep_text,
    count_lines,
    head,
    tail,
    find_files,
    extract_fields,
    sum_column,
    filter_and_extract
)


class TestGrepText:
    """Tests for grep_text function."""

    def test_basic_match(self):
        """Test basic pattern matching."""
        text = "line1\nerror here\nline3"
        result = grep_text("error", text)
        assert result == ["error here"]

    def test_with_context(self):
        """Test pattern matching with context lines."""
        text = "line1\nerror here\nline3"
        result = grep_text("error", text, context_lines=1)
        assert result == ["line1", "error here", "line3"]

    def test_multiple_matches(self):
        """Test multiple pattern matches."""
        text = "error1\nok\nerror2\nok\nerror3"
        result = grep_text("error", text)
        assert len(result) == 3
        assert all("error" in line for line in result)

    def test_regex_pattern(self):
        """Test regex pattern matching."""
        text = "user123\nadmin456\nuser789"
        result = grep_text(r"user\d+", text)
        assert len(result) == 2

    def test_no_matches(self):
        """Test when no matches found."""
        text = "line1\nline2\nline3"
        result = grep_text("notfound", text)
        assert result == []

    def test_overlapping_context(self):
        """Test context lines with overlapping matches."""
        text = "a\nerror1\nb\nerror2\nc"
        result = grep_text("error", text, context_lines=1)
        # Should merge overlapping ranges
        assert len(result) == 5  # All lines included


class TestCountLines:
    """Tests for count_lines function."""

    def test_count_lines_basic(self, tmp_path):
        """Test basic line counting."""
        file = tmp_path / "test.txt"
        file.write_text("line1\nline2\nline3")
        assert count_lines(str(file)) == 3

    def test_count_lines_empty(self, tmp_path):
        """Test counting empty file."""
        file = tmp_path / "empty.txt"
        file.write_text("")
        assert count_lines(str(file)) == 1  # Empty string splits to ['']

    def test_count_lines_single(self, tmp_path):
        """Test counting single line."""
        file = tmp_path / "single.txt"
        file.write_text("single line")
        assert count_lines(str(file)) == 1

    def test_count_lines_nonexistent(self):
        """Test counting nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            count_lines("nonexistent.txt")


class TestHead:
    """Tests for head function."""

    def test_head_default(self, tmp_path):
        """Test head with default 10 lines."""
        file = tmp_path / "test.txt"
        lines = [f"line{i}" for i in range(20)]
        file.write_text("\n".join(lines))
        result = head(str(file))
        assert len(result) == 10
        assert result[0] == "line0"
        assert result[9] == "line9"

    def test_head_custom_n(self, tmp_path):
        """Test head with custom line count."""
        file = tmp_path / "test.txt"
        file.write_text("a\nb\nc\nd\ne")
        result = head(str(file), n=3)
        assert result == ["a", "b", "c"]

    def test_head_more_than_file(self, tmp_path):
        """Test head requesting more lines than file has."""
        file = tmp_path / "test.txt"
        file.write_text("a\nb\nc")
        result = head(str(file), n=10)
        assert len(result) == 3

    def test_head_nonexistent(self):
        """Test head on nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            head("nonexistent.txt")


class TestTail:
    """Tests for tail function."""

    def test_tail_default(self, tmp_path):
        """Test tail with default 10 lines."""
        file = tmp_path / "test.txt"
        lines = [f"line{i}" for i in range(20)]
        file.write_text("\n".join(lines))
        result = tail(str(file))
        assert len(result) == 10
        assert result[0] == "line10"
        assert result[9] == "line19"

    def test_tail_custom_n(self, tmp_path):
        """Test tail with custom line count."""
        file = tmp_path / "test.txt"
        file.write_text("a\nb\nc\nd\ne")
        result = tail(str(file), n=3)
        assert result == ["c", "d", "e"]

    def test_tail_more_than_file(self, tmp_path):
        """Test tail requesting more lines than file has."""
        file = tmp_path / "test.txt"
        file.write_text("a\nb\nc")
        result = tail(str(file), n=10)
        assert len(result) == 3

    def test_tail_nonexistent(self):
        """Test tail on nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            tail("nonexistent.txt")


class TestFindFiles:
    """Tests for find_files function."""

    def test_find_files_basic(self, tmp_path):
        """Test basic file finding."""
        (tmp_path / "test1.py").touch()
        (tmp_path / "test2.py").touch()
        (tmp_path / "test.txt").touch()

        result = find_files(str(tmp_path), "*.py")
        assert len(result) == 2
        assert all(f.endswith(".py") for f in result)

    def test_find_files_recursive(self, tmp_path):
        """Test recursive file finding."""
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir2").mkdir()
        (tmp_path / "test1.py").touch()
        (tmp_path / "dir1" / "test2.py").touch()
        (tmp_path / "dir2" / "test3.py").touch()

        result = find_files(str(tmp_path), "*.py")
        assert len(result) == 3

    def test_find_files_with_exclude(self, tmp_path):
        """Test file finding with exclusions."""
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "test1.py").touch()
        (tmp_path / "__pycache__" / "test2.py").touch()

        result = find_files(str(tmp_path), "*.py", exclude=["__pycache__"])
        assert len(result) == 1
        assert "__pycache__" not in result[0]

    def test_find_files_no_matches(self, tmp_path):
        """Test finding files with no matches."""
        (tmp_path / "test.txt").touch()
        result = find_files(str(tmp_path), "*.py")
        assert result == []

    def test_find_files_sorted(self, tmp_path):
        """Test that results are sorted."""
        (tmp_path / "c.py").touch()
        (tmp_path / "a.py").touch()
        (tmp_path / "b.py").touch()

        result = find_files(str(tmp_path), "*.py")
        assert result == sorted(result)


class TestExtractFields:
    """Tests for extract_fields function."""

    def test_extract_fields_basic(self):
        """Test basic field extraction."""
        text = "user1 100 active\nuser2 200 inactive"
        result = extract_fields(text, field_indices=[1, 3])
        assert result == [["user1", "active"], ["user2", "inactive"]]

    def test_extract_fields_single(self):
        """Test extracting single field."""
        text = "user1 100 active\nuser2 200 inactive"
        result = extract_fields(text, field_indices=[1])
        assert result == [["user1"], ["user2"]]

    def test_extract_fields_with_delimiter(self):
        """Test field extraction with custom delimiter."""
        text = "user1:100:active\nuser2:200:inactive"
        result = extract_fields(text, field_indices=[1, 3], delimiter=":")
        assert result == [["user1", "active"], ["user2", "inactive"]]

    def test_extract_fields_out_of_range(self):
        """Test extracting fields that don't exist."""
        text = "a b c"
        result = extract_fields(text, field_indices=[1, 5])
        assert result == [["a"]]  # Field 5 doesn't exist

    def test_extract_fields_empty_lines(self):
        """Test field extraction skips empty lines."""
        text = "a b c\n\nd e f"
        result = extract_fields(text, field_indices=[1])
        assert len(result) == 2

    def test_extract_fields_whitespace_delimiter(self):
        """Test field extraction with whitespace."""
        text = "a    b    c"  # Multiple spaces
        result = extract_fields(text, field_indices=[1, 3])
        assert result == [["a", "c"]]


class TestSumColumn:
    """Tests for sum_column function."""

    def test_sum_column_basic(self):
        """Test basic column summation."""
        text = "item1 100\nitem2 200\nitem3 300"
        total = sum_column(text, column=2)
        assert total == 600.0

    def test_sum_column_floats(self):
        """Test summing floating point numbers."""
        text = "a 1.5\nb 2.5\nc 3.0"
        total = sum_column(text, column=2)
        assert total == 7.0

    def test_sum_column_with_non_numeric(self):
        """Test summing with non-numeric values."""
        text = "item1 100\nitem2 abc\nitem3 300"
        total = sum_column(text, column=2)
        assert total == 400.0  # Skips non-numeric

    def test_sum_column_empty(self):
        """Test summing empty text."""
        text = ""
        total = sum_column(text, column=1)
        assert total == 0.0

    def test_sum_column_with_delimiter(self):
        """Test summing with custom delimiter."""
        text = "a:100\nb:200\nc:300"
        total = sum_column(text, column=2, delimiter=":")
        assert total == 600.0

    def test_sum_column_first_column(self):
        """Test summing first column."""
        text = "100 a\n200 b\n300 c"
        total = sum_column(text, column=1)
        assert total == 600.0


class TestFilterAndExtract:
    """Tests for filter_and_extract function."""

    def test_filter_and_extract_basic(self):
        """Test basic filtering and extraction."""
        text = "ERROR user1\nINFO user2\nERROR user3"
        result = filter_and_extract(text, "ERROR", field_index=2)
        assert result == ["user1", "user3"]

    def test_filter_and_extract_no_matches(self):
        """Test filtering with no matches."""
        text = "INFO user1\nINFO user2"
        result = filter_and_extract(text, "ERROR", field_index=2)
        assert result == []

    def test_filter_and_extract_regex(self):
        """Test filtering with regex pattern."""
        text = "ERROR1 user1\nERROR2 user2\nINFO user3"
        result = filter_and_extract(text, r"ERROR\d+", field_index=2)
        assert result == ["user1", "user2"]

    def test_filter_and_extract_with_delimiter(self):
        """Test filtering and extraction with delimiter."""
        text = "ERROR:user1:data\nINFO:user2:data\nERROR:user3:data"
        result = filter_and_extract(text, "ERROR", field_index=2, delimiter=":")
        assert result == ["user1", "user3"]

    def test_filter_and_extract_first_field(self):
        """Test extracting first field from matches."""
        text = "ERROR user1\nINFO user2\nERROR user3"
        result = filter_and_extract(text, "ERROR", field_index=1)
        assert result == ["ERROR", "ERROR"]

    def test_filter_and_extract_out_of_range(self):
        """Test extracting field that doesn't exist."""
        text = "ERROR user1\nERROR user2"
        result = filter_and_extract(text, "ERROR", field_index=5)
        assert result == []


# Integration tests
class TestIntegration:
    """Integration tests combining multiple utilities."""

    def test_grep_and_sum(self):
        """Test combining grep and sum operations."""
        text = "ERROR 100\nINFO 50\nERROR 200\nINFO 75\nERROR 300"
        # Find ERROR lines, extract second field, sum them
        errors = grep_text("ERROR", text)
        error_text = "\n".join(errors)
        total = sum_column(error_text, column=2)
        assert total == 600.0

    def test_filter_extract_and_count(self):
        """Test filtering, extracting, and counting."""
        text = "ERROR user1\nINFO user2\nERROR user3\nERROR user4"
        users = filter_and_extract(text, "ERROR", field_index=2)
        assert len(users) == 3

    def test_file_operations_chain(self, tmp_path):
        """Test chaining file operations."""
        file = tmp_path / "test.txt"
        content = "\n".join([f"line{i}" for i in range(100)])
        file.write_text(content)

        # Get first 5 and last 5 lines
        first = head(str(file), n=5)
        last = tail(str(file), n=5)

        assert first[0] == "line0"
        assert last[-1] == "line99"
        assert len(first) + len(last) == 10
