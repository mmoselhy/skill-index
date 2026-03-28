"""Tests for the anthropics/skills adapter."""
from __future__ import annotations

from unittest.mock import patch

from adapters.anthropic_skills import AnthropicSkillsAdapter


SAMPLE_SKILL_MD = """---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces
license: Apache-2.0
---

# Frontend Design

Build high-quality web UIs with modern CSS and component patterns.

## Architecture
- Use component composition over inheritance
- Keep components focused and reusable
"""


class TestAnthropicSkillsAdapter:
    def test_init(self) -> None:
        adapter = AnthropicSkillsAdapter()
        assert adapter.repo == "anthropics/skills"
        assert adapter.trust == "official"

    @patch("adapters.anthropic_skills.get_tree")
    @patch("adapters.anthropic_skills.get_file")
    def test_crawl_parses_skill_md(self, mock_get_file, mock_get_tree) -> None:
        mock_get_tree.return_value = [
            {"path": "skills/frontend-design/SKILL.md", "type": "blob"},
            {"path": "skills/frontend-design/scripts/build.sh", "type": "blob"},
            {"path": "README.md", "type": "blob"},
        ]
        mock_get_file.return_value = SAMPLE_SKILL_MD

        adapter = AnthropicSkillsAdapter()
        skills = adapter.crawl()

        assert len(skills) == 1
        skill = skills[0]
        assert skill.name == "frontend-design"
        assert "Create distinctive" in skill.description
        assert skill.language == "any"
        assert "architecture" in skill.categories

    @patch("adapters.anthropic_skills.get_tree")
    @patch("adapters.anthropic_skills.get_file")
    def test_crawl_skips_non_skill_dirs(self, mock_get_file, mock_get_tree) -> None:
        mock_get_tree.return_value = [
            {"path": "README.md", "type": "blob"},
            {"path": "LICENSE", "type": "blob"},
        ]

        adapter = AnthropicSkillsAdapter()
        skills = adapter.crawl()
        assert len(skills) == 0
        mock_get_file.assert_not_called()
