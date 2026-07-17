# Code Analysis Skills

## 🎯 Overview

Skills for analyzing source code using AST-based techniques with Tree-sitter.

## 📋 Prerequisites

- Python 3.11+
- Tree-sitter CLI and Python bindings
- Understanding of AST (Abstract Syntax Tree) concepts
- Familiarity with Python, JavaScript, TypeScript syntax

## 🏗️ Core Concepts

### AST (Abstract Syntax Tree)
- Tree representation of source code structure
- Each node represents a syntactic construct (function, class, variable, etc.)
- Tree-sitter provides efficient parsing and querying

### Tree-sitter Architecture
```
Source Code
    ↓
Tree-sitter Parser (language-specific)
    ↓
AST (Abstract Syntax Tree)
    ↓
Tree-sitter Query
    ↓
Extracted Symbols
```

## 🛠️ Required Tools

```bash
# Install Tree-sitter CLI
npm install -g tree-sitter-cli

# Install Python bindings
pip install tree-sitter

# Install language parsers
tree-sitter install python javascript typescript
```

## 📚 Common Patterns

### 1. Parsing Source Code

```python
from tree_sitter import Language, Parser

# Build language
Language.build_library(
    '/path/to/build/my-languages.so',
    ['tree-sitter-python', 'tree-sitter-javascript']
)

# Create parser
PYTHON_LANGUAGE = Language('/path/to/build/my-languages.so', 'python')
parser = Parser()
parser.set_language(PYTHON_LANGUAGE)

# Parse source code
tree = parser.parse(source_code)
```

### 2. Tree-sitter Queries

```python
from tree_sitter import Query, QueryCursor

# Define query for function extraction
function_query = """
(function_definition
  name: (identifier) @function.name
  body: (block) @function.def
)
"""

# Execute query
query = Query(PYTHON_LANGUAGE, function_query)
query_cursor = QueryCursor(query)
matches = query_cursor.matches(tree.root_node)

# Process matches
for pattern_index, captures in matches:
    name_node = captures.get('function.name', [None])[0]
    if name_node:
        function_name = source_code[name_node.start_byte:name_node.end_byte]
        print(f"Found function: {function_name}")
```

### 3. Query Files

Create query files in `ai-service/analysis/queries/`:

**python.py:**
```python
FUNCTION_QUERY = """
(function_definition
  name: (identifier) @function.name
  body: (block) @function.def
)
"""

CLASS_QUERY = """
(class_definition
  name: (identifier) @class.name
  body: (block) @class.def
)
"""

IMPORT_QUERY = """
(import_statement
  name: (dotted_name) @import.name
)
"""
```

## 🎯 Best Practices

### 1. Query Optimization
- Use specific capture names for easy extraction
- Limit query scope to relevant nodes
- Avoid overly broad patterns

### 2. Error Handling
```python
try:
    tree = parser.parse(source_code)
except Exception as e:
    print(f"Parse error: {e}")
    return []
```

### 3. Language Detection
```python
def detect_language(file_path: str) -> str:
    """Detect language from file extension."""
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
    }
    ext = Path(file_path).suffix.lower()
    return extension_map.get(ext, 'unknown')
```

## 🔍 Symbol Extraction

### Function Extraction
```python
from analysis.extractors.function_extractor import FunctionExtractor

extractor = FunctionExtractor()
functions = extractor.extract(
    language=PYTHON_LANGUAGE,
    tree=tree,
    source=source_code,
    language_name='python'
)
```

### Class Extraction
```python
from analysis.extractors.class_extractor import ClassExtractor

extractor = ClassExtractor()
classes = extractor.extract(
    language=PYTHON_LANGUAGE,
    tree=tree,
    source=source_code,
    language_name='python'
)
```

### Import Extraction
```python
from analysis.extractors.import_extractor import ImportExtractor

extractor = ImportExtractor()
imports = extractor.extract(
    language=PYTHON_LANGUAGE,
    tree=tree,
    source=source_code,
    language_name='python'
)
```

## 🧪 Testing

### Test Query Extraction
```python
def test_function_extraction():
    source = """
def hello(name):
    return f"Hello, {name}!"
    """
    parser = ParserFactory.get_parser('python')
    tree = parser.parse(source)
    
    extractor = FunctionExtractor()
    functions = extractor.extract(
        language=parser.language,
        tree=tree,
        source=source,
        language_name='python'
    )
    
    assert len(functions) == 1
    assert functions[0]['name'] == 'hello'
```

## 📖 Resources

- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [Tree-sitter Python](https://github.com/tree-sitter/tree-sitter-python)
- [Tree-sitter JavaScript](https://github.com/tree-sitter/tree-sitter-javascript)
- [Tree-sitter TypeScript](https://github.com/tree-sitter/tree-sitter-typescript)

## 🚨 Troubleshooting

### Parser Not Found
```bash
# Install the parser
tree-sitter install python

# Rebuild the language library
Language.build_library('/path/to/build/my-languages.so', ['tree-sitter-python'])
```

### Query Syntax Error
- Check query syntax with `tree-sitter query` CLI
- Use [Tree-sitter Playground](https://tree-sitter.github.io/tree-sitter/playground) for testing

### Memory Issues
- Limit file size for parsing
- Use streaming for large files
- Consider incremental parsing