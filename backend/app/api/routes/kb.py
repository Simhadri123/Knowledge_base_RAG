from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...auth.deps import get_current_user
from ...db.session import get_db
from ...models import KBArticle
from ...schemas.kb import KBCreateRequest, KBListItem, KBResponse, KBUpdateRequest
from ...services.kb_service import (
    create_kb,
    delete_kb,
    get_kb,
    list_user_kbs,
    list_published_kbs,
    publish_kb,
    update_kb,
)

router = APIRouter()


def _ensure_owner(kb: KBArticle, user_id: int) -> None:
    if kb.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")


def _kb_response(kb: KBArticle) -> KBResponse:
    return KBResponse(
        id=kb.id,
        owner_id=kb.owner_id,
        owner_username=kb.owner.username if getattr(kb, "owner", None) else None,
        title=kb.title,
        source_document=kb.source_document,
        source_document_url=kb.source_document_url,
        content_md=kb.content_md,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
        is_published=kb.is_published,
    )


@router.post("/kb/create", response_model=KBResponse)
async def kb_create(
    payload: KBCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> KBResponse:
    kb = create_kb(db, current_user.id, payload.title, payload.content_md, payload.source_document, payload.source_document_url)
    return _kb_response(kb)


@router.put("/kb/{kb_id}", response_model=KBResponse)
async def kb_update(
    kb_id: int,
    payload: KBUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> KBResponse:
    kb = get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="KB not found")
    _ensure_owner(kb, current_user.id)
    kb = update_kb(db, kb, payload.title, payload.content_md, payload.source_document, payload.source_document_url)
    return _kb_response(kb)


@router.delete("/kb/{kb_id}")
async def kb_delete(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    kb = get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="KB not found")
    _ensure_owner(kb, current_user.id)
    delete_kb(db, kb)
    return {"status": "deleted"}


@router.get("/kb/my-kbs", response_model=list[KBListItem])
async def kb_my_kbs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[KBListItem]:
    kbs = list_user_kbs(db, current_user.id)
    return [
        KBListItem(
            id=kb.id,
            owner_username=current_user.username,
            title=kb.title,
            source_document=kb.source_document,
            created_at=kb.created_at,
            updated_at=kb.updated_at,
            is_published=kb.is_published,
        )
        for kb in kbs
    ]


@router.get("/kb/published", response_model=list[KBListItem])
async def kb_published(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[KBListItem]:
    kbs = list_published_kbs(db)
    return [
        KBListItem(
            id=kb.id,
            owner_username=kb.owner.username if getattr(kb, "owner", None) else None,
            title=kb.title,
            source_document=kb.source_document,
            created_at=kb.created_at,
            updated_at=kb.updated_at,
            is_published=kb.is_published,
        )
        for kb in kbs
    ]


@router.get("/kb/{kb_id}", response_model=KBResponse)
async def kb_get(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> KBResponse:
    kb = get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="KB not found")
    if kb.owner_id != current_user.id and not kb.is_published:
        raise HTTPException(status_code=403, detail="Not authorized")
    return _kb_response(kb)


@router.post("/kb/{kb_id}/publish", response_model=KBResponse)
async def kb_publish(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> KBResponse:
    kb = get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="KB not found")
    _ensure_owner(kb, current_user.id)
    kb = publish_kb(db, kb, True)
    return _kb_response(kb)


@router.post("/kb/{kb_id}/unpublish", response_model=KBResponse)
async def kb_unpublish(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> KBResponse:
    kb = get_kb(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="KB not found")
    _ensure_owner(kb, current_user.id)
    kb = publish_kb(db, kb, False)
    return _kb_response(kb)
