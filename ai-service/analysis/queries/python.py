"""Tree-sitter queries for Python symbol extraction."""

FUNCTION_QUERY = """
(function_definition
  name: (identifier) @function.name
  body: (block) @function.body) @function.def
"""

CLASS_QUERY = """
(class_definition
  name: (identifier) @class.name
  body: (block) @class.body) @class.def
"""

IMPORT_QUERY = """
(import_statement
  name: (dotted_name) @import.module) @import.def

(import_from_statement
  module_name: (dotted_name) @import.module) @import.def

(import_from_statement
  name: (import_list
    name: (identifier) @import.named)) @import.def
"""

EXPORT_QUERY = """
(function_definition
  name: (identifier) @export.name) @export.def

(class_definition
  name: (identifier) @export.name) @export.def
"""

VARIABLE_QUERY = """
(assignment
  left: (identifier) @variable.name) @variable.def

(assignment
  left: (attribute) @variable.name) @variable.def

(variable_declaration
  name: (identifier) @variable.name) @variable.def
"""

# Queries for call extraction
CALL_QUERY = """
(call
  function: (identifier) @call.function) @call.expr

(call
  function: (attribute) @call.function) @call.expr

(call
  function: (member_expression
    property: (identifier) @call.function) @call.expr)
"""
