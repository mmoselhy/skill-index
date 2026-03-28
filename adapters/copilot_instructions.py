"""Adapter for github/awesome-copilot repository (official GitHub copilot instructions)."""
from __future__ import annotations

import logging
import re

from adapters.base import RawSkill
from adapters.classifier import FOLDER_MAP, classify_categories, slugify
from adapters.github_api import get_file, get_tree

logger = logging.getLogger(__name__)

REPO = "github/awesome-copilot"

# Map directory names to (language, framework).
COPILOT_LANG_MAP: dict[str, tuple[str, str | None]] = {
    **{k: v for k, v in FOLDER_MAP.items()},
    "csharp": ("any", "csharp"),
    "c-sharp": ("any", "csharp"),
    "bicep": ("any", "bicep"),
    "terraform": ("any", "terraform"),
    "docker": ("any", "docker"),
    "kubernetes": ("any", "kubernetes"),
    "github-actions": ("any", "github-actions"),
    "astro": ("typescript", "astro"),
    "blazor": ("any", "blazor"),
    "azure": ("any", "azure"),
}


class CopilotInstructionsAdapter:
    """Crawl github/awesome-copilot and extract instruction files."""

    repo = REPO
    trust = "official"

    def crawl(self) -> list[RawSkill]:
        """Fetch repo tree, find instruction markdown files."""
        tree = get_tree(self.repo)
        if not tree:
            logger.warning("Empty tree for %s", self.repo)
            return []

        instruction_paths = [
            item["path"]
            for item in tree
            if item["type"] == "blob"
            and item["path"].startswith("instructions/")
            and item["path"].endswith(".instructions.md")
        ]

        skills: list[RawSkill] = []
        for path in instruction_paths:
            match = re.match(r"instructions/([^/]+)/", path)
            if not match:
                continue

            tech_name = match.group(1)
            lang_fw = COPILOT_LANG_MAP.get(tech_name.lower())
            language = lang_fw[0] if lang_fw else "any"
            framework = lang_fw[1] if lang_fw else None

            content = get_file(self.repo, path)
            if not content:
                continue

            display_name = tech_name.replace("-", " ").title()
            categories = classify_categories(content)

            skills.append(
                RawSkill(
                    name=f"{display_name} Copilot Instructions",
                    content=content,
                    source_path=path,
                    language=language,
                    framework=framework,
                    categories=categories,
                    description=f"GitHub Copilot instructions for {display_name}.",
                    tags=[slugify(display_name), "copilot"],
                )
            )

        logger.info("Crawled %d skills from %s", len(skills), self.repo)
        return skills
