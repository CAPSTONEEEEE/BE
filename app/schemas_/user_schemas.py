from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    """회원가입 시 받는 데이터 형식"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=50)
    username: str

class UserLogin(BaseModel):
    """로그인 시 받는 데이터 형식"""
    email: EmailStr
    password: str

class UserOut(BaseModel):
    """API 응답 시 보낼 사용자 정보 (비밀번호 제외)"""
    id: int
    email: EmailStr
    username: str

    class Config:
        from_attributes = True # SQLAlchemy 모델 객체를 이 Pydantic 모델로 변환 가능하게 함