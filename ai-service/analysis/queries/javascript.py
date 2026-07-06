"""Tree-sitter queries for JavaScript symbol extraction."""

FUNCTION_QUERY = """
(function_declaration
  name: (identifier) @function.name) @function.def

(method_definition
  name: (property_identifier) @function.name) @function.def

(pair
  key: (property_identifier) @function.name
  value: (arrow_function)) @function.def

(variable_declarator
  name: (identifier) @function.name
  value: (arrow_function)) @function.def
"""

CLASS_QUERY = """
(class_declaration
  name: (identifier) @class.name) @class.def
"""
