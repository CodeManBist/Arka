1. Purpose

The graph model represents code structure and dependencies for impact analysis.

2. Graph Architecture

- In-memory adjacency graph using dictionaries
- Two main graphs: Call Graph (symbol-level) and Import Graph (file-level)
- Supports efficient BFS/DFS traversal
- Computes metrics: in-degree, out-degree, centrality

3. Node Types

- FUNCTION: Function definitions
- CLASS: Class definitions
- METHOD: Class methods
- FILE: Source files/modules
- MODULE: Imported modules
- VARIABLE: Variables and constants
- IMPORT: Import statements
- EXPORT: Export statements

4. Edge Types

- CALL: Function/method calls another function
- IMPORT: File imports another file/module
- INHERITANCE: Class extends another class
- USAGE: Variable/function usage
- EXPORT: Export relationship
- CONTAINS: File contains symbol

5. Node Schema

```python
@dataclass
class Node:
    id: str                    # Unique identifier
    name: str                 # Symbol name
    node_type: NodeType       # FUNCTION, CLASS, METHOD, FILE, etc.
    file_path: str            # Source file path
    language: str             # Programming language
    start_line: int           # Starting line number
    end_line: int             # Ending line number
    is_entry_point: bool      # Entry point flag
    is_test_file: bool        # Test file flag
    has_test_coverage: bool   # Test coverage flag
    in_degree: int            # Number of incoming edges
    out_degree: int           # Number of outgoing edges
    centrality: float         # Centrality score (0-1)
    metadata: dict            # Additional metadata
```

6. Edge Schema

```python
@dataclass
class Edge:
    id: str                    # Unique identifier
    source_id: str             # Source node ID
    target_id: str             # Target node ID
    edge_type: EdgeType        # CALL, IMPORT, INHERITANCE, etc.
    weight: float              # Edge weight (default 1.0)
    line_number: int           # Line number where edge occurs
    metadata: dict             # Additional metadata
```

7. Symbol IDs

Format: `{file_path}:{node_type}:{name}`
Example: `src/payments.py:function:process_payment`

8. Call Graph

- Nodes: FUNCTION, CLASS, METHOD
- Edges: CALL, INHERITANCE
- Purpose: Track function/method call relationships
- Used for: Impact analysis when functions change

9. Import Graph

- Nodes: FILE, MODULE
- Edges: IMPORT, EXPORT
- Purpose: Track file-to-file dependencies
- Used for: Repository overview, critical service identification

10. Traversal Algorithms

- BFS: Breadth-first search for finding all reachable nodes
- DFS: Depth-first search for path finding
- Transitive Closure: Find all nodes reachable within N hops
- Path Finding: Find all paths between two nodes

11. Cycle Detection

- Graph supports cycle detection via traversal
- Used to identify circular dependencies
- Currently: Not explicitly implemented but traversal handles cycles

12. Risk Score Calculation

Formula:
```
risk_score = (direct_callers + transitive_callers) * critical_multiplier * no_test_penalty

where:
- critical_multiplier: 1.5 if critical path (payment, auth, etc.)
- no_test_penalty: 1.2 if no test coverage

Risk Levels:
- CRITICAL: score >= 50
- HIGH: score >= 20
- MEDIUM: score >= 5
- LOW: score < 5
```

13. Confidence Score Calculation

Formula:
```
confidence = 1.0 - (unresolved_symbols * 0.1)

where:
- unresolved_symbols: Number of symbols that couldn't be resolved
- Minimum confidence: 0.0
- Maximum confidence: 1.0
```

14. Graph Caching

- Currently: Graphs built on-demand, not cached
- Future: Cache graphs in memory or database
- Consideration: Memory usage for large repositories

15. Performance Considerations

- BFS/DFS: O(V + E) time complexity
- Transitive closure: O(V * E) worst case
- Memory: O(V + E) for graph storage
- Optimization: Limit traversal depth (default: 3)

16. Future Neo4j Mapping

Planned schema for Neo4j:
```cypher
CREATE (f:Function {name: 'process_payment', file: 'src/payments.py'})
CREATE (g:Function {name: 'charge_user', file: 'src/payments.py'})
CREATE (f)-[:CALLS]->(g)
```

17. Limitations

- Static analysis only (no runtime information)
- Cannot detect dynamic imports, reflection, eval()
- Limited by Tree-sitter parser capabilities
- Large repositories may have memory constraints

18. Examples

Repository Structure:
```
Repository
  File (src/payments.py)
       Function (process_payment)
       Function (charge_user)
       Class (PaymentService)
            Method (process)
```

Edge Types:
```
process_payment --[CALLS]--> charge_user
PaymentService --[CONTAINS]--> process
src/payments.py --[IMPORTS]--> src/utils.py
```

Traversal Example:
```
Changed Function: process_payment
       
        Direct Callers (17)
       
        Transitive Callers (23)
       
        Affected Files (5)
       
        Risk Score: 45.5 (HIGH)
       
        Confidence: 94%
       
        Codex Summary: "Adding currency parameter breaks 17 call sites..."
```