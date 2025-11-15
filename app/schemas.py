# BE/app/schemas.py

from pydantic import BaseModel, Field, EmailStr, model_validator, ValidationInfo
from typing import List, Optional
from datetime import datetime

from app.models.recommend_models import TourInfoOut
# ======================================================
# ▼▼▼ 1. Recommand 스키마  ▼▼▼
# ======================================================

## 1. 챗봇 스키마 
# 챗봇에 전송하는 사용자의 메시지 모델입니다.
class ChatbotRequest(BaseModel):
    message: str = Field(..., description="챗봇에게 보낼 사용자의 메시지.")

# 챗봇의 단순 텍스트 응답 모델입니다.
class ChatbotResponse(BaseModel):
    response: str = Field(..., description="챗봇의 텍스트 응답.")


## 2. 추천 스키마 
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

## 3. 챗봇-추천 결합 스키마 
# 챗봇의 응답과 함께 추천 목록도 포함하는 고급 모델입니다.
# 챗봇이 특정 여행지를 추천할 때 사용될 수 있습니다.
class ChatRecommendResponse(BaseModel):
    response: str = Field(..., description="챗봇의 텍스트 응답.")
    recommendations: List[TourInfoOut] = Field([], description="추천된 DB 기반여행지 목록.")
    recommendations: List[RecommendationOut] = Field([], description="추천된 여행지 목록.")
    
# ======================================================
# ▼▼▼ 2. Festival 스키마  ▼▼▼
# ======================================================
class FestivalResponse(BaseModel):
    contentid: str
    title: str
    location: Optional[str] = None
    event_start_date: str
    event_end_date: str
    mapx: float
    mapy: float
    
    image_url: Optional[str] = None 
    modified_time: Optional[str] = None
    
class FestivalRead(FestivalResponse):
    # 사용자에게 응답할 때 사용
    id: int
    # Haversine 계산으로 추가되는 거리 필드 (km 단위)
    distance: Optional[float] = Field(
        None, description="사용자 위치에서 축제 위치까지의 거리 (km)."
    )
    class Config:
        from_attributes = True # Pydantic v2
        # orm_mode = True # Pydantic v1

class FestivalListResponse(BaseModel):
    """축제 목록 API의 전체 응답 구조"""
    total: int = Field(..., description="전체 축제 개수 (필터링 적용 후)")
    page: int
    size: int
    items: List[FestivalRead]


# ======================================================
# ▼▼▼ 3. Market & MarketUser 스키마  ▼▼▼
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
        
# ======================================================
# ▼▼▼ 4. Authentication & General User Schemas ▼▼▼
# ======================================================

# --- General User (일반 사용자 인증) ---
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    # 일반 사용자 회원가입 요청
    password: str = Field(..., min_length=8)
    
    # +사업자 여부 (기본값 False)
    is_business: bool = False 
    
    # +사업자 등록 번호 (선택적 필드, 사업자일 경우에만 필요)
    business_registration_number: Optional[str] = None 
    
    # 사업자 등록 번호 유효성 검사 로직 추가
    @model_validator(mode='after')
    @classmethod
    def validate_business_registration_number(cls, model_instance, info: ValidationInfo):
        
        is_business = model_instance.is_business
        business_number = model_instance.business_registration_number
        
        # 유효성 검사 로직
        if is_business:
            if not business_number:
                # 사업자인데 번호가 없는 경우
                raise ValueError('사업자는 사업자 등록 번호를 입력해야 합니다.')
            if len(business_number) != 10 or not business_number.isdigit():
                # 번호 형식이 잘못된 경우
                raise ValueError('사업자 등록 번호는 10자리의 숫자여야 합니다.')
        
        # 유효성 검사를 통과한 모델 인스턴스를 반환합니다.
        return model_instance
    
    model_config = {
        "from_attributes": True
    }

class UserLogin(BaseModel):
    # 일반 사용자 로그인 요청
    email: EmailStr
    password: str

class Token(BaseModel):
    # 로그인 성공 시 반환되는 JWT 토큰 응답
    access_token: str
    token_type: str
    user_id: int
    email: EmailStr
    username: str

class UserRead(UserBase):
    # 일반 사용자 정보 조회/응답
    id: int
    is_active: bool
    
    is_business: bool
    business_registration_number: Optional[str]
    
    model_config = {
        "from_attributes": True
    }
    
# ======================================================
# ▼▼▼ 5. Favorites Schemas ▼▼▼
# ======================================================
from typing import Literal

# 찜 추가/제거 요청 시 사용
class FavoriteRequest(BaseModel):
    # item_type은 정해진 문자열(Literal)만 받도록 하여 안정성 확보
    item_type: Literal["FESTIVAL", "PRODUCT", "SPOT"] = Field(
        ..., description="찜 항목의 종류 (FESTIVAL, PRODUCT, SPOT 중 하나)"
    )
    item_id: int = Field(..., description="찜 항목의 고유 ID")

# 찜 조회 시 단일 항목의 응답
class FavoriteItemOut(BaseModel):
    # 찜 항목의 실제 ID (축제 ID, 상품 ID 등)
    item_id: int = Field(..., description="찜 항목의 고유 ID")
    # 찜 항목의 타입
    item_type: str = Field(..., description="찜 항목의 타입 (FESTIVAL, PRODUCT, SPOT)")
    # 프론트엔드 표시에 사용될 핵심 정보
    title: str = Field(..., description="찜 항목의 제목")
    image_url: Optional[str] = Field(None, description="찜 항목의 썸네일 이미지 URL")
    
    class Config:
        from_attributes = True

# 통합 찜 목록 조회 시 응답
class FavoriteListResponse(BaseModel):
    festivals: List[FavoriteItemOut] = Field([], description="찜한 축제 목록")
    products: List[FavoriteItemOut] = Field([], description="찜한 마켓 상품 목록")
    spots: List[List[FavoriteItemOut]] = Field([], description="찜한 추천 여행지 목록")