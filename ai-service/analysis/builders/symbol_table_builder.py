"""Build a repository-wide symbol table."""

from pathlib import Path

from models.symbol import Symbol
from models.symbol_table import SymbolTable


class SymbolTableBuilder:
    """Build a SymbolTable from extracted repository symbols."""

    def build(self, repository: dict) -> SymbolTable:

        table = SymbolTable()

        for file in repository["files"]:

            relative_file = Path(file["path"]).name
            language = file["language"]

            self._add_symbols(
                table,
                file["functions"],
                "function",
                language,
                relative_file,
            )

            self._add_symbols(
                table,
                file["classes"],
                "class",
                language,
                relative_file,
            )

            self._add_symbols(
                table,
                file["imports"],
                "import",
                language,
                relative_file,
            )

            self._add_symbols(
                table,
                file["exports"],
                "export",
                language,
                relative_file,
            )

            self._add_symbols(
                table,
                file["variables"],
                "variable",
                language,
                relative_file,
            )

        return table

    def _add_symbols(
        self,
        table: SymbolTable,
        symbols: list,
        kind: str,
        language: str,
        file: str,
    ) -> None:

        for symbol in symbols:

            table.add(
                Symbol(
                    id=f"{file}::{symbol['name']}",
                    name=symbol["name"],
                    kind=kind,
                    language=language,
                    file=file,
                    start_line=symbol["start_line"],
                    end_line=symbol["end_line"],
                )
            )