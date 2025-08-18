# app/router/recommend_router.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends

# 절대경로로 통일
from app.models.recommend_models import (
    RandomRecommendRequest,
    RandomRecommendResponse,
    ChatRecommendRequest,
    ChatRecommendResponse,
)
from app.services.recommend_service import RecommendationService
# 필요 시 DB 의존성 주입 가능 (서비스가 DB를 사용한다면 주석 해제)
# from app.services.common_service import get_db
# from sqlalchemy.orm import Session

router = APIRouter(prefix="/recommend", tags=["recommend"])

# 서비스 인스턴스는 라우터 모듈 레벨에서 1회 생성
recommender = RecommendationService()

@router.post("/random", response_model=RandomRecommendResponse, summary="랜덤 여행지 추천")
async def recommend_random(request: RandomRecommendRequest):
    """
    사용자가 선택한 테마를 기반으로 지역 무관 랜덤 추천을 제공합니다.
    """
    try:
        # db: Session = Depends(get_db) 가 필요하다면 시그니처에 추가
        return await recommender.get_random_recommendations(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"recommend_random failed: {e}")

@router.post("/chat", response_model=ChatRecommendResponse, summary="대화 기반 맞춤 추천")
async def recommend_chat(request: ChatRecommendRequest):
    """
    대화에서 수집한 선호도를 기반으로 OpenAI를 이용해 맞춤 여행지를 추천합니다.
    """
    try:
        return await recommender.get_chat_recommendations(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"recommend_chat failed: {e}")
