# app/services/recommend_service.py
from __future__ import annotations

import os
import json
import random
import asyncio
from typing import List, Optional

from fastapi import HTTPException

from app.models.recommend_models import (
    RandomRecommendRequest,
    RandomRecommendResponse,
    ChatRecommendRequest,
    ChatRecommendResponse,
    TravelDestination,
    ChatRole,
)

# OpenAI (선택 의존) — 없거나 키 미설정이면 더미 응답으로 폴백
_OPENAI_AVAILABLE = True
try:
    from openai import AsyncOpenAI  # type: ignore
except Exception:
    _OPENAI_AVAILABLE = False


def _get_openai_client() -> Optional["AsyncOpenAI"]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not _OPENAI_AVAILABLE or not api_key:
        return None
    return AsyncOpenAI(api_key=api_key)


class RecommendationService:
    """
    여행지 추천 로직 서비스
    - 랜덤 추천: 내부 더미 데이터에서 샘플링
    - 대화 기반 추천: OpenAI 호출(가능 시) 또는 더미 응답
    """

    # 임시 데이터셋 (테마별 후보)
    DUMMY_DATA = {
        "휴양": [
            {"title": "제주도 서귀포", "description": "아름다운 해변과 조용한 분위기의 휴양지"},
            {"title": "강릉 경포호", "description": "호수와 바다가 어우러진 평화로운 산책 코스"},
            {"title": "여수 돌산도", "description": "밤바다 야경이 아름답고 휴식에 제격"},
        ],
        "액티비티": [
            {"title": "속초 설악산", "description": "등산/케이블카로 즐기는 아웃도어 액티비티"},
            {"title": "양양 서핑 해변", "description": "파도가 좋아 서핑 입문/숙련 모두 추천"},
            {"title": "단양 패러글라이딩", "description": "창공에서 만나는 남한강 풍경"},
        ],
        "전시/관람형": [
            {"title": "서울 예술의전당", "description": "다양한 공연/전시를 즐길 수 있는 복합 문화 공간"},
            {"title": "전주 한옥마을", "description": "전통 한옥과 골목 산책, 먹거리 탐방"},
            {"title": "부산 영화의 전당", "description": "국제영화제의 열기를 느끼는 명소"},
        ],
        "이색 체험": [
            {"title": "담양 죽녹원", "description": "대나무 숲길 힐링과 이색 포토스팟"},
            {"title": "평창 양떼목장", "description": "초원에서 양들과 교감하는 체험"},
            {"title": "안동 하회마을", "description": "전통 민속마을에서의 고즈넉한 시간"},
        ],
    }

    async def get_random_recommendations(
        self, request: RandomRecommendRequest
    ) -> RandomRecommendResponse:
        # 테마 매칭 후보 수집
        candidates: List[TravelDestination] = []
        for theme in request.themes:
            if theme in self.DUMMY_DATA:
                for d in self.DUMMY_DATA[theme]:
                    candidates.append(
                        TravelDestination(
                            title=d["title"],
                            description=d["description"],
                            reason=[theme],
                        )
                    )

        # 부족하면 전체에서 보충
        if len(candidates) < 5:
            all_items = [
                TravelDestination(title=itm["title"], description=itm["description"])
                for items in self.DUMMY_DATA.values()
                for itm in items
            ]
            final = random.sample(all_items, k=min(5, len(all_items)))
        else:
            final = random.sample(candidates, k=5)

        return RandomRecommendResponse(
            message="랜덤 여행지 추천이 완료되었습니다.",
            recommendations=final,
        )

    async def get_chat_recommendations(
        self, request: ChatRecommendRequest
    ) -> ChatRecommendResponse:
        user_message = (
            request.conversation[-1].content if request.conversation else ""
        )

        client = _get_openai_client()
        if client:
            # OpenAI 호출(가능한 경우)
            try:
                prompt = (
                    "다음 사용자의 선호와 대화를 바탕으로 한국 내 여행지 3곳을 추천해줘. "
                    "각 여행지는 title, description, reason(키워드 배열) 필드를 포함해 JSON 배열로만 응답해.\n\n"
                    f"사용자 마지막 메시지: {user_message}"
                )
                # gpt-4o-mini 등 경량 모델을 추천(실제 배포 환경에 맞춰 설정)
                model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

                resp = await client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful travel assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                )
                content = resp.choices[0].message.content  # type: ignore[attr-defined]
                data = json.loads(content)

                recs = [
                    TravelDestination(
                        title=item.get("title", "추천 여행지"),
                        description=item.get("description", ""),
                        reason=item.get("reason", []),
                    )
                    for item in data
                ]

                return ChatRecommendResponse(
                    message="대화 기반 맞춤형 여행지 추천이 완료되었습니다.",
                    recommendations=recs,
                )
            except Exception as e:
                # OpenAI 실패 → 더미로 폴백
                print(f"[OpenAI error] {e} — fallback to dummy")
                # 잠깐 대기(실패 시 딜레이가 있었다고 가정)
                await asyncio.sleep(0.5)

        # 폴백 응답(키 미설정/라이브러리 없음/에러)
        dummy = [
            TravelDestination(
                title="서울 익선동 한옥마을",
                description="복고풍 감성과 현대적 감성이 공존하는 골목 산책 코스",
                reason=["도시", "레트로", "맛집"],
            ),
            TravelDestination(
                title="인제 자작나무 숲",
                description="사계절 내내 은은한 자작나무 숲에서 힐링 산책",
                reason=["자연", "힐링", "산책"],
            ),
            TravelDestination(
                title="군산 근대역사박물관",
                description="근대사 전시로 역사적 배경을 배우기 좋은 실내 명소",
                reason=["역사", "교육", "실내"],
            ),
        ]
        return ChatRecommendResponse(
            message="(폴백) 대화 기반 맞춤형 여행지 추천이 완료되었습니다.",
            recommendations=dummy,
        )
