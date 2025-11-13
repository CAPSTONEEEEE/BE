from __future__ import annotations
import os
import json
import random
from typing import List, Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI
from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.db.database import SessionLocal 
from app.models.recommend_models import RecommendTourInfo, TourInfoOut # ORM 모델 및 스키마 임포트
from sqlalchemy.orm import Session
from sqlalchemy import or_

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

# DB에서 관광지 정보를 검색하는 함수 추가
def get_tour_info_by_keywords(db: Session, keywords: List[str]) -> List[TourInfoOut]:
    """
    키워드를 사용하여 recommend_tourInfo 테이블에서 관광지 정보를 검색합니다.
    (예시: title, cat1, cat2, cat3에 키워드가 포함된 경우)
    """
    if not keywords:
        return []
        
    search_filters = []
    for keyword in keywords:
        # DB 필드에 키워드가 포함되는 OR 조건을 생성
        search_filters.append(RecommendTourInfo.title.like(f"%{keyword}%"))
        search_filters.append(RecommendTourInfo.cat1.like(f"%{keyword}%"))
        search_filters.append(RecommendTourInfo.cat2.like(f"%{keyword}%"))
        search_filters.append(RecommendTourInfo.cat3.like(f"%{keyword}%"))
        
    # 모든 키워드에 대해 OR 조건으로 검색
    db_results = db.query(RecommendTourInfo).filter(or_(*search_filters)).limit(5).all()
    
    # ORM 모델을 Pydantic 스키마로 변환
    return [TourInfoOut.model_validate(item) for item in db_results]


# 핵심 RAG 로직을 수행하는 함수 (기존 get_chatbot_response 대체)
async def get_chatbot_search_keywords_and_recommendations(user_message: str):
    if not openai_client:
        raise HTTPException(status_code=503, detail="AI 서비스 연결에 문제가 있습니다.")

    # 1. GPT 시스템/사용자 프롬프트 구성 (요청하신 형식 반영)
    
    # NOTE: 사용자 메시지에 따라 {age}, {relation} 등의 값을 파싱해야 하지만, 
    # 현재는 전체 메시지를 하나의 {user_message}로 처리합니다.
    # 실제로는 Pydantic 모델로 요청을 받아 필요한 값을 추출해야 합니다.
    
    # 임시로 user_message를 전체 요구사항으로 간주하고 프롬프트에 넣는 예시
    system_prompt = (
        "[역할]\n당신은 한국의 소도시·중소도시 여행을 큐레이션하는 전문가입니다. 아래 요구사항을 모두 반영하여 여행지 3곳을 추천하세요."
        # ... (나머지 [요구사항]과 [생성 규칙] 생략 - 전체를 문자열로 구성)
        "\n[출력 형식 - 반드시 그대로 준수]\n"
        "1. 요약 섹션 (자연어)\n"
        '"{주요 요구사항 요약}에 맞는 여행을 선호하시는군요! {요구사항}을 위해 \'{확장 키워드1}\', \'{확장 키워드2}\'{(선택) \'확장 키워드3\'}로 키워드를 확장했습니다.\n'
        '당신에게 꼭 맞는 여행지 3곳을 추천해드립니다."\n\n'
        "2. 출력(JSON 스키마)\n"
        '{ "recommendations": [ { "contentid": "...", "title": "...", "summary": "..." }, ... ], "keywords": ["확장 키워드1", "확장 키워드2"] }\n\n'
        "3. 최종 한 줄 안내:\n"
        '"※ 일부 정보는 운영 상황에 따라 변동될 수 있으니 방문 전 최신 안내를 확인해 주세요."'
    )

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message} # 사용자 문구를 요구사항으로 사용
            ],
            temperature=0.7,
            # 모델이 JSON을 반환하도록 강제
            response_format={"type": "json_object"} 
        )
        
        # 2. GPT 응답 파싱
        ai_response_json = json.loads(response.choices[0].message.content)
        
        # 자연어 요약 텍스트는 응답의 텍스트 부분에서 직접 추출하거나, 
        # 아니면 JSON 외의 부분(프롬프트의 요약 섹션)을 파싱해야 합니다.
        # JSON 포맷 강제 시, 자연어 요약은 별도 파싱 또는 프론트에서 구성이 필요합니다.
        
        # 현재는 JSON의 키워드만 추출하여 DB 검색에 사용
        keywords = ai_response_json.get("keywords", [])
        
        # 3. DB 검색 (Retrieval)
        with SessionLocal() as db:
            db_tour_infos = get_tour_info_by_keywords(db, keywords)
        
        # 4. 결과 반환
        return {
            "ai_response_text": response.choices[0].message.content, # GPT의 전체 응답(JSON)
            "db_recommendations": db_tour_infos, # DB에서 찾은 관광지 정보 (TourInfoOut 리스트)
            "keywords": keywords
        }

    except Exception as e:
        print(f"RAG 처리 중 오류 발생: {e}")
        # 오류 발생 시 빈 정보로 반환하거나, 적절한 HTTPException 발생
        raise HTTPException(status_code=500, detail="RAG 기반 추천 처리 중 오류가 발생했습니다.")