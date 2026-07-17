"""Tree-sitter queries for Python symbol extraction."""

FUNCTION_QUERY = """
(function_definition
  name: (identifier) @function.name) @function.def
"""

CLASS_QUERY = """
(class_definition
  name: (identifier) @class.name) @class.def
"""

IMPORT_QUERY = """
(import_statement
  name: (dotted_name) @import.module) @import.def

(import_from_statement
  module_name: (dotted_name) @import.module) @import.def
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
"""
