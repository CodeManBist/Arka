"""Extract class symbols using Tree-sitter queries."""

from __future__ import annotations

from typing import Any

from tree_sitter import Language, Query, QueryCursor, Tree

from analysis.queries.registry import get_class_query


class ClassExtractor:
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
            List of class symbols with name, line range, body, and methods.
        """
        if query_string is None:
            if language_name is None:
                raise ValueError(
                    "Either language_name or query_string must be provided."
                )
            query_string = get_class_query(language_name)

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

            # Extract body
            body = self._extract_body(range_node, source_bytes)

            # Extract methods from the class body
            methods = self._extract_methods(range_node, source, language)

            key = (name, start_line)
            if key in seen:
                continue
            seen.add(key)

            symbols.append(
                {
                    "name": name,
                    "start_line": start_line,
                    "end_line": end_line,
                    "body": body,
                    "methods": methods,
                }
            )

        return symbols
    
    def _extract_body(self, node, source_bytes: bytes) -> str:
        """Extract the body of a class from its AST node."""
        # Look for a block/class_body child
        for child in node.children:
            if child.type in ["block", "class_body", "statement_block"]:
                start = child.start_byte
                end = child.end_byte
                return source_bytes[start:end].decode("utf-8", errors="ignore")
        
        return ""
    
    def _extract_methods(self, class_node, source: str, language: Language) -> list[dict[str, Any]]:
        """Extract methods from a class body."""
        methods = []
        
        # Look for method_definition nodes in the class body
        for child in class_node.children:
            if child.type == "class_body":
                for method_node in child.children:
                    if method_node.type == "method_definition":
                        method = self._extract_method(method_node, source)
                        if method:
                            methods.append(method)
        
        return methods
    
    def _extract_method(self, method_node, source: str) -> dict[str, Any]:
        """Extract a single method from its AST node."""
        source_bytes = source.encode("utf-8")
        
        # Get method name
        name = ""
        for child in method_node.children:
            if child.type == "property_identifier":
                name = source_bytes[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
                break
        
        if not name:
            return {}
        
        # Get body
        body = ""
        for child in method_node.children:
            if child.type in ["block", "statement_block"]:
                body = source_bytes[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
                break
        
        return {
            "name": name,
            "start_line": method_node.start_point[0] + 1,
            "end_line": method_node.end_point[0] + 1,
            "body": body,
        }
