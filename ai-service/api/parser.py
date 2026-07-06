from pathlib import Path

from fastapi import APIRouter, HTTPException

from analysis.extractors.class_extractor import ClassExtractor
from analysis.extractors.function_extractor import FunctionExtractor
from analysis.language_detector import LanguageDetector
from analysis.parser_factory import ParserFactory
from schemas.analyze_file_request import AnalyzeFileRequest

router = APIRouter()


@router.post("/analyze-file")
def analyze_file(request: AnalyzeFileRequest):

    file_path = Path(request.file_path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    language_name = LanguageDetector.detect(str(file_path))

    parser = ParserFactory.get_parser(language_name)

    source = file_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    tree = parser.parse(source)

    function_extractor = FunctionExtractor()
    class_extractor = ClassExtractor()

    functions = function_extractor.extract(
        language=parser.language,
        tree=tree,
        source=source,
        language_name=language_name,
    )

    classes = class_extractor.extract(
        language=parser.language,
        tree=tree,
        source=source,
        language_name=language_name,
    )

    return {
        "success": True,
        "language": language_name,
        "file": file_path.name,
        "functions": functions,
        "classes": classes,
    }