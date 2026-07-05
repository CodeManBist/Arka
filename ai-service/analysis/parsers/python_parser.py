from tree_sitter import Language, Parser
import tree_sitter_python

from .base_parser import BaseParser


class PythonParser(BaseParser):

    def __init__(self):
        language = Language(tree_sitter_python.language())
        self.parser = Parser(language)

    def parse(self, source: str):
        return self.parser.parse(source.encode("utf8"))