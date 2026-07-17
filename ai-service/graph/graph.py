"""Graph data structure for call graphs and import graphs."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict, deque
import uuid

from .node import Node, NodeType, RiskLevel
from .edge import Edge, EdgeType


class Graph:
    """
    Directed graph data structure for representing call graphs and import graphs.
    Supports efficient traversal, path finding, and impact analysis.
    """
    
    def __init__(self):
        """Initialize an empty graph."""
        self.nodes: Dict[str, Node] = {}  # node_id -> Node
        self.edges: Dict[str, Edge] = {}  # edge_id -> Edge
        
        # Adjacency lists for efficient traversal
        self.outgoing_edges: Dict[str, List[str]] = defaultdict(list)  # source_id -> [edge_id, ...]
        self.incoming_edges: Dict[str, List[str]] = defaultdict(list)  # target_id -> [edge_id, ...]
        
        # Indexes for fast lookup
        self.file_to_nodes: Dict[str, List[str]] = defaultdict(list)  # file_path -> [node_id, ...]
        self.name_to_nodes: Dict[str, List[str]] = defaultdict(list)  # node_name -> [node_id, ...]
        self.type_to_nodes: Dict[str, List[str]] = defaultdict(list)  # node_type -> [node_id, ...]
    
    def add_node(self, node: Node) -> None:
        """Add a node to the graph."""
        if node.id in self.nodes:
            # Update existing node
            existing = self.nodes[node.id]
            existing.name = node.name
            existing.node_type = node.node_type
            existing.file_path = node.file_path
            existing.language = node.language
            existing.start_line = node.start_line
            existing.end_line = node.end_line
            existing.metadata.update(node.metadata)
        else:
            self.nodes[node.id] = node
            self.file_to_nodes[node.file_path].append(node.id)
            self.name_to_nodes[node.name].append(node.id)
            self.type_to_nodes[node.node_type.value].append(node.id)
    
    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph."""
        if edge.id in self.edges:
            # Update existing edge weight
            existing = self.edges[edge.id]
            existing.weight += edge.weight
        else:
            self.edges[edge.id] = edge
            self.outgoing_edges[edge.source_id].append(edge.id)
            self.incoming_edges[edge.target_id].append(edge.id)
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Get an edge by ID."""
        return self.edges.get(edge_id)
    
    def get_nodes_by_file(self, file_path: str) -> List[Node]:
        """Get all nodes in a specific file."""
        node_ids = self.file_to_nodes.get(file_path, [])
        return [self.nodes[node_id] for node_id in node_ids if node_id in self.nodes]
    
    def get_nodes_by_name(self, name: str) -> List[Node]:
        """Get all nodes with a specific name."""
        node_ids = self.name_to_nodes.get(name, [])
        return [self.nodes[node_id] for node_id in node_ids if node_id in self.nodes]
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[Node]:
        """Get all nodes of a specific type."""
        node_ids = self.type_to_nodes.get(node_type.value, [])
        return [self.nodes[node_id] for node_id in node_ids if node_id in self.nodes]
    
    def get_outgoing_edges(self, node_id: str) -> List[Edge]:
        """Get all outgoing edges from a node."""
        edge_ids = self.outgoing_edges.get(node_id, [])
        return [self.edges[edge_id] for edge_id in edge_ids if edge_id in self.edges]
    
    def get_incoming_edges(self, node_id: str) -> List[Edge]:
        """Get all incoming edges to a node."""
        edge_ids = self.incoming_edges.get(node_id, [])
        return [self.edges[edge_id] for edge_id in edge_ids if edge_id in self.edges]
    
    def get_predecessors(self, node_id: str) -> List[Node]:
        """Get all predecessor nodes (nodes with edges pointing to this node)."""
        incoming_edges = self.get_incoming_edges(node_id)
        predecessors = []
        for edge in incoming_edges:
            predecessor = self.get_node(edge.source_id)
            if predecessor:
                predecessors.append(predecessor)
        return predecessors
    
    def get_successors(self, node_id: str) -> List[Node]:
        """Get all successor nodes (nodes this node points to)."""
        outgoing_edges = self.get_outgoing_edges(node_id)
        successors = []
        for edge in outgoing_edges:
            successor = self.get_node(edge.target_id)
            if successor:
                successors.append(successor)
        return successors
    
    def get_callers(self, node_id: str) -> List[Node]:
        """Get all nodes that call this node (for call graphs)."""
        incoming_edges = self.get_incoming_edges(node_id)
        callers = []
        for edge in incoming_edges:
            if edge.edge_type == EdgeType.CALL:
                caller = self.get_node(edge.source_id)
                if caller:
                    callers.append(caller)
        return callers
    
    def get_callees(self, node_id: str) -> List[Node]:
        """Get all nodes called by this node (for call graphs)."""
        outgoing_edges = self.get_outgoing_edges(node_id)
        callees = []
        for edge in outgoing_edges:
            if edge.edge_type == EdgeType.CALL:
                callee = self.get_node(edge.target_id)
                if callee:
                    callees.append(callee)
        return callees
    
    def get_importers(self, node_id: str) -> List[Node]:
        """Get all nodes that import this node (for import graphs)."""
        incoming_edges = self.get_incoming_edges(node_id)
        importers = []
        for edge in incoming_edges:
            if edge.edge_type == EdgeType.IMPORT:
                importer = self.get_node(edge.source_id)
                if importer:
                    importers.append(importer)
        return importers
    
    def get_imported(self, node_id: str) -> List[Node]:
        """Get all nodes imported by this node (for import graphs)."""
        outgoing_edges = self.get_outgoing_edges(node_id)
        imported = []
        for edge in outgoing_edges:
            if edge.edge_type == EdgeType.IMPORT:
                imported_node = self.get_node(edge.target_id)
                if imported_node:
                    imported.append(imported_node)
        return imported
    
    def bfs(self, start_node_id: str, max_depth: Optional[int] = None) -> Dict[str, int]:
        """
        Breadth-first search from a starting node.
        Returns a dictionary of node_id -> distance from start.
        """
        visited: Dict[str, int] = {}
        queue = deque([(start_node_id, 0)])
        
        while queue:
            current_id, distance = queue.popleft()
            
            if current_id in visited:
                continue
            visited[current_id] = distance
            
            if max_depth is not None and distance >= max_depth:
                continue
            
            successors = self.get_successors(current_id)
            for successor in successors:
                if successor.id not in visited:
                    queue.append((successor.id, distance + 1))
        
        return visited
    
    def dfs(self, start_node_id: str, max_depth: Optional[int] = None) -> List[str]:
        """
        Depth-first search from a starting node.
        Returns a list of visited node IDs.
        """
        visited: Set[str] = set()
        stack = [(start_node_id, 0)]
        result: List[str] = []
        
        while stack:
            current_id, depth = stack.pop()
            
            if current_id in visited:
                continue
            visited.add(current_id)
            result.append(current_id)
            
            if max_depth is not None and depth >= max_depth:
                continue
            
            successors = self.get_successors(current_id)
            for successor in successors:
                if successor.id not in visited:
                    stack.append((successor.id, depth + 1))
        
        return result
    
    def find_paths(
        self, 
        start_node_id: str, 
        end_node_id: str, 
        max_depth: Optional[int] = None
    ) -> List[List[str]]:
        """
        Find all paths from start to end node.
        Returns a list of paths, where each path is a list of node IDs.
        """
        paths: List[List[str]] = []
        
        def dfs_path(
            current_id: str, 
            path: List[str], 
            visited: Set[str],
            depth: int
        ):
            if current_id == end_node_id:
                paths.append(path + [current_id])
                return
            
            if max_depth is not None and depth >= max_depth:
                return
            
            if current_id in visited:
                return
            
            visited.add(current_id)
            successors = self.get_successors(current_id)
            
            for successor in successors:
                dfs_path(successor.id, path + [current_id], visited.copy(), depth + 1)
        
        dfs_path(start_node_id, [], set(), 0)
        return paths
    
    def get_transitive_closure(
        self, 
        start_node_ids: List[str], 
        max_depth: Optional[int] = None,
        edge_types: Optional[List[EdgeType]] = None
    ) -> Set[str]:
        """
        Get all nodes reachable from the start nodes.
        
        Args:
            start_node_ids: List of starting node IDs
            max_depth: Maximum depth to traverse
            edge_types: If specified, only follow edges of these types
            
        Returns:
            Set of all reachable node IDs
        """
        visited: Set[str] = set()
        queue = deque([(node_id, 0) for node_id in start_node_ids])
        
        while queue:
            current_id, depth = queue.popleft()
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            if max_depth is not None and depth >= max_depth:
                continue
            
            outgoing_edges = self.get_outgoing_edges(current_id)
            for edge in outgoing_edges:
                if edge_types is None or edge.edge_type in edge_types:
                    successor = self.get_node(edge.target_id)
                    if successor and successor.id not in visited:
                        queue.append((successor.id, depth + 1))
        
        return visited
    
    def compute_centrality(self) -> Dict[str, float]:
        """
        Compute centrality scores for all nodes using PageRank-like algorithm.
        Returns a dictionary of node_id -> centrality score.
        """
        # Simple implementation: centrality = in_degree + out_degree
        centrality: Dict[str, float] = {}
        
        for node_id, node in self.nodes.items():
            in_degree = len(self.get_incoming_edges(node_id))
            out_degree = len(self.get_outgoing_edges(node_id))
            centrality[node_id] = float(in_degree + out_degree)
        
        # Normalize to 0-1 range
        if centrality:
            max_centrality = max(centrality.values())
            if max_centrality > 0:
                for node_id in centrality:
                    centrality[node_id] /= max_centrality
        
        return centrality
    
    def to_dict(self) -> dict[str, Any]:
        """Convert entire graph to dictionary for serialization."""
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": {edge_id: edge.to_dict() for edge_id, edge in self.edges.items()},
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Graph":
        """Create graph from dictionary."""
        graph = cls()
        
        for node_data in data.get("nodes", {}).values():
            node = Node.from_dict(node_data)
            graph.add_node(node)
        
        for edge_data in data.get("edges", {}).values():
            edge = Edge.from_dict(edge_data)
            graph.add_edge(edge)
        
        return graph
    
    def get_statistics(self) -> dict[str, Any]:
        """Get graph statistics."""
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "files": len(self.file_to_nodes),
            "languages": len(set(
                node.language for node in self.nodes.values()
            )),
            "node_types": {
                node_type.value: count 
                for node_type, count in self.type_to_nodes.items()
            },
            "edge_types": {
                edge_type.value: sum(
                    1 for edge in self.edges.values() 
                    if edge.edge_type == edge_type
                )
                for edge_type in EdgeType
            },
        }
