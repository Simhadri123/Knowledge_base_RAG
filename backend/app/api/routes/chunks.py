from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from ...schemas.chunking import (
    ChunkFromExtractedRequest,
    ChunkFromTextRequest,
    ChunkResponse,
)
from ...services.chunk_service import chunk_from_extracted, chunk_from_text

router = APIRouter()


@router.post("/chunks/from-text", response_model=ChunkResponse)
async def chunk_from_text_endpoint(payload: ChunkFromTextRequest) -> ChunkResponse:
    try:
        result = await run_in_threadpool(
            chunk_from_text,
            payload.text,
            payload.source,
            payload.chunk_size,
            payload.chunk_overlap,
            payload.save,
        )
        return ChunkResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Chunking failed") from exc


@router.post("/chunks/from-extracted", response_model=ChunkResponse)
async def chunk_from_extracted_endpoint(
    payload: ChunkFromExtractedRequest,
) -> ChunkResponse:
    try:
        result = await run_in_threadpool(
            chunk_from_extracted,
            payload.extracted_filename,
            payload.chunk_size,
            payload.chunk_overlap,
            payload.save,
        )
        return ChunkResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Chunking failed") from exc
