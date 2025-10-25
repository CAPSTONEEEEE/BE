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
    return user_service.create_user(db=db, user_create=user)

# 로그인
@router.post("/login", response_model=user_schemas.UserOut)
def login_for_access_token(user_login: user_schemas.UserLogin, db: Session = Depends(get_db)):
    """로그인 (개발용 임시)"""
    # 1. 기존 인증 로직을 전부 주석 처리하거나 삭제합니다.
    # user = user_service.authenticate_user(db, user_login=user_login)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="이메일 또는 비밀번호가 올바르지 않습니다.",
    #     )
    
    # 2. 대신, 미리 만들어둔 가짜 사용자 정보를 즉시 반환합니다.
    #    (UserOut 스키마 형식과 일치해야 합니다.)
    mock_user = {
        "id": 1, 
        "email": "test@example.com", 
        "username": "테스트유저"
    }
    return mock_user
@router.get("/healthcheck")
def health_check():
    return {"status": "ok"}