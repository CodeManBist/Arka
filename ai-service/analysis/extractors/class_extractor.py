"""Extract class symbols using Tree-sitter queries."""

from __future__ import annotations

import logging
from typing import Any

from tree_sitter import Language, Query, QueryCursor, Tree

from analysis.queries.registry import get_class_query

logger = logging.getLogger(__name__)


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

        logger.debug(f"Extracting classes with query: {query_string}")
        logger.debug(f"Found {len(matches)} class matches")

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
            body = self._extract_body(range_node, source_bytes, name, language_name or "")
            
            logger.debug(f"Class '{name}' at line {start_line}: body length = {len(body)}")

            # Extract methods from the class body
            methods = self._extract_methods(range_node, source, language, language_name or "")
            
            logger.debug(f"  Extracted {len(methods)} methods from class '{name}'")

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

        logger.debug(f"Extracted {len(symbols)} classes")
        return symbols
    
    def _extract_body(self, node, source_bytes: bytes, class_name: str = "", language: str = "") -> str:
        """Extract the body of a class from its AST node."""
        # Define body node types for different languages
        body_node_types = ["block", "class_body", "statement_block"]
        
        # Look for a body node child
        for child in node.children:
            if child.type in body_node_types:
                start = child.start_byte
                end = child.end_byte
                body = source_bytes[start:end].decode("utf-8", errors="ignore")
                logger.debug(f"  Found {child.type} body for class '{class_name}' ({language}): {len(body)} chars")
                return body
        
        return ""
    
    def _extract_methods(self, class_node, source: str, language: Language, language_name: str) -> list[dict[str, Any]]:
        """Extract methods from a class body."""
        methods = []
        source_bytes = source.encode("utf-8")
        
        # Define method node types for different languages
        method_node_types = ["method_definition", "function_definition"]
        body_node_types = ["block", "class_body", "statement_block"]
        
        # Look for method nodes in the class body
        for child in class_node.children:
            if child.type in body_node_types:
                for method_node in child.children:
                    if method_node.type in method_node_types:
                        method = self._extract_method(method_node, source, language_name)
                        if method:
                            methods.append(method)
        
        return methods
    
    def _extract_method(self, method_node, source: str, language_name: str) -> dict[str, Any]:
        """Extract a single method from its AST node."""
        source_bytes = source.encode("utf-8")
        
        # Get method name
        name = ""
        for child in method_node.children:
            if child.type in ["property_identifier", "identifier"]:
                name = source_bytes[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
                break
        
        if not name:
            return {}
        
        # Get body
        body = ""
        body_node_types = ["block", "statement_block"]
        
        for child in method_node.children:
            if child.type in body_node_types:
                body = source_bytes[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
                break
        
        return {
            "name": name,
            "start_line": method_node.start_point[0] + 1,
            "end_line": method_node.end_point[0] + 1,
            "body": body,
        }
