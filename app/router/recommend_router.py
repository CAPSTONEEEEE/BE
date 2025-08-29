# backend/app/router/recommend_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

# 필요한 Pydantic 모델과 서비스, 데이터베이스 함수를 임포트합니다.
from app.models.recommend_models import (
    RecommendationOut,
    RecommendationCreate,
    RecommendationUpdate,
    RandomRecommendRequest,
    RandomRecommendResponse,
    ChatRecommendRequest,
    ChatRecommendResponse,
)
from app.services.recommend_service import RecommendationService
from app.database import get_db


# APIRouter 객체를 생성합니다.
# tags를 '추천'으로 설정하여 API 문서에서 그룹화되도록 합니다.
router = APIRouter(tags=["추천"])


# --------------------------
# CRUD Endpoints
# --------------------------
@router.post("/recommendations", summary="추천 항목 생성", response_model=RecommendationOut, status_code=status.HTTP_201_CREATED)
def create_recommendation(
    item_data: RecommendationCreate,
    db: Session = Depends(get_db)
):
    """새로운 추천 항목을 생성합니다."""
    service = RecommendationService(db)
    return service.create_recommendation(item_data)


@router.get("/recommendations", summary="모든 추천 항목 조회", response_model=List[RecommendationOut])
def get_all_recommendations(db: Session = Depends(get_db)):
    """데이터베이스에 있는 모든 추천 항목을 조회합니다."""
    service = RecommendationService(db)
    return service.get_all_recommendations()


@router.get("/recommendations/{item_id}", summary="특정 추천 항목 조회", response_model=RecommendationOut)
def get_recommendation_by_id(item_id: int, db: Session = Depends(get_db)):
    """ID로 특정 추천 항목을 조회합니다."""
    service = RecommendationService(db)
    return service.get_recommendation_by_id(item_id)


@router.put("/recommendations/{item_id}", summary="추천 항목 업데이트", response_model=RecommendationOut)
def update_recommendation(
    item_id: int,
    item_data: RecommendationUpdate,
    db: Session = Depends(get_db)
):
    """특정 추천 항목을 업데이트합니다."""
    service = RecommendationService(db)
    return service.update_recommendation(item_id, item_data)


@router.delete("/recommendations/{item_id}", summary="추천 항목 삭제", status_code=status.HTTP_204_NO_CONTENT)
def delete_recommendation(item_id: int, db: Session = Depends(get_db)):
    """특정 추천 항목을 삭제합니다."""
    service = RecommendationService(db)
    service.delete_recommendation(item_id)
    return {"message": "Recommendation deleted successfully"}


# --------------------------
# Recommendation Logic Endpoints (기존 로직)
# --------------------------
@router.post("/random", summary="랜덤 여행지 추천", response_model=RandomRecommendResponse)
def get_random_recommendations(
    request: RandomRecommendRequest,
    db: Session = Depends(get_db)
):
    """
    사용자가 선택한 테마에 따라 랜덤으로 여행지를 추천합니다.
    """
    service = RecommendationService(db)
    return service.get_random_recommendations(request.themes)


@router.post("/chat", summary="대화 기반 여행지 추천", response_model=ChatRecommendResponse)
def get_chat_recommendations(
    request: ChatRecommendRequest,
    db: Session = Depends(get_db)
):
    """
    대화 기록을 바탕으로 맞춤형 여행지를 추천합니다.
    """
    service = RecommendationService(db)
    return service.get_chat_recommendations(request)
