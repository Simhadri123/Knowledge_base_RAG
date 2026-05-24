from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import KNOWLEDGE_ASSETS_DIR, UPLOAD_DIR
from .db.init_db import init_db
from .api.router import api_router

app = FastAPI(
    title="Enterprise Knowledge Extraction API",
    version="1.0.0",
    description="REST APIs for upload, extraction, chunking, and knowledge generation.",
)
app.include_router(api_router, prefix="/api/v1")
app.mount("/assets", StaticFiles(directory=KNOWLEDGE_ASSETS_DIR), name="assets")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}
