import os
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import user_service
from app.security import create_access_token, verify_password, get_password_hash
import app.security as security
from app.schemas import UserCreate, UserLogin, UserRead, Token 
from app.models.base_user_models import User


router = APIRouter(prefix="/auth", tags=["Auth & Users"])

# ======================================================
# 1. 회원가입 (Register)
# ======================================================
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="회원가입")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """새로운 사용자를 등록합니다."""
    
    # 1. 이메일 중복 확인
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 등록된 이메일입니다.")
    
    # 2. 사업자 등록 번호 중복 확인 (사업자인 경우에만)
    if user.is_business and user.business_registration_number:
        existing_business_user = db.query(User).filter(
            User.business_registration_number == user.business_registration_number 
        ).first()
        
        if existing_business_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 등록된 사업자 번호입니다.")
    
    # 3. 사용자 생성
    created_user = user_service.create_user(db=db, user_create=user)
    
    # 4. UserRead 스키마로 반환
    return created_user

# ======================================================
# 2. 로그인 (Login & Token 발급)
# ======================================================
@router.post("/login", response_model=Token)
async def login_for_access_token(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    이메일과 비밀번호를 검증하고 JWT 액세스 토큰을 발급합니다.
    """
    # 1. 사용자 인증
    user = user_service.authenticate_user(db, email=user_login.email, password=user_login.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. 토큰 생성
    access_token = create_access_token(
        data={"sub": user.email},
    )
    
    # 3. 토큰 + 사용자 정보 반환 (★ 최소 수정: 아래 2줄만 추가됨)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_business": user.is_business,  # ★ 추가
        "business_registration_number": user.business_registration_number  # ★ 추가
    }

# ======================================================
# 3. 현재 사용자 정보 조회
# ======================================================
@router.get("/users/me", response_model=UserRead)
def read_users_me(current_user: UserRead = Depends(security.get_current_user)):
    """현재 로그인된 사용자 정보를 반환합니다."""
    return current_user

@router.get("/healthcheck")
def health_check():
    return {"status": "ok"}
