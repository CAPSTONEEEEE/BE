# app/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional

## 1. 챗봇 스키마
# 챗봇에 전송하는 사용자의 메시지 모델입니다.
class ChatbotRequest(BaseModel):
    message: str = Field(..., description="챗봇에게 보낼 사용자의 메시지.")

# 챗봇의 단순 텍스트 응답 모델입니다.
class ChatbotResponse(BaseModel):
    response: str = Field(..., description="챗봇의 텍스트 응답.")


## 2. 추천 스키마
# 단일 추천 항목(여행지, 상품 등)을 위한 모델입니다.
class RecommendationOut(BaseModel):
    id: int = Field(..., description="추천 항목의 고유 ID.")
    title: str = Field(..., description="추천 항목의 제목.")
    description: Optional[str] = Field(None, description="항목에 대한 간략한 설명.")
    image_url: Optional[str] = Field(None, description="항목 이미지의 URL.")
    tags: List[str] = Field([], description="항목과 관련된 태그 목록.")

# 랜덤 추천 API의 요청 본문 모델입니다.
class RandomRecommendRequest(BaseModel):
    themes: List[str] = Field(..., description="사용자가 선택한 테마 목록.")

# 랜덤 추천 API의 전체 응답 모델입니다.
class RandomRecommendResponse(BaseModel):
    message: str = Field("랜덤 여행지 추천이 완료되었습니다.", description="응답 상태 메시지.")
    recommendations: List[RecommendationOut] = Field([], description="추천된 여행지 목록.")

## 3. 챗봇-추천 결합 스키마
# 챗봇의 응답과 함께 추천 목록도 포함하는 고급 모델입니다.
# 챗봇이 특정 여행지를 추천할 때 사용될 수 있습니다.
class ChatRecommendResponse(BaseModel):
    response: str = Field(..., description="챗봇의 텍스트 응답.")
    recommendations: List[RecommendationOut] = Field([], description="추천된 여행지 목록.")