# Impact Analysis Skills

## 🎯 Overview

Skills for analyzing the impact of code changes using graph traversal and risk scoring.

## 📋 Prerequisites

- Understanding of graph traversal algorithms (BFS, DFS)
- Knowledge of call graphs and dependency graphs
- Familiarity with risk assessment concepts
- Python programming skills

## 🏗️ Core Concepts

### Impact Analysis Pipeline

```
Code Change (git diff or symbol selection)
    ↓
Symbol Detection (extract changed symbols)
    ↓
Graph Traversal (find affected nodes)
    ↓
Risk Scoring (calculate impact severity)
    ↓
Confidence Scoring (assess analysis reliability)
    ↓
AI Summary (generate human-readable explanation)
    ↓
Suggested Mitigation (recommend actions)
```

### Impact Types

- **Direct Callers**: Functions that directly call the changed symbol
- **Transitive Callers**: Functions that call functions that call the changed symbol (N levels deep)
- **Importers**: Files that import the changed symbol
- **Inheritors**: Classes that inherit from the changed class

## 🛠️ Required Tools

```bash
# Python standard library
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
from collections import defaultdict, deque
```

## 📚 Common Patterns

### 1. Impact Traversal Engine

```python
from graph.impact_traversal import ImpactTraversalEngine

# Initialize engine with graphs
engine = ImpactTraversalEngine(
    call_graph=call_graph,
    import_graph=import_graph
)

# Analyze impact of a symbol change
result = engine.analyze_impact(
    symbol_name='process_payment',
    symbol_type='function',
    file_path='src/payments.py',
    max_depth=3,
    include_transitive=True
)

# Result contains:
# - direct_callers: Number of direct callers
# - transitive_callers: Number of transitive callers
# - affected_files: Set of affected file paths
# - affected_symbols: Set of affected symbol names
# - risk_level: RiskLevel enum (LOW, MEDIUM, HIGH, CRITICAL)
# - risk_score: Float score
# - confidence_score: Float (0-1)
# - ai_summary: Human-readable summary
# - suggested_fix: Recommended mitigation
```

### 2. Diff-Based Analysis

```python
from analysis.diff_parser import DiffParser

# Parse git diff
parser = DiffParser()
changed_symbols = parser.parse_diff(diff_string)

# Analyze each changed symbol
for symbol_info in changed_symbols:
    result = engine.analyze_impact(
        symbol_name=symbol_info.name,
        symbol_type=symbol_info.symbol_type,
        file_path=symbol_info.file_path,
        max_depth=3
    )
    print(f"Symbol: {symbol_info.name}, Risk: {result.risk_level.value}")
```

### 3. Risk Scoring

```python
def calculate_risk_score(
    direct_callers: int,
    transitive_callers: int,
    affected_files: Set[str],
    affected_nodes: List[Node]
) -> Tuple[RiskLevel, float]:
    """Calculate risk score based on impact analysis."""
    
    # Base score: number of affected callers
    score = float(direct_callers + transitive_callers)
    
    # Boost score for critical paths
    critical_patterns = ['payment', 'billing', 'auth', 'security', 'database']
    critical_multiplier = 1.0
    for file_path in affected_files:
        for pattern in critical_patterns:
            if pattern.lower() in file_path.lower():
                critical_multiplier *= 1.5
                break
    
    # Boost score for files without test coverage
    no_test_penalty = 1.0
    for node in affected_nodes:
        if not node.is_test_file and not node.has_test_coverage:
            no_test_penalty *= 1.2
    
    # Apply multipliers
    score *= critical_multiplier * no_test_penalty
    score = min(score, 100.0)
    
    # Determine risk level
    if score >= 50:
        risk_level = RiskLevel.CRITICAL
    elif score >= 20:
        risk_level = RiskLevel.HIGH
    elif score >= 5:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW
    
    return risk_level, score
```

### 4. Confidence Scoring

```python
def calculate_confidence_score(
    unresolved_symbols: Set[str],
    target_nodes_found: bool,
    analysis_completeness: float
) -> float:
    """Calculate confidence score based on analysis completeness."""
    
    # Start with high confidence
    confidence = 1.0
    
    # Reduce confidence for unresolved symbols
    if unresolved_symbols:
        confidence *= (1.0 - len(unresolved_symbols) * 0.1)
    
    # Reduce confidence if target symbol not found
    if not target_nodes_found:
        confidence *= 0.5
    
    # Apply analysis completeness factor
    confidence *= analysis_completeness
    
    # Ensure confidence is between 0 and 1
    confidence = max(0.0, min(1.0, confidence))
    
    return round(confidence, 2)
```

### 5. AI Summary Generation

```python
def generate_ai_summary(
    result: ImpactResult
) -> str:
    """Generate a human-readable summary of the impact."""
    
    total_affected = result.direct_callers + result.transitive_callers
    
    if total_affected == 0:
        return f"No impact detected for changing '{result.changed_symbol}'."
    
    summary_parts = [
        f"Changing '{result.changed_symbol}' affects {total_affected} callers",
        f"across {len(result.affected_files)} files."
    ]
    
    # Add critical path information
    critical_files = []
    for file_path in result.affected_files:
        critical_patterns = ['payment', 'billing', 'auth', 'security']
        if any(pattern in file_path.lower() for pattern in critical_patterns):
            critical_files.append(file_path)
    
    if critical_files:
        summary_parts.append(f"Critical paths affected: {', '.join(critical_files[:3])}")
    
    # Add confidence information
    confidence_pct = int(result.confidence_score * 100)
    summary_parts.append(f"Confidence: {confidence_pct}%")
    
    return " ".join(summary_parts)
```

### 6. Suggested Fix Generation

