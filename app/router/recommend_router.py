# API 엔드포인트를 정의하고 요청을 서비스 계층으로 연결

from fastapi import APIRouter, HTTPException, Depends
from .recommend_models import (
    RandomRecommendRequest,
    RandomRecommendResponse,
    ChatRecommendRequest,
    ChatRecommendResponse,
)
from .recommend_service import RecommendationService

router = APIRouter(prefix="/recommend", tags=["추천"])

# RecommendationService 인스턴스 생성
recommender = RecommendationService()

@router.post("/random", response_model=RandomRecommendResponse)
async def recommend_random(request: RandomRecommendRequest):
    """
    **랜덤 여행지 추천**
    
    사용자가 선택한 테마를 기반으로 지역에 상관없이 무작위 여행지를 추천합니다.
    """
    try:
        return await recommender.get_random_recommendations(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatRecommendResponse)
async def recommend_chat(request: ChatRecommendRequest):
    """
    **사용자 맞춤형 여행지 추천**
    
    챗봇과 대화하며 수집한 취향 정보를 기반으로 OpenAI API를 이용해 여행지를 추천합니다.
    """
    try:
        return await recommender.get_chat_recommendations(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
