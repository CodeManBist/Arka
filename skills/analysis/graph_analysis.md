# Graph Analysis Skills

## 🎯 Overview

Skills for building and analyzing call graphs and import graphs for impact analysis.

## 📋 Prerequisites

- Understanding of graph theory concepts
- Familiarity with directed graphs
- Knowledge of call graphs and dependency graphs
- Python data structures (dicts, sets, lists)

## 🏗️ Core Concepts

### Graph Types

#### Call Graph
- **Nodes**: Functions, methods, classes
- **Edges**: CALL relationships (function A calls function B)
- **Purpose**: Track function-level dependencies
- **Use Case**: Impact analysis when functions change

#### Import Graph
- **Nodes**: Files, modules
- **Edges**: IMPORT relationships (file A imports file B)
- **Purpose**: Track file-level dependencies
- **Use Case**: Repository overview, critical service identification

### Graph Representation

```python
# Adjacency list representation
class Graph:
    def __init__(self):
        self.nodes = {}  # node_id -> Node
        self.edges = {}  # edge_id -> Edge
        self.outgoing_edges = defaultdict(list)  # source_id -> [edge_id, ...]
        self.incoming_edges = defaultdict(list)  # target_id -> [edge_id, ...]
```

## 🛠️ Required Tools

```bash
# Python standard library
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
```

## 📚 Common Patterns

### 1. Building a Call Graph

```python
from graph.call_graph_builder import CallGraphBuilder

# Build from repository data
builder = CallGraphBuilder()
call_graph = builder.build_from_repository(repository_data)

# Access graph properties
nodes = call_graph.nodes
edges = call_graph.edges
stats = call_graph.get_statistics()
```

### 2. Building an Import Graph

```python
from graph.import_graph_builder import ImportGraphBuilder

# Build from repository data
builder = ImportGraphBuilder()
import_graph = builder.build_from_repository(repository_data)

# Find critical services (high fan-in)
critical_services = [
    node for node in import_graph.nodes.values()
    if node.in_degree > 5
]
```

### 3. Graph Traversal

#### Breadth-First Search (BFS)
```python
# Find all nodes reachable from a starting node
visited = call_graph.bfs(start_node_id, max_depth=3)

# visited is a dict: {node_id: distance_from_start}
for node_id, distance in visited.items():
    print(f"Node {node_id} is {distance} hops away")
```

#### Depth-First Search (DFS)
```python
# Find all nodes in DFS order
node_ids = call_graph.dfs(start_node_id, max_depth=3)

# node_ids is a list of node IDs in DFS order
for node_id in node_ids:
    node = call_graph.get_node(node_id)
    print(f"Visited: {node.name}")
```

#### Transitive Closure
```python
# Find all nodes reachable from multiple start nodes
reachable = call_graph.get_transitive_closure(
    start_node_ids=['node1', 'node2'],
    max_depth=2,
    edge_types=[EdgeType.CALL]
)

# reachable is a set of node IDs
print(f"Reachable nodes: {len(reachable)}")
```

### 4. Finding Callers and Callees

```python
# Get direct callers of a function
callers = call_graph.get_callers(function_node_id)

# Get functions called by a function
callees = call_graph.get_callees(function_node_id)

# Get all predecessors (nodes with edges pointing to this node)
predecessors = call_graph.get_predecessors(node_id)

# Get all successors (nodes this node points to)
successors = call_graph.get_successors(node_id)
```

### 5. Path Finding

```python
# Find all paths from start to end
paths = call_graph.find_paths(
    start_node_id='function_a',
    end_node_id='function_b',
    max_depth=5
)

# paths is a list of paths, each path is a list of node IDs
for i, path in enumerate(paths):
    print(f"Path {i+1}: {' -> '.join(path)}")
```

## 🎯 Best Practices

### 1. Node ID Generation
```python
def generate_node_id(file_path: str, name: str, node_type: str) -> str:
    """Generate a unique node ID."""
    safe_name = re.sub(r'[^a-zA-Z0-9_.]', '_', name)
    return f"{file_path}:{node_type}:{safe_name}"

# Example: src/payments.py:function:process_payment
```

