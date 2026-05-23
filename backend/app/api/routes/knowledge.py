from fastapi import APIRouter, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from ...schemas.knowledge import (
    KnowledgeAssetResponse,
    KnowledgeApproveRequest,
    KnowledgeApproveResponse,
    KnowledgeFromExtractedRequest,
    KnowledgeFromTextRequest,
    KnowledgeResponse,
)
from ...services.asset_service import save_image_asset
from ...services.knowledge_service import (
    approve_knowledge,
    generate_from_extracted,
    generate_from_text,
)

router = APIRouter()


@router.post("/knowledge/from-text", response_model=KnowledgeResponse)
async def knowledge_from_text(payload: KnowledgeFromTextRequest) -> KnowledgeResponse:
    try:
        result = await run_in_threadpool(
            generate_from_text,
            payload.text,
            payload.source,
            payload.chunk_size,
            payload.chunk_overlap,
            payload.max_parts,
            payload.save_output,
        )
        return KnowledgeResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Knowledge extraction failed") from exc


@router.post("/knowledge/from-extracted", response_model=KnowledgeResponse)
async def knowledge_from_extracted(
    payload: KnowledgeFromExtractedRequest,
) -> KnowledgeResponse:
    try:
        result = await run_in_threadpool(
            generate_from_extracted,
            payload.extracted_filename,
            payload.chunk_size,
            payload.chunk_overlap,
            payload.max_parts,
            payload.save_output,
        )
        return KnowledgeResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Knowledge extraction failed") from exc


@router.post("/knowledge/approve", response_model=KnowledgeApproveResponse)
async def knowledge_approve(
    payload: KnowledgeApproveRequest,
) -> KnowledgeApproveResponse:
    try:
        result = await run_in_threadpool(
            approve_knowledge,
            payload.source,
            payload.title,
            payload.content,
        )
        return KnowledgeApproveResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Knowledge approval failed") from exc


@router.post("/knowledge/assets", response_model=KnowledgeAssetResponse)
async def knowledge_asset_upload(
    file: UploadFile = File(...),
) -> KnowledgeAssetResponse:
    try:
        result = await run_in_threadpool(save_image_asset, file)
        return KnowledgeAssetResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Asset upload failed") from exc
