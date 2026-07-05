from tree_sitter import Language, Parser
import tree_sitter_javascript

from .base_parser import BaseParser


class JavaScriptParser(BaseParser):

    def __init__(self):
        language = Language(tree_sitter_javascript.language())
        self.parser = Parser(language)

    def parse(self, source: str):
        return self.parser.parse(source.encode("utf8"))