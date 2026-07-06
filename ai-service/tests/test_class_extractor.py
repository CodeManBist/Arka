"""Tests for class extraction using the official Tree-sitter Query API."""

from analysis.extractors.class_extractor import ClassExtractor
from analysis.parser_factory import ParserFactory


def _extract_classes(language: str, source: str) -> list[dict]:
    parser = ParserFactory.get_parser(language)
    tree = parser.parse(source)
    extractor = ClassExtractor()
    return extractor.extract(parser.language, tree, source, language_name=language)


def test_extract_javascript_classes() -> None:
    source = """
class User {
    constructor() {}
}
"""

    classes = _extract_classes("javascript", source)

    assert len(classes) == 1
    assert classes[0]["name"] == "User"
    assert classes[0]["start_line"] == 2


def test_extract_python_classes() -> None:
    source = """
class Animal:
    pass
"""

    classes = _extract_classes("python", source)

    assert len(classes) == 1
    assert classes[0]["name"] == "Animal"
    assert classes[0]["start_line"] == 2


def test_extract_typescript_classes() -> None:
    source = """
class Account {
    balance = 0;
}

interface Repository {
    find(id: string): void;
}
"""

    classes = _extract_classes("typescript", source)
    names = {item["name"] for item in classes}

    assert "Account" in names
    assert "Repository" in names
