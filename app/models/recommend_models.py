# API 요청 및 응답에 사용될 Pydantic 데이터 모델 정의

from typing import List, Optional
from pydantic import BaseModel, Field

# --- 공통 모델 ---
class TravelDestination(BaseModel):
    """추천 여행지 정보 모델"""
    title: str = Field(..., description="여행지 이름")
    description: str = Field(..., description="여행지 요약 설명")
    reason: Optional[List[str]] = Field(None, description="추천 이유")

# --- 랜덤 여행지 추천 모델 ---
class RandomRecommendRequest(BaseModel):
    """랜덤 여행지 추천 요청 모델"""
    themes: List[str] = Field(..., description="사용자가 선택한 여행 테마 목록 (예: '휴양', '액티비티')")

class RandomRecommendResponse(BaseModel):
    """랜덤 여행지 추천 응답 모델"""
    message: str = Field(..., description="응답 메시지")
    recommendations: List[TravelDestination] = Field(..., description="추천된 여행지 목록")

# --- 챗봇 기반 여행지 추천 모델 ---
class ChatMessage(BaseModel):
    """챗봇 대화 메시지 모델"""
    role: str = Field(..., description="메시지 역할 (user 또는 assistant)")
    content: str = Field(..., description="메시지 내용")

class ChatRecommendRequest(BaseModel):
    """챗봇 기반 추천 요청 모델"""
    conversation: List[ChatMessage] = Field(..., description="대화 기록")
    user_id: Optional[str] = Field(None, description="사용자 ID (필요시)")

class ChatRecommendResponse(BaseModel):
    """챗봇 기반 추천 응답 모델"""
    message: str = Field(..., description="응답 메시지")
    recommendations: List[TravelDestination] = Field(..., description="추천된 여행지 목록")