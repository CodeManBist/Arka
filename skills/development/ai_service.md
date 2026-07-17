# AI Service Development Skills

## 🎯 Overview

Skills for developing the Blast Radius AI service using FastAPI and Python.

## 📋 Prerequisites

- Python 3.11+
- FastAPI framework
- Tree-sitter Python bindings
- Understanding of AST and graph theory
- Async/await in Python

## 🏗️ Core Concepts

### Project Structure

```
ai-service/
├── analysis/
│   ├── scanner.py              # Repository scanning
│   ├── parser_factory.py       # Parser creation
│   ├── repository_parser.py    # Repository parsing
│   ├── diff_parser.py          # Git diff parsing
│   └── parsers/               # Language-specific parsers
│       ├── python_parser.py
│       ├── javascript_parser.py
│       └── typescript_parser.py
├── graph/
│   ├── node.py                # Node representation
│   ├── edge.py                # Edge representation
│   ├── graph.py               # Graph data structure
│   ├── call_graph_builder.py  # Call graph construction
│   ├── import_graph_builder.py # Import graph construction
│   └── impact_traversal.py    # Impact analysis engine
├── api/
│   ├── parser.py              # Parser API endpoints
│   ├── repository.py          # Repository API endpoints
│   └── blast_radius.py        # Blast Radius API endpoints
├── models/
│   ├── symbol.py              # Symbol representation
│   ├── symbol_table.py        # Symbol table
│   └── ...
├── app.py                    # FastAPI application
├── requirements.txt
└── Dockerfile
```

### Service Architecture

```
FastAPI Application
    ↓
API Routers
    ↓
Service Layer
    ↓
Analysis Modules (Scanner, Parser, Extractor)
    ↓
Graph Modules (Builder, Traversal)
    ↓
Tree-sitter Parsers
    ↓
AST Generation
```

## 🛠️ Required Tools

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Tree-sitter CLI
npm install -g tree-sitter-cli

# Install language parsers
tree-sitter install python javascript typescript

# Run the service
uvicorn app:app --reload
```

## 📚 Common Patterns

### 1. FastAPI Application Setup

```python
# app.py
from fastapi import FastAPI
from api.parser import router as parser_router
from api.repository import router as repository_router
from api.blast_radius import router as blast_radius_router

app = FastAPI(
    title="Blast Radius AI Service",
    description="AI-powered impact analysis engine",
    version="1.0.0"
)

app.include_router(parser_router)
app.include_router(repository_router)
app.include_router(blast_radius_router)

@app.get("/")
def health():
    return {
        "status": "running",
        "service": "Blast Radius AI Service",
        "version": "1.0.0"
    }
```

### 2. API Router

```python
# api/blast_radius.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

router = APIRouter(prefix="/api/blast-radius", tags=["blast-radius"])

class BlastRadiusRequest(BaseModel):
    repository_path: str
    symbol_name: str
    symbol_type: str = "function"
    file_path: str | None = None
    max_depth: int = 3

