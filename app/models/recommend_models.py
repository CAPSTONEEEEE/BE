# backend/app/models/recommend_models.py

from __future__ import annotations
from typing import List, Optional
from enum import Enum
import json

from pydantic import BaseModel, Field, HttpUrl, validator
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime

# 데이터베이스 모델의 기본 클래스를 임포트합니다.
from app.models.common_models import Base


# =========================
# SQLAlchemy ORM Models (데이터베이스 테이블용)
# =========================

class Recommendation(Base):
    """
    추천 데이터를 저장하는 데이터베이스 테이블 모델.
    이 모델은 추천 여행지, 콘텐츠 등 다양한 추천 항목을 담을 수 있습니다.
    """
    __tablename__ = "recommendations"

    # 기본키
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # 추천 항목의 제목
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    # 추천 항목의 요약 설명
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # 추천 이유(키포인트 목록) - JSON 문자열로 저장
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # 태그 목록 - JSON 문자열로 저장
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # 추천 항목의 이미지 URL
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # 생성 시간
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # 업데이트 시간
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())


# =========================
# Pydantic Schemas (API 요청/응답용)
# =========================

class RecommendationBase(BaseModel):
    """추천 항목의 기본 스키마 (생성/업데이트에 사용)"""
    title: str = Field(..., description="추천 항목 이름")
    description: Optional[str] = Field(None, description="추천 항목 요약 설명")
    reason: Optional[List[str]] = Field(None, description="추천 이유(키 포인트 목록)")
    tags: Optional[List[str]] = Field(None, description="추천 항목 관련 태그 목록")
    image_url: Optional[HttpUrl] = Field(None, description="추천 항목 이미지 URL")
    
    # 리스트 데이터를 JSON 문자열로 변환하여 DB에 저장
    @validator('reason', 'tags', pre=True, always=True)
    def serialize_list_to_json(cls, v):
        if isinstance(v, list):
            return json.dumps(v)
        return v
    
    class Config:
        from_attributes = True


class RecommendationCreate(RecommendationBase):
    """추천 항목 생성 스키마"""
    title: str = Field(..., description="추천 항목 이름")
    tags: List[str] = Field(..., description="최소 하나 이상의 태그")


class RecommendationUpdate(BaseModel):
    """추천 항목 업데이트 스키마"""
    title: Optional[str] = None
    description: Optional[str] = None
    reason: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    image_url: Optional[HttpUrl] = None

    # 업데이트 시 리스트 데이터를 JSON 문자열로 변환
    @validator('reason', 'tags', pre=True, always=True)
    def serialize_list_to_json(cls, v):
        if isinstance(v, list):
            return json.dumps(v)
        return v


class RecommendationOut(RecommendationBase):
    """추천 항목 출력 스키마 (ID 포함, DB에서 가져올 때 사용)"""
    id: int = Field(..., description="추천 항목 ID")
    created_at: datetime
    updated_at: datetime

    # DB에 저장된 JSON 문자열을 다시 리스트로 변환
    @validator('reason', 'tags', pre=True, always=True)
    def deserialize_json_to_list(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


# 기타 추천 스키마 (기존 로직 유지)

class RandomRecommendRequest(BaseModel):
    """랜덤 여행지 추천 요청"""
    themes: List[str] = Field(..., description="선택한 테마 목록 (예: 휴양, 액티비티)")


class RandomRecommendResponse(BaseModel):
    """랜덤 여행지 추천 응답"""
    message: str = Field(..., description="응답 메시지")
    recommendations: List[RecommendationOut] = Field(..., description="추천된 여행지")


class ChatRole(str, Enum):
    """대화 참여자의 역할"""
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """채팅 메시지"""
    role: ChatRole = Field(..., description="대화 참여자 역할")
    content: str = Field(..., description="메시지 내용")


class ChatRecommendRequest(BaseModel):
    """대화 기반 여행지 추천 요청"""
    messages: List[ChatMessage] = Field(..., description="사용자와의 이전 대화 기록")


class ChatRecommendResponse(BaseModel):
    """대화 기반 여행지 추천 응답"""
    message: str = Field(..., description="응답 메시지")
    recommendations: List[RecommendationOut] = Field(..., description="추천된 여행지")

