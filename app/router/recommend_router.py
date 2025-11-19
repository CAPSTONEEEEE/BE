# app/router/recommend_router.py

# 1. 필요한 라이브러리 및 스키마 임포트
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional

from app.schemas import (
    ChatbotRequest,       
    RandomRecommendRequest,
    RandomRecommendResponse,
    ChatRecommendResponse,
)

from app.services.recommend_service import (
    get_chatbot_search_keywords_and_recommendations
)

# 2. APIRouter 인스턴스 정의 (가장 중요)
# 모든 라우트(경로)를 정의하기 전에 반드시 이 부분이 와야 합니다.
router = APIRouter(tags=["추천"])


# 3. 라우터 엔드포인트 정의
# AI 챗봇 엔드포인트
@router.post("/chatbot", summary="RAG 기반 AI 챗봇 추천", response_model=ChatRecommendResponse)
async def chatbot_endpoint(request: ChatbotRequest):
    try:
        # 새로운 RAG 서비스 함수 호출 및 결과 수신
        result = await get_chatbot_search_keywords_and_recommendations(request.message)
        
        # result는 dict 형태로 {"ai_response_text": ..., "db_recommendations": ...}를 포함함
        # 수신된 결과를 ChatRecommendResponse 스키마에 맞춰 반환
        return ChatRecommendResponse(
            response=result["ai_response_text"],
            recommendations=result["db_recommendations"] # DB 검색 결과(TourInfoOut 리스트)
        )
    except HTTPException as e:
        # 이미 처리된 HTTP 예외는 그대로 raise
        raise e
    except Exception as e:
        # ⚠️ 예상치 못한 일반 예외(OpenAI 통신 오류 등) 발생 시 500 처리
        print(f"챗봇 라우터 내부 오류: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"챗봇 서비스 처리 중 알 수 없는 서버 오류가 발생했습니다. 상세: {e.__class__.__name__}"
        )

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