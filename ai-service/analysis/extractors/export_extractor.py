"""Extract export symbols using Tree-sitter queries."""

from __future__ import annotations

from tree_sitter import Language, Tree

from analysis.extractors.base_extractor import BaseQueryExtractor
from analysis.queries.registry import get_export_query


class ExportExtractor(BaseQueryExtractor):
    """Extract export symbols from a syntax tree."""

    NAME_CAPTURE = "export.name"
    DEFINITION_CAPTURE = "export.def"

    def extract(
        self,
        language: Language,
        tree: Tree,
        source: str,
        language_name: str | None = None,
        query_string: str | None = None,
    ) -> list[dict]:

        if query_string is None:

            if language_name is None:
                raise ValueError(
                    "Either language_name or query_string must be provided."
                )

            query_string = get_export_query(language_name)

        return super().extract(
            language=language,
            tree=tree,
            source=source,
            query_string=query_string,
        )