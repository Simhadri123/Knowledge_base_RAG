from fastapi import APIRouter

from .routes import chunks, health, knowledge, upload

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(upload.router, tags=["Files"])
api_router.include_router(chunks.router, tags=["Chunks"])
api_router.include_router(knowledge.router, tags=["Knowledge"])
