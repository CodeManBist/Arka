from dataclasses import dataclass


@dataclass(slots=True)
class Symbol:
    """Represents one symbol extracted from a source file."""

    id: str

    name: str

    kind: str

    language: str

    file: str

    start_line: int

    end_line: int