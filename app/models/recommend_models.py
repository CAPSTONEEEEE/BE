# app/models/recommend_models.py
from __future__ import annotations
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, Field


# -------------------------
# 공통 (추천 항목 표현)
# -------------------------
class TravelDestination(BaseModel):
    """추천 여행지 정보"""
    title: str = Field(..., description="여행지 이름")
    description: str = Field(..., description="여행지 요약 설명")
    reason: Optional[List[str]] = Field(None, description="추천 이유(키 포인트 목록)")

# -------------------------
# 랜덤 추천
# -------------------------
class RandomRecommendRequest(BaseModel):
    """랜덤 여행지 추천 요청"""
    themes: List[str] = Field(..., description="선택한 테마 목록 (예: 휴양, 액티비티)")

class RandomRecommendResponse(BaseModel):
    """랜덤 여행지 추천 응답"""
    message: str = Field(..., description="응답 메시지")
    recommendations: List[TravelDestination] = Field(..., description="추천된 여행지")

# -------------------------
# 대화 기반 추천
