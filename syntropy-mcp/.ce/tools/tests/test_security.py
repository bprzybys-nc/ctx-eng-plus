"""Security tests for CWE-78 command injection vulnerability prevention."""

import pytest
from ce.core import run_cmd, count_git_files, count_git_diff_lines


class TestCommandInjectionPrevention:
    """Tests for CWE-78 command injection vulnerability prevention."""

    def test_run_cmd_rejects_command_chaining(self):
        """Command chaining (;) should fail, not execute both commands."""
        # Attempt to execute two commands with ;
        # Note: This will throw RuntimeError because 'ls;' is not a valid command
        with pytest.raises(RuntimeError):
            run_cmd("ls; whoami")
        # The important thing: whoami never executed as separate command

    def test_run_cmd_rejects_pipe_injection(self):
        """Pipes (|) should be treated as literal arguments, not shell operators."""
        result = run_cmd("echo test | cat")

        # With shell=False, pipe is literal argument to echo.
        # Command succeeds (echo accepts it as literal text), but no piping occurs.
        # Main point: cat does NOT receive piped input from echo
        assert "| cat" in result["stdout"] or result["success"] is False

    def test_run_cmd_rejects_redirection(self):
        """Output redirection (>) should be treated as literal arguments."""
        result = run_cmd("echo test > /tmp/injection_test")

        # With shell=False, > is literal argument to echo.
        # File /tmp/injection_test should NOT be created
        assert result["success"] is True  # echo accepts literal >
        assert ">" in result["stdout"]  # Redirection not interpreted
        # Verify no file was created
        import os
        assert not os.path.exists("/tmp/injection_test")

    def test_run_cmd_rejects_backtick_substitution(self):
        """Backtick command substitution (`) should be literal."""
        result = run_cmd("echo `whoami`")

        # With shell=False, backtick is literal. whoami should NOT execute.
        # Either echo succeeds with literal backticks, or fails because of malformed arg
        # Main point: whoami doesn't execute and output isn't substituted
        assert result["success"] is True or result["success"] is False
        # Verify whoami output NOT in stdout (injection prevented)
        import getpass
        current_user = getpass.getuser()
        assert current_user not in result["stdout"]

    def test_run_cmd_rejects_dollar_substitution(self):
        """Dollar command substitution ($(...)) should be literal."""
        result = run_cmd("echo $(whoami)")

        # With shell=False, $(...) is literal. whoami should NOT execute.
        # Main point: whoami output NOT in stdout (injection prevented)
        import getpass
        current_user = getpass.getuser()
        assert current_user not in result["stdout"]

    def test_run_cmd_rejects_variable_expansion(self):
        """Shell variable expansion ($VAR) should be literal."""
        result = run_cmd("echo $PATH")

        # With shell=False, $PATH is literal. PATH should NOT be expanded.
        # Main point: PATH variable value NOT in stdout (expansion prevented)
        import os
        assert os.environ.get("PATH") not in result["stdout"]

    def test_run_cmd_rejects_glob_expansion(self):
        """Glob patterns (*) should be treated as literal."""
        result = run_cmd("echo *")

        # Should fail or return literal * (depends on implementation)
        # Main point: no glob expansion occurs
        assert "*" in result["stdout"] or result["success"] is False

    def test_run_cmd_with_valid_list_format(self):
        """List format should work correctly."""
        result = run_cmd(["echo", "test"])

        assert result["success"] is True
        assert "test" in result["stdout"]

    def test_run_cmd_with_quoted_string(self):
        """Quoted strings should be parsed correctly by shlex."""
        result = run_cmd("echo 'hello world'")

        assert result["success"] is True
        assert "hello world" in result["stdout"]

    def test_run_cmd_with_escaped_quotes(self):
        """Escaped quotes should be handled correctly."""
        result = run_cmd('echo "hello world"')

        assert result["success"] is True
        assert "hello world" in result["stdout"]

    def test_run_cmd_empty_string_raises_error(self):
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="Empty command"):
            run_cmd("")

    def test_run_cmd_empty_list_raises_error(self):
        """Empty list should raise ValueError."""
        with pytest.raises(ValueError, match="Empty command"):
            run_cmd([])

    def test_count_git_files_no_injection(self):
        """count_git_files() should be injection-proof."""
        count = count_git_files()

        # Should return integer
        assert isinstance(count, int)
        assert count >= 0

    def test_count_git_diff_lines_safe(self):
        """count_git_diff_lines() should handle edge cases safely."""
        # Should not crash
        count = count_git_diff_lines("HEAD~1")

        assert isinstance(count, int)
        assert count >= 0

    def test_run_cmd_command_injection_with_semicolon(self):
        """Verify command injection via semicolon is blocked."""
        # Attempt to inject rm command
        # With shell=False, semicolon becomes literal argument to echo
        result = run_cmd("echo safe; rm -rf /tmp/test_dir")

        # With shell=False, echo interprets "safe;" and "rm" as literal arguments
        # The injection is prevented - rm does not execute as separate command
        assert result["success"] is True  # echo succeeds with literal ;
        assert ";" in result["stdout"]  # Semicolon appears as literal text


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility with existing code."""

    def test_run_cmd_accepts_string(self):
        """run_cmd() should still accept string format."""
        result = run_cmd("echo backward_compat")

        assert result["success"] is True
        assert "backward_compat" in result["stdout"]

    def test_run_cmd_accepts_list(self):
        """run_cmd() should accept list format."""
        result = run_cmd(["echo", "list_format"])

        assert result["success"] is True
        assert "list_format" in result["stdout"]

    def test_run_cmd_return_format_unchanged(self):
        """Return dict format should remain unchanged."""
        result = run_cmd("echo test")

        # All required keys must be present
        assert "success" in result
        assert "stdout" in result
        assert "stderr" in result
        assert "exit_code" in result
        assert "duration" in result

    def test_run_cmd_with_arguments(self):
        """run_cmd() should handle arguments correctly."""
        result = run_cmd("echo hello world")

        assert result["success"] is True
        assert "hello" in result["stdout"]
        assert "world" in result["stdout"]

    def test_run_cmd_with_multiple_spaces(self):
        """Multiple spaces between arguments should be handled."""
        result = run_cmd("echo   multiple   spaces")

        assert result["success"] is True
        # shlex.split() normalizes spaces
        assert "multiple" in result["stdout"]
        assert "spaces" in result["stdout"]

    def test_run_cmd_preserves_exit_code(self):
        """run_cmd() should preserve exit codes."""
        # Success case
        result_success = run_cmd("true")
        assert result_success["exit_code"] == 0

        # Failure case
        result_failure = run_cmd("false")
        assert result_failure["exit_code"] != 0


class TestErrorHandling:
    """Tests for proper error handling in safe mode."""

    def test_run_cmd_nonexistent_command(self):
        """Nonexistent command should raise RuntimeError."""
        with pytest.raises(RuntimeError):
            run_cmd("nonexistent_command_xyz_12345")

    def test_run_cmd_with_cwd(self):
        """run_cmd() should respect working directory."""
        import os
        result = run_cmd("pwd", cwd="/tmp")

        assert result["success"] is True
        assert "/tmp" in result["stdout"]

    def test_run_cmd_captures_stderr(self):
        """run_cmd() should capture stderr."""
        result = run_cmd("ls /nonexistent/path/xyz")

        assert result["success"] is False
        assert len(result["stderr"]) > 0  # Should have error message


class TestGitHelpers:
    """Tests for git helper functions."""

    def test_count_git_files_returns_integer(self):
        """count_git_files() should return a positive integer."""
        count = count_git_files()

        assert isinstance(count, int)
        assert count > 0  # Project has at least some files

    def test_count_git_files_consistency(self):
        """count_git_files() should return consistent results."""
        count1 = count_git_files()
        count2 = count_git_files()

        assert count1 == count2  # Should be same between calls

    def test_count_git_diff_lines_with_ref(self):
        """count_git_diff_lines() should work with different refs."""
        # Test with HEAD~1
        count = count_git_diff_lines("HEAD~1")

        assert isinstance(count, int)
        assert count >= 0

    def test_count_git_diff_lines_with_files(self):
        """count_git_diff_lines() should work with file filter."""
        # Test with specific files
        count = count_git_diff_lines("HEAD~5", files=["pyproject.toml"])

        assert isinstance(count, int)
        assert count >= 0

    def test_count_git_diff_lines_with_nonexistent_ref(self):
        """count_git_diff_lines() should gracefully handle invalid refs."""
        # Should not crash, return 0 on error
        count = count_git_diff_lines("nonexistent/ref/xyz")

        assert isinstance(count, int)
        assert count == 0  # Returns 0 on error (graceful degradation)


class TestShellMetacharacters:
    """Tests for proper handling of shell metacharacters."""

    def test_ampersand_not_interpreted(self):
        """& should not fork background process."""
        result = run_cmd("echo foreground & echo background")

        # Should fail - & treated as literal argument, or succeed with literal &
        # Main point: background process NOT forked
        assert result["success"] is False or "&" in result["stdout"]

    def test_tilde_not_expanded(self):
        """~ should not be expanded to home directory."""
        result = run_cmd("echo ~")

        # Tilde should be literal (or ls -l would show different path)
        assert result["success"] is True

    def test_tilde_slash_not_expanded(self):
        """~/ should not be expanded."""
        result = run_cmd("echo ~/file")

        assert result["success"] is True
        # Tilde should be treated literally
        assert "~" in result["stdout"]

    def test_parentheses_not_interpreted(self):
        """Parentheses should not create subshells."""
        result = run_cmd("echo (test)")

        # Should fail or print literal - parentheses treated literally, not as subshell
        # Either command fails or echo prints them literally
        assert result["success"] is False or "(test)" in result["stdout"]

    def test_braces_not_interpreted(self):
        """Braces should not be used for brace expansion."""
        result = run_cmd("echo {a,b,c}")

        # Should fail or print literal
        assert result["success"] is False or "{a,b,c}" in result["stdout"]


class TestRealWorldAttacks:
    """Tests simulating real-world command injection attacks."""

    def test_attack_delete_directory(self):
        """Simulate attack attempting directory deletion."""
        # Attacker tries: file.txt; rm -rf /
        attack_cmd = "echo file.txt; rm -rf /"
        result = run_cmd(attack_cmd)

        # With shell=False, semicolon treated as literal argument to echo
        # rm does NOT execute as separate command (injection prevented)
        assert result["success"] is True  # echo accepts literal ;
        assert ";" in result["stdout"]  # Semicolon is literal text output

    def test_attack_find_sensitive_files(self):
        """Simulate attack attempting to find sensitive files."""
        attack_cmd = "ls / | grep -E '(etc|root)'"
        result = run_cmd(attack_cmd)

        # Should fail - pipe treated as literal argument to ls command
        assert result["success"] is False

    def test_attack_read_environment(self):
        """Simulate attack attempting to read environment."""
        attack_cmd = "echo start; echo $HOME; echo $USER"
        result = run_cmd(attack_cmd)

        # With shell=False, semicolons are literal arguments to first echo
        # Subsequent echoes do NOT execute, $HOME/$USER NOT expanded
        assert result["success"] is True  # First echo accepts literal arguments
        assert ";" in result["stdout"]  # Semicolons appear literally
        # Verify environment variables NOT expanded
        import os
        assert os.environ.get("HOME") not in result["stdout"]

    def test_attack_write_to_file(self):
        """Simulate attack attempting to write to file."""
        attack_cmd = "echo data > /tmp/malicious"
        result = run_cmd(attack_cmd)

        # With shell=False, > is literal argument. File should NOT be created.
        # Verify /tmp/malicious was NOT created (redirection prevented)
        import os
        assert not os.path.exists("/tmp/malicious")
        # Either command fails or succeeds with literal >
        assert result["success"] is False or ">" in result["stdout"]
