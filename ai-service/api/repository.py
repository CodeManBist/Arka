"""API endpoints for repository analysis."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import logging

from analysis.repository_parser import RepositoryParser
from analysis.repository_manager import InvalidRepositoryError, CloneError
from schemas.analyze_repository_request import AnalyzeRepositoryRequest

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/repository", tags=["repository"])


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


@router.post("/analyze")
def analyze_repository(request: AnalyzeRepositoryRequest):
    """
    Analyze a repository (local path or GitHub URL).
    
    This endpoint:
    1. Resolves the repository input (local path or GitHub URL)
    2. Parses all source files
    3. Extracts symbols (functions, classes, imports, etc.)
    4. Returns the complete repository analysis
    
    For GitHub URLs, the repository is cloned to a temporary directory
    and automatically cleaned up after analysis.
    """
    try:
        parser = RepositoryParser()
        
        try:
            result = parser.parse_repository_with_cleanup(request.repository_path)
        except InvalidRepositoryError as e:
            return create_error_response(
                e,
                error_type="invalid_repository",
                status_code=400
            )
        except CloneError as e:
            return create_error_response(
                e,
                error_type="clone_error",
                status_code=400
            )
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return create_error_response(e, error_type="repository_analysis_error")


@router.post("/analyze-no-cleanup")
def analyze_repository_no_cleanup(request: AnalyzeRepositoryRequest):
    """
    Analyze a repository without automatic cleanup.
    
    Use this when you need to keep the temporary directory around
    for multiple operations.
    """
    try:
        parser = RepositoryParser()
        
        try:
            result = parser.parse_repository_no_cleanup(request.repository_path)
        except InvalidRepositoryError as e:
            return create_error_response(
                e,
                error_type="invalid_repository",
                status_code=400
            )
        except CloneError as e:
            return create_error_response(
                e,
                error_type="clone_error",
                status_code=400
            )
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return create_error_response(e, error_type="repository_analysis_error")


@router.get("/health")
def repository_health():
    """Health check for repository API."""
    return {
        "status": "healthy",
        "service": "Repository API",
        "version": "1.0.0"
    }
