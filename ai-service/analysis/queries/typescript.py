"""Tree-sitter queries for TypeScript symbol extraction."""

FUNCTION_QUERY = """
(function_declaration
  name: (identifier) @function.name) @function.def

(method_definition
  name: (property_identifier) @function.name) @function.def

(method_signature
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
  name: (type_identifier) @class.name) @class.def

(interface_declaration
  name: (type_identifier) @class.name) @class.def
"""
