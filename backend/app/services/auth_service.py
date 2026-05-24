from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from ..auth.security import create_access_token, hash_password, verify_password
from ..models import User


def create_user(db: Session, username: str, email: str, password: str) -> User:
    existing = (
        db.query(User)
        .filter((User.username == username) | (User.email == email))
        .first()
    )
    if existing:
        raise ValueError("Username or email already exists")

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def login_for_access_token(db: Session, username: str, password: str) -> str:
    user = authenticate_user(db, username, password)
    if not user:
        raise ValueError("Invalid credentials")
    return create_access_token(str(user.id))
