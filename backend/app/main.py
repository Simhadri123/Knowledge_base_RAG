from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import KNOWLEDGE_ASSETS_DIR
from .api.router import api_router

app = FastAPI(
    title="Enterprise Knowledge Extraction API",
    version="1.0.0",
    description="REST APIs for upload, extraction, chunking, and knowledge generation.",
)
app.include_router(api_router, prefix="/api/v1")
app.mount("/assets", StaticFiles(directory=KNOWLEDGE_ASSETS_DIR), name="assets")


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}
