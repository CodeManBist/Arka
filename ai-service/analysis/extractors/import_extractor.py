"""Extract import symbols using Tree-sitter queries."""

from __future__ import annotations

from tree_sitter import Language, Tree

from analysis.extractors.base_extractor import BaseQueryExtractor
from analysis.queries.registry import get_import_query


class ImportExtractor(BaseQueryExtractor):
    """Extract import symbols from a syntax tree."""

    NAME_CAPTURE = "import.module"
    DEFINITION_CAPTURE = "import.def"

    def extract(
        self,
        language: Language,
        tree: Tree,
        source: str,
        language_name: str | None = None,
        query_string: str |None = None,
    ) -> list[dict]:

        if query_string is None:
            if language_name is None:
                raise ValueError(
                    "Either language_name or query_string must be provided."
                )

            query_string = get_import_query(language_name)

        return super().extract(
            language=language,
            tree=tree,
            source=source,
            query_string=query_string,
        )