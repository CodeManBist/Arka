from pathlib import Path

from fastapi import APIRouter, HTTPException

from schemas.parse_request import ParseRequest
from analysis.language_detector import LanguageDetector
from analysis.parser_factory import ParserFactory

router = APIRouter()


@router.post("/parse-file")
def parse_file(request: ParseRequest):

    file_path = Path(request.file_path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    language = LanguageDetector.detect(str(file_path))

    parser = ParserFactory.get_parser(language)

    source = file_path.read_text(encoding="utf-8")

    tree = parser.parse(source)

    return {
        "success": True,
        "language": language,
        "file": file_path.name,
        "root_node": str(tree.root_node)
    }