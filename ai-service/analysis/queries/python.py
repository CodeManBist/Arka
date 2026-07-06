"""Tree-sitter queries for Python symbol extraction."""

FUNCTION_QUERY = """
(function_definition
  name: (identifier) @function.name) @function.def
"""

CLASS_QUERY = """
(class_definition
  name: (identifier) @class.name) @class.def
"""
