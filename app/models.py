# backend/app/models.py
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Pydantic 모델 정의 ---
# 요청 및 응답 데이터 유효성 검사를 위해 사용됩니다.

# 회원
class UserCreate(BaseModel):
    id: str
    password: str
    email: str
    nickname: str
    gender: Optional[str] = None
    birthday: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    email: str
    nickname: str
    gender: Optional[str] = None
    birthday: Optional[str] = None

class UserLogin(BaseModel):
    id: str
    password: str

class Token(BaseModel):
    message: str
    token: str
    data: dict

# 추천
class Recommendation(BaseModel):
    title: str
    score: float
    distanceKm: float
    reason: List[str]

class RecommendResponse(BaseModel):
    message: str
    data: dict

# 콘텐츠 (축제, 상품)
class Festival(BaseModel):
    name: str
    description: str
    latitude: float
    longitude: float

class Product(BaseModel):
    name: str
    price: int
    description: str
    image_url: str

# 사용자 상호작용
class Favorite(BaseModel):
    item_id: str

class Review(BaseModel):
    user_id: str
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str
