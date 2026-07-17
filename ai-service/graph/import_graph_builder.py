"""Build import graphs from parsed repository data."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set
import re
from pathlib import Path

from .graph import Graph
from .node import Node, NodeType
from .edge import Edge, EdgeType

logger = logging.getLogger(__name__)


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
        
        logger.info(f"Created {len(self.graph.nodes)} file nodes")
        
        # Second pass: Create import edges
        self._create_import_edges(repository_data)
        
        logger.info(f"Created {len(self.graph.edges)} import edges")
        
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
        # Build a mapping of all files by their path and name
        file_info: Dict[str, Dict[str, Any]] = {}
        for file_data in repository_data.get("files", []):
            file_path = file_data["path"]
            file_name = Path(file_path).name
            file_stem = Path(file_path).stem
            
            file_info[file_path] = {
                "path": file_path,
                "name": file_name,
                "stem": file_stem,
                "language": file_data["language"],
                "exports": [e.get("name", "") for e in file_data.get("exports", [])],
            }
        
        logger.debug(f"File info: {len(file_info)} files indexed")
        
        # Create edges based on imports
        for file_data in repository_data.get("files", []):
            file_path = file_data["path"]
            file_node_id = self._generate_file_node_id(file_path)
            
            for imp in file_data.get("imports", []):
                import_path = imp.get("path", "")
                import_name = imp.get("name", "")
                named_imports = imp.get("named_imports", [])
                
                if not import_path:
                    continue
                
                # Try to resolve the import path to a file
                imported_file_path = self._resolve_import_path(
                    import_path, file_path, file_info
                )
                
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
                                "import_path": import_path,
                                "import_name": import_name,
                                "named_imports": named_imports,
                            }
                        )
                        self.graph.add_edge(edge)
                        logger.debug(f"  Created import edge: {file_path} -> {imported_file_path}")
                    else:
                        logger.debug(f"  Target node not found: {imported_node_id}")
                else:
                    logger.debug(f"  Could not resolve import: {import_path} from {file_path}")
    
    def _resolve_import_path(
        self,
        import_path: str,
        caller_file_path: str,
        file_info: Dict[str, Dict[str, Any]]
    ) -> Optional[str]:
        """Resolve an import path to an actual file path."""
        import_path = import_path.strip()
        
        # Remove quotes if present
        if import_path.startswith('"') or import_path.startswith("'"):
            import_path = import_path[1:-1]
        
        # Handle empty path
        if not import_path:
            return None
        
        logger.debug(f"  Resolving import: {import_path} from {caller_file_path}")
        
        # Case 1: Relative import (starts with .)
        if import_path.startswith("."):
            caller_dir = Path(caller_file_path).parent
            
            # Handle ./
            if import_path.startswith("./"):
                import_path = import_path[2:]
            elif import_path.startswith("."):
                import_path = import_path[1:]
            
            # Try to find the file
            candidate_path = (caller_dir / import_path).resolve()
            
            # Try different extensions
            for ext in ["", ".js", ".ts", ".jsx", ".tsx", ".py"]:
                test_path = str(candidate_path) + ext
                if test_path in file_info:
                    logger.debug(f"    Resolved relative import to: {test_path}")
                    return test_path
                
                # Also try with index files
                test_index_path = str(Path(test_path).parent / "index" + ext)
                if test_index_path in file_info:
                    logger.debug(f"    Resolved relative import to index: {test_index_path}")
                    return test_index_path
            
            # Try without the first part of the path
            parts = import_path.split("/")
            for i in range(len(parts)):
                partial_path = Path(*parts[i:])
                for ext in ["", ".js", ".ts", ".jsx", ".tsx", ".py"]:
                    test_path = str(caller_dir / partial_path) + ext
                    if test_path in file_info:
                        logger.debug(f"    Resolved relative import (partial) to: {test_path}")
                        return test_path
        
        # Case 2: Absolute import (no leading ., no /)
        elif "/" not in import_path and "\\" not in import_path:
            # This is a module name, try to find matching files
            import_stem = Path(import_path).stem
            
            # Look for files with matching name
            for file_path, info in file_info.items():
                file_stem = info["stem"]
                
                # Direct match
                if file_stem == import_stem or file_stem == import_path:
                    logger.debug(f"    Resolved module import to: {file_path}")
                    return file_path
                
                # Match with extension
                if Path(file_path).name == import_path:
                    logger.debug(f"    Resolved module import (by name) to: {file_path}")
                    return file_path
                
                # Check if this file exports the imported name
                if import_path in info.get("exports", []):
                    logger.debug(f"    Resolved module import (by export) to: {file_path}")
                    return file_path
            
            # Try to find index files
            for ext in [".js", ".ts", ".jsx", ".tsx", ".py"]:
                index_path = f"{import_path}/index{ext}"
                if index_path in file_info:
                    logger.debug(f"    Resolved module import to index: {index_path}")
                    return index_path
                
                # Also try without leading /
                index_path = f"{import_path.replace('/', Path.sep)}index{ext}"
                if index_path in file_info:
                    logger.debug(f"    Resolved module import to index (normalized): {index_path}")
                    return index_path
        
        # Case 3: Path import (starts with / or contains /)
        else:
            # Try to find the file directly
            for file_path in file_info:
                if import_path in file_path or file_path.endswith(import_path):
                    logger.debug(f"    Resolved path import to: {file_path}")
                    return file_path
            
            # Try with extensions
            for ext in [".js", ".ts", ".jsx", ".tsx", ".py"]:
                test_path = import_path + ext
                if test_path in file_info:
                    logger.debug(f"    Resolved path import with extension to: {test_path}")
                    return test_path
        
        logger.debug(f"    Could not resolve import: {import_path}")
        return None
    
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
        
        if Path(file_path).name == "index.js" and import_path.endswith("/index"):
            return True
        
        if Path(file_path).name == "index.ts" and import_path.endswith("/index"):
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
