"""Tests for function extraction using the official Tree-sitter Query API."""

from analysis.extractors.function_extractor import FunctionExtractor
from analysis.parser_factory import ParserFactory


def _extract_functions(language: str, source: str) -> list[dict]:
    parser = ParserFactory.get_parser(language)
    tree = parser.parse(source)
    extractor = FunctionExtractor()
    return extractor.extract(parser.language, tree, source, language_name=language)


def test_extract_javascript_functions() -> None:
    source = """
function greet(name) {
    return name;
}

class User {
    save() {
        return true;
    }
}

const run = () => {};
"""

    functions = _extract_functions("javascript", source)
    names = {item["name"] for item in functions}

    assert "greet" in names
    assert "save" in names
    assert "run" in names

    greet = next(item for item in functions if item["name"] == "greet")
    assert greet["start_line"] == 2
    assert greet["end_line"] >= greet["start_line"]


def test_extract_python_functions() -> None:
    source = """
def add(a, b):
    return a + b

class Calculator:
    def multiply(self, a, b):
        return a * b
"""

    functions = _extract_functions("python", source)
    names = {item["name"] for item in functions}

    assert "add" in names
    assert "multiply" in names

    add = next(item for item in functions if item["name"] == "add")
    assert add["start_line"] == 2
    assert add["end_line"] >= add["start_line"]


def test_extract_typescript_functions() -> None:
    source = """
function compute(value: number): number {
    return value * 2;
}

class Service {
    fetch(): void {}
}

const handle = (event: Event) => {};
"""

    functions = _extract_functions("typescript", source)
    names = {item["name"] for item in functions}

    assert "compute" in names
    assert "fetch" in names
    assert "handle" in names

    compute = next(item for item in functions if item["name"] == "compute")
    assert compute["start_line"] == 2
    assert compute["end_line"] >= compute["start_line"]
