from fastapi import APIRouter, HTTPException, status, Depends, Path
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas_ import user_schemas
from app.services import user_service  

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# 회원가입
@router.post("/register", response_model=user_schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    """새로운 사용자를 등록합니다."""
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    return user_service.create_user(db=db, user=user)

# 로그인
@router.post("/login", response_model=user_schemas.UserOut)
def login_for_access_token(user_login: user_schemas.UserLogin, db: Session = Depends(get_db)):
    """로그인"""
    user = user_service.authenticate_user(db, user_login=user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )
    return user
