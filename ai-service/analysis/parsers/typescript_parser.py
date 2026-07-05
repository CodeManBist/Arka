from tree_sitter import Language, Parser
import tree_sitter_typescript

from .base_parser import BaseParser


class TypeScriptParser(BaseParser):

    def __init__(self):
        language = Language(tree_sitter_typescript.language_typescript())
        self.parser = Parser(language)

    def parse(self, source: str):
        return self.parser.parse(source.encode("utf8"))