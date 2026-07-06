from abc import ABC, abstractmethod

from tree_sitter import Language, Tree


class BaseParser(ABC):
    """Abstract parser backed by the official py-tree-sitter API."""

    @property
    @abstractmethod
    def language(self) -> Language:
        """Return the Tree-sitter Language used by this parser."""

    @abstractmethod
    def parse(self, source: str) -> Tree:
        """Parse source code and return a syntax tree."""
        pass