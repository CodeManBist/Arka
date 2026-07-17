"""Graph edge representation."""

from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class EdgeType(Enum):
    """Types of edges in the graph."""
    CALL = "call"  # Function/method calls another function
    IMPORT = "import"  # File imports another file/module
    INHERITANCE = "inheritance"  # Class inherits from another class
    USAGE = "usage"  # Variable/function usage
    EXPORT = "export"  # Export relationship


@dataclass(slots=True)
class Edge:
    """Represents an edge between two nodes in the graph."""
    
    id: str
    source_id: str  # Source node ID
    target_id: str  # Target node ID
    edge_type: EdgeType
    weight: float = 1.0  # Edge weight (default 1.0)
    line_number: int = 0  # Line number where this edge occurs
    
    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        return self.id == other.id
    
    def to_dict(self) -> dict[str, Any]:
        """Convert edge to dictionary for serialization."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.edge_type.value,
            "weight": self.weight,
            "line_number": self.line_number,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Edge":
        """Create edge from dictionary."""
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            edge_type=EdgeType(data["type"]),
            weight=data.get("weight", 1.0),
            line_number=data.get("line_number", 0),
            metadata=data.get("metadata", {}),
        )
    
    def generate_id(self, source_id: str, target_id: str, edge_type: EdgeType) -> str:
        """Generate a unique edge ID."""
        return f"{source_id}->{target_id}:{edge_type.value}"
