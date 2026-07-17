# Unit Testing Skills

## 🎯 Overview

Skills for writing unit tests for the Blast Radius project using pytest and Jest.

## 📋 Prerequisites

- Python 3.11+ with pytest
- Node.js 22+ with Jest
- Understanding of test-driven development
- Familiarity with mocking and fixtures

## 🏗️ Core Concepts

### Testing Pyramid

```
        /\
       /  \     Unit Tests (Fast, Isolated)
      /----\
     /      \   Integration Tests (Component Interaction)
    /--------\
   /          \ E2E Tests (Full System)
  /------------\
```

### Test Structure

```
ai-service/tests/
├── test_parser_factory.py
├── test_repository_parser.py
├── test_function_extractor.py
├── test_class_extractor.py
├── test_call_graph_builder.py
├── test_impact_traversal.py
└── test_diff_parser.py

frontend/__tests__/
├── api/
│   └── blastRadius.test.tsx
├── components/
│   └── RiskBadge.test.tsx
└── pages/
    └── blast-radius.test.tsx
```

## 🛠️ Required Tools

```bash
# Python
pip install pytest pytest-asyncio pytest-mock

# Node.js
npm install --save-dev jest @testing-library/react @testing-library/jest-dom ts-jest
```

## 📚 Common Patterns

### 1. Python Unit Tests with pytest

```python
# tests/test_function_extractor.py
import pytest
from analysis.extractors.function_extractor import FunctionExtractor
from analysis.parser_factory import ParserFactory

def test_extract_functions_from_python():
    """Test extracting functions from Python code."""
    source = """
def hello(name):
    return f"Hello, {name}!"

def goodbye(name):
    return f"Goodbye, {name}!"
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
    
    assert len(functions) == 2
    assert functions[0]['name'] == 'hello'
    assert functions[1]['name'] == 'goodbye'

def test_extract_functions_from_javascript():
    """Test extracting functions from JavaScript code."""
    source = """
function add(a, b) {
    return a + b;
}

const subtract = (a, b) => a - b;
"""
    
    parser = ParserFactory.get_parser('javascript')
    tree = parser.parse(source)
    
    extractor = FunctionExtractor()
    functions = extractor.extract(
        language=parser.language,
        tree=tree,
        source=source,
        language_name='javascript'
    )
    
    assert len(functions) == 2
    assert functions[0]['name'] == 'add'
    assert functions[1]['name'] == 'subtract'
```

### 2. Mocking External Dependencies

```python
# tests/test_repository_parser.py
from unittest.mock import patch, MagicMock
from analysis.repository_parser import RepositoryParser

def test_parse_repository_with_mock():
    """Test repository parsing with mocked scanner."""
    mock_files = [
        {"path": "test.py", "language": "python"}
    ]
    
    with patch('analysis.repository_parser.RepositoryScanner') as mock_scanner:
        mock_scanner.return_value.scan.return_value = mock_files
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.read.return_value = "def test():\n    pass\n"
            
            parser = RepositoryParser()
            result = parser.parse_repository("/fake/path")
            
            assert result["repository"]["total_files"] == 1
```

### 3. Async Tests with pytest-asyncio

```python
# tests/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app import app

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

@pytest.mark.asyncio
async def test_analyze_endpoint(client):
    """Test the analyze endpoint."""
    # Mock the repository parser
    with patch('api.blast_radius.RepositoryParser') as mock_parser:
        mock_parser.return_value.parse_repository.return_value = {
            "repository": {
                "files": [
                    {
                        "path": "test.py",
                        "language": "python",
                        "functions": [{"name": "test_func", "start_line": 1, "end_line": 5}]
                    }
                ]
            },
            "symbol_table": {}
        }
        
        response = client.post("/api/blast-radius/analyze", json={
            "repository_path": "/test",
            "symbol_name": "test_func",
            "symbol_type": "function"
        })
        
        assert response.status_code == 200
        assert response.json()["success"] is True
```

### 4. Parameterized Tests

