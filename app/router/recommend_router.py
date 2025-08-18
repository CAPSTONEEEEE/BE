# backend/app/router/recommend_router.py

from fastapi import APIRouter

# APIRouter 객체를 생성합니다.
# tags를 '추천'으로 설정하여 API 문서에서 그룹화되도록 합니다.
router = APIRouter(tags=["추천"])

@router.get("/recommend")
def get_recommendations_mock():
    """
    사용자 맞춤형 여행지 추천 리스트를 반환하는 Mock API입니다.
    """
    # 실제 데이터베이스나 로직 없이 가상의 JSON 데이터를 반환합니다.
    return [
        {"id": 1, "title": "보령 머드 축제", "location": "충남 보령", "rating": 4.8},
        {"id": 2, "title": "전주 한옥마을 투어", "location": "전북 전주", "rating": 4.5},
        {"id": 3, "title": "담양 죽녹원 산책", "location": "전남 담양", "rating": 4.9},
        {"id": 4, "title": "거제도 외도 보타니아", "location": "경남 거제", "rating": 4.7},
    ]

