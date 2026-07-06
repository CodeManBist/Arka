from fastapi import FastAPI

from api.parser import router as parser_router
from api.repository import router as repository_router

app = FastAPI(title="Arka AI Service")

app.include_router(parser_router)
app.include_router(repository_router)


@app.get("/")
def health():
    return {
        "status": "running",
        "service": "Arka AI Service"
    }