```python
def generate_suggested_fix(
    result: ImpactResult
) -> str:
    """Generate a suggested fix based on the impact analysis."""
    
    if result.risk_level == RiskLevel.CRITICAL:
        return ("Consider breaking this change into smaller, safer increments. "
                "Add comprehensive tests before making this change.")
    elif result.risk_level == RiskLevel.HIGH:
        if result.direct_callers > 10:
            return ("Introduce the change as optional first (e.g., with a default parameter), "
                    "then migrate callers incrementally.")
        return "Ensure all affected callers are updated and tested."
    elif result.risk_level == RiskLevel.MEDIUM:
        return "Review the affected files and add tests for the changed behavior."
    else:
        return "Low risk change. Proceed with normal testing."
```

## 🎯 Best Practices

### 1. Traversal Depth

```python
# Default depth for most analyses
DEFAULT_DEPTH = 3

# Use deeper traversal for critical changes
CRITICAL_DEPTH = 5

# Use shallower traversal for quick checks
QUICK_DEPTH = 1

# Configure based on repository size
if repository_size > 10000:  # Large repository
    max_depth = 2
elif repository_size > 1000:  # Medium repository
    max_depth = 3
else:  # Small repository
    max_depth = 4
```

### 2. Caching Results

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_impact_analysis(
    symbol_name: str,
    symbol_type: str,
    file_path: str,
    max_depth: int = 3
) -> ImpactResult:
    """Cache impact analysis results."""
    # ... implementation ...
    pass
```

### 3. Parallel Analysis

```python
from concurrent.futures import ThreadPoolExecutor

def analyze_multiple_symbols(
    symbols: List[Dict[str, str]],
    max_workers: int = 4
) -> List[ImpactResult]:
    """Analyze multiple symbols in parallel."""
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for symbol_info in symbols:
            future = executor.submit(
                engine.analyze_impact,
                symbol_name=symbol_info['name'],
                symbol_type=symbol_info['type'],
                file_path=symbol_info.get('file'),
                max_depth=3
            )
            futures.append(future)
        
        results = []
        for future in futures:
            results.append(future.result())
        
        return results
```

### 4. Incremental Analysis

```python
def analyze_incremental_change(
    old_repository_data: dict,
    new_repository_data: dict,
    changed_files: List[str]
) -> ImpactResult:
    """Analyze only changed files for better performance."""
    
    # Build graphs only for changed files
    changed_graph = build_graph_for_files(new_repository_data, changed_files)
    
    # Find changed symbols
    changed_symbols = find_changed_symbols(old_repository_data, new_repository_data)
    
    # Analyze impact
    results = []
    for symbol in changed_symbols:
        result = engine.analyze_impact(
            symbol_name=symbol['name'],
            symbol_type=symbol['type'],
            file_path=symbol['file'],
            max_depth=3
        )
        results.append(result)
    
    return aggregate_results(results)
```

## 🧪 Testing

### Test Impact Analysis

```python
def test_impact_analysis():
    # Create test repository data
    repository_data = {
        "files": [
            {
                "path": "src/payments.py",
                "language": "python",
                "functions": [
                    {"name": "process_payment", "start_line": 10, "end_line": 20},
                    {"name": "charge_user", "start_line": 22, "end_line": 30}
                ]
            },
            {
                "path": "src/api.py",
                "language": "python",
                "functions": [
                    {"name": "payment_endpoint", "start_line": 5, "end_line": 15}
                ]
            }
        ]
    }
    
    # Build graphs
    call_graph = CallGraphBuilder().build_from_repository(repository_data)
    import_graph = ImportGraphBuilder().build_from_repository(repository_data)
    
    # Create engine
    engine = ImpactTraversalEngine(call_graph, import_graph)
    
    # Analyze impact
    result = engine.analyze_impact(
        symbol_name='process_payment',
        symbol_type='function',
        file_path='src/payments.py',
        max_depth=2
    )
    
    # Verify result
    assert result.changed_symbol == 'process_payment'
    assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
    assert 0 <= result.confidence_score <= 1
```

### Test Diff Parsing

```python
def test_diff_parsing():
    diff = """
diff --git a/src/payments.py b/src/payments.py
index abc123..def456 100644
--- a/src/payments.py
+++ b/src/payments.py
@@ -10,7 +10,7 @@ class PaymentService:
 
 @app.route('/process', methods=['POST'])
-def process_payment(user):
+def process_payment(user, currency):
     # Process payment logic
     amount = calculate_amount(user)
     return charge_user(user, amount)
"""
    
    parser = DiffParser()
    changed_symbols = parser.parse_diff(diff)
    
    assert len(changed_symbols) == 1
    assert changed_symbols[0].name == 'process_payment'
    assert changed_symbols[0].symbol_type == 'function'
    assert changed_symbols[0].change_type == 'modified'
```

## 📖 Resources

- [Graph Traversal Algorithms](https://en.wikipedia.org/wiki/Graph_traversal)
- [Risk Assessment Techniques](https://en.wikipedia.org/wiki/Risk_assessment)
- [Static Analysis Tools](https://en.wikipedia.org/wiki/Static_program_analysis)

## 🚨 Troubleshooting

### No Impact Detected
- Verify the symbol exists in the graph
- Check that the symbol name and type are correct
- Ensure the file path is correct
- Verify the graph was built correctly

### Low Confidence Score
- Check for unresolved symbols
- Verify all dependencies are properly parsed
- Ensure dynamic imports are handled (they reduce confidence)

### High Risk Score for Simple Changes
- Verify critical path patterns are appropriate
- Check test coverage flags
- Review risk scoring formula

### Performance Issues
- Reduce traversal depth
- Limit the number of files analyzed
- Use caching for repeated analyses
- Consider incremental analysis