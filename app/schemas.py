# BE/app/schemas.py

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

from app.models.recommend_models import TourInfoOut

## 1. 챗봇 스키마 (팀원 작업 보존)
# 챗봇에 전송하는 사용자의 메시지 모델입니다.
class ChatbotRequest(BaseModel):
    message: str = Field(..., description="챗봇에게 보낼 사용자의 메시지.")

# 챗봇의 단순 텍스트 응답 모델입니다.
class ChatbotResponse(BaseModel):
    response: str = Field(..., description="챗봇의 텍스트 응답.")


## 2. 추천 스키마 (팀원 작업 보존)
# 단일 추천 항목(여행지, 상품 등)을 위한 모델입니다.
class RecommendationOut(BaseModel):
    id: int = Field(..., description="추천 항목의 고유 ID.")
    title: str = Field(..., description="추천 항목의 제목.")
    description: Optional[str] = Field(None, description="항목에 대한 간략한 설명.")
    image_url: Optional[str] = Field(None, description="항목 이미지의 URL.")
    tags: List[str] = Field([], description="항목과 관련된 태그 목록.")

# 랜덤 추천 API의 요청 본문 모델입니다.
class RandomRecommendRequest(BaseModel):
    themes: List[str] = Field(..., description="사용자가 선택한 테마 목록.")

# 랜덤 추천 API의 전체 응답 모델입니다.
class RandomRecommendResponse(BaseModel):
    message: str = Field("랜덤 여행지 추천이 완료되었습니다.", description="응답 상태 메시지.")
    recommendations: List[RecommendationOut] = Field([], description="추천된 여행지 목록.")

## 3. 챗봇-추천 결합 스키마 (팀원 작업 보존)
# 챗봇의 응답과 함께 추천 목록도 포함하는 고급 모델입니다.
# 챗봇이 특정 여행지를 추천할 때 사용될 수 있습니다.
class ChatRecommendResponse(BaseModel):
    response: str = Field(..., description="챗봇의 텍스트 응답.")
    recommendations: List[TourInfoOut] = Field([], description="추천된 DB 기반여행지 목록.")

# ======================================================
# ▼▼▼ 4. Market & User 스키마 (새로 추가) ▼▼▼
# ======================================================

# --- User (market_users) ---

class MarketUserBase(BaseModel):
    email: EmailStr
    username: str

class MarketUserCreate(MarketUserBase):
    password: str = Field(..., min_length=8)
    is_seller: bool = False
    business_number: Optional[str] = None

class MarketUserLogin(BaseModel):
    email: EmailStr
    password: str

class MarketUserOut(MarketUserBase):
    id: int
    is_seller: bool
    seller_status: str
    
    class Config:
        from_attributes = True # ORM 객체를 Pydantic 모델로 자동 변환

# --- Product Image (market_product_images) ---

class MarketProductImageOut(BaseModel):
    id: int
    image_url: str
    is_thumbnail: bool
    
    class Config:
        from_attributes = True

# --- QnA (market_qna) ---

class MarketQnaCreateSchema(BaseModel):
    title: str = Field(..., max_length=255)
    body: str

class MarketQnaUpdateSchema(BaseModel):
    answer_body: str # 판매자의 답변

class MarketQnaOut(BaseModel):
    id: int
    product_id: int
    author: MarketUserOut # 질문자 정보
    title: str
    body: str
    created_at: datetime
    
    answer_body: Optional[str]
    answerer: Optional[MarketUserOut] # 답변자 정보
    answered_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# --- Product (market_products) ---

class MarketProductCreateSchema(BaseModel):
    # FormData에서 받는 필드들
    title: str = Field(..., max_length=255)
    price: int
    shop_name: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    summary: Optional[str] = None
    seller_note: Optional[str] = None
    delivery_info: Optional[str] = Field(None, max_length=255)
    region: Optional[str] = Field(None, max_length=50)

class MarketProductUpdateSchema(MarketProductCreateSchema):
    # 부분 업데이트를 위해 모든 필드를 Optional로
    title: Optional[str] = Field(None, max_length=255)
    price: Optional[int] = None
    # ... (다른 필드들도 필요시 Optional로 추가)

class MarketProductOut(BaseModel):
    # MarketHome.js 목록 및 상세보기에 필요한 필드
    id: int
    title: str
    price: int
    shop_name: Optional[str]
    location: Optional[str]
    summary: Optional[str]
    seller_note: Optional[str]
    delivery_info: Optional[str]
    region: Optional[str]
    rating: float
    likes: int
    created_at: datetime
    
    seller: MarketUserOut # 판매자 정보
    images: List[MarketProductImageOut] = [] # 상품 이미지 목록
    
    # 상세 보기 시 Q&A 목록 (선택적 포함)
    qna_list: List[MarketQnaOut] = [] 

    class Config:
        from_attributes = True

# --- Wishlist (market_wishlist) ---

class MarketWishlistOut(BaseModel):
    id: int
    user_id: int
    product: MarketProductOut # 찜한 상품의 전체 정보
    created_at: datetime
    
    class Config:
        from_attributes = True