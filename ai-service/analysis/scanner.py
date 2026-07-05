from pathlib import Path


IGNORE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    "__pycache__",
    "venv"
}


SUPPORTED_EXTENSIONS = {
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".py": "python",
}


class RepositoryScanner:

    def scan(self, repository_path: str):

        files = []

        root = Path(repository_path)

        for path in root.rglob("*"):

            if path.is_dir():
                continue

            if any(part in IGNORE_DIRS for part in path.parts):
                continue

            extension = path.suffix

            if extension not in SUPPORTED_EXTENSIONS:
                continue

            files.append(
                {
                    "path": str(path),
                    "language": SUPPORTED_EXTENSIONS[extension],
                }
            )

        return files