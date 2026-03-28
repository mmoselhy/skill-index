#!/usr/bin/env python3
"""Build the skill index by crawling trusted sources and merging results."""
from __future__ import annotations

import importlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from adapters.base import RawSkill, load_sources
from adapters.classifier import classify_categories, slugify
from adapters.github_api import raw_url

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

TRUST_ORDER = {"official": 0, "community": 1, "contributed": 2}

# Map adapter names to module.ClassName
ADAPTER_REGISTRY: dict[str, tuple[str, str]] = {
    "anthropic_skills": ("adapters.anthropic_skills", "AnthropicSkillsAdapter"),
    "copilot_instructions": ("adapters.copilot_instructions", "CopilotInstructionsAdapter"),
    "cursorrules": ("adapters.cursorrules", "CursorrulesAdapter"),
}


def raw_skill_to_index_entry(
    raw: RawSkill,
    source_repo: str,
    trust: str,
    source_prefix: str,
) -> dict:
    """Convert a RawSkill into an index.json entry dict."""
    return {
        "id": f"{source_prefix}-{slugify(raw.name)}",
        "name": raw.name,
        "language": raw.language,
        "framework": raw.framework,
        "categories": raw.categories,
        "description": raw.description,
        "source_repo": source_repo,
        "source_path": raw.source_path,
        "content_url": raw_url(source_repo, raw.source_path),
        "trust": trust,
        "format": "markdown",
        "tags": raw.tags,
        "updated_at": raw.updated_at,
    }


def deduplicate(entries: list[dict]) -> list[dict]:
    """Deduplicate by (language, framework, name). Keep highest trust."""
    seen: dict[tuple, dict] = {}
    for entry in entries:
        key = (
            entry.get("language", "").lower(),
            (entry.get("framework") or "").lower(),
            entry.get("name", "").lower(),
        )
        existing = seen.get(key)
        if existing is None:
            seen[key] = entry
        else:
            # Keep higher trust (lower order number)
            existing_rank = TRUST_ORDER.get(existing["trust"], 99)
            new_rank = TRUST_ORDER.get(entry["trust"], 99)
            if new_rank < existing_rank:
                seen[key] = entry
    return list(seen.values())


def _load_contributed(contributed_dir: Path) -> list[dict]:
    """Load manually contributed skills from contributed/*.md."""
    entries: list[dict] = []
    if not contributed_dir.is_dir():
        return entries
    for md_file in sorted(contributed_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        name = md_file.stem.replace("-", " ").title()
        categories = classify_categories(content)
        entries.append({
            "id": f"contributed-{slugify(name)}",
            "name": name,
            "language": "any",
            "framework": None,
            "categories": categories,
            "description": f"Community-contributed skill: {name}.",
            "source_repo": "",
            "source_path": f"contributed/{md_file.name}",
            "content_url": "",
            "trust": "contributed",
            "format": "markdown",
            "tags": [],
            "updated_at": "",
        })
    return entries


def build_index(
    sources_file: Path | None = None,
    contributed_dir: Path | None = None,
    output_file: Path | None = None,
) -> None:
    """Main build pipeline: load sources, run adapters, dedupe, write index."""
    root = Path(__file__).parent
    sources_file = sources_file or root / "sources.json"
    contributed_dir = contributed_dir or root / "contributed"
    output_file = output_file or root / "index.json"

    configs = load_sources(sources_file)
    all_entries: list[dict] = []
    sources_crawled: list[str] = []

    for config in configs:
        adapter_info = ADAPTER_REGISTRY.get(config.adapter)
        if adapter_info is None:
            logger.warning("Unknown adapter: %s (skipping %s)", config.adapter, config.repo)
            continue

        module_name, class_name = adapter_info
        try:
            module = importlib.import_module(module_name)
            adapter_class = getattr(module, class_name)
            adapter = adapter_class()
            raw_skills = adapter.crawl()
        except Exception:
            logger.warning("Adapter %s failed for %s", config.adapter, config.repo, exc_info=True)
            continue

        source_prefix = config.repo.split("/")[-1].lower().replace("-", "")
        for raw in raw_skills:
            entry = raw_skill_to_index_entry(raw, config.repo, config.trust, source_prefix)
            all_entries.append(entry)

        sources_crawled.append(config.repo)
        logger.info("  %s: %d skills", config.repo, len(raw_skills))

    # Add contributed skills
    contributed = _load_contributed(contributed_dir)
    all_entries.extend(contributed)

    # Deduplicate
    deduped = deduplicate(all_entries)

    # Sort: official first, then community, then contributed
    deduped.sort(key=lambda e: (TRUST_ORDER.get(e["trust"], 99), e["name"].lower()))

    # Count by trust
    counts = {}
    for e in deduped:
        counts[e["trust"]] = counts.get(e["trust"], 0) + 1

    index = {
        "version": 2,
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources_crawled": sources_crawled,
        "skills": deduped,
    }

    output_file.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")

    stats_parts = [f"{v} {k}" for k, v in sorted(counts.items(), key=lambda x: TRUST_ORDER.get(x[0], 99))]
    logger.info(
        "Built index: %d skills from %d sources (%s)",
        len(deduped), len(sources_crawled), ", ".join(stats_parts),
    )


if __name__ == "__main__":
    build_index()
