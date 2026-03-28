"""GitHub API helpers for fetching repo trees and file contents."""
from __future__ import annotations

import json
import logging
import os
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
GITHUB_RAW = "https://raw.githubusercontent.com"
TIMEOUT = 15


def _headers() -> dict[str, str]:
    """Build request headers, including auth token if available."""
    headers = {"User-Agent": "skill-index-builder/1.0"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def get_tree(repo: str, path_prefix: str = "") -> list[dict]:
    """Fetch the file tree for a repo (or subdirectory).

    Returns a list of dicts with 'path' and 'type' keys.
    Uses the Git Trees API with recursive=1 for efficiency.
    """
    url = f"{GITHUB_API}/repos/{repo}/git/trees/HEAD?recursive=1"
    try:
        req = Request(url, headers=_headers())
        with urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
        tree = data.get("tree", [])
        if path_prefix:
            prefix = path_prefix.rstrip("/") + "/"
            tree = [
                {**item, "path": item["path"][len(prefix):]}
                for item in tree
                if item["path"].startswith(prefix)
            ]
        return tree
    except Exception:
        logger.warning("Failed to fetch tree for %s", repo, exc_info=True)
        return []


def get_file(repo: str, path: str, branch: str = "main") -> str | None:
    """Fetch raw file content from a GitHub repo."""
    url = f"{GITHUB_RAW}/{repo}/{branch}/{path}"
    try:
        req = Request(url, headers=_headers())
        with urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read().decode("utf-8")
    except Exception:
        logger.debug("Failed to fetch %s/%s", repo, path, exc_info=True)
        return None


def raw_url(repo: str, path: str, branch: str = "main") -> str:
    """Construct the raw.githubusercontent.com URL for a file."""
    return f"{GITHUB_RAW}/{repo}/{branch}/{path}"
