# backend/app/router/recommend_router.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# APIRouter 객체를 생성합니다.
# tags를 '추천'으로 설정하여 API 문서에서 그룹화되도록 합니다.
router = APIRouter(tags=["추천"])

# Pydantic 모델을 정의합니다.
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


# ---------------------------
# Recommendations
# ---------------------------
@router.get("/recommend", summary="여행지 추천")
def get_recommendations_mock() -> List[RecommendationItem]:
    """
    사용자 맞춤형 여행지 추천 리스트를 반환하는 Mock API입니다.
    """
    # 실제 데이터베이스나 로직 없이 가상의 JSON 데이터를 반환합니다.
    return [
        {"id": 1, "title": "보령 머드 축제", "location": "충남 보령", "rating": 4.8},
        {"id": 2, "title": "전주 한옥마을 투어", "location": "전북 전주", "rating": 4.5},
        {"id": 3, "title": "담양 죽녹원 산책", "location": "전남 담양", "rating": 4.9},
        {"id": 4, "title": "거제도 외도 보타니아", "location": "경남 거제", "rating": 4.7},
    ]


@router.post("/keywords", summary="관심 키워드 설정")
def set_user_keywords_mock(payload: Keywords):
    """
    사용자의 관심 키워드를 설정하는 Mock API입니다.
    """
    # 실제 로직은 여기에 구현됩니다.
    return {"message": "키워드 설정 성공"}


@router.get("/keywords", summary="관심 키워드 기반 추천", response_model=List[ContentItem])
def get_recommendations_by_keywords_mock(keywords: Optional[List[str]] = None) -> List[ContentItem]:
    """
    관심 키워드 기반 콘텐츠를 추천하는 Mock API입니다.
    """
    if keywords is None:
        # 이 부분은 실제로는 422 오류를 반환하게 될 것입니다.
        return []

    # 실제 로직 없이 가상의 데이터를 반환합니다.
    mock_data = {
        "맛집": {"title": "전주 한옥마을 맛집 투어", "keywords": ["전주", "맛집"]},
        "축제": {"title": "함평 나비 대축제", "keywords": ["함평", "축제"]},
        "여행": {"title": "제주도 해안도로 드라이브", "keywords": ["제주도", "여행"]},
    }
    recommended_content = []
    for keyword in keywords:
        if keyword in mock_data:
            recommended_content.append(mock_data[keyword])

    return recommended_content


@router.post("/gpt-summary", summary="GPT 기반 요약", response_model=SummaryResponse)
def get_gpt_summary_mock(payload: GptSummary) -> SummaryResponse:
    """
    GPT를 활용한 콘텐츠 요약 Mock API입니다.
    """
    # 실제 GPT API 호출 없이 가상의 요약 텍스트를 반환합니다.
    dummy_summary = f"'{payload.text[:20]}...'의 내용이 요약되었습니다."
    return SummaryResponse(summary=dummy_summary)


@router.get("/random", summary="랜덤 여행지 추천", response_model=RandomDestinationResponse)
def get_random_destination_mock() -> RandomDestinationResponse:
    """
    랜덤 여행지를 추천하는 Mock API입니다.
    """
    import random
    destinations = [
        "강원도 속초",
        "경상북도 경주",
        "전라남도 여수",
        "충청북도 단양",
        "부산 해운대",
    ]
    random_destination = random.choice(destinations)
    return RandomDestinationResponse(title=random_destination)
