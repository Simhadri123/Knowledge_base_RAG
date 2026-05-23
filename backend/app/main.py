from fastapi import FastAPI

from .routes import router

app = FastAPI(title="Phase 1 Knowledge Extraction")
app.include_router(router)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}
