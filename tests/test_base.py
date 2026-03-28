"""Tests for adapter base data structures."""
from __future__ import annotations

from adapters.base import RawSkill, SourceConfig, load_sources


class TestRawSkill:
    def test_create_raw_skill(self) -> None:
        skill = RawSkill(
            name="Test Skill",
            content="# Test\nSome content",
            source_path="skills/test.md",
            language="python",
            framework=None,
            categories=["testing"],
            description="A test skill",
            tags=["test"],
            updated_at="2026-03-28",
        )
        assert skill.name == "Test Skill"
        assert skill.language == "python"
        assert skill.framework is None
        assert skill.categories == ["testing"]


class TestSourceConfig:
    def test_create_source_config(self) -> None:
        config = SourceConfig(
            repo="anthropics/skills",
            adapter="anthropic_skills",
            trust="official",
            enabled=True,
        )
        assert config.repo == "anthropics/skills"
        assert config.trust == "official"

    def test_create_with_path_prefix(self) -> None:
        config = SourceConfig(
            repo="anthropics/claude-code",
            adapter="anthropic_plugins",
            trust="official",
            enabled=True,
            path_prefix="plugins",
        )
        assert config.path_prefix == "plugins"


class TestLoadSources:
    def test_load_sources_from_json(self, tmp_path) -> None:
        sources_file = tmp_path / "sources.json"
        sources_file.write_text(
            '{"sources": [{"repo": "anthropics/skills", "adapter": "anthropic_skills", '
            '"trust": "official", "enabled": true}]}'
        )
        configs = load_sources(sources_file)
        assert len(configs) == 1
        assert configs[0].repo == "anthropics/skills"

    def test_disabled_sources_excluded(self, tmp_path) -> None:
        sources_file = tmp_path / "sources.json"
        sources_file.write_text(
            '{"sources": ['
            '{"repo": "a/b", "adapter": "x", "trust": "official", "enabled": true},'
            '{"repo": "c/d", "adapter": "y", "trust": "community", "enabled": false}'
            ']}'
        )
        configs = load_sources(sources_file)
        assert len(configs) == 1
        assert configs[0].repo == "a/b"
