# main.py
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Body, Path, Query
from pydantic import BaseModel, Field

# --- Pydantic 모델 정의 ---
# 요청 및 응답 데이터 유효성 검사를 위해 사용됩니다.
# API 명세서에 맞춰 필요한 모델을 정의합니다.

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

# --- FastAPI 애플리케이션 초기화 ---
app = FastAPI(
    title="소소행 API",
    description="소도시 여행 추천 및 지역 콘텐츠 제공을 위한 RESTful API",
    version="1.0.0"
)

# 임시 데이터베이스 (실제로는 DB 사용)
db_users = {}
db_festivals = {
    "festival-001": Festival(name="논산딸기축제", description="맛있는 딸기 축제입니다.", latitude=36.1, longitude=127.1),
    "festival-002": Festival(name="보령머드축제", description="머드 체험을 즐길 수 있습니다.", latitude=36.3, longitude=126.5),
}
db_products = {
    "prod-001": Product(name="수제 막걸리", price=12000, description="정읍에서 직접 빚은 막걸리", image_url="http://example.com/img1.jpg"),
    "prod-002": Product(name="전통 한지 부채", price=8000, description="수공예 한지 부채", image_url="http://example.com/img2.jpg"),
}
db_favorites = {}

# --- 회원 관리 엔드포인트 ---
@app.post("/users", tags=["회원 관리"])
async def signup(user: UserCreate):
    """
    새로운 사용자 계정을 생성합니다.
    """
    if user.id in db_users:
        raise HTTPException(status_code=409, detail="이미 존재하는 사용자 ID입니다.")
    db_users[user.id] = user
    return {"message": "회원가입 성공", "data": {"id": user.id}}

@app.post("/auth/login", tags=["회원 관리"])
async def login(user: UserLogin):
    """
    사용자 인증 및 토큰을 발급합니다.
    """
    if user.id not in db_users or db_users[user.id].password != user.password:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    # 실제로는 JWT 토큰을 생성하여 반환합니다.
    token = f"dummy_jwt_token_for_{user.id}"
    return {"message": "로그인 성공", "token": token, "data": {"id": user.id}}

@app.get("/users/{user_id}", tags=["회원 관리"])
async def get_user_profile(user_id: str = Path(..., title="사용자 ID")):
    """
    특정 사용자의 프로필 정보를 조회합니다.
    """
    if user_id not in db_users:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    user_data = db_users[user_id]
    return user_data

# --- 추천 및 콘텐츠 조회 엔드포인트 ---
@app.get("/recommend", tags=["추천 및 콘텐츠 조회"])
async def get_recommendations(
    lat: float = Query(..., ge=-90, le=90, description="위도"),
    lng: float = Query(..., ge=-180, le=180, description="경도"),
    themes: Optional[str] = Query(None, description="테마 목록 (쉼표로 구분, 예: family,pet,nature)"),
    dateFrom: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    dateTo: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    radiusKm: int = Query(50, ge=1, le=100, description="반경 (km)"),
    limit: int = Query(20, ge=1, le=50, description="결과 수 제한"),
    minPopularity: Optional[float] = Query(None, ge=0, description="최소 인기 점수")
):
    """
    사용자 위치, 테마, 날짜, 거리 등 필터를 기반으로 콘텐츠를 추천합니다.
    """
    # 실제 추천 로직 (캐시, TourAPI 연동, 스코어링 등)이 여기에 구현됩니다.
    # 이 예시에서는 더미 데이터를 반환합니다.
    return {
        "message": "추천 리스트 조회 성공",
        "data": {
            "items": [
                {
                    "title": "추천 아이템 1",
                    "score": 0.9,
                    "distanceKm": 5.2,
                    "reason": ["가족 친화적", "자연"]
                },
                {
                    "title": "추천 아이템 2",
                    "score": 0.8,
                    "distanceKm": 10.1,
                    "reason": ["자연경관"]
                }
            ]
        }
    }

@app.get("/festivals", tags=["추천 및 콘텐츠 조회"])
async def get_festivals(
    lat: Optional[float] = Query(None, description="위도"),
    lng: Optional[float] = Query(None, description="경도")
):
    """
    전체 축제 목록을 조회하며, 위치 기반 필터를 적용할 수 있습니다.
    """
    # 이 예시에서는 모든 축제를 반환합니다.
    return list(db_festivals.values())

@app.get("/festivals/{festival_id}", tags=["추천 및 콘텐츠 조회"])
async def get_festival_detail(festival_id: str = Path(..., title="축제 ID")):
    """
    특정 축제의 상세 정보를 반환합니다.
    """
    if festival_id not in db_festivals:
        raise HTTPException(status_code=404, detail="해당 축제를 찾을 수 없습니다.")
    return db_festivals[festival_id]

@app.get("/products", tags=["추천 및 콘텐츠 조회"])
async def get_products():
    """
    마켓에 등록된 전체 상품 목록을 조회합니다.
    """
    return list(db_products.values())

@app.get("/products/{product_id}", tags=["추천 및 콘텐츠 조회"])
async def get_product_detail(product_id: str = Path(..., title="상품 ID")):
    """
    특정 상품의 상세 정보를 반환합니다.
    """
    if product_id not in db_products:
        raise HTTPException(status_code=404, detail="해당 상품을 찾을 수 없습니다.")
    return db_products[product_id]

# --- 사용자 상호작용 엔드포인트 ---
@app.get("/users/{user_id}/favorites", tags=["사용자 상호작용"])
async def get_favorites(user_id: str = Path(..., title="사용자 ID")):
    """
    사용자가 찜한 모든 항목(상품, 여행지 등)을 조회합니다.
    """
    return db_favorites.get(user_id, [])

@app.post("/users/{user_id}/favorites/{item_id}", tags=["사용자 상호작용"])
async def add_favorite(
    user_id: str = Path(..., title="사용자 ID"),
    item_id: str = Path(..., title="찜할 아이템 ID")
):
    """
    찜 목록에 특정 아이템을 추가합니다.
    """
    if user_id not in db_favorites:
        db_favorites[user_id] = []
    if item_id not in db_favorites[user_id]:
        db_favorites[user_id].append(item_id)
    return {"message": "찜 목록 추가 성공"}

@app.delete("/users/{user_id}/favorites/{item_id}", tags=["사용자 상호작용"])
async def remove_favorite(
    user_id: str = Path(..., title="사용자 ID"),
    item_id: str = Path(..., title="삭제할 아이템 ID")
):
    """
    찜 목록에서 특정 아이템을 삭제합니다.
    """
    if user_id in db_favorites and item_id in db_favorites[user_id]:
        db_favorites[user_id].remove(item_id)
    return {"message": "찜 목록 삭제 성공"}