"""Unit tests for BlendConfig class."""

import pytest
from pathlib import Path
from ce.config_loader import BlendConfig


class TestBlendConfigLoading:
    """Test config file loading and validation."""

    def test_load_valid_config(self):
        """Test loading valid blend-config.yml."""
        config_path = Path(__file__).parent.parent.parent / ".ce" / "blend-config.yml"
        config = BlendConfig(config_path)
        assert config._config is not None
        assert "domains" in config._config

    def test_missing_config_file(self):
        """Test error when config file doesn't exist."""
        with pytest.raises(ValueError, match="Config file not found"):
            BlendConfig(Path("/nonexistent/path/blend-config.yml"))

    def test_missing_domains_section(self):
        """Test error when domains section missing."""
        import tempfile
        import yaml

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump({"other": "value"}, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Missing required section"):
                BlendConfig(Path(temp_path))
        finally:
            Path(temp_path).unlink()


class TestGetOutputPath:
    """Test output path retrieval."""

    @pytest.fixture
    def config(self):
        """Load test config."""
        config_path = Path(__file__).parent.parent.parent / ".ce" / "blend-config.yml"
        return BlendConfig(config_path)

    def test_get_claude_dir_output_path(self, config):
        """Test getting .claude directory output path."""
        path = config.get_output_path("claude_dir")
        assert path == Path(".ce/.claude")

    def test_get_claude_md_output_path(self, config):
        """Test getting CLAUDE.md output path."""
        path = config.get_output_path("claude_md")
        assert path == Path("CLAUDE.md")

    def test_get_serena_memories_output_path(self, config):
        """Test getting .serena/memories/ output path."""
        path = config.get_output_path("serena_memories")
        assert path == Path(".serena/memories/")

    def test_get_examples_output_path(self, config):
        """Test getting .ce/examples/ output path."""
        path = config.get_output_path("examples")
        assert path == Path(".ce/examples/")

    def test_get_prps_output_path(self, config):
        """Test getting .ce/PRPs/ output path."""
        path = config.get_output_path("prps")
        assert path == Path(".ce/PRPs/")

    def test_invalid_output_domain(self, config):
        """Test error for invalid domain."""
        with pytest.raises(ValueError, match="Unknown output domain"):
            config.get_output_path("nonexistent_domain")


class TestGetFrameworkPath:
    """Test framework path retrieval."""

    @pytest.fixture
    def config(self):
        """Load test config."""
        config_path = Path(__file__).parent.parent.parent / ".ce" / "blend-config.yml"
        return BlendConfig(config_path)

    def test_get_serena_memories_framework_path(self, config):
        """Test getting framework .serena/memories/ path."""
        path = config.get_framework_path("serena_memories")
        assert path == Path(".ce/.serena/memories/")

    def test_get_examples_framework_path(self, config):
        """Test getting framework examples path."""
        path = config.get_framework_path("examples")
        assert path == Path(".ce/examples/")

    def test_get_prps_framework_path(self, config):
        """Test getting framework PRPs path."""
        path = config.get_framework_path("prps")
        assert path == Path(".ce/PRPs/")

    def test_get_commands_framework_path(self, config):
        """Test getting framework commands path."""
        path = config.get_framework_path("commands")
        assert path == Path(".ce/.claude/commands/")

    def test_invalid_framework_domain(self, config):
        """Test error for invalid framework domain."""
        with pytest.raises(ValueError, match="Unknown framework domain"):
            config.get_framework_path("nonexistent_domain")


class TestGetLegacyPaths:
    """Test legacy path retrieval."""

    @pytest.fixture
    def config(self):
        """Load test config."""
        config_path = Path(__file__).parent.parent.parent / ".ce" / "blend-config.yml"
        return BlendConfig(config_path)

    def test_get_legacy_paths(self, config):
        """Test getting all legacy paths."""
        paths = config.get_legacy_paths()
        assert isinstance(paths, list)
        assert len(paths) > 0
        assert Path("PRPs/") in paths
        assert Path("examples/") in paths
        assert Path("context-engineering/") in paths

    def test_legacy_paths_are_pathlib_objects(self, config):
        """Test that legacy paths are Path objects."""
        paths = config.get_legacy_paths()
        for path in paths:
            assert isinstance(path, Path)


class TestGetDomainConfig:
    """Test domain-specific config retrieval."""

    @pytest.fixture
    def config(self):
        """Load test config."""
        config_path = Path(__file__).parent.parent.parent / ".ce" / "blend-config.yml"
        return BlendConfig(config_path)

    def test_get_settings_domain_config(self, config):
        """Test getting settings domain config."""
        domain_config = config.get_domain_config("settings")
        assert isinstance(domain_config, dict)
        assert "strategy" in domain_config

    def test_get_nonexistent_domain_config(self, config):
        """Test getting nonexistent domain returns empty dict."""
        domain_config = config.get_domain_config("nonexistent")
        assert domain_config == {}


class TestGetDomainLegacySources:
    """Test domain-specific legacy source retrieval."""

    @pytest.fixture
    def config(self):
        """Load test config."""
        config_path = Path(__file__).parent.parent.parent / ".ce" / "blend-config.yml"
        return BlendConfig(config_path)

    def test_get_prps_legacy_sources(self, config):
        """Test getting legacy sources for PRPs domain."""
        sources = config.get_domain_legacy_sources("prps")
        assert isinstance(sources, list)
        # PRPs has legacy_sources defined in domain config
        assert len(sources) > 0

    def test_get_memories_legacy_sources(self, config):
        """Test getting legacy sources for memories domain."""
        sources = config.get_domain_legacy_sources("memories")
        assert isinstance(sources, list)
        # Memories may not have domain-specific legacy_source,
        # so we just verify it returns a list (empty is ok)
        assert isinstance(sources, list)
