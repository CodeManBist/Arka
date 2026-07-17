from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from api.parser import router as parser_router
from api.repository import router as repository_router
from api.blast_radius import router as blast_radius_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Blast Radius AI Service")

# Configure CORS
# Allow all origins for development, can be restricted in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
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


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Blast Radius AI Service starting up...")
    logger.info("CORS enabled: All origins allowed")
    

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Blast Radius AI Service shutting down...")
