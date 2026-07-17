"""Graph node representation."""

from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class NodeType(Enum):
    """Types of nodes in the graph."""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    FILE = "file"
    MODULE = "module"
    VARIABLE = "variable"
    IMPORT = "import"
    EXPORT = "export"


class RiskLevel(Enum):
    """Risk levels for impact analysis."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class Node:
    """Represents a node in the call graph or import graph."""
    
    id: str
    name: str
    node_type: NodeType
    file_path: str
    language: str
    start_line: int = 0
    end_line: int = 0
    
    # Metadata for risk analysis
    is_entry_point: bool = False
    is_test_file: bool = False
    has_test_coverage: bool = False
    
    # Graph metrics
    in_degree: int = 0  # Number of incoming edges
    out_degree: int = 0  # Number of outgoing edges
    centrality: float = 0.0  # Centrality score
    
    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.id == other.id
    
    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.node_type.value,
            "file_path": self.file_path,
            "language": self.language,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "is_entry_point": self.is_entry_point,
            "is_test_file": self.is_test_file,
            "has_test_coverage": self.has_test_coverage,
            "in_degree": self.in_degree,
            "out_degree": self.out_degree,
            "centrality": self.centrality,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Node":
        """Create node from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            node_type=NodeType(data["type"]),
            file_path=data["file_path"],
            language=data["language"],
            start_line=data.get("start_line", 0),
            end_line=data.get("end_line", 0),
            is_entry_point=data.get("is_entry_point", False),
            is_test_file=data.get("is_test_file", False),
            has_test_coverage=data.get("has_test_coverage", False),
            in_degree=data.get("in_degree", 0),
            out_degree=data.get("out_degree", 0),
            centrality=data.get("centrality", 0.0),
            metadata=data.get("metadata", {}),
        )
