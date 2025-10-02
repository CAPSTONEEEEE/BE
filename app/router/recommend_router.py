# app/router/recommend_router.py

# 1. 필요한 라이브러리 및 스키마 임포트
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional

from app.schemas import (
    ChatbotRequest,         
    RecommendationOut,
    RandomRecommendRequest,
    RandomRecommendResponse,
    ChatRecommendResponse,
)

from app.services.recommend_service import (
    get_chatbot_response,
    get_random_recommendations_from_db
)

# 2. APIRouter 인스턴스 정의 (가장 중요)
# 모든 라우트(경로)를 정의하기 전에 반드시 이 부분이 와야 합니다.
router = APIRouter(tags=["추천"])


# 3. 라우터 엔드포인트 정의
# AI 챗봇 엔드포인트
@router.post("/chatbot", summary="AI 챗봇과 대화", response_model=ChatRecommendResponse)
async def chatbot_endpoint(request: ChatbotRequest):
    try:
        ai_response_text = await get_chatbot_response(request.message)
        
        return ChatRecommendResponse(
            response=ai_response_text,
            recommendations=[]
        )
    except HTTPException as e:
        raise e

# 랜덤 추천 엔드포인트
@router.post("/random_recommendations", summary="랜덤 여행지 추천", response_model=RandomRecommendResponse)
def get_random_recommendations(request: RandomRecommendRequest):
    try:
        recommendations = get_random_recommendations_from_db(themes=request.themes)
        
        return RandomRecommendResponse(
            message="랜덤 여행지 추천이 완료되었습니다.",
            recommendations=recommendations
        )
    except HTTPException as e:
        raise e