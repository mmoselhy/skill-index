"""Tests for category classification and language detection."""
from __future__ import annotations

from adapters.classifier import classify_categories, detect_language_framework, slugify


class TestClassifyCategories:
    def test_testing_keywords(self) -> None:
        content = "Use pytest fixtures for setup. Write assertions with assert."
        cats = classify_categories(content)
        assert "testing" in cats

    def test_error_handling_keywords(self) -> None:
        content = "Catch exceptions with try/except. Raise ValueError for invalid input."
        cats = classify_categories(content)
        assert "error-handling" in cats

    def test_multiple_categories(self) -> None:
        content = (
            "Use snake_case naming conventions. "
            "Format code with ruff linter. "
            "Write tests with pytest."
        )
        cats = classify_categories(content)
        assert "naming-conventions" in cats
        assert "code-style" in cats
        assert "testing" in cats

    def test_fallback_when_no_match(self) -> None:
        content = "Hello world."
        cats = classify_categories(content)
        assert cats == ["architecture", "code-style"]

    def test_architecture_keywords(self) -> None:
        content = "Organize project structure with modules. Use dependency injection pattern."
        cats = classify_categories(content)
        assert "architecture" in cats


class TestDetectLanguageFramework:
    def test_nextjs(self) -> None:
        lang, fw = detect_language_framework("nextjs-cursorrules-prompt-file")
        assert lang == "typescript"
        assert fw == "next"

    def test_python_plain(self) -> None:
        lang, fw = detect_language_framework("python-cursorrules-prompt-file")
        assert lang == "python"
        assert fw is None

    def test_fastapi(self) -> None:
        lang, fw = detect_language_framework("fastapi-cursorrules-prompt-file")
        assert lang == "python"
        assert fw == "fastapi"

    def test_unknown_returns_none(self) -> None:
        lang, fw = detect_language_framework("unknown-thing")
        assert lang is None
        assert fw is None


class TestSlugify:
    def test_basic(self) -> None:
        assert slugify("Pytest Patterns") == "pytest-patterns"

    def test_special_chars(self) -> None:
        assert slugify("Next.js + React!") == "next-js-react"

    def test_leading_trailing(self) -> None:
        assert slugify("  --hello--  ") == "hello"
