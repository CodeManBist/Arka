"""Parse repositories and build a symbol index using Tree-sitter queries."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from analysis.extractors.class_extractor import ClassExtractor
from analysis.extractors.function_extractor import FunctionExtractor
from analysis.extractors.import_extractor import ImportExtractor
from analysis.parser_factory import ParserFactory
from analysis.scanner import RepositoryScanner
from analysis.extractors.export_extractor import ExportExtractor
from analysis.extractors.variable_extractor import VariableExtractor
class RepositoryParser:
    """Orchestrate repository scanning, parsing, and symbol extraction."""

    def __init__(self) -> None:
        self.scanner = RepositoryScanner()
        self.variable_extractor = VariableExtractor()
        self.export_extractor = ExportExtractor()
        self.function_extractor = FunctionExtractor()
        self.class_extractor = ClassExtractor()
        self.import_extractor = ImportExtractor()

    def parse_repository(self, repository_path: str) -> dict[str, Any]:
        """
        Parse every supported source file in a repository.

        Pipeline:
            RepositoryScanner
                    ↓
            ParserFactory
                    ↓
            FunctionExtractor
                    ↓
            ClassExtractor
                    ↓
            ImportExtractor
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

            source = Path(file["path"]).read_text(
                encoding="utf-8",
                errors="ignore",
            )

            tree = parser.parse(source)

            functions = self.function_extractor.extract(
                language=parser.language,
                tree=tree,
                source=source,
                language_name=language_name,
            )

            classes = self.class_extractor.extract(
                language=parser.language,
                tree=tree,
                source=source,
                language_name=language_name,
            )

            imports = self.import_extractor.extract(
                language=parser.language,
                tree=tree,
                source=source,
                language_name=language_name,
            )

            exports = self.export_extractor.extract(
                language=parser.language,
                tree=tree,
                source=source,
                language_name=language_name,
            )

            variables = self.variable_extractor.extract(
                language=parser.language,
                tree=tree,
                source=source,
                language_name=language_name,
            )

            repository["files"].append(
                {
                    "path": file["path"],
                    "language": language_name,
                    "functions": functions,
                    "classes": classes,
                    "imports": imports,
                    "exports": exports,
                    "variables": variables,
                }
            )

        return repository