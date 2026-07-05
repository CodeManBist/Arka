from fastapi import FastAPI

from api.parser import router as parser_router

app = FastAPI(title="Arka AI Service")


app.include_router(parser_router)


@app.get("/")
def health():
    return {
        "status": "running",
        "service": "Arka AI Service"
    }