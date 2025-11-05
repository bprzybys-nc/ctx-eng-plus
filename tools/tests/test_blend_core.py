"""Unit tests for core blending framework."""

import pytest
from pathlib import Path
import tempfile
import shutil

from ce.blending.core import backup_context, BlendingOrchestrator
from ce.blending.strategies.base import BlendStrategy


class MockBlendStrategy(BlendStrategy):
    """Mock strategy for testing."""

    def can_handle(self, domain: str) -> bool:
        return domain == "mock"

    def blend(self, framework_content, target_content, context):
        return "blended_content"

    def validate(self, blended_content, context):
        return blended_content == "blended_content"

    def get_domain_name(self):
        return "Mock"


def test_backup_context_creates_and_removes_backup():
    """Test backup context manager creates and removes backups."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("original")

        # Use backup context
        with backup_context(test_file) as backup:
            # Backup should exist
            assert backup.exists()
            assert backup.read_text() == "original"

            # Modify file
            test_file.write_text("modified")

        # Backup should be removed after success
        assert not backup.exists()
        assert test_file.read_text() == "modified"


def test_backup_context_restores_on_exception():
    """Test backup context restores file on exception."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("original")

        try:
            with backup_context(test_file) as backup:
                # Modify file
                test_file.write_text("modified")
                # Raise exception
                raise ValueError("Test error")
        except ValueError:
            pass

        # File should be restored
        assert test_file.read_text() == "original"


def test_blending_orchestrator_registers_strategies():
    """Test strategy registration."""
    config = {"domains": {}}
    orchestrator = BlendingOrchestrator(config, dry_run=True)

    strategy = MockBlendStrategy()
    orchestrator.register_strategy(strategy)

    assert len(orchestrator.strategies) == 1
    assert orchestrator.strategies[0] == strategy


def test_blending_orchestrator_run_phase_validates_phase():
    """Test run_phase validates phase name."""
    config = {"domains": {}}
    orchestrator = BlendingOrchestrator(config, dry_run=True)

    with pytest.raises(ValueError, match="Unknown phase"):
        orchestrator.run_phase("invalid_phase", Path("."))


def test_blending_orchestrator_phase_stubs():
    """Test phase methods exist (stubs for subsequent PRPs)."""
    config = {"domains": {}}
    orchestrator = BlendingOrchestrator(config, dry_run=True)

    # All phase stubs should return dict
    result = orchestrator.run_phase("detect", Path("."))
    assert isinstance(result, dict)
    assert result["phase"] == "detect"
    assert result["implemented"] == False
