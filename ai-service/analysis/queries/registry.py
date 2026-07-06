"""Registry for language-specific Tree-sitter queries and grammars."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

from tree_sitter import Language

import tree_sitter_javascript
import tree_sitter_python
import tree_sitter_typescript

if TYPE_CHECKING:
    from types import ModuleType

_GRAMMARS: dict[str, tuple[ModuleType, str]] = {
    "javascript": (tree_sitter_javascript, "language"),
    "typescript": (tree_sitter_typescript, "language_typescript"),
    "python": (tree_sitter_python, "language"),
}


def get_language(language: str) -> Language:
    """Return the Tree-sitter Language object for a supported language."""
    key = language.lower()
    if key not in _GRAMMARS:
        raise ValueError(f"Unsupported language: {language}")

    module, factory_name = _GRAMMARS[key]
    return Language(getattr(module, factory_name)())


def _load_query_module(language: str) -> ModuleType:
    """Dynamically load the query plugin for a language."""
    key = language.lower()
    if key not in _GRAMMARS:
        raise ValueError(f"Unsupported language: {language}")

    return importlib.import_module(f"analysis.queries.{key}")


def get_function_query(language: str) -> str:
    """Return the function extraction query for a language."""
    return _load_query_module(language).FUNCTION_QUERY


def get_class_query(language: str) -> str:
    """Return the class extraction query for a language."""
    return _load_query_module(language).CLASS_QUERY
