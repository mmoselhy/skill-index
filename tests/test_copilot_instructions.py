"""Tests for the github/awesome-copilot adapter."""
from __future__ import annotations

from unittest.mock import patch

from adapters.copilot_instructions import CopilotInstructionsAdapter


class TestCopilotInstructionsAdapter:
    def test_init(self) -> None:
        adapter = CopilotInstructionsAdapter()
        assert adapter.repo == "github/awesome-copilot"
        assert adapter.trust == "official"

    @patch("adapters.copilot_instructions.get_tree")
    @patch("adapters.copilot_instructions.get_file")
    def test_crawl_finds_markdown_instructions(self, mock_get_file, mock_get_tree) -> None:
        mock_get_tree.return_value = [
            {"path": "instructions/python/python.instructions.md", "type": "blob"},
            {"path": "instructions/csharp/csharp.instructions.md", "type": "blob"},
            {"path": "README.md", "type": "blob"},
        ]
        mock_get_file.side_effect = [
            "# Python\nUse type hints. Use pytest for testing. Format with ruff.",
            "# C#\nUse async/await patterns. Follow .NET naming conventions.",
        ]

        adapter = CopilotInstructionsAdapter()
        skills = adapter.crawl()

        assert len(skills) == 2
        python_skill = next(s for s in skills if s.language == "python")
        assert python_skill.language == "python"
        assert "testing" in python_skill.categories or "code-style" in python_skill.categories

    @patch("adapters.copilot_instructions.get_tree")
    def test_crawl_handles_empty_tree(self, mock_get_tree) -> None:
        mock_get_tree.return_value = []
        adapter = CopilotInstructionsAdapter()
        skills = adapter.crawl()
        assert len(skills) == 0
