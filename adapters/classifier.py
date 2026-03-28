"""Category classification and language/framework detection for unstructured content."""
from __future__ import annotations

import re

# Keyword → category mapping. Each keyword list is checked against lowercased content.
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "naming-conventions": [
        "naming", "convention", "snake_case", "camelcase", "pascalcase",
        "variable name", "function name", "class name",
    ],
    "error-handling": [
        "error", "exception", "try", "catch", "except", "raise", "throw",
        "error handling", "error response",
    ],
    "testing": [
        "test", "spec", "assert", "mock", "fixture", "pytest", "jest",
        "vitest", "mocha", "unittest",
    ],
    "imports-and-dependencies": [
        "import", "require", "dependency", "module", "package",
        "from import", "import from",
    ],
    "documentation": [
        "docstring", "jsdoc", "comment", "documentation", "godoc",
        "type annotation", "type hint",
    ],
    "architecture": [
        "architect", "structure", "layout", "pattern", "directory",
        "module", "layer", "component", "service", "controller",
        "dependency injection", "middleware",
    ],
    "code-style": [
        "format", "lint", "style", "indent", "semicolon", "quote",
        "prettier", "eslint", "ruff", "black", "line length",
    ],
    "logging-and-observability": [
        "log", "logging", "trace", "tracing", "metric", "monitor",
        "observability", "structlog", "winston", "pino",
    ],
}

# Minimum keyword hits to assign a category.
CATEGORY_THRESHOLD = 2

# Folder name → (language, framework) mapping for awesome-cursorrules.
FOLDER_MAP: dict[str, tuple[str, str | None]] = {
    "nextjs": ("typescript", "next"),
    "next-js": ("typescript", "next"),
    "react": ("typescript", "react"),
    "react-native": ("typescript", "react-native"),
    "angular": ("typescript", "angular"),
    "vue": ("typescript", "vue"),
    "vuejs": ("typescript", "vue"),
    "svelte": ("typescript", "svelte"),
    "sveltekit": ("typescript", "svelte"),
    "typescript": ("typescript", None),
    "javascript": ("javascript", None),
    "nodejs": ("javascript", "node"),
    "node": ("javascript", "node"),
    "express": ("javascript", "express"),
    "nestjs": ("typescript", "nest"),
    "python": ("python", None),
    "django": ("python", "django"),
    "fastapi": ("python", "fastapi"),
    "flask": ("python", "flask"),
    "go": ("go", None),
    "golang": ("go", None),
    "gin": ("go", "gin"),
    "rust": ("rust", None),
    "actix": ("rust", "actix"),
    "tokio": ("rust", "tokio"),
    "java": ("java", None),
    "spring": ("java", "spring"),
    "spring-boot": ("java", "spring"),
    "kotlin": ("java", "kotlin"),
    "swift": ("any", "swift"),
    "swiftui": ("any", "swiftui"),
    "flutter": ("any", "flutter"),
    "dart": ("any", "dart"),
    "ruby": ("any", "ruby"),
    "rails": ("any", "rails"),
    "php": ("any", "php"),
    "laravel": ("any", "laravel"),
    "elixir": ("any", "elixir"),
    "c-sharp": ("any", "csharp"),
    "dotnet": ("any", "dotnet"),
}


def classify_categories(content: str) -> list[str]:
    """Classify content into skillgen categories using keyword matching.

    Returns a list of matching category slugs. Falls back to
    ["architecture", "code-style"] if no keywords match.
    """
    lower = content.lower()
    matched: list[str] = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in lower)
        if hits >= CATEGORY_THRESHOLD:
            matched.append(category)
    return matched if matched else ["architecture", "code-style"]


def detect_language_framework(folder_name: str) -> tuple[str | None, str | None]:
    """Detect language and framework from a folder name.

    Strips common suffixes like '-cursorrules-prompt-file' before lookup.
    Returns (language, framework) or (None, None) if not recognized.
    """
    clean = folder_name.lower()
    for suffix in ["-cursorrules-prompt-file", "-cursor-rules", "-cursorrules", "-rules"]:
        if clean.endswith(suffix):
            clean = clean[: -len(suffix)]
            break

    result = FOLDER_MAP.get(clean)
    if result:
        return result
    return None, None


def slugify(name: str) -> str:
    """Convert a name to a filename-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")
