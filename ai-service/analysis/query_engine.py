from __future__ import annotations

from tree_sitter import Language, Query, QueryCursor, Tree

class QueryEngine:
    """Executes Tree-sitter queries and returns captures."""

    def execute(
        self,
        language: Language,
        tree: Tree,
        query_string: str,
    ):
        query = Query(language, query_string)
        cursor = QueryCursor(query)

        return cursor.captures(tree.root_node)
    
    def get_import_query(language: str) -> str:
        """Return the import extraction query for a language."""
        return _load_query_module(language).IMPORT_QUERY