"""Unit tests for simple blending strategies (PRPs and Commands)."""

import pytest
from pathlib import Path
from ce.blending.strategies.simple import PRPMoveStrategy, CommandOverwriteStrategy


class TestPRPMoveStrategy:
    """Tests for PRPMoveStrategy."""

    def test_prp_move_adds_user_header(self, tmp_path):
        """PRPs without YAML header get type: user header added."""
        # Setup
        source = tmp_path / "source" / "PRPs"
        target = tmp_path / "target" / ".ce" / "PRPs"
        source.mkdir(parents=True)

        prp_file = source / "PRP-1-test.md"
        prp_file.write_text("# PRP-1: Test Feature\n\nContent here")

        # Execute
        strategy = PRPMoveStrategy()
        result = strategy.execute({
            "source_dir": source,
            "target_dir": target
        })

        # Verify
        assert result["prps_moved"] == 1
        assert result["prps_skipped"] == 0
        assert len(result["errors"]) == 0

        # Check header added
        moved_content = (target / "feature-requests" / "PRP-1-test.md").read_text()
        assert "type: user" in moved_content
        assert "source: target-project" in moved_content
        assert "# PRP-1: Test Feature" in moved_content

    def test_prp_move_preserves_all_ids(self, tmp_path):
        """No ID deduplication - multiple PRPs with same ID coexist."""
        # Setup
        source = tmp_path / "source" / "PRPs"
        target = tmp_path / "target" / ".ce" / "PRPs"
        source.mkdir(parents=True)
        (target / "executed").mkdir(parents=True)

        # Create two different PRPs with ID=1
        prp_file1 = source / "PRP-1-auth.md"
        prp_file1.write_text("# PRP-1: Authentication\n\nAuth feature")

        prp_file2 = source / "PRP-1-logging.md"
        prp_file2.write_text("# PRP-1: Logging\n\nLogging feature")

        # Execute
        strategy = PRPMoveStrategy()
        result = strategy.execute({
            "source_dir": source,
            "target_dir": target
        })

        # Verify - both should be moved (no ID deduplication)
        assert result["prps_moved"] == 2
        assert result["prps_skipped"] == 0
        assert (target / "feature-requests" / "PRP-1-auth.md").exists()
        assert (target / "feature-requests" / "PRP-1-logging.md").exists()

    def test_prp_move_hash_dedupe(self, tmp_path):
        """Skips if exact file already exists (hash match)."""
        # Setup
        source = tmp_path / "source" / "PRPs"
        target = tmp_path / "target" / ".ce" / "PRPs"
        source.mkdir(parents=True)
        (target / "feature-requests").mkdir(parents=True)

        content = "---\ntype: user\n---\n\n# PRP-2: Duplicate\n\nSame content"

        # Create identical files in source and target
        prp_file = source / "PRP-2-dup.md"
        prp_file.write_text(content)

        target_file = target / "feature-requests" / "PRP-2-dup.md"
        target_file.write_text(content)

        # Execute
        strategy = PRPMoveStrategy()
        result = strategy.execute({
            "source_dir": source,
            "target_dir": target
        })

        # Verify - should skip (hash match)
        assert result["prps_moved"] == 0
        assert result["prps_skipped"] == 1

    def test_prp_status_detection_completed(self, tmp_path):
        """Parses completed status → executed directory."""
        # Setup
        source = tmp_path / "source" / "PRPs"
        target = tmp_path / "target" / ".ce" / "PRPs"
        source.mkdir(parents=True)

        prp_file = source / "PRP-3-done.md"
        prp_file.write_text("# PRP-3: Done Feature\n\nStatus: completed\n\nWork finished")

        # Execute
        strategy = PRPMoveStrategy()
        result = strategy.execute({
            "source_dir": source,
            "target_dir": target
        })

        # Verify - should be in executed directory
        assert result["prps_moved"] == 1
        assert (target / "executed" / "PRP-3-done.md").exists()
        assert not (target / "feature-requests" / "PRP-3-done.md").exists()

    def test_prp_status_detection_default(self, tmp_path):
        """Default status → feature-requests directory."""
        # Setup
        source = tmp_path / "source" / "PRPs"
        target = tmp_path / "target" / ".ce" / "PRPs"
        source.mkdir(parents=True)

        prp_file = source / "PRP-4-pending.md"
        prp_file.write_text("# PRP-4: Pending Feature\n\nStatus: in_progress\n\nWork ongoing")

        # Execute
        strategy = PRPMoveStrategy()
        result = strategy.execute({
            "source_dir": source,
            "target_dir": target
        })

        # Verify - should be in feature-requests directory (default)
        assert result["prps_moved"] == 1
        assert (target / "feature-requests" / "PRP-4-pending.md").exists()
        assert not (target / "executed" / "PRP-4-pending.md").exists()

    def test_prp_preserves_existing_header(self, tmp_path):
        """PRPs with existing YAML header are not modified."""
        # Setup
        source = tmp_path / "source" / "PRPs"
        target = tmp_path / "target" / ".ce" / "PRPs"
        source.mkdir(parents=True)

        original_content = """---
prp_id: PRP-5
status: pending
---

# PRP-5: Existing Header

Has header already"""

        prp_file = source / "PRP-5-existing.md"
        prp_file.write_text(original_content)

        # Execute
        strategy = PRPMoveStrategy()
        result = strategy.execute({
            "source_dir": source,
            "target_dir": target
        })

        # Verify - header preserved (not duplicated)
        assert result["prps_moved"] == 1
        moved_content = (target / "feature-requests" / "PRP-5-existing.md").read_text()
        assert moved_content == original_content
        assert moved_content.count("---") == 2  # Only one header

    def test_prp_handles_missing_source(self, tmp_path):
        """Gracefully handles missing source directory."""
        # Setup
        source = tmp_path / "nonexistent" / "PRPs"
        target = tmp_path / "target" / ".ce" / "PRPs"

        # Execute
        strategy = PRPMoveStrategy()
        result = strategy.execute({
            "source_dir": source,
            "target_dir": target
        })

        # Verify - returns error, no crash
        assert result["prps_moved"] == 0
        assert result["prps_skipped"] == 0
        assert len(result["errors"]) == 1
        assert "does not exist" in result["errors"][0]


