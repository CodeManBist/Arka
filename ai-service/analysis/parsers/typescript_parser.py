from tree_sitter import Language, Parser
import tree_sitter_typescript

from .base_parser import BaseParser


class TypeScriptParser(BaseParser):

    def __init__(self) -> None:
        self._language = Language(tree_sitter_typescript.language_typescript())
        self.parser = Parser(self._language)

    @property
    def language(self) -> Language:
        return self._language

    def parse(self, source: str):
        return self.parser.parse(source.encode("utf8"))