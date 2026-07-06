"""Parse repositories and build a symbol index using Tree-sitter queries."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from analysis.extractors.class_extractor import ClassExtractor
from analysis.extractors.function_extractor import FunctionExtractor
from analysis.parser_factory import ParserFactory
from analysis.scanner import RepositoryScanner


class RepositoryParser:
    """Orchestrate repository scanning, parsing, and symbol extraction."""

    def __init__(self) -> None:
        self.scanner = RepositoryScanner()
        self.function_extractor = FunctionExtractor()
        self.class_extractor = ClassExtractor()

    def parse_repository(self, repository_path: str) -> dict[str, Any]:
        """
        Parse every supported source file in a repository.

        Pipeline:
            RepositoryScanner -> ParserFactory -> FunctionExtractor -> ClassExtractor
        """
        files = self.scanner.scan(repository_path)

        repository: dict[str, Any] = {
            "repository": Path(repository_path).name,
            "total_files": len(files),
            "files": [],
        }

        for file in files:
            language_name = file["language"]
            parser = ParserFactory.get_parser(language_name)

            source = Path(file["path"]).read_text(encoding="utf-8", errors="ignore")
            tree = parser.parse(source)

            functions = self.function_extractor.extract(
                parser.language,
                tree,
                source,
                language_name=language_name,
            )
            classes = self.class_extractor.extract(
                parser.language,
                tree,
                source,
                language_name=language_name,
            )

            repository["files"].append(
                {
                    "path": file["path"],
                    "language": language_name,
                    "functions": functions,
                    "classes": classes,
                }
            )

        return repository
