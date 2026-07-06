"""Extract class symbols using Tree-sitter queries."""

from __future__ import annotations

from typing import Any

from tree_sitter import Language, Tree

from analysis.extractors.base_extractor import BaseQueryExtractor
from analysis.queries.registry import get_class_query


class ClassExtractor(BaseQueryExtractor):
    """Extract class definitions from a parsed syntax tree."""

    NAME_CAPTURE = "class.name"
    DEFINITION_CAPTURE = "class.def"

    def extract(
        self,
        language: Language,
        tree: Tree,
        source: str,
        language_name: str | None = None,
        query_string: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Extract classes from a syntax tree.

        Args:
            language: Tree-sitter Language object used to compile the query.
            tree: Parsed syntax tree.
            source: Original source code for resolving symbol text.
            language_name: Language identifier used to load the query plugin.
            query_string: Optional pre-loaded query string.

        Returns:
            List of class symbols with name and line range.
        """
        if query_string is None:
            if language_name is None:
                raise ValueError(
                    "Either language_name or query_string must be provided."
                )
            query_string = get_class_query(language_name)

        return super().extract(language, tree, source, query_string)
