from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...auth.deps import get_current_user
from ...db.session import get_db
from ...schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse
from ...services.auth_service import create_user, login_for_access_token

router = APIRouter()


@router.post("/auth/signup", response_model=UserResponse)
async def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> UserResponse:
    try:
        user = create_user(db, payload.username, payload.email, payload.password)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/auth/login", response_model=TokenResponse)
async def login(payload: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenResponse:
    try:
        token = login_for_access_token(db, payload.username, payload.password)
        return TokenResponse(access_token=token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/auth/me", response_model=UserResponse)
async def me(current_user=Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at.isoformat(),
    )
