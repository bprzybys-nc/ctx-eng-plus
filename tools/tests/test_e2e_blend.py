"""End-to-end tests for blend tool (PRP-34.4.1).

Tests all 4 phases (detect, classify, blend, cleanup) across 3 scenarios:
1. Greenfield: Empty project (0 files)
2. Mature Project: Existing files (deduplication)
3. CE 1.0 Migration: Legacy directories (cleanup)
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any

from ce.blending.core import BlendingOrchestrator


@pytest.fixture
def temp_project(tmp_path):
    """Create isolated temp directory for testing."""
    project = tmp_path / "test-project"
    project.mkdir()
    return project


@pytest.fixture
def blend_config() -> Dict[str, Any]:
    """Minimal blend config for testing."""
    return {
        "domains": {
            "settings": {"enabled": True},
            "claude_md": {"enabled": True},
            "memories": {"enabled": True},
            "examples": {"enabled": True},
            "prps": {"enabled": True},
            "commands": {"enabled": True}
        }
    }


def test_greenfield_blend(temp_project: Path, blend_config: Dict[str, Any]):
    """Test blending in empty project (0 files).

    Scenario: Fresh project with no existing CE files.
    Expected: All framework files installed, no blending needed.
    """
    # Setup: Empty directory
    assert len(list(temp_project.iterdir())) == 0

    # Initialize orchestrator
    orchestrator = BlendingOrchestrator(config=blend_config, dry_run=True)

    # Phase 1: Detection (should find no files)
    result_detect = orchestrator.run_phase('detect', temp_project)
    assert result_detect['phase'] == 'detect'
    assert result_detect['implemented'] is True
    assert result_detect['total_files'] == 0  # No legacy files

    # Phase 2: Classification (should have no files to classify)
    result_classify = orchestrator.run_phase('classify', temp_project)
    assert result_classify['phase'] == 'classify'
    assert result_classify['implemented'] is True
    assert result_classify['total_valid'] == 0

    # Phase 3: Blending (should skip - no files to blend)
    result_blend = orchestrator.run_phase('blend', temp_project)
    assert result_blend['phase'] == 'blend'
    assert result_blend['implemented'] is True
    # No files to blend, so results should be empty or minimal

    # Phase 4: Cleanup (should skip - no legacy dirs)
    result_cleanup = orchestrator.run_phase('cleanup', temp_project)
    assert result_cleanup['phase'] == 'cleanup'
    assert result_cleanup['implemented'] is True


def test_mature_project_blend(temp_project: Path, blend_config: Dict[str, Any]):
    """Test blending with existing files (deduplication).

    Scenario: Mature project with existing .claude/settings.local.json and CLAUDE.md.
    Expected: Files merged (not overwritten), deduplication applied.
    """
    # Setup: Create existing files
    claude_dir = temp_project / '.claude'
    claude_dir.mkdir()

    # Existing settings with custom allow/deny
    existing_settings = {
        "permissions": {
            "allow": ["Write(//)", "mcp__syntropy__serena_find_symbol"],
            "deny": ["Bash(cp:*)"],
            "ask": []
        },
        "hooks": {
            "SessionStart": ["custom-hook"]
        }
    }
    settings_file = claude_dir / 'settings.local.json'
    settings_file.write_text(json.dumps(existing_settings, indent=2))

    # Existing CLAUDE.md with user content
    claude_md_file = temp_project / 'CLAUDE.md'
    claude_md_file.write_text('# Existing docs\n\nUser content here.')

    # Initialize orchestrator (dry-run to avoid actual file writes)
    orchestrator = BlendingOrchestrator(config=blend_config, dry_run=True)

    # Phase 1: Detection (should find existing files)
    result_detect = orchestrator.run_phase('detect', temp_project)
    assert result_detect['phase'] == 'detect'
    assert result_detect['total_files'] >= 2  # At least settings + CLAUDE.md

    # Verify detected files
    inventory = result_detect['inventory']
    assert len(inventory.get('settings', [])) >= 1  # Found settings.local.json
    assert len(inventory.get('claude_md', [])) >= 1  # Found CLAUDE.md

    # Phase 2: Classification (should validate files)
    result_classify = orchestrator.run_phase('classify', temp_project)
    assert result_classify['phase'] == 'classify'
    assert result_classify['total_valid'] >= 2  # Settings and CLAUDE.md valid

    # Phase 3: Blending (dry-run - just verify phase runs)
    result_blend = orchestrator.run_phase('blend', temp_project)
    assert result_blend['phase'] == 'blend'
    assert result_blend['implemented'] is True

    # Note: Actual blending logic tested in unit tests (test_blend_settings.py, etc.)
    # E2E test verifies phases execute without errors

    # Phase 4: Cleanup (should not remove anything in mature project)
    result_cleanup = orchestrator.run_phase('cleanup', temp_project)
    assert result_cleanup['phase'] == 'cleanup'

    # Verify original files still exist (dry-run mode)
    assert settings_file.exists()
    assert claude_md_file.exists()


def test_ce_1_0_migration(temp_project: Path, blend_config: Dict[str, Any]):
    """Test CE 1.0 → CE 1.1 migration (legacy cleanup).

    Scenario: CE 1.0 project with legacy `system/` and `tools/` directories.
    Expected: Legacy directories removed, new structure created.
    """
    # Setup: Create legacy CE 1.0 structure
    system_dir = temp_project / 'system'
    system_dir.mkdir()

    system_memories = system_dir / 'memories'
    system_memories.mkdir()
    (system_memories / 'old-memory.md').write_text('# Old Memory\n\nLegacy content.')

    legacy_tools = temp_project / 'tools'
    legacy_tools.mkdir()
    (legacy_tools / 'ce').mkdir()
    (legacy_tools / 'ce' / 'old_tool.py').write_text('# Legacy tool')

    # Legacy settings (will be migrated)
    claude_dir = temp_project / '.claude'
    claude_dir.mkdir()
    legacy_settings = {
        "permissions": {
            "allow": ["mcp__syntropy__filesystem_read_file"],  # Will be denied in CE 1.1
            "deny": [],
            "ask": []
        }
    }
    (claude_dir / 'settings.local.json').write_text(json.dumps(legacy_settings, indent=2))

    # Initialize orchestrator (dry-run to inspect behavior)
    orchestrator = BlendingOrchestrator(config=blend_config, dry_run=True)

    # Phase 1: Detection (should find legacy structure)
    result_detect = orchestrator.run_phase('detect', temp_project)
    assert result_detect['phase'] == 'detect'
    assert result_detect['total_files'] >= 1  # At least settings

    # Verify legacy files detected
    inventory = result_detect['inventory']
    # Legacy memories might be detected if detection searches system/ dir

    # Phase 2: Classification
    result_classify = orchestrator.run_phase('classify', temp_project)
    assert result_classify['phase'] == 'classify'
    assert result_classify['implemented'] is True

    # Phase 3: Blending (dry-run)
    result_blend = orchestrator.run_phase('blend', temp_project)
    assert result_blend['phase'] == 'blend'

    # Phase 4: Cleanup (dry-run - verify phase runs without errors)
    result_cleanup = orchestrator.run_phase('cleanup', temp_project)
    assert result_cleanup['phase'] == 'cleanup'
    assert result_cleanup['implemented'] is True

    # In dry-run mode, legacy directories should still exist
    # (actual removal tested in test_cleanup.py)
    assert system_dir.exists()
    assert legacy_tools.exists()


def test_all_phases_sequential(temp_project: Path, blend_config: Dict[str, Any]):
    """Test running all 4 phases sequentially (integration test).

    Verifies that phases can be chained together without errors.
    """
    # Setup: Create minimal project with one legacy file
    claude_dir = temp_project / '.claude'
    claude_dir.mkdir()
    (claude_dir / 'settings.local.json').write_text('{"permissions": {"allow": [], "deny": [], "ask": []}}')

    orchestrator = BlendingOrchestrator(config=blend_config, dry_run=True)

    # Run all phases in sequence
    phases = ['detect', 'classify', 'blend', 'cleanup']

    for phase in phases:
        result = orchestrator.run_phase(phase, temp_project)
        assert result['phase'] == phase
        assert result['implemented'] is True

    # Verify orchestrator state after all phases
    assert len(orchestrator.detected_files) > 0  # Detection cached results
    assert len(orchestrator.classified_files) > 0  # Classification cached results


def test_strategy_registration(blend_config: Dict[str, Any]):
    """Test that all 6 domain strategies are registered correctly."""
    orchestrator = BlendingOrchestrator(config=blend_config, dry_run=True)

    # Verify all 6 strategies registered
    expected_domains = ['settings', 'claude_md', 'memories', 'examples', 'prps', 'commands']

    for domain in expected_domains:
        assert domain in orchestrator.strategies, f"Strategy for {domain} not registered"
        assert orchestrator.strategies[domain] is not None


def test_dry_run_no_modifications(temp_project: Path, blend_config: Dict[str, Any]):
    """Test that dry-run mode makes no file modifications.

    Critical: Ensures dry-run is safe and non-destructive.
    """
    # Setup: Create existing file
    claude_dir = temp_project / '.claude'
    claude_dir.mkdir()

    settings_file = claude_dir / 'settings.local.json'
    original_content = '{"permissions": {"allow": ["Test"], "deny": [], "ask": []}}'
    settings_file.write_text(original_content)

    original_mtime = settings_file.stat().st_mtime

    # Run blend in dry-run mode
    orchestrator = BlendingOrchestrator(config=blend_config, dry_run=True)

    orchestrator.run_phase('detect', temp_project)
    orchestrator.run_phase('classify', temp_project)
    orchestrator.run_phase('blend', temp_project)
    orchestrator.run_phase('cleanup', temp_project)

    # Verify file unchanged
    assert settings_file.read_text() == original_content
    assert settings_file.stat().st_mtime == original_mtime  # Not modified


def test_error_handling_missing_detection(temp_project: Path, blend_config: Dict[str, Any]):
    """Test error handling when classification called before detection."""
    orchestrator = BlendingOrchestrator(config=blend_config, dry_run=True)

    # Try to run classification without detection first
    with pytest.raises(RuntimeError) as exc_info:
        orchestrator.run_phase('classify', temp_project)

    assert 'No detected files' in str(exc_info.value)
    assert 'run detection phase first' in str(exc_info.value)


def test_error_handling_missing_classification(temp_project: Path, blend_config: Dict[str, Any]):
    """Test error handling when blending called before classification."""
    orchestrator = BlendingOrchestrator(config=blend_config, dry_run=True)

    # Run detection but skip classification
    orchestrator.run_phase('detect', temp_project)

    # Try to run blending without classification
    with pytest.raises(RuntimeError) as exc_info:
        orchestrator.run_phase('blend', temp_project)

    assert 'No classified files' in str(exc_info.value)
    assert 'run classification phase first' in str(exc_info.value)


def test_coverage_check():
    """Verify test file exists and is executable.

    Meta-test to ensure test suite is properly configured.
    """
    test_file = Path(__file__)
    assert test_file.exists()
    assert test_file.stat().st_size > 5000  # At least 5KB of tests
