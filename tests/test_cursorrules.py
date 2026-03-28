"""Tests for the awesome-cursorrules adapter."""
from __future__ import annotations

from unittest.mock import patch

from adapters.cursorrules import CursorrulesAdapter


class TestCursorrulesAdapter:
    def test_init(self) -> None:
        adapter = CursorrulesAdapter()
        assert adapter.repo == "PatrickJS/awesome-cursorrules"
        assert adapter.trust == "community"

    @patch("adapters.cursorrules.get_tree")
    @patch("adapters.cursorrules.get_file")
    def test_crawl_parses_folder_structure(self, mock_get_file, mock_get_tree) -> None:
        """Adapter correctly parses folder names and fetches .cursorrules files."""
        mock_get_tree.return_value = [
            {"path": "rules/nextjs-cursorrules-prompt-file/.cursorrules", "type": "blob"},
            {"path": "rules/python-cursorrules-prompt-file/.cursorrules", "type": "blob"},
            {"path": "rules/unknown-thing/.cursorrules", "type": "blob"},
            {"path": "README.md", "type": "blob"},
        ]
        mock_get_file.side_effect = [
            "Use Server Components by default. Only use 'use client' when needed.",
            "Use snake_case for function names. Use pytest for testing.",
            "Some unknown content about coding.",
        ]

        adapter = CursorrulesAdapter()
        skills = adapter.crawl()

        assert len(skills) == 3

        nextjs = next(s for s in skills if "next" in s.name.lower() or s.framework == "next")
        assert nextjs.language == "typescript"
        assert nextjs.framework == "next"

        python_skill = next(s for s in skills if s.language == "python")
        assert python_skill.framework is None

    @patch("adapters.cursorrules.get_tree")
    @patch("adapters.cursorrules.get_file")
    def test_crawl_skips_empty_content(self, mock_get_file, mock_get_tree) -> None:
        mock_get_tree.return_value = [
            {"path": "rules/python-cursorrules-prompt-file/.cursorrules", "type": "blob"},
        ]
        mock_get_file.return_value = None
        adapter = CursorrulesAdapter()
        skills = adapter.crawl()
        assert len(skills) == 0
