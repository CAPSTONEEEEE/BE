# BE/app/schemas.py

from pydantic import BaseModel, Field, EmailStr, model_validator, ValidationInfo, computed_field
from typing import List, Optional
from datetime import datetime

from app.models.recommend_models import TourInfoOut

# ▼▼▼ [핵심 수정 1] 파일 최상단에서 settings 로드하는 라인을 주석 처리 또는 삭제합니다. ▼▼▼
# from app.core.config import get_settings
# settings = get_settings()
# ▲▲▲ [핵심 수정 1] ▲▲▲


# ======================================================
# ▼▼▼ 1. Recommand 스키마  ▼▼▼
# ======================================================

## 1. 챗봇 스키마 
# (이하 생략 - 기존 코드와 동일)
class ChatbotRequest(BaseModel):
    message: str = Field(..., description="챗봇에게 보낼 사용자의 메시지.")

class ChatbotResponse(BaseModel):
    response: str = Field(..., description="챗봇의 텍스트 응답.")

## 2. 추천 스키마 
class RecommendationOut(BaseModel):
    id: int = Field(..., description="추천 항목의 고유 ID.")
    title: str = Field(..., description="추천 항목의 제목.")
    description: Optional[str] = Field(None, description="항목에 대한 간략한 설명.")
    image_url: Optional[str] = Field(None, description="항목 이미지의 URL.")
    tags: List[str] = Field([], description="항목과 관련된 태그 목록.")

class RandomRecommendRequest(BaseModel):
    themes: List[str] = Field(..., description="사용자가 선택한 테마 목록.")

class RandomRecommendResponse(BaseModel):
    message: str = Field("랜덤 여행지 추천이 완료되었습니다.", description="응답 상태 메시지.")
    recommendations: List[RecommendationOut] = Field([], description="추천된 여행지 목록.")

## 3. 챗봇-추천 결합 스키마 
class ChatRecommendResponse(BaseModel):
    response: str = Field(..., description="챗봇의 텍스트 응답.")
    recommendations: List[TourInfoOut] = Field([], description="추천된 DB 기반여행지 목록.")
    # recommendations: List[RecommendationOut] = Field([], description="추천된 여행지 목록.")
    
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
    id: int
    distance: Optional[float] = Field(
        None, description="사용자 위치에서 축제 위치까지의 거리 (km)."
    )
    class Config:
        from_attributes = True 

class FestivalListResponse(BaseModel):
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
        from_attributes = True 

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
    answer_body: str 

class MarketQnaOut(BaseModel):
    id: int
    product_id: int
    author: MarketUserOut 
    title: str
    body: str
    created_at: datetime
    
    answer_body: Optional[str]
    answerer: Optional[MarketUserOut] 
    answered_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# --- Product (market_products) ---
class MarketProductCreateSchema(BaseModel):
    title: str = Field(..., max_length=255)
    price: int
    shop_name: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    summary: Optional[str] = None
    seller_note: Optional[str] = None
    delivery_info: Optional[str] = Field(None, max_length=255)
    region: Optional[str] = Field(None, max_length=50)

class MarketProductUpdateSchema(MarketProductCreateSchema):
    title: Optional[str] = Field(None, max_length=255)
    price: Optional[int] = None

class MarketProductOut(BaseModel):
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
    
    seller: MarketUserOut 
    images: List[MarketProductImageOut] = [] 
    qna_list: List[MarketQnaOut] = [] 
    
    @computed_field(return_type=Optional[str])
    @property
    def image(self) -> Optional[str]:
        """
        MarketHome.js 썸네일을 위해 URL을 반환합니다.
        상대 경로인 경우, 프론트엔드에서 Base URL을 붙일 수 있도록 그대로 반환합니다.
        """
        if not self.images:
            return None
        
        # 1. 썸네일로 지정된 이미지를 찾습니다.
        target_image = next(
            (img for img in self.images if img.is_thumbnail), 
            None
        )
        
        # 2. 썸네일이 없으면, 0번째 이미지를 사용합니다.
        if not target_image:
            target_image = self.images[0]

        url = target_image.image_url

        # 3. 이미 http로 시작하는 절대 경로(외부 이미지 등)면 그대로 반환
        if url.startswith("http://") or url.startswith("https://"):
            return url
        
        # 4. [핵심 수정] 상대 경로(/static/...)라면 서버 URL을 붙이지 않고 그대로 반환합니다.
        # 프론트엔드(MarketHome.js)가 자신의 환경(Localhost/Emulator/Device)에 맞는 URL을 붙이도록 합니다.
        return url
    
    class Config:
        from_attributes = True

# --- Wishlist (market_wishlist) ---
class MarketWishlistOut(BaseModel):
    id: int
    user_id: int
    product: MarketProductOut 
    created_at: datetime
    
    class Config:
        from_attributes = True
        
# ======================================================
# ▼▼▼ 4. Authentication & General User Schemas ▼▼▼
# ======================================================
# (이하 생략 - 기존 코드와 동일)

# --- General User (일반 사용자 인증) ---
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    is_business: bool = False 
    business_registration_number: Optional[str] = None 
    
    @model_validator(mode='after')
    @classmethod
    def validate_business_registration_number(cls, model_instance, info: ValidationInfo):
        
        is_business = model_instance.is_business
        business_number = model_instance.business_registration_number
        
        if is_business:
            if not business_number:
                raise ValueError('사업자는 사업자 등록 번호를 입력해야 합니다.')
            if len(business_number) != 10 or not business_number.isdigit():
                raise ValueError('사업자 등록 번호는 10자리의 숫자여야 합니다.')
        
        return model_instance
    
    model_config = {
        "from_attributes": True
    }

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: EmailStr
    username: str

class UserRead(UserBase):
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

class FavoriteRequest(BaseModel):
    item_type: Literal["FESTIVAL", "PRODUCT", "SPOT"] = Field(
        ..., description="찜 항목의 종류 (FESTIVAL, PRODUCT, SPOT 중 하나)"
    )
    item_id: int = Field(..., description="찜 항목의 고유 ID")

class FavoriteItemOut(BaseModel):
    item_id: int = Field(..., description="찜 항목의 고유 ID")
    item_type: str = Field(..., description="찜 항목의 타입 (FESTIVAL, PRODUCT, SPOT)")
    title: str = Field(..., description="찜 항목의 제목")
    image_url: Optional[str] = Field(None, description="찜 항목의 썸네일 이미지 URL")
    
    class Config:
        from_attributes = True

class FavoriteListResponse(BaseModel):
    festivals: List[FavoriteItemOut] = Field([], description="찜한 축제 목록")
    products: List[FavoriteItemOut] = Field([], description="찜한 마켓 상품 목록")
    spots: List[List[FavoriteItemOut]] = Field([], description="찜한 추천 여행지 목록")