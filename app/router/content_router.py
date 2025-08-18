# backend/app/router/content_router.py

from typing import Optional
from fastapi import APIRouter, HTTPException, Path, Query
from app.models import Festival, Product, Review, Recommendation

# APIRouter 객체 생성
router = APIRouter(tags=["추천 및 콘텐츠 조회", "사용자 상호작용"])

# 임시 데이터베이스 (실제로는 DB 사용)
db_festivals = {
    "festival-001": Festival(name="논산딸기축제", description="맛있는 딸기 축제입니다.", latitude=36.1, longitude=127.1),
    "festival-002": Festival(name="보령머드축제", description="머드 체험을 즐길 수 있습니다.", latitude=36.3, longitude=126.5),
}
db_products = {
    "prod-001": Product(name="수제 막걸리", price=12000, description="정읍에서 직접 빚은 막걸리", image_url="http://example.com/img1.jpg"),
    "prod-002": Product(name="전통 한지 부채", price=8000, description="수공예 한지 부채", image_url="http://example.com/img2.jpg"),
}
db_favorites = {}

# --- 추천 및 콘텐츠 조회 엔드포인트 ---
@router.get("/recommend")
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

@router.get("/festivals")
async def get_festivals(
    lat: Optional[float] = Query(None, description="위도"),
    lng: Optional[float] = Query(None, description="경도")
):
    """
    전체 축제 목록을 조회하며, 위치 기반 필터를 적용할 수 있습니다.
    """
    return list(db_festivals.values())

@router.get("/festivals/{festival_id}")
async def get_festival_detail(festival_id: str = Path(..., title="축제 ID")):
    """
    특정 축제의 상세 정보를 반환합니다.
    """
    if festival_id not in db_festivals:
        raise HTTPException(status_code=404, detail="해당 축제를 찾을 수 없습니다.")
    return db_festivals[festival_id]

@router.get("/products")
async def get_products():
    """
    마켓에 등록된 전체 상품 목록을 조회합니다.
    """
    return list(db_products.values())

@router.get("/products/{product_id}")
async def get_product_detail(product_id: str = Path(..., title="상품 ID")):
    """
    특정 상품의 상세 정보를 반환합니다.
    """
    if product_id not in db_products:
        raise HTTPException(status_code=404, detail="해당 상품을 찾을 수 없습니다.")
    return db_products[product_id]

@router.get("/users/{user_id}/favorites", tags=["사용자 상호작용"])
async def get_favorites(user_id: str = Path(..., title="사용자 ID")):
    """
    사용자가 찜한 모든 항목(상품, 여행지 등)을 조회합니다.
    """
    return db_favorites.get(user_id, [])

@router.post("/users/{user_id}/favorites/{item_id}", tags=["사용자 상호작용"])
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

@router.delete("/users/{user_id}/favorites/{item_id}", tags=["사용자 상호작용"])
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
