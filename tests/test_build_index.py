"""Tests for the index build pipeline."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from adapters.base import RawSkill
from build_index import build_index, deduplicate, raw_skill_to_index_entry


def _make_raw_skill(
    name: str = "Test Skill",
    language: str = "python",
    framework: str | None = None,
    source_path: str = "test.md",
) -> RawSkill:
    return RawSkill(
        name=name,
        content="# Test\nContent here.",
        source_path=source_path,
        language=language,
        framework=framework,
        categories=["testing"],
        description="A test skill.",
        tags=["test"],
        updated_at="2026-03-28",
    )


class TestRawSkillToIndexEntry:
    def test_converts_correctly(self) -> None:
        raw = _make_raw_skill()
        entry = raw_skill_to_index_entry(
            raw, source_repo="anthropics/skills", trust="official", source_prefix="anthropic"
        )
        assert entry["id"] == "anthropic-test-skill"
        assert entry["name"] == "Test Skill"
        assert entry["language"] == "python"
        assert entry["trust"] == "official"
        assert entry["source_repo"] == "anthropics/skills"
        assert "raw.githubusercontent.com" in entry["content_url"]
        assert entry["format"] == "markdown"


class TestDeduplicate:
    def test_keeps_highest_trust(self) -> None:
        entries = [
            {"id": "a-pytest", "name": "Pytest", "language": "python",
             "framework": None, "trust": "community", "source_repo": "a/b"},
            {"id": "b-pytest", "name": "Pytest", "language": "python",
             "framework": None, "trust": "official", "source_repo": "c/d"},
        ]
        result = deduplicate(entries)
        assert len(result) == 1
        assert result[0]["trust"] == "official"

    def test_different_languages_kept(self) -> None:
        entries = [
            {"id": "a-skill", "name": "Testing", "language": "python",
             "framework": None, "trust": "community", "source_repo": "a/b"},
            {"id": "b-skill", "name": "Testing", "language": "typescript",
             "framework": None, "trust": "community", "source_repo": "c/d"},
        ]
        result = deduplicate(entries)
        assert len(result) == 2

    def test_same_name_same_framework_deduped(self) -> None:
        entries = [
            {"id": "a-react", "name": "React", "language": "typescript",
             "framework": "react", "trust": "community", "source_repo": "a/b"},
            {"id": "b-react", "name": "React", "language": "typescript",
             "framework": "react", "trust": "community", "source_repo": "c/d"},
        ]
        result = deduplicate(entries)
        assert len(result) == 1


class TestBuildIndex:
    def test_build_writes_valid_json(self, tmp_path: Path) -> None:
        # Create a minimal sources.json with no enabled sources
        sources_file = tmp_path / "sources.json"
        sources_file.write_text('{"sources": []}')

        # Create contributed/ with one skill
        contributed_dir = tmp_path / "contributed"
        contributed_dir.mkdir()
        (contributed_dir / "custom-skill.md").write_text("# Custom\nMy custom skill.")

        output_file = tmp_path / "index.json"
        build_index(
            sources_file=sources_file,
            contributed_dir=contributed_dir,
            output_file=output_file,
        )

        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data["version"] == 2
        assert isinstance(data["skills"], list)
        assert len(data["skills"]) == 1
        assert data["skills"][0]["trust"] == "contributed"
