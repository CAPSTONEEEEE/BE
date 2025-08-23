# backend/app/services/recommend_service.py

from __future__ import annotations
import os
import random
from typing import List, Optional
import json
import asyncio

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.recommend_models import UserKeyword
from app.services.common_service import SessionLocal, Base, engine

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# ----------------------------------------------------
# Pydantic 모델은 recommend_models.py에 이미 정의되어 있습니다.
# ----------------------------------------------------

# GPT API 호출을 위한 설정 (API 키가 없으면 더미 응답으로 대체)
_OPENAI_AVAILABLE = True
try:
    from openai import AsyncOpenAI  # type: ignore
except ImportError:
    _OPENAI_AVAILABLE = False
    
def _get_openai_client() -> Optional["AsyncOpenAI"]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not _OPENAI_AVAILABLE or not api_key:
        return None
    return AsyncOpenAI(api_key=api_key)


class RecommendationService:
    """
    여행지 추천 관련 비즈니스 로직 서비스
    """

    def __init__(self, db: Session):
        self.db = db
        self.openai_client = _get_openai_client()

    def set_user_keywords(self, user_id: int, keywords: List[str]):
        """
        사용자의 관심 키워드를 데이터베이스에 저장하거나 업데이트합니다.
        """
        # 기존 키워드 확인 (임시로 user_id=1 가정)
        user_keywords = self.db.query(UserKeyword).filter(UserKeyword.user_id == user_id).first()
        
        if user_keywords:
            # 기존 키워드가 있으면 업데이트
            user_keywords.keywords = ','.join(keywords)
            self.db.commit()
            self.db.refresh(user_keywords)
        else:
            # 없으면 새로 생성
            new_keywords = UserKeyword(user_id=user_id, keywords=','.join(keywords))
            self.db.add(new_keywords)
            self.db.commit()
            self.db.refresh(new_keywords)
        
        return {"message": "키워드 설정 성공"}

    def get_recommendations_by_keywords(self, user_id: int):
        """
        데이터베이스에 저장된 키워드를 바탕으로 콘텐츠를 추천합니다.
        (현재는 Mock 데이터 사용)
        """
        # 데이터베이스에서 사용자의 키워드 조회 (임시로 user_id=1 가정)
        user_keywords_db = self.db.query(UserKeyword).filter(UserKeyword.user_id == user_id).first()
        if not user_keywords_db:
            return {"message": "저장된 키워드가 없습니다."}

        user_keywords = user_keywords_db.keywords.split(',')

        # 실제로는 이 부분에서 데이터베이스 쿼리를 통해 콘텐츠를 찾습니다.
        # 예시: self.db.query(Content).filter(Content.keywords.overlaps(user_keywords))
        
        mock_data = [
            {"title": "전주 한옥마을 맛집 투어", "keywords": ["전주", "맛집"]},
            {"title": "함평 나비 대축제", "keywords": ["함평", "축제"]},
            {"title": "제주도 해안도로 드라이브", "keywords": ["제주도", "여행"]},
        ]
        
        recommended_content = []
        for item in mock_data:
            if any(keyword in user_keywords for keyword in item['keywords']):
                recommended_content.append(item)
                
        return {"message": "추천 콘텐츠 리스트 조회 성공", "data": recommended_content}

    async def get_gpt_summary(self, text: str):
        """
        GPT를 활용하여 텍스트를 요약합니다.
        """
        # 실제 GPT API 호출 로직
        if self.openai_client:
            try:
                prompt = f"다음 텍스트를 3문장 이내로 요약해줘:\n\n{text}"
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100
                )
                summary = response.choices[0].message.content.strip()
                return {"message": "텍스트 요약 성공", "data": {"summary": summary}}
            except Exception as e:
                print(f"[OpenAI API Error] {e} - Falling back to mock data.")
                # API 호출 실패 시 더미 데이터로 대체
                dummy_summary = f"'{text[:20]}...' 의 내용이 요약되었습니다."
                return {"message": "텍스트 요약 성공", "data": {"summary": dummy_summary}}
        else:
            # API 키가 없거나 라이브러리가 설치되지 않은 경우
            dummy_summary = f"'{text[:20]}...' 의 내용이 요약되었습니다."
            return {"message": "텍스트 요약 성공", "data": {"summary": dummy_summary}}


    def get_random_destination(self):
        """
        랜덤 여행지를 추천합니다.
        """
        destinations = [
            "강원도 속초",
            "경상북도 경주",
            "전라남도 여수",
            "충청북도 단양",
            "부산 해운대",
        ]
        random_destination = random.choice(destinations)
        return {"message": "랜덤 여행지 추천 성공", "data": {"title": random_destination}}