class TestCommandOverwriteStrategy:
    """Tests for CommandOverwriteStrategy."""

    def test_command_backup(self, tmp_path):
        """User commands backed up before overwrite."""
        # Setup
        source = tmp_path / "source" / "commands"
        target = tmp_path / "target" / ".claude" / "commands"
        backup = tmp_path / "target" / ".claude" / "commands.backup"
        source.mkdir(parents=True)
        target.mkdir(parents=True)

        # Create framework command
        framework_cmd = source / "test-cmd.md"
        framework_cmd.write_text("# Framework Command\n\nFramework version")

        # Create existing user command
        user_cmd = target / "test-cmd.md"
        user_cmd.write_text("# User Command\n\nUser version")

        # Execute
        strategy = CommandOverwriteStrategy()
        result = strategy.execute({
            "source_dir": source,
            "target_dir": target,
            "backup_dir": backup
        })

        # Verify - user command backed up
        assert result["commands_overwritten"] == 1
        assert result["commands_backed_up"] == 1
        assert (backup / "test-cmd.md").exists()
        assert (backup / "test-cmd.md").read_text() == "# User Command\n\nUser version"

    def test_command_overwrite(self, tmp_path):
        """Framework commands overwrite existing user commands."""
        # Setup
        source = tmp_path / "source" / "commands"
        target = tmp_path / "target" / ".claude" / "commands"
        backup = tmp_path / "target" / ".claude" / "commands.backup"
        source.mkdir(parents=True)
        target.mkdir(parents=True)

        # Create framework command
        framework_cmd = source / "test-cmd.md"
        framework_cmd.write_text("# Framework Command\n\nFramework version")

        # Create existing user command
        user_cmd = target / "test-cmd.md"
        user_cmd.write_text("# User Command\n\nUser version")

        # Execute
        strategy = CommandOverwriteStrategy()
        result = strategy.execute({
            "source_dir": source,
            "target_dir": target,
            "backup_dir": backup
        })

        # Verify - target has framework version
        assert result["commands_overwritten"] == 1
        assert (target / "test-cmd.md").read_text() == "# Framework Command\n\nFramework version"

    def test_command_hash_dedupe(self, tmp_path):
        """Skips if identical command already exists."""
        # Setup
        source = tmp_path / "source" / "commands"
        target = tmp_path / "target" / ".claude" / "commands"
        backup = tmp_path / "target" / ".claude" / "commands.backup"
        source.mkdir(parents=True)
        target.mkdir(parents=True)

        content = "# Same Command\n\nIdentical content"

        # Create identical files
        framework_cmd = source / "test-cmd.md"
        framework_cmd.write_text(content)

        user_cmd = target / "test-cmd.md"
        user_cmd.write_text(content)

        # Execute
        strategy = CommandOverwriteStrategy()
        result = strategy.execute({
            "source_dir": source,
            "target_dir": target,
            "backup_dir": backup
        })

        # Verify - skipped (hash match)
        assert result["commands_overwritten"] == 0
        assert result["commands_backed_up"] == 0
        assert result["commands_skipped"] == 1

    def test_command_new_file(self, tmp_path):
        """New framework commands copied without backup."""
        # Setup
        source = tmp_path / "source" / "commands"
        target = tmp_path / "target" / ".claude" / "commands"
        backup = tmp_path / "target" / ".claude" / "commands.backup"
        source.mkdir(parents=True)
        target.mkdir(parents=True)

        # Create framework command (no existing user command)
        framework_cmd = source / "new-cmd.md"
        framework_cmd.write_text("# New Command\n\nNew framework command")

        # Execute
        strategy = CommandOverwriteStrategy()
        result = strategy.execute({
            "source_dir": source,
            "target_dir": target,
            "backup_dir": backup
        })

        # Verify - copied without backup
        assert result["commands_overwritten"] == 1
        assert result["commands_backed_up"] == 0
        assert (target / "new-cmd.md").exists()
        assert not (backup / "new-cmd.md").exists()

    def test_command_handles_missing_source(self, tmp_path):
        """Gracefully handles missing source directory."""
        # Setup
        source = tmp_path / "nonexistent" / "commands"
        target = tmp_path / "target" / ".claude" / "commands"
        backup = tmp_path / "target" / ".claude" / "commands.backup"

        # Execute
        strategy = CommandOverwriteStrategy()
        result = strategy.execute({
            "source_dir": source,
            "target_dir": target,
            "backup_dir": backup
        })

        # Verify - returns error, no crash
        assert result["commands_overwritten"] == 0
        assert result["commands_backed_up"] == 0
        assert len(result["errors"]) == 1
        assert "does not exist" in result["errors"][0]

    def test_command_multiple_files(self, tmp_path):
        """Handles multiple command files correctly."""
        # Setup
        source = tmp_path / "source" / "commands"
        target = tmp_path / "target" / ".claude" / "commands"
        backup = tmp_path / "target" / ".claude" / "commands.backup"
        source.mkdir(parents=True)
        target.mkdir(parents=True)

        # Create multiple framework commands
        (source / "cmd1.md").write_text("Command 1")
        (source / "cmd2.md").write_text("Command 2")
        (source / "cmd3.md").write_text("Command 3")

        # Create one existing user command
        (target / "cmd1.md").write_text("Old Command 1")

        # Execute
        strategy = CommandOverwriteStrategy()
        result = strategy.execute({
            "source_dir": source,
            "target_dir": target,
            "backup_dir": backup
        })

        # Verify
        assert result["commands_overwritten"] == 3
        assert result["commands_backed_up"] == 1  # Only cmd1 backed up
        assert (target / "cmd1.md").read_text() == "Command 1"
        assert (target / "cmd2.md").read_text() == "Command 2"
        assert (target / "cmd3.md").read_text() == "Command 3"
        assert (backup / "cmd1.md").read_text() == "Old Command 1"
