from dataclasses import dataclass, field

from models.symbol import Symbol


@dataclass(slots=True)
class SymbolTable:
    """Stores all symbols extracted from a repository."""

    symbols: list[Symbol] = field(default_factory=list)

    def add(self, symbol: Symbol) -> None:
        """Add a symbol to the table."""
        self.symbols.append(symbol)

    def extend(self, symbols: list[Symbol]) -> None:
        """Add multiple symbols."""
        self.symbols.extend(symbols)

    def find_by_name(self, name: str) -> list[Symbol]:
        """Find every symbol with the given name."""
        return [symbol for symbol in self.symbols if symbol.name == name]

    def find_by_kind(self, kind: str) -> list[Symbol]:
        """Find every symbol of a given kind."""
        return [symbol for symbol in self.symbols if symbol.kind == kind]

    def find_by_file(self, file: str) -> list[Symbol]:
        """Find every symbol belonging to a file."""
        return [symbol for symbol in self.symbols if symbol.file == file]

    def __len__(self) -> int:
        return len(self.symbols)