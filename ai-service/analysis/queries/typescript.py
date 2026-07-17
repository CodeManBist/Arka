"""Tree-sitter queries for TypeScript symbol extraction."""

FUNCTION_QUERY = """
(function_declaration
  name: (identifier) @function.name) @function.def

(method_definition
  name: (property_identifier) @function.name) @function.def

(arrow_function) @function.def

(function_expression
  name: (identifier) @function.name) @function.def
"""

CLASS_QUERY = """
(class_declaration
  name: (identifier) @class.name) @class.def
"""

IMPORT_QUERY = """
(import_statement
  source: (string) @import.path) @import.def

(import_clause
  name: (identifier) @import.named) @import.def

(from_clause
  name: (identifier) @import.module) @import.def

(namespace_import
  name: (identifier) @import.named) @import.def
"""

EXPORT_QUERY = """
(export_statement
  declaration: (function_declaration
    name: (identifier) @export.name) @export.def)

(export_statement
  declaration: (class_declaration
    name: (identifier) @export.name) @export.def)

(named_export
  name: (identifier) @export.name) @export.def

(export_assignment
  name: (identifier) @export.name) @export.def
"""

VARIABLE_QUERY = """
(variable_declaration
  declarator: (variable_declarator
    name: (identifier) @variable.name) @variable.def)

(assignment_expression
  left: (identifier) @variable.name) @variable.def

(lexical_declaration
  declarator: (variable_declarator
    name: (identifier) @variable.name) @variable.def)
"""
