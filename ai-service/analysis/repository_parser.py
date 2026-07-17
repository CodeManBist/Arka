"""Parse repositories and build a symbol index using Tree-sitter queries."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Optional, Tuple

from analysis.extractors.class_extractor import ClassExtractor
from analysis.extractors.function_extractor import FunctionExtractor
from analysis.extractors.import_extractor import ImportExtractor
from analysis.parser_factory import ParserFactory
from analysis.scanner import RepositoryScanner
from analysis.extractors.export_extractor import ExportExtractor
from analysis.extractors.variable_extractor import VariableExtractor
from analysis.builders.symbol_table_builder import SymbolTableBuilder
from analysis.repository_manager import (
    RepositoryManager,
    get_repository_manager,
    InvalidRepositoryError,
    CloneError,
)


class RepositoryParser:
    """Orchestrate repository scanning, parsing, and symbol extraction."""

    def __init__(self, github_token: Optional[str] = None) -> None:
        self.scanner = RepositoryScanner()
        self.variable_extractor = VariableExtractor()
        self.export_extractor = ExportExtractor()
        self.function_extractor = FunctionExtractor()
        self.class_extractor = ClassExtractor()
        self.import_extractor = ImportExtractor()
        self.symbol_table_builder = SymbolTableBuilder()
        self.repository_manager = get_repository_manager(github_token)
        self._temp_dirs: list[Path] = []  # Track temp dirs for cleanup

    def parse_repository(
        self, 
        repository_input: str,
        cleanup: bool = True
    ) -> dict[str, Any]:
        """
        Parse every supported source file in a repository.

        This method handles both local paths and GitHub URLs:
        - Local paths: Parse directly
        - GitHub URLs: Clone to temp dir, parse, then cleanup

        Pipeline:
            RepositoryManager (resolve input)
                    
            
            
            
            
->
            RepositoryScanner
                    
            
            
            
            
->
            ParserFactory
                    
            
            
            
            
->
            FunctionExtractor
                    
            
            
            
            
->
            ClassExtractor
                    
            
            
            
            
->
            ImportExtractor

        Args:
            repository_input: Local path or GitHub URL
            cleanup: Whether to clean up temporary directories after parsing
            
        Returns:
            Dictionary with 'repository' and 'symbol_table' keys
            
        Raises:
            InvalidRepositoryError: If the input is invalid
            CloneError: If cloning fails
            Exception: If parsing fails
        """
        # Resolve the repository input to a local path
        resolved_path, is_temporary, original_url = self.repository_manager.resolve_repository(
            repository_input
        )
        
        try:
            # Validate the repository
            if not self.repository_manager.validate_repository(resolved_path):
                raise InvalidRepositoryError(
                    f"No valid repository found at: {repository_input}"
                )
            
            # Track temp directory for cleanup
            if is_temporary:
                self._temp_dirs.append(resolved_path)
            
            # Scan the repository
            files = self.scanner.scan(str(resolved_path))

            repository: dict[str, Any] = {
                "repository": Path(repository_input).name if not original_url else Path(original_url).name,
                "repository_path": str(resolved_path),
                "original_input": repository_input,
                "is_temporary": is_temporary,
                "total_files": len(files),
                "files": [],
            }

            for file in files:
                file_path = file["path"]
                language_name = file["language"]

                # Read source code
                try:
                    source = Path(file_path).read_text(
                        encoding="utf-8",
                        errors="ignore",
                    )
                except (UnicodeDecodeError, OSError) as e:
                    # Skip files that can't be read
                    continue

                # Parse with Tree-sitter
                try:
                    parser = ParserFactory.get_parser(language_name)
                    tree = parser.parse(source)
                except Exception as e:
                    # Skip files that can't be parsed
                    continue

                # Extract symbols
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
                        "path": file_path,
                        "language": language_name,
                        "functions": functions,
                        "classes": classes,
                        "imports": imports,
                        "exports": exports,
                        "variables": variables,
                    }
                )

            symbol_table = self.symbol_table_builder.build(repository)

            result = {
                "repository": repository,
                "symbol_table": symbol_table,
            }
            
            return result
            
        finally:
            # Clean up temporary directories if requested
            if cleanup:
                self._cleanup_temp_dirs()

    def _cleanup_temp_dirs(self) -> None:
        """Clean up all tracked temporary directories."""
        for temp_dir in self._temp_dirs:
            try:
                self.repository_manager.cleanup_repository(temp_dir)
            except Exception:
                # Ignore cleanup errors
                pass
        self._temp_dirs.clear()

    def parse_repository_with_cleanup(
        self, 
        repository_input: str
    ) -> dict[str, Any]:
        """
        Parse a repository with automatic cleanup.
        
        This is the recommended method for most use cases as it ensures
        temporary directories are cleaned up even if parsing fails.
        
        Args:
            repository_input: Local path or GitHub URL
            
        Returns:
            Dictionary with 'repository' and 'symbol_table' keys
        """
        return self.parse_repository(repository_input, cleanup=True)

    def parse_repository_no_cleanup(
        self, 
        repository_input: str
    ) -> dict[str, Any]:
        """
        Parse a repository without automatic cleanup.
        
        Use this when you need to keep the temporary directory around
        for multiple operations.
        
        Args:
            repository_input: Local path or GitHub URL
            
        Returns:
            Dictionary with 'repository' and 'symbol_table' keys
        """
        return self.parse_repository(repository_input, cleanup=False)

    def cleanup(self) -> None:
        """Explicitly clean up all temporary directories."""
        self._cleanup_temp_dirs()
        self.repository_manager.cleanup_all()
