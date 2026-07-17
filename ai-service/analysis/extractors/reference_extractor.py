"""Extract identifier references using Tree-sitter queries."""

from __future__ import annotations

from tree_sitter import Language, Tree

from analysis.extractors.base_extractor import BaseQueryExtractor
from analysis.queries.registry import get_reference_query


class ReferenceExtractor(BaseQueryExtractor):
    """Extract identifier references."""

    NAME_CAPTURE = "reference.name"
    DEFINITION_CAPTURE = "reference.def"

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

            query_string = get_reference_query(language_name)

        return super().extract(
            language=language,
            tree=tree,
            source=source,
            query_string=query_string,
        )