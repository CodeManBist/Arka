from analysis.parsers.typescript_parser import TypeScriptParser
from analysis.parsers.javascript_parser import JavaScriptParser
from analysis.parsers.python_parser import PythonParser


class ParserFactory:

    @staticmethod
    def get_parser(language: str):

        language = language.lower()

        if language == "typescript":
            return TypeScriptParser()

        if language == "javascript":
            return JavaScriptParser()

        if language == "python":
            return PythonParser()

        raise Exception(f"Unsupported language: {language}")