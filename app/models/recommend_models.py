# backend/app/models/recommend_models.py

from __future__ import annotations
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

# 데이터베이스 모델의 기본 클래스를 임포트
from app.services.common_service import Base


# -------------------------
# Pydantic 모델 (API 요청/응답용)
# -------------------------

class RecommendationItem(BaseModel):
    id: int
    title: str
    location: str
    rating: float

class Keywords(BaseModel):
    keywords: List[str]

class ContentItem(BaseModel):
    title: str
    keywords: List[str]

class GptSummary(BaseModel):
    text: str

class SummaryResponse(BaseModel):
    summary: str

class RandomDestinationResponse(BaseModel):
    title: str


# -------------------------
# SQLAlchemy 모델 (데이터베이스 테이블용)
# -------------------------

class UserKeyword(Base):
    """
    사용자의 관심 키워드를 저장하는 데이터베이스 테이블 모델.
    """
    __tablename__ = "user_keywords"

    # 기본키
    id = Column(Integer, primary_key=True, index=True)
    # 사용자 ID (외래키, 실제 유저 테이블과 연결될 예정)
    user_id = Column(Integer, index=True)
    # 키워드 (쉼표로 구분된 문자열로 저장)
    keywords = Column(String)
    # 생성 시간
    created_at = Column(DateTime, default=datetime.utcnow)
