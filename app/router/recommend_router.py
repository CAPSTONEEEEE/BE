# backend/app/router/recommend_router.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.services.common_service import get_db

from app.models.recommend_models import (
    Keywords, ContentItem, GptSummary, SummaryResponse, RandomDestinationResponse, RecommendationItem
)
from app.services.recommend_service import RecommendationService


# APIRouter 객체를 생성합니다.
# tags를 '추천'으로 설정하여 API 문서에서 그룹화되도록 합니다.
router = APIRouter(tags=["추천"])

# ---------------------------
# Recommendations
# ---------------------------
@router.get("/recommend", summary="여행지 추천", response_model=List[RecommendationItem])
def get_recommendations_mock():
    """
    사용자 맞춤형 여행지 추천 리스트를 반환하는 Mock API입니다.
    """
    # 이 엔드포인트는 Mock을 유지합니다.
    return [
        {"id": 1, "title": "보령 머드 축제", "location": "충남 보령", "rating": 4.8},
        {"id": 2, "title": "전주 한옥마을 투어", "location": "전북 전주", "rating": 4.5},
        {"id": 3, "title": "담양 죽녹원 산책", "location": "전남 담양", "rating": 4.9},
        {"id": 4, "title": "거제도 외도 보타니아", "location": "경남 거제", "rating": 4.7},
    ]


@router.post("/keywords", summary="관심 키워드 설정")
def set_user_keywords(payload: Keywords, db: Session = Depends(get_db)):
    """
    사용자의 관심 키워드를 데이터베이스에 저장하는 API입니다.
    """
    service = RecommendationService(db)
    # user_id는 임시로 1을 사용합니다.
    return service.set_user_keywords(user_id=1, keywords=payload.keywords)


@router.get("/keywords", summary="관심 키워드 기반 추천")
def get_recommendations_by_keywords(db: Session = Depends(get_db)):
    """
    데이터베이스에 저장된 키워드를 기반으로 콘텐츠를 추천하는 API입니다.
    """
    service = RecommendationService(db)
    # user_id는 임시로 1을 사용합니다.
    return service.get_recommendations_by_keywords(user_id=1)


@router.post("/gpt-summary", summary="GPT 기반 요약")
async def get_gpt_summary(payload: GptSummary):
    """
    GPT를 활용한 콘텐츠 요약 API입니다.
    """
    service = RecommendationService(db=None)  # 이 기능은 DB를 사용하지 않아 None을 전달
    return await service.get_gpt_summary(text=payload.text)


@router.get("/random", summary="랜덤 여행지 추천")
def get_random_destination():
    """
    랜덤 여행지를 추천하는 API입니다.
    """
    service = RecommendationService(db=None)  # 이 기능은 DB를 사용하지 않아 None을 전달
    return service.get_random_destination()
