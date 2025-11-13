import os
from typing import Optional, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from app.db.database import get_db
from app.models.base_user_models import User
from app.schemas import UserCreate, UserLogin, UserRead
from app.security import get_password_hash, verify_password 
from app.core.config import get_settings

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ======================================================
# 사용자 CRUD 로직
# ======================================================

def get_user_by_email(db: Session, email: str):
    """이메일로 사용자를 조회합니다."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_create: UserCreate):
    """새 사용자를 생성하고 비밀번호를 해시하여 DB에 저장합니다."""
    # 비밀번호 해시
    hashed_password = get_password_hash(user_create.password)
    
    # User 모델 인스턴스 생성
    db_user = User(
        email=user_create.email,
        username=user_create.username, 
        hashed_password=hashed_password,
        is_active=True
    )
    
    # DB에 저장
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ======================================================
# 인증 로직
# ======================================================

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """사용자 인증: 이메일로 조회 후 비밀번호 검증"""
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    # 비밀번호 검증 (security.py의 함수 사용)
    if not verify_password(password, user.hashed_password):
        return None
    return user
