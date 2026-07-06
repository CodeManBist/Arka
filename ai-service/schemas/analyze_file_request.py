from pydantic import BaseModel


class AnalyzeFileRequest(BaseModel):
    file_path: str