"""Adapter for anthropics/skills repository (official Anthropic agent skills)."""
from __future__ import annotations

import logging
import re

import yaml

from adapters.base import RawSkill
from adapters.classifier import classify_categories
from adapters.github_api import get_file, get_tree, raw_url

logger = logging.getLogger(__name__)

REPO = "anthropics/skills"


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Split YAML frontmatter from markdown body.

    Returns (metadata_dict, body_string). Returns ({}, content) if no frontmatter.
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match:
        return {}, content
    try:
        metadata = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}, content
    return metadata, match.group(2)


class AnthropicSkillsAdapter:
    """Crawl anthropics/skills and extract skills from SKILL.md files."""

    repo = REPO
    trust = "official"

    def crawl(self) -> list[RawSkill]:
        """Fetch repo tree, find SKILL.md files, parse frontmatter."""
        tree = get_tree(self.repo)
        if not tree:
            logger.warning("Empty tree for %s", self.repo)
            return []

        skill_paths = [
            item["path"]
            for item in tree
            if item["type"] == "blob"
            and item["path"].startswith("skills/")
            and item["path"].endswith("/SKILL.md")
        ]

        skills: list[RawSkill] = []
        for path in skill_paths:
            content = get_file(self.repo, path)
            if not content:
                continue

            metadata, body = _parse_frontmatter(content)
            name = metadata.get("name", path.split("/")[-2])
            description = metadata.get("description", "")
            categories = classify_categories(body)

            skills.append(
                RawSkill(
                    name=name,
                    content=content,
                    source_path=path,
                    language="any",
                    framework=None,
                    categories=categories,
                    description=description,
                    tags=[name],
                )
            )

        logger.info("Crawled %d skills from %s", len(skills), self.repo)
        return skills
