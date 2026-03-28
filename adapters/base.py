"""Base data structures and protocol for source adapters."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass
class RawSkill:
    """A skill extracted from a source before normalization."""

    name: str
    content: str
    source_path: str
    language: str
    framework: str | None
    categories: list[str]
    description: str
    tags: list[str] = field(default_factory=list)
    updated_at: str = ""


@dataclass
class SourceConfig:
    """Configuration for a single source in sources.json."""

    repo: str
    adapter: str
    trust: str
    enabled: bool
    path_prefix: str = ""


class Adapter(Protocol):
    """Protocol that all source adapters must implement."""

    repo: str
    trust: str

    def crawl(self) -> list[RawSkill]: ...


def load_sources(path: Path) -> list[SourceConfig]:
    """Load and filter enabled sources from sources.json."""
    data = json.loads(path.read_text(encoding="utf-8"))
    configs: list[SourceConfig] = []
    for item in data["sources"]:
        config = SourceConfig(
            repo=item["repo"],
            adapter=item["adapter"],
            trust=item["trust"],
            enabled=item.get("enabled", True),
            path_prefix=item.get("path_prefix", ""),
        )
        if config.enabled:
            configs.append(config)
    return configs
