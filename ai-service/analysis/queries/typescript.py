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

IMPORT_QUERY = """
(import_statement
  source: (string) @import.module) @import.def
"""

EXPORT_QUERY = """
(export_statement
  declaration: (function_declaration
    name: (identifier) @export.name)) @export.def

(export_statement
  declaration: (class_declaration
    name: (type_identifier) @export.name)) @export.def

(export_statement
  declaration: (lexical_declaration
    (variable_declarator
      name: (identifier) @export.name))) @export.def

(export_statement
  declaration: (interface_declaration
    name: (type_identifier) @export.name)) @export.def
"""

VARIABLE_QUERY = """
(variable_declaration
  (variable_declarator
    name: (identifier) @variable.name) @variable.def)
"""