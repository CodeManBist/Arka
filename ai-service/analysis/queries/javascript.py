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

IMPORT_QUERY = """
(import_statement
  source: (string) @import.module) @import.def

(call_expression
  function: (identifier) @_require
  (#eq? @_require "require")
  arguments: (arguments
    (string) @import.module)) @import.def
"""

EXPORT_QUERY = """
(export_statement
  declaration: (function_declaration
    name: (identifier) @export.name)) @export.def

(export_statement
  declaration: (class_declaration
    name: (identifier) @export.name)) @export.def

(export_statement
  declaration: (lexical_declaration
    (variable_declarator
      name: (identifier) @export.name))) @export.def

(assignment_expression
  left: (member_expression
    object: (identifier) @_module
    property: (property_identifier) @_exports)
  (#eq? @_module "module")
  (#eq? @_exports "exports")) @export.def

(assignment_expression
  left: (member_expression
    object: (identifier) @_exports
    property: (property_identifier) @export.name)
  (#eq? @_exports "exports")) @export.def
"""

VARIABLE_QUERY = """
(variable_declarator
  name: (identifier) @variable.name) @variable.def
"""