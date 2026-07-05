from pathlib import Path


LANGUAGE_MAP = {
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".py": "python",
}


class LanguageDetector:

    @staticmethod
    def detect(file_path: str) -> str:

        extension = Path(file_path).suffix.lower()

        if extension not in LANGUAGE_MAP:
            raise ValueError(f"Unsupported language: {extension}")

        return LANGUAGE_MAP[extension]