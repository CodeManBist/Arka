from pydantic import BaseModel


class AnalyzeRepositoryRequest(BaseModel):
    repository_path: str