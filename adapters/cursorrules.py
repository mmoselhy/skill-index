"""Adapter for PatrickJS/awesome-cursorrules repository."""
from __future__ import annotations

import logging
import re

from adapters.base import RawSkill
from adapters.classifier import classify_categories, detect_language_framework, slugify
from adapters.github_api import get_file, get_tree, raw_url

logger = logging.getLogger(__name__)

REPO = "PatrickJS/awesome-cursorrules"


class CursorrulesAdapter:
    """Crawl awesome-cursorrules and extract skills from .cursorrules files."""

    repo = REPO
    trust = "community"

    def crawl(self) -> list[RawSkill]:
        """Fetch repo tree, find .cursorrules files, extract metadata."""
        tree = get_tree(self.repo)
        if not tree:
            logger.warning("Empty tree for %s", self.repo)
            return []

        cursorrule_files = [
            item["path"]
            for item in tree
            if item["type"] == "blob"
            and item["path"].startswith("rules/")
            and item["path"].endswith(".cursorrules")
        ]

        skills: list[RawSkill] = []
        for file_path in cursorrule_files:
            match = re.match(r"rules/([^/]+)/", file_path)
            if not match:
                continue

            folder_name = match.group(1)
            language, framework = detect_language_framework(folder_name)

            content = get_file(self.repo, file_path)
            if not content:
                continue

            display_name = folder_name.replace("-cursorrules-prompt-file", "")
            display_name = display_name.replace("-", " ").title()

            categories = classify_categories(content)

            skills.append(
                RawSkill(
                    name=f"{display_name} Cursor Rules",
                    content=content,
                    source_path=file_path,
                    language=language or "any",
                    framework=framework,
                    categories=categories,
                    description=f"Cursor rules for {display_name} development.",
                    tags=[slugify(display_name)],
                )
            )

        logger.info("Crawled %d skills from %s", len(skills), self.repo)
        return skills
