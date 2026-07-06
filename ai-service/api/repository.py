from pathlib import Path

from fastapi import APIRouter, HTTPException

from analysis.repository_parser import RepositoryParser
from schemas.analyze_repository_request import AnalyzeRepositoryRequest

router = APIRouter()


@router.post("/analyze-repository")
def analyze_repository(request: AnalyzeRepositoryRequest):

    repository_path = Path(request.repository_path)

    if not repository_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Repository not found"
        )

    if not repository_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail="Provided path is not a directory"
        )

    parser = RepositoryParser()

    return {
        "success": True,
        "data": parser.parse_repository(str(repository_path))
    }