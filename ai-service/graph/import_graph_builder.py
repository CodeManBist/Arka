"""Build import graphs from parsed repository data."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
import re

from .graph import Graph
from .node import Node, NodeType
from .edge import Edge, EdgeType


class ImportGraphBuilder:
    """
    Builds an import graph from repository parsing results.
    
    The import graph represents file-to-file dependencies.
    Nodes are files/modules.
    Edges represent import relationships between files.
    """
    
    def __init__(self):
        """Initialize the import graph builder."""
        self.graph = Graph()
    
    def build_from_repository(self, repository_data: dict[str, Any]) -> Graph:
        """
        Build an import graph from repository parsing results.
        
        Args:
            repository_data: Dictionary containing repository parsing results
                with 'files' key containing list of file data
                
        Returns:
            Graph containing the import graph
        """
        self.graph = Graph()
        
        # First pass: Create file nodes
        self._create_file_nodes(repository_data)
        
        # Second pass: Create import edges
        self._create_import_edges(repository_data)
        
        # Compute graph metrics
        self._compute_graph_metrics()
        
        return self.graph
    
    def _create_file_nodes(self, repository_data: dict[str, Any]) -> None:
        """Create nodes for all files."""
        for file_data in repository_data.get("files", []):
            file_path = file_data["path"]
            language = file_data["language"]
            
            # Create a file node
            node_id = self._generate_file_node_id(file_path)
            node = Node(
                id=node_id,
                name=Path(file_path).name,
                node_type=NodeType.FILE,
                file_path=file_path,
                language=language,
                metadata={
                    "total_functions": len(file_data.get("functions", [])),
                    "total_classes": len(file_data.get("classes", [])),
                    "total_imports": len(file_data.get("imports", [])),
                    "total_exports": len(file_data.get("exports", [])),
                }
            )
            self.graph.add_node(node)
    
    def _create_import_edges(self, repository_data: dict[str, Any]) -> None:
        """Create edges for import relationships."""
        # Build a mapping of import paths to file paths
        import_path_to_file: Dict[str, str] = {}
        
        for file_data in repository_data.get("files", []):
            file_path = file_data["path"]
            for imp in file_data.get("imports", []):
                import_path = imp.get("path", "")
                if import_path:
                    import_path_to_file[import_path] = file_path
        
        # Create edges based on imports
        for file_data in repository_data.get("files", []):
            file_path = file_data["path"]
            file_node_id = self._generate_file_node_id(file_path)
            
            for imp in file_data.get("imports", []):
                import_path = imp.get("path", "")
                if not import_path:
                    continue
                
                # Try to find the imported file
                imported_file_path = import_path_to_file.get(import_path)
                
                # Handle relative imports
                if not imported_file_path and import_path.startswith("."):
                    # Resolve relative import
                    import_dir = Path(file_path).parent
                    resolved_path = (import_dir / import_path).resolve()
                    imported_file_path = str(resolved_path)
                
                # Handle absolute imports (try to find matching file)
                if not imported_file_path:
                    # Look for files that match the import path
                    for other_file_data in repository_data.get("files", []):
                        other_file_path = other_file_data["path"]
                        if self._file_matches_import(other_file_path, import_path):
                            imported_file_path = other_file_path
                            break
                
                if imported_file_path:
                    imported_node_id = self._generate_file_node_id(imported_file_path)
                    
                    # Only create edge if both nodes exist
                    if imported_node_id in self.graph.nodes:
                        edge_id = f"{file_node_id}->{imported_node_id}:import"
                        edge = Edge(
                            id=edge_id,
                            source_id=file_node_id,
                            target_id=imported_node_id,
                            edge_type=EdgeType.IMPORT,
                            metadata={
                                "source_file": file_path,
                                "target_file": imported_file_path,
                                "import_path": import_path
                            }
                        )
                        self.graph.add_edge(edge)
    
    def _file_matches_import(self, file_path: str, import_path: str) -> bool:
        """Check if a file path matches an import path."""
        # Remove file extension for comparison
        file_stem = Path(file_path).stem
        import_stem = Path(import_path).stem
        
        # Direct match
        if file_stem == import_stem:
            return True
        
        # Match with .js/.ts/.py extensions
        file_without_ext = Path(file_path).with_suffix("")
        if str(file_without_ext) == import_path:
            return True
        
        # Handle index files
        if Path(file_path).name == "index.py" and import_path.endswith("/index"):
            return True
        
        return False
    
    def _compute_graph_metrics(self) -> None:
        """Compute metrics for all nodes in the graph."""
        # Update in_degree and out_degree for all nodes
        for node_id, node in self.graph.nodes.items():
            node.in_degree = len(self.graph.get_incoming_edges(node_id))
            node.out_degree = len(self.graph.get_outgoing_edges(node_id))
        
        # Compute centrality
        centrality = self.graph.compute_centrality()
        for node_id, score in centrality.items():
            if node_id in self.graph.nodes:
                self.graph.nodes[node_id].centrality = score
        
        # Mark entry point files (files with no incoming imports)
        for node in self.graph.nodes.values():
            if node.in_degree == 0:
                node.is_entry_point = True
    
    def _generate_file_node_id(self, file_path: str) -> str:
        """Generate a unique file node ID."""
        # Normalize path for use in ID
        normalized_path = file_path.replace("/", "_").replace("\\", "_")
        return f"file:{normalized_path}"


# Import Path for compatibility
from pathlib import Path
