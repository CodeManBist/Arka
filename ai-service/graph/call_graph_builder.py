"""Build call graphs from parsed repository data."""

from __future__ import annotations

import re
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path
import uuid

from .graph import Graph
from .node import Node, NodeType
from .edge import Edge, EdgeType

logger = logging.getLogger(__name__)


class CallGraphBuilder:
    """
    Builds a call graph from repository parsing results.
    
    The call graph represents function/method calls between symbols.
    Nodes are functions, methods, or classes.
    Edges represent calls from one symbol to another.
    """
    
    def __init__(self):
        """Initialize the call graph builder."""
        self.graph = Graph()
        self.source_cache: Dict[str, str] = {}  # file_path -> source code
        
        # Track which functions exist for reference resolution
        self.function_names: Dict[str, Set[str]] = {}  # file_path -> set of function names
        self.class_names: Dict[str, Set[str]] = {}  # file_path -> set of class names
        self.imported_symbols: Dict[str, Dict[str, str]] = {}  # file_path -> {symbol_name: source_file}
    
    def build_from_repository(self, repository_data: dict[str, Any]) -> Graph:
        """
        Build a call graph from repository parsing results.
        
        Args:
            repository_data: Dictionary containing repository parsing results
                with 'files' key containing list of file data
                
        Returns:
            Graph containing the call graph
        """
        self.graph = Graph()
        self.source_cache = {}
        self.function_names = {}
        self.class_names = {}
        self.imported_symbols = {}
        
        logger.info(f"Building call graph for repository with {len(repository_data.get('files', []))} files")
        
        # First pass: Create nodes for all functions, classes, and methods
        self._create_symbol_nodes(repository_data)
        
        logger.info(f"Created {len(self.graph.nodes)} symbol nodes")
        
        # Second pass: Build import mapping
        self._build_import_mapping(repository_data)
        
        # Third pass: Create call edges by analyzing function bodies
        self._create_call_edges(repository_data)
        
        logger.info(f"Created {len(self.graph.edges)} call edges")
        
        # Fourth pass: Create inheritance edges
        self._create_inheritance_edges(repository_data)
        
        # Compute graph metrics
        self._compute_graph_metrics()
        
        return self.graph
    
    def _create_symbol_nodes(self, repository_data: dict[str, Any]) -> None:
        """Create nodes for all functions, classes, and methods."""
        for file_data in repository_data.get("files", []):
            file_path = file_data["path"]
            language = file_data["language"]
            
            # Track function names for this file
            self.function_names[file_path] = set()
            self.class_names[file_path] = set()
            
            # Cache source code for AST-based call extraction
            try:
                self.source_cache[file_path] = Path(file_path).read_text(
                    encoding="utf-8", errors="ignore"
                )
            except Exception:
                self.source_cache[file_path] = ""
            
            # Create function nodes
            for func in file_data.get("functions", []):
                node_id = self._generate_node_id(
                    file_path, 
                    func["name"], 
                    NodeType.FUNCTION
                )
                has_body = bool(func.get("body", ""))
                logger.debug(f"  Function node '{func['name']}': has_body={has_body}, body_len={len(func.get('body', ''))}")
                
                node = Node(
                    id=node_id,
                    name=func["name"],
                    node_type=NodeType.FUNCTION,
                    file_path=file_path,
                    language=language,
                    start_line=func.get("start_line", 0),
                    end_line=func.get("end_line", 0),
                    metadata={"original": func, "body": func.get("body", "")}
                )
                self.graph.add_node(node)
                self.function_names[file_path].add(func["name"])
            
            # Create class nodes
            for cls in file_data.get("classes", []):
                node_id = self._generate_node_id(
                    file_path, 
                    cls["name"], 
                    NodeType.CLASS
                )
                node = Node(
                    id=node_id,
                    name=cls["name"],
                    node_type=NodeType.CLASS,
                    file_path=file_path,
                    language=language,
                    start_line=cls.get("start_line", 0),
                    end_line=cls.get("end_line", 0),
                    metadata={"original": cls, "body": cls.get("body", "")}
                )
                self.graph.add_node(node)
                self.class_names[file_path].add(cls["name"])
                
                # Create method nodes for each class
                for method in cls.get("methods", []):
                    method_node_id = self._generate_node_id(
                        file_path, 
                        f"{cls['name']}.{method['name']}", 
                        NodeType.METHOD
                    )
                    method_node = Node(
                        id=method_node_id,
                        name=method["name"],
                        node_type=NodeType.METHOD,
                        file_path=file_path,
                        language=language,
                        start_line=method.get("start_line", 0),
                        end_line=method.get("end_line", 0),
                        metadata={
                            "original": method,
                            "class_name": cls["name"],
                            "body": method.get("body", "")
                        }
                    )
                    self.graph.add_node(method_node)
    
    def _build_import_mapping(self, repository_data: dict[str, Any]) -> None:
        """Build a mapping of imported symbols to their source files."""
        for file_data in repository_data.get("files", []):
            file_path = file_data["path"]
            self.imported_symbols[file_path] = {}
            
            for imp in file_data.get("imports", []):
                # Handle different import formats
                import_name = imp.get("name", "")
                import_path = imp.get("path", "")
                
                if import_name and import_path:
                    self.imported_symbols[file_path][import_name] = import_path
                
                # Handle named imports
                for named_import in imp.get("named_imports", []):
                    self.imported_symbols[file_path][named_import] = import_path
    
    def _create_call_edges(self, repository_data: dict[str, Any]) -> None:
        """Create edges for function/method calls using AST-based extraction."""
        logger.info("Creating call edges...")
        
        for file_data in repository_data.get("files", []):
            file_path = file_data["path"]
            language = file_data["language"]
            
            # Get source code for this file
            source = self.source_cache.get(file_path, "")
            if not source:
                logger.warning(f"  No source cached for {file_path}")
                continue
            
            # Extract calls using AST-based approach
            calls = self._extract_calls_from_source(source, file_path, language, file_data)
            
            logger.info(f"  File {file_path}: extracted {len(calls)} calls")
            if len(calls) > 0:
                logger.debug(f"    Sample calls: {calls[:3]}")
            
            for call in calls:
                caller_name = call.get("caller", "")
                callee_name = call.get("callee", "")
                line_number = call.get("line", 0)
                
                if not caller_name or not callee_name:
                    continue
                
                # Find the caller node
                caller_nodes = self._find_caller_node(caller_name, file_path)
                
                # Find the callee node
                callee_nodes = self._resolve_callee(callee_name, file_path)
                
                # Create edges between all matching caller-callee pairs
                for caller_node in caller_nodes:
                    for callee_node in callee_nodes:
                        edge_id = f"{caller_node.id}->{callee_node.id}:call"
                        edge = Edge(
                            id=edge_id,
                            source_id=caller_node.id,
                            target_id=callee_node.id,
                            edge_type=EdgeType.CALL,
                            line_number=line_number,
                            metadata={
                                "caller_file": file_path,
                                "callee_file": callee_node.file_path
                            }
                        )
                        self.graph.add_edge(edge)
    
    def _extract_calls_from_source(
        self,
        source: str,
        file_path: str,
        language: str,
        file_data: dict[str, Any]
    ) -> List[dict[str, Any]]:
        """Extract function/method calls from source code using AST + regex hybrid."""
        calls = []
        
        # First, try to extract calls from function bodies if available
        for func in file_data.get("functions", []):
            func_name = func.get("name", "")
            func_body = func.get("body", "")
            start_line = func.get("start_line", 0)
            
            if func_body:
                # Extract called functions from the body using improved regex
                called_functions = self._extract_called_functions_from_body(
                    func_body, language, start_line
                )
                for callee, line in called_functions:
                    calls.append({
                        "caller": func_name,
                        "callee": callee,
                        "line": line
                    })
            else:
                logger.debug(f"    Function '{func_name}' has no body")
        
        # Extract calls from class methods
        for cls in file_data.get("classes", []):
            class_name = cls.get("name", "")
            for method in cls.get("methods", []):
                method_name = method.get("name", "")
                method_body = method.get("body", "")
                start_line = method.get("start_line", 0)
                
                if method_body:
                    called_functions = self._extract_called_functions_from_body(
                        method_body, language, start_line
                    )
                    for callee, line in called_functions:
                        calls.append({
                            "caller": f"{class_name}.{method_name}",
                            "callee": callee,
                            "line": line
                        })
                else:
                    logger.debug(f"    Method '{class_name}.{method_name}' has no body")
        
        return calls
    
    def _extract_called_functions_from_body(
        self,
        code: str,
        language: str,
        base_line: int
    ) -> List[Tuple[str, int]]:
        """Extract function names that are being called from code."""
        called_functions = []
        lines = code.split('\n')
        
        # Improved patterns for different languages
        if language == "python":
            patterns = [
                # function_name(
                r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                # self.method_name(
                r'\b(self\.)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                # obj.method_name(
                r'\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                # ClassName(
                r'\b([A-Z][a-zA-Z0-9_]*)\s*\(',
            ]
        elif language in ["javascript", "typescript"]:
            patterns = [
                # function_name(
                r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                # this.method_name(
                r'\b(this\.)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                # obj.method_name(
                r'\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                # new ClassName(
                r'\bnew\s+([A-Z][a-zA-Z0-9_]*)\s*\(',
                # ClassName(
                r'\b([A-Z][a-zA-Z0-9_]*)\s*\(',
            ]
        else:
            patterns = [
                r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                r'\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            ]
        
        for line_num, line in enumerate(lines, start=base_line):
            for pattern in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    # Extract the function name from the match
                    groups = match.groups()
                    for group in groups:
                        if group and group != "self" and group != "this" and group != "new":
                            # Filter out common false positives
                            if group not in ['if', 'for', 'while', 'with', 'try', 'catch', 'finally', 
                                            'return', 'break', 'continue', 'import', 'from', 'as',
                                            'def', 'class', 'function', 'const', 'let', 'var', 'export',
                                            'default', 'new', 'delete', 'typeof', 'instanceof', 'void']:
                                called_functions.append((group, line_num))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_calls = []
        for func, line in called_functions:
            if func not in seen:
                seen.add(func)
                unique_calls.append((func, line))
        
        return unique_calls
    
    def _find_caller_node(self, caller_name: str, file_path: str) -> List[Node]:
        """Find the caller node in the graph."""
        nodes = []
        
        # First, try to find exact match in the same file
        same_file_nodes = [
            node for node in self.graph.nodes.values()
            if node.file_path == file_path and node.name == caller_name
        ]
        nodes.extend(same_file_nodes)
        
        # Check if it's a method call (ClassName.methodName)
        if "." in caller_name:
            parts = caller_name.split(".")
            if len(parts) >= 2:
                # Try to find as method
                method_nodes = [
                    node for node in self.graph.nodes.values()
                    if node.node_type == NodeType.METHOD and 
                    node.name == parts[-1] and
                    node.file_path == file_path
                ]
                nodes.extend(method_nodes)
        
        # Fallback: search all nodes
        if not nodes:
            all_nodes = self.graph.get_nodes_by_name(caller_name)
            nodes.extend(all_nodes)
        
        return nodes
    
    def _resolve_callee(self, callee_name: str, caller_file: str) -> List[Node]:
        """Resolve a callee name to actual nodes in the graph."""
        nodes = []
        
        # First, try to find exact match in the same file
        same_file_nodes = [
            node for node in self.graph.nodes.values()
            if node.file_path == caller_file and node.name == callee_name
        ]
        nodes.extend(same_file_nodes)
        
        # Check if it's a method call (obj.method)
        if "." in callee_name:
            parts = callee_name.split(".")
            if len(parts) == 2:
                class_name, method_name = parts
                method_nodes = [
                    node for node in self.graph.nodes.values()
                    if node.node_type == NodeType.METHOD and 
                    node.metadata.get("class_name") == class_name and
                    node.name == method_name
                ]
                nodes.extend(method_nodes)
        
        # Check imported symbols
        if caller_file in self.imported_symbols:
            if callee_name in self.imported_symbols[caller_file]:
                import_path = self.imported_symbols[caller_file][callee_name]
                imported_nodes = [
                    node for node in self.graph.nodes.values()
                    if node.file_path == import_path and node.name == callee_name
                ]
                nodes.extend(imported_nodes)
        
        # Fallback: search all files for the function name
        if not nodes:
            all_nodes = self.graph.get_nodes_by_name(callee_name)
            nodes.extend(all_nodes)
        
        return nodes
    
    def _create_inheritance_edges(self, repository_data: dict[str, Any]) -> None:
        """Create edges for class inheritance."""
        for file_data in repository_data.get("files", []):
            for cls in file_data.get("classes", []):
                class_name = cls.get("name", "")
                base_classes = cls.get("base_classes", [])
                
                for base_class in base_classes:
                    # Find the class node
                    class_nodes = self.graph.get_nodes_by_name(class_name)
                    base_nodes = self.graph.get_nodes_by_name(base_class)
                    
                    for class_node in class_nodes:
                        for base_node in base_nodes:
                            edge_id = f"{class_node.id}->{base_node.id}:inheritance"
                            edge = Edge(
                                id=edge_id,
                                source_id=class_node.id,
                                target_id=base_node.id,
                                edge_type=EdgeType.INHERITANCE,
                                metadata={
                                    "class_file": class_node.file_path,
                                    "base_file": base_node.file_path
                                }
                            )
                            self.graph.add_edge(edge)
    
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
        
        # Mark test files
        for node in self.graph.nodes.values():
            if "test" in node.file_path.lower() or "spec" in node.file_path.lower():
                node.is_test_file = True
    
    def _generate_node_id(self, file_path: str, name: str, node_type: NodeType) -> str:
        """Generate a unique node ID."""
        # Sanitize the name for use in ID
        safe_name = re.sub(r'[^a-zA-Z0-9_.]', '_', name)
        return f"{file_path}:{node_type.value}:{safe_name}"
