# backend/app/services/recommend_service.py

from __future__ import annotations
import os
import json
import random
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.recommend_models import (
    Recommendation,
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationOut,
    RandomRecommendRequest,
    RandomRecommendResponse,
    ChatRecommendRequest,
    ChatRecommendResponse,
)
from fastapi import HTTPException


# =========================
# RecommendationService
# =========================

class RecommendationService:
    """
    추천 관련 비즈니스 로직 서비스.
    - 데이터베이스와 직접 연동하여 추천 항목에 대한 CRUD 기능을 제공합니다.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_all_recommendations(self) -> List[Recommendation]:
        """모든 추천 항목을 조회합니다."""
        return self.db.query(Recommendation).all()

    def get_recommendation_by_id(self, item_id: int) -> Optional[Recommendation]:
        """ID로 특정 추천 항목을 조회합니다. 없으면 None 반환."""
        item = self.db.query(Recommendation).filter(Recommendation.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        return item

    def create_recommendation(self, item_data: RecommendationCreate) -> Recommendation:
        """새로운 추천 항목을 생성합니다."""
        # Pydantic 모델의 데이터를 DB 모델에 맞게 변환
        db_item = Recommendation(**item_data.model_dump())
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update_recommendation(self, item_id: int, item_data: RecommendationUpdate) -> Recommendation:
        """기존 추천 항목을 업데이트합니다."""
        db_item = self.get_recommendation_by_id(item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        # Pydantic 모델에서 변경된 필드만 추출하여 업데이트
        update_data = item_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def delete_recommendation(self, item_id: int):
        """추천 항목을 삭제합니다."""
        db_item = self.get_recommendation_by_id(item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        self.db.delete(db_item)
        self.db.commit()
        return {"message": "Recommendation deleted successfully"}

    def get_random_recommendations(self, themes: List[str]) -> RandomRecommendResponse:
        """
        선택된 테마에 기반한 랜덤 여행지 추천 알고리즘을 구현합니다.
        """
        if not themes:
            raise HTTPException(status_code=400, detail="Themes list cannot be empty")
        
        # `or_` 연산자를 사용하여 여러 테마에 해당하는 항목을 조회
        filters = [Recommendation.tags.like(f'%"{theme}"%') for theme in themes]
        recommendation_candidates = self.db.query(Recommendation).filter(or_(*filters)).all()

        if not recommendation_candidates:
            raise HTTPException(status_code=404, detail="No recommendations found for the given themes")

        # 후보가 4개 이상이면 무작위로 4개만 선택, 아니면 전체 반환
        if len(recommendation_candidates) > 4:
            final_recommendations = random.sample(recommendation_candidates, 4)
        else:
            final_recommendations = recommendation_candidates

        # Pydantic 모델로 변환
        recommendations_out = [RecommendationOut.model_validate(rec) for rec in final_recommendations]

        return RandomRecommendResponse(
            message="랜덤 여행지 추천이 완료되었습니다.",
            recommendations=recommendations_out,
        )

    # 이 부분은 대화 기반 추천 로직이 들어갈 곳입니다.
    # 기존 코드와 같이 OpenAI API를 활용하거나, 키워드 매칭 로직으로 구현할 수 있습니다.
    async def get_chat_recommendations(self, request: ChatRecommendRequest) -> ChatRecommendResponse:
        """
        대화 기록을 바탕으로 맞춤형 여행지를 추천합니다.
        """
        # 현재는 더미 응답으로 폴백
        dummy_data = [
            Recommendation(title="서울 익선동 한옥마을", description="복고풍 감성", tags=json.dumps(["도시", "레트로"])),
            Recommendation(title="인제 자작나무 숲", description="힐링 산책", tags=json.dumps(["자연", "힐링"])),
        ]
        recommendations_out = [RecommendationOut.model_validate(rec) for rec in dummy_data]
        return ChatRecommendResponse(
            message="대화 기반 맞춤형 여행지 추천이 완료되었습니다.",
            recommendations=recommendations_out
        )

