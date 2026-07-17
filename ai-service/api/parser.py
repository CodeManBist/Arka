"""API endpoints for file parsing."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
from pydantic import BaseModel
import logging

from analysis.extractors.class_extractor import ClassExtractor
from analysis.extractors.export_extractor import ExportExtractor
from analysis.extractors.function_extractor import FunctionExtractor
from analysis.extractors.import_extractor import ImportExtractor
from analysis.extractors.variable_extractor import VariableExtractor
from analysis.language_detector import LanguageDetector
from analysis.parser_factory import ParserFactory
from schemas.analyze_file_request import AnalyzeFileRequest

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/parser", tags=["parser"])


class ErrorResponse(BaseModel):
    """Standard error response model."""
    success: bool = False
    error: str
    error_type: str
    details: Optional[Dict[str, Any]] = None


def create_error_response(
    error: Exception, 
    error_type: str = "unknown_error",
    status_code: int = 500
) -> JSONResponse:
    """Create a standardized error response."""
    error_message = str(error)
    
    # Log the error
    logger.error(f"{error_type}: {error_message}")
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": error_message,
            "error_type": error_type,
            "details": {
                "type": type(error).__name__,
            }
        }
    )


@router.post("/analyze-file")
def analyze_file(request: AnalyzeFileRequest):
    """
    Analyze a single source file.
    
    This endpoint:
    1. Detects the file's language
    2. Parses it with Tree-sitter
    3. Extracts all symbols (functions, classes, imports, exports, variables)
    4. Returns the extracted symbols
    """
    try:
        file_path = Path(request.file_path)

        if not file_path.exists():
            return create_error_response(
                Exception(f"File not found: {request.file_path}"),
                error_type="file_not_found",
                status_code=404
            )

        if not file_path.is_file():
            return create_error_response(
                Exception(f"Path is not a file: {request.file_path}"),
                error_type="not_a_file",
                status_code=400
            )

        # Detect language
        try:
            language_name = LanguageDetector.detect(str(file_path))
        except Exception as e:
            return create_error_response(
                e,
                error_type="language_detection_failed",
                status_code=400
            )

        # Parse the file
        try:
            parser = ParserFactory.get_parser(language_name)
        except Exception as e:
            return create_error_response(
                e,
                error_type="parser_not_available",
                status_code=400
            )

        # Read source code
        try:
            source = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except (UnicodeDecodeError, OSError) as e:
            return create_error_response(
                e,
                error_type="file_read_failed",
                status_code=400
            )

        # Parse with Tree-sitter
        try:
            tree = parser.parse(source)
        except Exception as e:
            return create_error_response(
                e,
                error_type="parsing_failed",
                status_code=400
            )

        # Extract symbols
        function_extractor = FunctionExtractor()
        class_extractor = ClassExtractor()
        import_extractor = ImportExtractor()
        export_extractor = ExportExtractor()
        variable_extractor = VariableExtractor()

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

        imports = import_extractor.extract(
            language=parser.language,
            tree=tree,
            source=source,
            language_name=language_name,
        )

        exports = export_extractor.extract(
            language=parser.language,
            tree=tree,
            source=source,
            language_name=language_name,
        )

        variables = variable_extractor.extract(
            language=parser.language,
            tree=tree,
            source=source,
            language_name=language_name,
        )

        return {
            "success": True,
            "language": language_name,
            "file": str(file_path),
            "file_name": file_path.name,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "exports": exports,
            "variables": variables,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return create_error_response(e, error_type="file_analysis_error")


@router.get("/health")
def parser_health():
    """Health check for parser API."""
    return {
        "status": "healthy",
        "service": "Parser API",
        "version": "1.0.0",
        "supported_languages": ["python", "javascript", "typescript"]
    }
