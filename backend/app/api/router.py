from fastapi import APIRouter

from .routes import auth, chatbot, chunks, health, kb, knowledge, upload

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(upload.router, tags=["Files"])
api_router.include_router(chunks.router, tags=["Chunks"])
api_router.include_router(knowledge.router, tags=["Knowledge"])
api_router.include_router(chatbot.router, tags=["Chatbot"])
api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(kb.router, tags=["KnowledgeBase"])
