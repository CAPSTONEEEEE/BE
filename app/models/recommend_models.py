from __future__ import annotations
from typing import List, Optional
from enum import Enum
import json

from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_validator
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime

from app.db.database import Base


# =========================
# SQLAlchemy ORM Models
# =========================

class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # JSON 문자열
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)    # JSON 문자열
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())


# =========================
# Pydantic Schemas (API 요청/응답용)
# =========================

class RecommendationBase(BaseModel):
    title: str = Field(..., description="추천 항목 이름")
    description: Optional[str] = Field(None, description="추천 항목 요약 설명")
    reason: Optional[List[str]] = Field(None, description="추천 이유(키 포인트 목록)")
    tags: Optional[List[str]] = Field(None, description="추천 항목 관련 태그 목록")
    image_url: Optional[HttpUrl] = Field(None, description="추천 항목 이미지 URL")

    @field_validator("reason", "tags", mode="before")
    @classmethod
    def serialize_list_to_json(cls, v):
        if isinstance(v, list):
            return json.dumps(v)
        return v

    model_config = ConfigDict(from_attributes=True)


class RecommendationCreate(RecommendationBase):
    title: str = Field(..., description="추천 항목 이름")
    tags: List[str] = Field(..., description="최소 하나 이상의 태그")


class RecommendationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    reason: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    image_url: Optional[HttpUrl] = None

    @field_validator("reason", "tags", mode="before")
    @classmethod
    def serialize_list_to_json(cls, v):
        if isinstance(v, list):
            return json.dumps(v)
        return v


class RecommendationOut(RecommendationBase):
    id: int = Field(..., description="추천 항목 ID")
    created_at: datetime
    updated_at: datetime

    @field_validator("reason", "tags", mode="before")
    @classmethod
    def deserialize_json_to_list(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


# =========================
# 기타 추천 스키마 (랜덤/채팅 추천)
# =========================

class RandomRecommendRequest(BaseModel):
    themes: List[str] = Field(..., description="선택한 테마 목록 (예: 휴양, 액티비티)")


class RandomRecommendResponse(BaseModel):
    message: str = Field(..., description="응답 메시지")
    recommendations: List[RecommendationOut] = Field(..., description="추천된 여행지")


class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    role: ChatRole = Field(..., description="대화 참여자 역할")
    content: str = Field(..., description="메시지 내용")


class ChatRecommendRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="사용자와의 이전 대화 기록")


class ChatRecommendResponse(BaseModel):
    message: str = Field(..., description="응답 메시지")
    recommendations: List[RecommendationOut] = Field(..., description="추천된 여행지")
