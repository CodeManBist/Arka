from dataclasses import dataclass


@dataclass(slots=True)
class Node:
    """Represents a node in the repository graph."""

    id: str

    kind: str

    name: str

    language: str

    file: str