```python
# tests/test_call_graph_builder.py
import pytest
from graph.call_graph_builder import CallGraphBuilder

@pytest.mark.parametrize("language,source,expected_functions", [
    ("python", "def hello():\n    pass\n", ["hello"]),
    ("python", "def hello():\n    pass\n\ndef world():\n    pass\n", ["hello", "world"]),
    ("javascript", "function test() {}\n", ["test"]),
])
def test_extract_functions_parameterized(language, source, expected_functions):
    """Test function extraction with different inputs."""
    repository_data = {
        "files": [
            {
                "path": f"test.{language}",
                "language": language,
                "functions": [{"name": name, "start_line": i+1, "end_line": i+2} 
                            for i, name in enumerate(expected_functions)]
            }
        ]
    }
    
    builder = CallGraphBuilder()
    graph = builder.build_from_repository(repository_data)
    
    assert len(graph.nodes) == len(expected_functions)
    for func_name in expected_functions:
        nodes = graph.get_nodes_by_name(func_name)
        assert len(nodes) > 0
```

### 5. Frontend Tests with Jest

```typescript
// __tests__/components/RiskBadge.test.tsx
import { render, screen } from '@testing-library/react';
import RiskBadge from '@/components/RiskBadge';

describe('RiskBadge', () => {
  const riskLevels = ['low', 'medium', 'high', 'critical'] as const;
  
  riskLevels.forEach((level) => {
    it(`renders ${level} badge correctly`, () => {
      render(<RiskBadge riskLevel={level} />);
      
      const badge = screen.getByText(level.toUpperCase());
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveClass(`bg-${level}-600`);
    });
  });
});
```

### 6. API Integration Tests

```typescript
// __tests__/api/blastRadius.test.tsx
import { fetchRepositoryOverview } from '@/lib/api';

global.fetch = jest.fn();

describe('fetchRepositoryOverview', () => {
  it('fetches repository overview successfully', async () => {
    const mockData = {
      repository: 'test-repo',
      total_files: 10,
      language_breakdown: { python: 5, javascript: 5 }
    };
    
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockData)
    });
    
    const result = await fetchRepositoryOverview('/path/to/repo');
    expect(result).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/blast-radius/repository-overview',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
    );
  });

  it('handles API errors', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.resolve({ error: 'Internal server error' })
    });
    
    await expect(fetchRepositoryOverview('/path/to/repo'))
      .rejects
      .toThrow('Failed to fetch repository overview');
  });
});
```

### 7. Snapshot Testing

```typescript
// __tests__/pages/blast-radius.test.tsx
import { render } from '@testing-library/react';
import BlastRadiusPage from '@/app/blast-radius/page';

describe('BlastRadiusPage', () => {
  it('renders correctly', () => {
    const { container } = render(<BlastRadiusPage />);
    expect(container).toMatchSnapshot();
  });
});
```

## 🎯 Best Practices

### 1. Test Organization

- Group tests by module/functionality
- Use descriptive test names
- Keep tests focused on one thing
- Use fixtures for common test data

### 2. Test Naming

```python
# Good
def test_parse_repository_returns_correct_structure():
    pass

def test_function_extractor_handles_empty_file():
    pass

# Bad
def test_1():
    pass

def test_stuff():
    pass
```

### 3. Test Isolation

- Each test should be independent
- Use setup/teardown for shared resources
- Avoid global state
- Use fixtures for dependencies

### 4. Mocking Strategy

- Mock external services (APIs, databases)
- Don't mock what you're testing
- Use real implementations when possible
- Mock at the right level

### 5. Test Data

- Use realistic test data
- Keep test data small and focused
- Use factories for complex objects
- Avoid production data in tests

## 🧪 Testing Strategies

### 1. Test Coverage

```bash
# Python
pytest --cov=ai-service --cov-report=html tests/

# Node.js
jest --coverage --coverageDirectory=coverage
```

### 2. Test Fixtures

