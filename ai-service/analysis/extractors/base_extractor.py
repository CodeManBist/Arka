"""Base extractor using the official Tree-sitter Query API."""

from __future__ import annotations

from typing import Any

from tree_sitter import Language, Query, QueryCursor, Tree


class BaseQueryExtractor:
    """Execute Tree-sitter queries and map captures to symbol dictionaries."""

    NAME_CAPTURE = ""
    DEFINITION_CAPTURE = ""

    def extract(
        self,
        language: Language,
        tree: Tree,
        source: str,
        query_string: str,
    ) -> list[dict[str, Any]]:
        """Run a query against a syntax tree and return extracted symbols."""
        query = Query(language, query_string)
        query_cursor = QueryCursor(query)
        matches = query_cursor.matches(tree.root_node)

        symbols: list[dict[str, Any]] = []
        seen: set[tuple[str, int]] = set()
        source_bytes = source.encode("utf-8")

        for _pattern_index, captures in matches:
            name_nodes = captures.get(self.NAME_CAPTURE, [])
            if not name_nodes:
                continue

            name_node = name_nodes[0]
            definition_nodes = captures.get(self.DEFINITION_CAPTURE, [])
            range_node = definition_nodes[0] if definition_nodes else name_node

            name = source_bytes[name_node.start_byte : name_node.end_byte].decode(
                "utf-8"
            )
            start_line = range_node.start_point[0] + 1
            end_line = range_node.end_point[0] + 1

            key = (name, start_line)
            if key in seen:
                continue
            seen.add(key)

            symbols.append(
                {
                    "name": name,
                    "start_line": start_line,
                    "end_line": end_line,
                }
            )

        return symbols
