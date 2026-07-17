"""Impact traversal engine for analyzing code changes."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from .graph import Graph
from .node import Node, NodeType, RiskLevel
from .edge import Edge, EdgeType


class ImpactType(Enum):
    """Types of impact from a code change."""
    DIRECT_CALLER = "direct_caller"
    TRANSITIVE_CALLER = "transitive_caller"
    IMPORTER = "importer"
    INHERITOR = "inheritor"
    USAGE = "usage"


@dataclass
class ImpactResult:
    """Result of impact analysis for a code change."""
    
    # Changed symbol information
    changed_symbol: str
    changed_symbol_type: str
    changed_file: str
    
    # Impact statistics
    direct_callers: int = 0
    transitive_callers: int = 0
    affected_files: Set[str] = field(default_factory=set)
    affected_symbols: Set[str] = field(default_factory=set)
    
    # Risk assessment
    risk_level: RiskLevel = RiskLevel.LOW
    risk_score: float = 0.0
    confidence_score: float = 1.0  # 0-1, where 1 is highest confidence
    
    # Details
    call_chains: List[List[str]] = field(default_factory=list)
    affected_nodes: List[Node] = field(default_factory=list)
    
    # Suggested mitigation
    suggested_fix: str = ""
    ai_summary: str = ""
    
    # Metadata
    analysis_depth: int = 3  # Default traversal depth
    unresolved_symbols: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "changed_symbol": self.changed_symbol,
            "changed_symbol_type": self.changed_symbol_type,
            "changed_file": self.changed_file,
            "direct_callers": self.direct_callers,
            "transitive_callers": self.transitive_callers,
            "affected_files": list(self.affected_files),
            "affected_symbols": list(self.affected_symbols),
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "confidence_score": self.confidence_score,
            "call_chains": self.call_chains,
            "affected_nodes": [node.to_dict() for node in self.affected_nodes],
            "suggested_fix": self.suggested_fix,
            "ai_summary": self.ai_summary,
            "analysis_depth": self.analysis_depth,
            "unresolved_symbols": list(self.unresolved_symbols),
        }


class ImpactTraversalEngine:
    """
    Engine for traversing graphs to determine the impact of code changes.
    
    This engine can:
    - Find all callers of a changed function
    - Trace transitive dependencies
    - Calculate risk scores based on fan-out and criticality
    - Generate confidence scores based on static analysis completeness
    """
    
    def __init__(self, call_graph: Graph, import_graph: Optional[Graph] = None):
        """
        Initialize the impact traversal engine.
        
        Args:
            call_graph: The call graph to traverse
            import_graph: Optional import graph for additional analysis
        """
        self.call_graph = call_graph
        self.import_graph = import_graph
        
        # Critical path patterns (for higher risk scoring)
        self.critical_patterns = [
            "payment", "billing", "checkout", "transaction",
            "auth", "authentication", "authorization", "login", "logout",
            "security", "encrypt", "decrypt", "hash", "token",
            "database", "db", "query", "save", "update", "delete",
            "api", "endpoint", "route", "controller", "handler",
            "main", "app", "server", "start", "init"
        ]
        
        # Test file patterns
        self.test_patterns = ["test", "spec", "_test", ".test", ".spec"]
    
    def analyze_impact(
        self,
        symbol_name: str,
        symbol_type: str = "function",
        file_path: Optional[str] = None,
        max_depth: int = 3,
        include_transitive: bool = True
    ) -> ImpactResult:
        """
        Analyze the impact of changing a symbol.
        
        Args:
            symbol_name: Name of the symbol being changed
            symbol_type: Type of symbol (function, class, method, etc.)
            file_path: Optional file path to narrow down the symbol
            max_depth: Maximum depth for transitive traversal
            include_transitive: Whether to include transitive callers
            
        Returns:
            ImpactResult with full impact analysis
        """
        # Find the target node(s)
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
        
        # Initialize result
        result = ImpactResult(
            changed_symbol=symbol_name,
            changed_symbol_type=symbol_type,
            changed_file=file_path or target_nodes[0].file_path,
            analysis_depth=max_depth
        )
        
        # Track visited nodes and their distances
        visited: Dict[str, int] = {}
        call_chains: List[List[str]] = []
        
        # Analyze each target node
        for target_node in target_nodes:
            # Find direct callers
            direct_callers = self.call_graph.get_callers(target_node.id)
            result.direct_callers += len(direct_callers)
            
            # Track affected files and symbols
            for caller in direct_callers:
                result.affected_files.add(caller.file_path)
                result.affected_symbols.add(caller.name)
                result.affected_nodes.append(caller)
                
                # Record call chain
                call_chains.append([caller.id, target_node.id])
            
            # Find transitive callers if requested
            if include_transitive:
                transitive_result = self._find_transitive_callers(
                    target_node.id, 
                    max_depth, 
                    exclude_direct=True
                )
                result.transitive_callers += len(transitive_result["nodes"])
                
                for node_id, distance in transitive_result["nodes"].items():
                    node = self.call_graph.get_node(node_id)
                    if node:
                        result.affected_files.add(node.file_path)
                        result.affected_symbols.add(node.name)
                        result.affected_nodes.append(node)
                        
                        # Record call chain
                        call_chains.append([node_id, target_node.id])
        
        result.call_chains = call_chains
        
        # Calculate risk score
        result.risk_level, result.risk_score = self._calculate_risk_score(result)
        
        # Calculate confidence score
        result.confidence_score = self._calculate_confidence_score(result)
        
        # Generate AI summary (placeholder - will be enhanced with actual AI)
        result.ai_summary = self._generate_ai_summary(result)
        result.suggested_fix = self._generate_suggested_fix(result)
        
        return result
    
    def analyze_diff_impact(
        self,
        diff: str,
        repository_data: dict[str, Any],
        max_depth: int = 3
    ) -> List[ImpactResult]:
        """
        Analyze the impact of a git diff.
        
        Args:
            diff: Git diff string
            repository_data: Repository parsing results
            max_depth: Maximum depth for transitive traversal
            
        Returns:
            List of ImpactResults for each changed symbol
        """
        # Parse the diff to find changed symbols
        changed_symbols = self._parse_diff(diff)
        
        results = []
        for symbol_info in changed_symbols:
            symbol_name = symbol_info["name"]
            symbol_type = symbol_info.get("type", "function")
            file_path = symbol_info.get("file")
            
            result = self.analyze_impact(
                symbol_name=symbol_name,
                symbol_type=symbol_type,
                file_path=file_path,
                max_depth=max_depth
            )
            results.append(result)
        
        return results
    
    def _find_target_nodes(
        self, 
        symbol_name: str, 
        symbol_type: str, 
        file_path: Optional[str] = None
    ) -> List[Node]:
        """Find nodes matching the target symbol."""
        nodes = []
        
        # Try to find by name and type
        node_type = self._string_to_node_type(symbol_type)
        
        if file_path:
            # Look for nodes in the specific file
            file_nodes = self.call_graph.get_nodes_by_file(file_path)
            for node in file_nodes:
                if node.name == symbol_name and node.node_type == node_type:
                    nodes.append(node)
        
        # If not found or file_path not specified, search all nodes
        if not nodes:
            all_nodes = self.call_graph.get_nodes_by_name(symbol_name)
            for node in all_nodes:
                if node.node_type == node_type:
                    nodes.append(node)
        
        # If still not found, try partial matching
        if not nodes:
            for node in self.call_graph.nodes.values():
                if node.name == symbol_name:
                    nodes.append(node)
        
        return nodes
    
    def _string_to_node_type(self, type_str: str) -> NodeType:
        """Convert string type to NodeType enum."""
        type_mapping = {
            "function": NodeType.FUNCTION,
            "class": NodeType.CLASS,
            "method": NodeType.METHOD,
            "file": NodeType.FILE,
            "module": NodeType.MODULE,
            "variable": NodeType.VARIABLE,
        }
        return type_mapping.get(type_str.lower(), NodeType.FUNCTION)
    
    def _find_transitive_callers(
        self, 
        target_node_id: str, 
        max_depth: int, 
        exclude_direct: bool = False
    ) -> Dict[str, Any]:
        """
        Find all transitive callers of a node.
        
        Returns:
            Dictionary with 'nodes' (node_id -> distance) and 'paths' (list of paths)
        """
        visited: Dict[str, int] = {}
        paths: List[List[str]] = []
        
        # Use BFS to find all callers
        queue = [(target_node_id, 0, [target_node_id])]
        
        while queue:
            current_id, depth, path = queue.popleft()
            
            if current_id in visited:
                continue
            
            # Skip the target node itself if we want to exclude direct
            if exclude_direct and current_id == target_node_id:
                visited[current_id] = depth
                continue
            
            visited[current_id] = depth
            
            if depth > 0:
                paths.append(path)
            
            if depth >= max_depth:
                continue
            
            # Get predecessors (callers) and add to queue
            predecessors = self.call_graph.get_predecessors(current_id)
            for predecessor in predecessors:
                if predecessor.id not in visited:
                    new_path = path + [predecessor.id]
                    queue.append((predecessor.id, depth + 1, new_path))
        
        return {"nodes": visited, "paths": paths}
    
    def _calculate_risk_score(self, result: ImpactResult) -> Tuple[RiskLevel, float]:
        """Calculate risk score based on impact analysis."""
        total_affected = result.direct_callers + result.transitive_callers
        unique_files = len(result.affected_files)
        
        # Base score: number of affected callers
        score = float(total_affected)
        
        # Boost score for critical paths
        critical_multiplier = 1.0
        for file_path in result.affected_files:
            for pattern in self.critical_patterns:
                if pattern.lower() in file_path.lower():
                    critical_multiplier *= 1.5
                    break
        
        # Boost score for files without test coverage
        no_test_penalty = 1.0
        for node in result.affected_nodes:
            if not node.is_test_file and not node.has_test_coverage:
                no_test_penalty *= 1.2
        
        # Apply multipliers
        score *= critical_multiplier * no_test_penalty
        
        # Cap score and determine risk level
        score = min(score, 100.0)
        
        if score >= 50:
            risk_level = RiskLevel.CRITICAL
        elif score >= 20:
            risk_level = RiskLevel.HIGH
        elif score >= 5:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return risk_level, score
    
    def _calculate_confidence_score(self, result: ImpactResult) -> float:
        """Calculate confidence score based on analysis completeness."""
        # Start with high confidence
        confidence = 1.0
        
        # Reduce confidence for unresolved symbols
        if result.unresolved_symbols:
            confidence *= (1.0 - len(result.unresolved_symbols) * 0.1)
        
        # Reduce confidence if we couldn't find the target symbol
        if not result.affected_nodes and result.direct_callers == 0:
            confidence *= 0.5
        
        # Ensure confidence is between 0 and 1
        confidence = max(0.0, min(1.0, confidence))
        
        return round(confidence, 2)
    
    def _generate_ai_summary(self, result: ImpactResult) -> str:
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
            for pattern in self.critical_patterns:
                if pattern.lower() in file_path.lower():
                    critical_files.append(file_path)
                    break
        
        if critical_files:
            summary_parts.append(f"Critical paths affected: {', '.join(critical_files[:3])}")
        
        # Add confidence information
        confidence_pct = int(result.confidence_score * 100)
        summary_parts.append(f"Confidence: {confidence_pct}%")
        
        return " ".join(summary_parts)
    
    def _generate_suggested_fix(self, result: ImpactResult) -> str:
        """Generate a suggested fix based on the impact analysis."""
        if result.risk_level == RiskLevel.CRITICAL:
            return "Consider breaking this change into smaller, safer increments. " \
                   "Add comprehensive tests before making this change."
        elif result.risk_level == RiskLevel.HIGH:
            if result.direct_callers > 10:
                return "Introduce the change as optional first (e.g., with a default parameter), " \
                       "then migrate callers incrementally."
            return "Ensure all affected callers are updated and tested."
        elif result.risk_level == RiskLevel.MEDIUM:
            return "Review the affected files and add tests for the changed behavior."
        else:
            return "Low risk change. Proceed with normal testing."
    
    def _parse_diff(self, diff: str) -> List[Dict[str, Any]]:
        """Parse a git diff to extract changed symbols."""
        changed_symbols = []
        lines = diff.split('\n')
        
        current_file = None
        
        for line in lines:
            # Check for file header
            if line.startswith('diff --git'):
                parts = line.split()
                if len(parts) >= 4:
                    current_file = parts[3]  # new file path
            
            # Check for function/class definitions
            elif line.startswith('+') and not line.startswith('+++'):
                if current_file:
                    # Look for function definitions
                    func_match = re.match(r'\+.*(def|function|class|const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
                    if func_match:
                        symbol_type = func_match.group(1)
                        symbol_name = func_match.group(2)
                        
                        # Map to standard types
                        if symbol_type in ['def', 'function']:
                            symbol_type = 'function'
                        elif symbol_type == 'class':
                            symbol_type = 'class'
                        
                        changed_symbols.append({
                            "name": symbol_name,
                            "type": symbol_type,
                            "file": current_file
                        })
        
        return changed_symbols
