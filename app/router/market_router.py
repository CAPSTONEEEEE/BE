# app/router/market_router.py
from fastapi import APIRouter

router = APIRouter(prefix="/markets", tags=["markets"])

# Mock 데이터
mock_markets = [
    {
        "id": 1,
        "name": "함평 나비쌀 마켓",
        "description": "전남 함평의 대표 특산물 판매",
        "address": "전라남도 함평군 함평읍",
        "phone": "061-123-4567",
        "products": [
            {"id": 1, "name": "나비쌀 10kg", "price": 35000, "stock": 50},
            {"id": 2, "name": "나비쌀 20kg", "price": 65000, "stock": 30},
        ],
    },
    {
        "id": 2,
        "name": "부산 어묵 마켓",
        "description": "부산 명물 어묵 판매",
        "address": "부산광역시 중구",
        "phone": "051-987-6543",
        "products": [
            {"id": 3, "name": "부산 어묵 세트", "price": 20000, "stock": 100},
            {"id": 4, "name": "특선 어묵 모듬", "price": 30000, "stock": 80},
        ],
    },
]


@router.get("/")
def list_markets():
    """모든 로컬 마켓 목록"""
    return mock_markets


@router.get("/{market_id}")
def get_market(market_id: int):
    """특정 마켓 상세 조회"""
    market = next((m for m in mock_markets if m["id"] == market_id), None)
    return market or {"error": "Market not found"}