### 2. Edge ID Generation
```python
def generate_edge_id(source_id: str, target_id: str, edge_type: str) -> str:
    """Generate a unique edge ID."""
    return f"{source_id}->{target_id}:{edge_type}"

# Example: src/payments.py:function:process_payment->src/utils.py:function:charge:call
```

### 3. Graph Metrics
```python
# Compute centrality (simple version)
def compute_centrality(graph: Graph) -> Dict[str, float]:
    centrality = {}
    for node_id in graph.nodes:
        in_degree = len(graph.get_incoming_edges(node_id))
        out_degree = len(graph.get_outgoing_edges(node_id))
        centrality[node_id] = float(in_degree + out_degree)
    
    # Normalize to 0-1 range
    if centrality:
        max_centrality = max(centrality.values())
        if max_centrality > 0:
            for node_id in centrality:
                centrality[node_id] /= max_centrality
    
    return centrality
```

### 4. Cycle Detection
```python
def has_cycle(graph: Graph, start_node_id: str) -> bool:
    """Check if there's a cycle starting from a node."""
    visited = set()
    stack = set()
    
    def dfs(node_id: str) -> bool:
        if node_id in stack:
            return True
        if node_id in visited:
            return False
        
        visited.add(node_id)
        stack.add(node_id)
        
        for successor in graph.get_successors(node_id):
            if dfs(successor.id):
                return True
        
        stack.remove(node_id)
        return False
    
    return dfs(start_node_id)
```

## 🧪 Testing

### Test Graph Construction
```python
def test_call_graph_construction():
    # Create test repository data
    repository_data = {
        "files": [
            {
                "path": "src/main.py",
                "language": "python",
                "functions": [
                    {"name": "main", "start_line": 1, "end_line": 10},
                    {"name": "helper", "start_line": 12, "end_line": 20}
                ]
            }
        ]
    }
    
    # Build graph
    builder = CallGraphBuilder()
    graph = builder.build_from_repository(repository_data)
    
    # Verify graph properties
    assert len(graph.nodes) == 2
    assert "src/main.py:function:main" in graph.nodes
    assert "src/main.py:function:helper" in graph.nodes
```

### Test Graph Traversal
```python
def test_bfs_traversal():
    # Create a simple graph
    graph = Graph()
    
    # Add nodes
    graph.add_node(Node(id='a', name='A', node_type=NodeType.FUNCTION, file_path='test.py', language='python'))
    graph.add_node(Node(id='b', name='B', node_type=NodeType.FUNCTION, file_path='test.py', language='python'))
    graph.add_node(Node(id='c', name='C', node_type=NodeType.FUNCTION, file_path='test.py', language='python'))
    
    # Add edges
    graph.add_edge(Edge(id='a->b:call', source_id='a', target_id='b', edge_type=EdgeType.CALL))
    graph.add_edge(Edge(id='b->c:call', source_id='b', target_id='c', edge_type=EdgeType.CALL))
    
    # Test BFS
    visited = graph.bfs('a', max_depth=2)
    assert len(visited) == 3
    assert visited['a'] == 0
    assert visited['b'] == 1
    assert visited['c'] == 2
```

## 📖 Resources

- [Graph Theory Basics](https://en.wikipedia.org/wiki/Graph_theory)
- [NetworkX Documentation](https://networkx.org/) (for reference)
- [Python Graph Algorithms](https://realpython.com/python-data-structures/#graph-structures)

## 🚨 Troubleshooting

### Memory Issues with Large Graphs
- Limit traversal depth (default: 3)
- Use generators for large traversals
- Consider sampling for very large repositories

### Infinite Loops in Traversal
- Ensure cycle detection is in place
- Use visited sets to prevent re-visiting nodes
- Limit maximum depth

### Node/Edge Not Found
- Verify node/edge IDs are correct
- Check that nodes/edges were added to the graph
- Use graph.get_node() and graph.get_edge() for safe access