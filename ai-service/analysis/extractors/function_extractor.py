"""Extract function symbols using Tree-sitter queries."""

from __future__ import annotations

import logging
from typing import Any

from tree_sitter import Language, Query, QueryCursor, Tree

from analysis.queries.registry import get_function_query

logger = logging.getLogger(__name__)


class FunctionExtractor:
    """Extract function definitions from a parsed syntax tree."""

    NAME_CAPTURE = "function.name"
    DEFINITION_CAPTURE = "function.def"

    def extract(
        self,
        language: Language,
        tree: Tree,
        source: str,
        language_name: str | None = None,
        query_string: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Extract functions from a syntax tree.

        Args:
            language: Tree-sitter Language object used to compile the query.
            tree: Parsed syntax tree.
            source: Original source code for resolving symbol text.
            language_name: Language identifier used to load the query plugin.
            query_string: Optional pre-loaded query string.

        Returns:
            List of function symbols with name, line range, and body.
        """
        if query_string is None:
            if language_name is None:
                raise ValueError(
                    "Either language_name or query_string must be provided."
                )
            query_string = get_function_query(language_name)

        query = Query(language, query_string)
        query_cursor = QueryCursor(query)
        matches = query_cursor.matches(tree.root_node)

        symbols: list[dict[str, Any]] = []
        seen: set[tuple[str, int]] = set()
        source_bytes = source.encode("utf-8")

        logger.debug(f"Extracting functions with query: {query_string}")
        logger.debug(f"Found {len(matches)} function matches")

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

            # Extract body by finding the block/statement_block child
            # Pass language_name to handle different AST structures
            body = self._extract_body(range_node, source_bytes, name, language_name or "")
            
            logger.debug(f"Function '{name}' at line {start_line}: body length = {len(body)}")
            if len(body) < 50:
                logger.debug(f"  Body content: '{body}'")

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
                }
            )

        logger.debug(f"Extracted {len(symbols)} functions")
        return symbols
    
    def _extract_body(self, node, source_bytes: bytes, func_name: str = "", language: str = "") -> str:
        """Extract the body of a function from its AST node.
        
        Different languages use different node types for function bodies:
        - Python: 'block'
        - JavaScript/TypeScript: 'statement_block'
        """
        # Define body node types for different languages
        body_node_types = ["block", "statement_block"]
        
        # For JavaScript/TypeScript, also check for arrow function bodies
        if language in ["javascript", "typescript"]:
            body_node_types.extend(["arrow_function", "function_expression"])
        
        # Look for a body node child
        for child in node.children:
            if child.type in body_node_types:
                # Extract the text between the braces
                start = child.start_byte
                end = child.end_byte
                body = source_bytes[start:end].decode("utf-8", errors="ignore")
                logger.debug(f"  Found {child.type} body for '{func_name}' ({language}): {len(body)} chars")
                return body
        
        # If no body found, try to find the body by looking at siblings
        # after the name node
        for i, child in enumerate(node.children):
            if child.type == "identifier":
                # The next sibling after identifier should be parameters, then body
                if i + 2 < len(node.children):
                    body_node = node.children[i + 2]
                    if body_node.type in body_node_types:
                        body = source_bytes[body_node.start_byte:body_node.end_byte].decode("utf-8", errors="ignore")
                        logger.debug(f"  Found body via sibling for '{func_name}': {len(body)} chars")
                        return body
        
        # For arrow functions in JS/TS, the body might be the last child
        if language in ["javascript", "typescript"]:
            for child in node.children:
                if child.type in ["arrow_function"]:
                    # Arrow function body is usually the last child
                    if len(child.children) > 0:
                        body_node = child.children[-1]
                        if body_node.type in body_node_types:
                            body = source_bytes[body_node.start_byte:body_node.end_byte].decode("utf-8", errors="ignore")
                            logger.debug(f"  Found arrow function body for '{func_name}': {len(body)} chars")
                            return body
        
        # Debug: log all children
        logger.debug(f"  No body found for '{func_name}' (language: {language}). Node type: {node.type}, children: {[c.type for c in node.children]}")
        
        return ""
