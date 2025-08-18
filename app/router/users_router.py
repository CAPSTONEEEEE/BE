# backend/app/router/users_router.py

from typing import Optional
from fastapi import APIRouter, HTTPException, Path
from app.models import UserCreate, UserLogin, UserProfile

# APIRouter 객체 생성
# prefix='/users', tags=['회원 관리']로 설정하여 이 라우터의 모든 엔드포인트가
# /users로 시작하고, API 문서에서 '회원 관리' 그룹에 속하도록 합니다.
router = APIRouter(prefix="/users", tags=["회원 관리"])

# 임시 데이터베이스 (실제로는 DB 사용)
db_users = {}

# --- 회원 관리 엔드포인트 ---
@router.post("")
async def signup(user: UserCreate):
    """
    새로운 사용자 계정을 생성합니다.
    """
    if user.id in db_users:
        raise HTTPException(status_code=409, detail="이미 존재하는 사용자 ID입니다.")
    db_users[user.id] = user
    return {"message": "회원가입 성공", "data": {"id": user.id}}

@router.post("/login")
async def login(user: UserLogin):
    """
    사용자 인증 및 토큰을 발급합니다.
    """
    if user.id not in db_users or db_users[user.id].password != user.password:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    # 실제로는 JWT 토큰을 생성하여 반환합니다.
    token = f"dummy_jwt_token_for_{user.id}"
    return {"message": "로그인 성공", "token": token, "data": {"id": user.id}}

@router.get("/{user_id}")
async def get_user_profile(user_id: str = Path(..., title="사용자 ID")):
    """
    특정 사용자의 프로필 정보를 조회합니다.
    """
    if user_id not in db_users:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    user_data = db_users[user_id]
    return user_data

# 참고: 회원 탈퇴, 정보 수정 등의 엔드포인트도 여기에 추가할 수 있습니다.