@router.post("/analyze")
async def analyze_impact(request: BlastRadiusRequest) -> Dict[str, Any]:
    try:
        # Parse repository
        parser = RepositoryParser()
        repository_data = parser.parse_repository(request.repository_path)
        
        # Build graphs
        call_graph = CallGraphBuilder().build_from_repository(repository_data["repository"])
        import_graph = ImportGraphBuilder().build_from_repository(repository_data["repository"])
        
        # Analyze impact
        engine = ImpactTraversalEngine(call_graph, import_graph)
        result = engine.analyze_impact(
            symbol_name=request.symbol_name,
            symbol_type=request.symbol_type,
            file_path=request.file_path,
            max_depth=request.max_depth
        )
        
        return {"success": True, "result": result.to_dict()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Parser Factory

```python
# analysis/parser_factory.py
from tree_sitter import Language, Parser
from pathlib import Path

class ParserFactory:
    """Factory for creating Tree-sitter parsers."""
    
    _parsers: Dict[str, Parser] = {}
    _languages: Dict[str, Language] = {}
    
    @classmethod
    def get_parser(cls, language_name: str) -> Parser:
        """Get a parser for the specified language."""
        if language_name not in cls._parsers:
            cls._load_language(language_name)
        
        return cls._parsers[language_name]
    
    @classmethod
    def _load_language(cls, language_name: str) -> None:
        """Load a Tree-sitter language."""
        language_map = {
            'python': 'tree-sitter-python',
            'javascript': 'tree-sitter-javascript',
            'typescript': 'tree-sitter-typescript',
        }
        
        if language_name not in language_map:
            raise ValueError(f"Unsupported language: {language_name}")
        
        # Build language (simplified - actual implementation uses Language.build_library)
        language_path = Path(__file__).parent / "build" / "my-languages.so"
        Language.build_library(
            str(language_path),
            [language_map[language_name]]
        )
        
        language = Language(str(language_path), language_name)
        parser = Parser()
        parser.set_language(language)
        
        cls._languages[language_name] = language
        cls._parsers[language_name] = parser
```

### 4. Repository Parser

```python
# analysis/repository_parser.py
from analysis.extractors import (
    FunctionExtractor,
    ClassExtractor,
    ImportExtractor,
    ExportExtractor,
    VariableExtractor
)
from analysis.builders.symbol_table_builder import SymbolTableBuilder

class RepositoryParser:
    """Parse repositories and build symbol index."""
    
    def __init__(self):
        self.scanner = RepositoryScanner()
        self.function_extractor = FunctionExtractor()
        self.class_extractor = ClassExtractor()
        self.import_extractor = ImportExtractor()
        self.export_extractor = ExportExtractor()
        self.variable_extractor = VariableExtractor()
        self.symbol_table_builder = SymbolTableBuilder()
    
    def parse_repository(self, repository_path: str) -> Dict[str, Any]:
        """Parse every supported source file in a repository."""
        files = self.scanner.scan(repository_path)
        
        repository = {
            "repository": Path(repository_path).name,
            "total_files": len(files),
            "files": [],
        }
        
        for file in files:
            parser = ParserFactory.get_parser(file["language"])
            source = Path(file["path"]).read_text(encoding="utf-8", errors="ignore")
            tree = parser.parse(source)
            
            # Extract symbols
            functions = self.function_extractor.extract(
                language=parser.language,
                tree=tree,
                source=source,
                language_name=file["language"]
            )
            
            classes = self.class_extractor.extract(
                language=parser.language,
                tree=tree,
                source=source,
                language_name=file["language"]
            )
            
            imports = self.import_extractor.extract(
                language=parser.language,
                tree=tree,
                source=source,
                language_name=file["language"]
            )
            
            # ... more extraction
            
            repository["files"].append({
                "path": file["path"],
                "language": file["language"],
                "functions": functions,
                "classes": classes,
                "imports": imports,
                # ... more
            })
        
        symbol_table = self.symbol_table_builder.build(repository)
        return {"repository": repository, "symbol_table": symbol_table}
```

### 5. Call Graph Builder

```python
# graph/call_graph_builder.py
from graph.graph import Graph
from graph.node import Node, NodeType
from graph.edge import Edge, EdgeType

class CallGraphBuilder:
    """Build call graphs from parsed repository data."""
    
    def build_from_repository(self, repository_data: Dict[str, Any]) -> Graph:
        """Build a call graph from repository parsing results."""
        graph = Graph()
        
        # Create nodes for all functions, classes, methods
        self._create_symbol_nodes(repository_data, graph)
        
        # Build import mapping
        self._build_import_mapping(repository_data)
        
        # Create call edges
        self._create_call_edges(repository_data, graph)
        
        # Create inheritance edges
        self._create_inheritance_edges(repository_data, graph)
        
        # Compute metrics
        self._compute_graph_metrics(graph)
        
        return graph
```

### 6. Impact Traversal Engine

```python
# graph/impact_traversal.py
from graph.graph import Graph
from graph.node import Node, RiskLevel
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

@dataclass
class ImpactResult:
    changed_symbol: str
    changed_symbol_type: str
    changed_file: str
    direct_callers: int = 0
    transitive_callers: int = 0
    affected_files: Set[str] = field(default_factory=set)
    affected_symbols: Set[str] = field(default_factory=set)
    risk_level: RiskLevel = RiskLevel.LOW
    risk_score: float = 0.0
    confidence_score: float = 1.0
    suggested_fix: str = ""
    ai_summary: str = ""

class ImpactTraversalEngine:
    """Engine for traversing graphs to determine impact of code changes."""
    
    def analyze_impact(
        self,
        symbol_name: str,
        symbol_type: str = "function",
        file_path: str | None = None,
        max_depth: int = 3
    ) -> ImpactResult:
        """Analyze the impact of changing a symbol."""
        # Find target nodes
        target_nodes = self._find_target_nodes(symbol_name, symbol_type, file_path)
        
        if not target_nodes:
            return ImpactResult(
                changed_symbol=symbol_name,
                changed_symbol_type=symbol_type,
                changed_file=file_path or "unknown",
                risk_level=RiskLevel.LOW,
                confidence_score=0.0,
                unresolved_symbols={symbol_name}
            )
        
        # Analyze impact
        result = ImpactResult(
            changed_symbol=symbol_name,
            changed_symbol_type=symbol_type,
            changed_file=file_path or target_nodes[0].file_path
        )
        
        # Find direct and transitive callers
        for target_node in target_nodes:
            direct_callers = self.call_graph.get_callers(target_node.id)
            result.direct_callers += len(direct_callers)
            
            transitive = self._find_transitive_callers(target_node.id, max_depth)
            result.transitive_callers += len(transitive["nodes"])
        
        # Calculate scores
        result.risk_level, result.risk_score = self._calculate_risk_score(result)
        result.confidence_score = self._calculate_confidence_score(result)
        result.ai_summary = self._generate_ai_summary(result)
        result.suggested_fix = self._generate_suggested_fix(result)
        
        return result
```

## 🎯 Best Practices

### 1. Error Handling

```python
try:
    tree = parser.parse(source_code)
except Exception as e:
    logger.error(f"Parse error in {file_path}: {e}")
    return []
```

### 2. Performance Optimization

```python
# Cache parsers
_parsers: Dict[str, Parser] = {}

# Cache graphs
_graph_cache: Dict[str, Graph] = {}

# Limit traversal depth
MAX_DEPTH = 3
```

### 3. Memory Management

```python
# Use generators for large graphs
def traverse_large_graph(graph: Graph, start_node_id: str):
    """Generator for traversing large graphs."""
    visited = set()
    queue = deque([start_node_id])
    
    while queue:
        node_id = queue.popleft()
        if node_id in visited:
            continue
        visited.add(node_id)
        yield node_id
        
        for successor in graph.get_successors(node_id):
            if successor.id not in visited:
                queue.append(successor.id)
```

### 4. Type Hints

```python
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

# Use proper type hints for better IDE support
@dataclass
class Node:
    id: str
    name: str
    node_type: NodeType
    file_path: str
    language: str
    start_line: int = 0
    end_line: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### 5. Logging

```python
import logging

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use logging throughout
def parse_repository(self, repository_path: str) -> Dict[str, Any]:
    logger.info(f"Parsing repository: {repository_path}")
    try:
        # ... implementation
        logger.info(f"Successfully parsed {len(files)} files")
        return repository
    except Exception as e:
        logger.error(f"Failed to parse repository: {e}")
        raise
```

## 🧪 Testing

### Test Parser Factory

```python
# tests/test_parser_factory.py
import pytest
from analysis.parser_factory import ParserFactory

def test_get_parser():
    """Test getting parsers for different languages."""
    parser = ParserFactory.get_parser('python')
    assert parser is not None
    
    parser = ParserFactory.get_parser('javascript')
    assert parser is not None
    
    with pytest.raises(ValueError):
        ParserFactory.get_parser('unknown')
```

### Test Repository Parser

```python
# tests/test_repository_parser.py
from analysis.repository_parser import RepositoryParser

def test_parse_repository(tmp_path):
    """Test parsing a test repository."""
    # Create test files
    python_file = tmp_path / "test.py"
    python_file.write_text("def hello():\n    return 'world'\n")
    
    parser = RepositoryParser()
    result = parser.parse_repository(str(tmp_path))
    
    assert result["repository"]["total_files"] == 1
    assert len(result["repository"]["files"]) == 1
    assert len(result["repository"]["files"][0]["functions"]) == 1
```

### Test Call Graph Builder

```python
# tests/test_call_graph_builder.py
from graph.call_graph_builder import CallGraphBuilder

def test_build_call_graph():
    """Test building a call graph."""
    repository_data = {
        "files": [
            {
                "path": "test.py",
                "language": "python",
                "functions": [
                    {"name": "main", "start_line": 1, "end_line": 10},
                    {"name": "helper", "start_line": 12, "end_line": 20}
                ]
            }
        ]
    }
    
    builder = CallGraphBuilder()
    graph = builder.build_from_repository(repository_data)
    
    assert len(graph.nodes) == 2
    assert "test.py:function:main" in graph.nodes
    assert "test.py:function:helper" in graph.nodes
```

### Test Impact Traversal

```python
# tests/test_impact_traversal.py
from graph.impact_traversal import ImpactTraversalEngine, ImpactResult
from graph.graph import Graph
from graph.node import Node, NodeType
from graph.edge import Edge, EdgeType

def test_analyze_impact():
    """Test impact analysis."""
    # Create test graph
    graph = Graph()
    
    # Add nodes
    main = Node(id='test.py:function:main', name='main', node_type=NodeType.FUNCTION, file_path='test.py', language='python')
    helper = Node(id='test.py:function:helper', name='helper', node_type=NodeType.FUNCTION, file_path='test.py', language='python')
    
    graph.add_node(main)
    graph.add_node(helper)
    
    # Add edge
    graph.add_edge(Edge(id='main->helper:call', source_id='test.py:function:main', target_id='test.py:function:helper', edge_type=EdgeType.CALL))
    
    # Create engine
    engine = ImpactTraversalEngine(call_graph=graph)
    
    # Analyze impact
    result = engine.analyze_impact(
        symbol_name='helper',
        symbol_type='function',
        file_path='test.py',
        max_depth=2
    )
    
    assert result.changed_symbol == 'helper'
    assert result.direct_callers == 1
    assert result.risk_level.value in ['low', 'medium', 'high', 'critical']
```

## 📖 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [Python Typing](https://docs.python.org/3/library/typing.html)
- [Asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

## 🚨 Troubleshooting

### Parser Not Found
- Install Tree-sitter CLI: `npm install -g tree-sitter-cli`
- Install language parsers: `tree-sitter install python javascript typescript`
- Rebuild language library

### Import Errors
- Check Python path
- Verify virtual environment is activated
- Install missing dependencies: `pip install -r requirements.txt`

### Memory Issues
- Limit repository size
- Use generators for large graphs
- Implement caching
- Consider incremental parsing

### Performance Issues
- Profile with cProfile
- Optimize graph traversal
- Limit traversal depth
- Use caching for repeated analyses

### Type Errors
- Check type hints
- Verify return types
- Use mypy for type checking: `mypy ai-service`