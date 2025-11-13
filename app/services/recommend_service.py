from __future__ import annotations
import os
import json
import random
from typing import List, Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI
from fastapi import HTTPException
from pydantic import BaseModel, Field # 임시로 Pydantic 모델 임포트

# 환경 변수 로드
load_dotenv()

# =========================
# AI 클라이언트 초기화
# =========================

try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    openai_client = AsyncOpenAI(api_key=openai_api_key)
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    openai_client = None

# =========================
# 핵심 추천 서비스 로직
# =========================

async def get_chatbot_response(user_message: str) -> str:
    if not openai_client:
        raise HTTPException(status_code=503, detail="AI 서비스 연결에 문제가 있습니다. API 키를 확인해주세요.")

    system_prompt = (
        "당신은 소도시 여행을 전문적으로 추천해주는 친절한 여행 컨설턴트입니다. "
        "사용자의 요청에 맞춰 한국의 소도시 여행지를 2~3개 추천하고, 그 이유를 간결하게 설명해주세요. "
        "답변은 항상 한국어로 해야 합니다."
    )

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API 호출 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="AI 응답을 처리하는 중 오류가 발생했습니다. 다시 시도해 주세요.")

# 임시 모델 정의 (recommend_models.py가 아직 제대로 연결되지 않았기 때문)
class RecommendationOut(BaseModel):
    id: int = Field(..., description="추천 항목의 고유 ID.")
    title: str = Field(..., description="추천 항목의 제목.")
    description: Optional[str] = Field(None, description="항목에 대한 간략한 설명.")
    image_url: Optional[str] = Field(None, description="항목 이미지의 URL.")
    tags: List[str] = Field([], description="항목과 관련된 태그 목록.")

def get_random_recommendations_from_db(themes: List[str]):
    # 이 부분은 현재 DB 연결이 없으므로 항상 404를 반환하도록 수정했습니다.
    raise HTTPException(status_code=404, detail="No recommendations found for the given themes.")