from fastapi import FastAPI

from api.parser import router as parser_router
from api.repository import router as repository_router
from api.blast_radius import router as blast_radius_router

app = FastAPI(title="Blast Radius AI Service")

app.include_router(parser_router)
app.include_router(repository_router)
app.include_router(blast_radius_router)


@app.get("/")
def health():
    return {
        "status": "running",
        "service": "Blast Radius AI Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/",
            "parser": "/api/parser/*",
            "repository": "/api/repository/*",
            "blast_radius": "/api/blast-radius/*"
        }
    }