```python
# conftest.py
import pytest
from analysis.repository_parser import RepositoryParser

@pytest.fixture
def sample_repository(tmp_path):
    """Create a sample repository for testing."""
    python_file = tmp_path / "test.py"
    python_file.write_text("""
def hello(name):
    return f"Hello, {name}!"

class TestClass:
    def method(self):
        pass
""")
    
    return str(tmp_path)

@pytest.fixture
def repository_parser():
    """Create a repository parser instance."""
    return RepositoryParser()
```

### 3. Integration Tests

```python
# tests/test_integration.py
from analysis.repository_parser import RepositoryParser
from graph.call_graph_builder import CallGraphBuilder
from graph.impact_traversal import ImpactTraversalEngine

def test_full_analysis_pipeline(tmp_path):
    """Test the complete analysis pipeline."""
    # Create test files
    python_file = tmp_path / "main.py"
    python_file.write_text("""
def main():
    helper()

def helper():
    pass
""")
    
    # Parse repository
    parser = RepositoryParser()
    repository_data = parser.parse_repository(str(tmp_path))
    
    # Build graphs
    call_graph = CallGraphBuilder().build_from_repository(repository_data["repository"])
    
    # Analyze impact
    engine = ImpactTraversalEngine(call_graph)
    result = engine.analyze_impact(
        symbol_name='helper',
        symbol_type='function',
        file_path=str(python_file),
        max_depth=2
    )
    
    # Verify results
    assert result.changed_symbol == 'helper'
    assert result.direct_callers == 1
    assert 'main' in result.affected_symbols
```

### 4. Property-Based Testing

```python
# tests/test_graph_properties.py
from hypothesis import given, strategies as st
from graph.graph import Graph
from graph.node import Node, NodeType
from graph.edge import Edge, EdgeType

@given(
    nodes=st.lists(st.builds(Node, 
        id=st.text(min_size=1),
        name=st.text(min_size=1),
        node_type=st.sampled_from(list(NodeType)),
        file_path=st.text(min_size=1),
        language=st.text(min_size=1)
    ), min_size=1, max_size=10),
    edges=st.lists(st.builds(Edge,
        id=st.text(min_size=1),
        source_id=st.text(min_size=1),
        target_id=st.text(min_size=1),
        edge_type=st.sampled_from(list(EdgeType))
    ), min_size=0, max_size=20)
)
def test_graph_properties(nodes, edges):
    """Test that graph operations maintain invariants."""
    graph = Graph()
    
    # Add nodes
    for node in nodes:
        graph.add_node(node)
    
    # Add edges (only if source and target exist)
    for edge in edges:
        if edge.source_id in graph.nodes and edge.target_id in graph.nodes:
            graph.add_edge(edge)
    
    # Test invariants
    assert len(graph.nodes) == len(nodes)
    
    # Test that all edges reference existing nodes
    for edge_id, edge in graph.edges.items():
        assert edge.source_id in graph.nodes
        assert edge.target_id in graph.nodes
```

## 📖 Resources

- [pytest Documentation](https://docs.pytest.org)
- [Jest Documentation](https://jestjs.io/docs)
- [Testing Library React](https://testing-library.com/docs/react-testing-library/intro/)
- [Hypothesis for Property-Based Testing](https://hypothesis.readthedocs.io)

## 🚨 Troubleshooting

### Tests Not Running
- Check pytest/jest is installed
- Verify test file names match pattern (`test_*.py` or `*.test.ts`)
- Check for syntax errors

### Mocking Not Working
- Verify mock is in the right scope
- Check mock is called before assertion
- Use `patch.object` for class methods

### Async Tests Failing
- Use `@pytest.mark.asyncio` for pytest
- Use `async/await` properly
- Check for unhandled promises

### Test Coverage Low
- Add more test cases
- Test edge cases
- Test error conditions
- Use property-based testing

### Tests Too Slow
- Use pytest markers to skip slow tests
- Mock external dependencies
- Use smaller test data
- Run tests in parallel