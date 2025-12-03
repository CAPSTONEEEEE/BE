# app/services/recommend_service.py

from __future__ import annotations
import os
import json
import traceback
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI
from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.recommend_models import RecommendTourInfo, TourInfoOut

from math import radians, cos, sin, asin, sqrt

# --- OpenAI 클라이언트 초기화 ---
openai_client = None 
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        openai_client = AsyncOpenAI(api_key=openai_api_key)
    else:
        print("OPENAI_API_KEY가 없습니다.")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")

# =========================================================
# 1. [핵심] RAG 검증 및 추천 로직
# =========================================================
async def get_chatbot_search_keywords_and_recommendations(user_message: str, db: Session):
    if not openai_client:
        raise HTTPException(status_code=503, detail="AI 서비스 연결 불가")
    
    # 1. 입력 데이터 파싱
    try:
        input_data = json.loads(user_message)
        raw_msg = input_data.get("message", user_message)
        # 프론트에서 보내주는 current_profile과 turn_count 받기
        current_profile = input_data.get("current_profile", {})
        turn_count = input_data.get("turn_count", 0)
    except:
        raw_msg = user_message
        current_profile = {}
        turn_count = 0

    # 턴 증가 (초기값 보정)
    if turn_count == 0:
        # 첫 진입 시 초기화
        current_profile = {
            "style": None,    # 여행 스타일 (힐링, 액티비티 등)
            "who": None,      # 동행 (가족, 친구, 혼자)
            "when": None,     # 시기 (이번 주말, 가을 등)
            "transport": None # 교통 (자차, 뚜벅이)
        }
    
    turn_count += 1
    MAX_TURNS = 5  # 최대 질문 횟수

    print(f"🔄 Turn: {turn_count}, Input: {raw_msg}")
    print(f"📊 Current Profile: {current_profile}")

    try:
        # -----------------------------------------------------
        # Step 1: Router & Interviewer (정보 수집 및 키워드 확장)
        # -----------------------------------------------------
        
        # 시스템 프롬프트: 상태 관리자 역할
        system_prompt_router = f"""
        [Role]
        당신은 소도시 여행 전문가 '소소행'입니다. 
        사용자와 대화하며 [필수 정보]를 수집하여 {MAX_TURNS}턴 안에 최적의 여행지를 추천해야 합니다.

        [Target Profile Schema]
        - style: (예: 힐링, 액티비티, 호캉스, 맛집탐방)
        - who: (예: 혼자, 연인, 가족, 친구)
        - when: (예: 이번 주말, 여름 휴가, 10월)
        - transport: (예: 대중교통, 자차)

        [Current Status]
        - 현재 턴: {turn_count} / {MAX_TURNS}
        - 현재 수집된 정보: {json.dumps(current_profile, ensure_ascii=False)}

        [Task Rules]
        1. 사용자의 입력('{raw_msg}')을 분석하여 [Current Status]의 비어있는(null) 필드를 채우십시오.
        2. 만약 'style'이 모호하다면(예: "그냥 좋은 곳"), 구체적인 키워드 3가지를 제안하여 선택하게 하십시오.
        3. [필수 정보]가 모두 채워졌거나, 현재 턴이 {MAX_TURNS}에 도달했다면 즉시 'SEARCH_REQ' 상태로 전환하십시오.
        4. 아직 정보가 부족하다면 'QUESTION' 상태를 유지하고, **비어있는 항목 중 하나**에 대해 자연스럽게 질문하십시오. (한 번에 하나만 질문)

        [Output Format (JSON Only)]
        반드시 아래 JSON 형식으로만 응답하십시오.
        {{
            "status": "QUESTION" | "SEARCH_REQ",
            "updated_profile": {{ ...업데이트된 프로필... }},
            "next_question": "사용자에게 할 다음 질문 (status가 QUESTION일 때)",
            "search_keywords": ["키워드1", "키워드2", "지역명(선택)"] (status가 SEARCH_REQ일 때),
            "reasoning": "왜 이 상태를 선택했는지 설명"
        }}
        """

        response_router = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt_router},
                {"role": "user", "content": raw_msg}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        try:
            router_res = json.loads(response_router.choices[0].message.content)
        except json.JSONDecodeError:
            # AI가 JSON을 잘못 뱉었을 경우 예외 처리
            print("❌ AI JSON Parsing Error")
            return {
                "ai_response_text": "잠시 시스템 통신에 문제가 생겼습니다. 다시 한 번 말씀해 주시겠어요?",
                "db_recommendations": []
            }

        status = router_res.get("status")
        updated_profile = router_res.get("updated_profile", current_profile)

        # -----------------------------------------------------
        # CASE A: 아직 질문이 더 필요함 (QUESTION)
        # -----------------------------------------------------
        if status == "QUESTION":
            next_q = router_res.get("next_question")
            
            # 클라이언트 상태 업데이트용 데이터 패키징
            next_request_data = {
                "next_question": next_q,
                "current_profile": updated_profile,
                "turn_count": turn_count
            }
            
            # ---PROFILE_UPDATE--- 마커를 포함하여 일반 텍스트로 반환
            return {
                "ai_response_text": f"{next_q}\n\n---PROFILE_UPDATE---\n{json.dumps(next_request_data, ensure_ascii=False)}\n---END_PROFILE---",
                "db_recommendations": []
            }

        # -----------------------------------------------------
        # CASE B: 검색 요청 (SEARCH_REQ)
        # -----------------------------------------------------
        elif status == "SEARCH_REQ":
            keywords = router_res.get("search_keywords", [])
            print(f"🔎 AI 추출 검색 키워드: {keywords}")

            # 1. DB 검색 (검증)
            found_spots = search_spots_in_db(db, keywords)

            # 2. 검색 결과가 없을 경우 (유연한 대처)
            if not found_spots:
                # 검색 결과가 없으면, 키워드를 조금 더 일반적인 것으로 바꿔서 재질문 유도
                print("⚠️ DB 검색 결과 0건")
                fallback_msg = "원하시는 조건에 딱 맞는 소도시 정보를 찾기가 어렵네요. 😭\n조건을 조금만 넓혀서(예: '전라도 전체' 또는 '자연 힐링') 다시 추천해 드릴까요?"
                
                # 프로필은 유지하되, 턴 수는 유지하거나 리셋
                next_request_data = {
                    "next_question": fallback_msg,
                    "current_profile": updated_profile, 
                    "turn_count": turn_count - 1
                }
                return {
                     "ai_response_text": f"{fallback_msg}\n\n---PROFILE_UPDATE---\n{json.dumps(next_request_data, ensure_ascii=False)}\n---END_PROFILE---",
                    "db_recommendations": []
                }

            # 3. 최종 추천 멘트 생성 (검색된 데이터 기반)
            final_response = await generate_final_recommendation(found_spots, updated_profile)
            return final_response

    except Exception as e:
        print(f"🔥 Critical Error in Recommend Service: {e}")
        traceback.print_exc() # 로그에 상세 에러 출력
        return {
            "ai_response_text": "죄송합니다. 처리 중 오류가 발생했습니다. 다시 시도해 주세요.",
            "db_recommendations": []
        }

# =========================================================
# Helper: DB 검색 함수 (키워드 기반 LIKE 검색 + 소도시 필터)
# =========================================================
def search_spots_in_db(db: Session, keywords: List[str]) -> List[TourInfoOut]:
    
    # 1. 소도시 정의: 대도시 제외
    exclude_cities = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "제주"]
    
    query = db.query(RecommendTourInfo)
    
    query = query.filter(RecommendTourInfo.addr1.isnot(None))
    query = query.filter(RecommendTourInfo.addr1 != "")
    
    # 대도시 제외 필터 적용
    for city in exclude_cities:
        query = query.filter(RecommendTourInfo.addr1.notlike(f"%{city}%"))

    # 2. 키워드 검색 (OR 조건)
    # keywords 중 하나라도 포함되면 결과에 포함
    conditions = []
    for kw in keywords:
        kw = kw.strip()
        if len(kw) < 2: continue # 1글자 키워드는 무시 (너무 광범위)
        
        conditions.append(RecommendTourInfo.title.like(f"%{kw}%"))
        conditions.append(RecommendTourInfo.addr1.like(f"%{kw}%"))
        # 필요한 경우 cat1, cat2 등도 검색
        
    if conditions:
        query = query.filter(or_(*conditions))
    
    # 3. 결과 제한 (너무 많으면 AI 토큰 초과)
    # 랜덤 정렬을 원하면 func.random() 사용 가능 (DB 종류에 따라 다름)
    results = query.limit(3).all()
    
    # Pydantic 모델로 변환
    return [TourInfoOut.model_validate(item) for item in results]


# =========================================================
# Helper: 최종 생성 함수 (Generation)
# =========================================================
async def generate_final_recommendation(spots: List[TourInfoOut], profile: Dict):
    
    # DB 객체를 JSON으로 직렬화 (AI에게 Context로 주기 위함)
    spots_context = json.dumps([s.model_dump() for s in spots], ensure_ascii=False)
    
    system_prompt_final = f"""
    [Role]
    당신은 소도시 여행 전문가입니다. 사용자 프로필({profile})을 고려하여 추천 멘트를 작성합니다.
    
    [Context Data]
    {spots_context}

    [Mission]
    위 [Context Data]의 3개 여행지에 대해 각각 맞춤형 추천 이유를 작성하고, 전체적인 소개말을 작성하십시오.

    [Output Format (JSON Only)]
    반드시 아래 JSON 형식을 준수하십시오.
    {{
        "intro_message": "사용자님, {profile.get('style')} 스타일을 고려하여 ~한 곳들을 선정했습니다. (전체 요약 1~2문장)",
        "recommendations_detail": [
            {{
                "contentid": "여행지 ID (Context Data와 동일해야 함)",
                "ai_summary": "이 여행지를 추천하는 구체적인 이유와 매력 포인트 (3~4문장)"
            }},
        ]
    }}
    """

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt_final}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        res_json = json.loads(response.choices[0].message.content)
        intro_text = res_json.get("intro_message", "추천 여행지를 찾았습니다!")
        ai_details = res_json.get("recommendations_detail", [])
        
        final_recommendations = []
        
        for spot in spots:
            # 1. Pydantic 모델을 dict로 변환
            spot_dict = spot.model_dump()
            
            # 2. AI 결과 매칭
            matching_detail = next(
                (item for item in ai_details if str(item.get("contentid")) == str(spot.contentid)), 
                None
            )
            
            # 3. ai_summary 필드 주입
            if matching_detail and matching_detail.get("ai_summary"):
                spot_dict["ai_summary"] = matching_detail.get("ai_summary")
            else:
                spot_dict["ai_summary"] = spot.addr1 # 실패 시 주소 사용

            final_recommendations.append(TourInfoOut(**spot_dict))

        return {
            "ai_response_text": intro_text,
            "db_recommendations": final_recommendations # 이제 올바른 객체 리스트 반환
        }
        
    except Exception as e:
        print(f"Generation Error: {e}")
        traceback.print_exc() # 서버 로그에 에러 원인 출력
        return {
             "ai_response_text": "추천 결과를 불러오는 중 문제가 발생했습니다.",
             "db_recommendations": spots # 기본 데이터라도 반환
        }
        
# =========================================================
# 여행지 상세정보 관련
# =========================================================     
def haversine(lon1, lat1, lon2, lat2):
    """
    두 지점(위도/경도) 사이의 거리를 계산 (단위: km)
    """
    if lon1 is None or lat1 is None or lon2 is None or lat2 is None:
        return 99999 # 거리 계산 불가 시 큰 값 반환

    # 10진수 -> 라디안 변환
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine 공식
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # 지구 반지름 (km)
    return c * r

def get_nearby_spots(contentid: str, db: Session, limit_km: float = 20.0) -> Dict[str, Any]:
    """
    특정 contentid의 좌표를 기준으로 반경 20km 이내의 여행지를 찾습니다.
    """
    # 1. 기준이 되는 여행지 정보 조회 (이게 실패하면 404가 뜹니다)
    target_spot = db.query(RecommendTourInfo).filter(RecommendTourInfo.contentid == contentid).first()
    
    if not target_spot:
        print(f"❌ Error: Content ID {contentid} not found in DB.") # [디버깅 로그]
        return {"target": None, "nearby_spots": []}

    # 좌표가 없는 경우(데이터 누락) 예외 처리
    if target_spot.mapx is None or target_spot.mapy is None:
        return {"target": TourInfoOut.model_validate(target_spot), "nearby_spots": []}

    target_x = target_spot.mapx # 경도
    target_y = target_spot.mapy # 위도

    # 2. 전체 여행지 조회 (자신 제외, 좌표 있는 것만)
    all_spots = db.query(RecommendTourInfo).filter(
        RecommendTourInfo.contentid != contentid, 
        RecommendTourInfo.mapx.isnot(None),
        RecommendTourInfo.mapy.isnot(None)
    ).all()

    nearby_list = []
    
    # 3. 거리 계산 (Haversine 공식)
    for spot in all_spots:
        try:
            dist = haversine(target_x, target_y, spot.mapx, spot.mapy)
            if dist <= limit_km:
                spot_data = TourInfoOut.model_validate(spot).model_dump()
                spot_data['distance'] = round(dist, 2) # 거리(km) 소수점 2자리
                nearby_list.append(spot_data)
        except Exception:
            continue # 계산 에러 시 건너뜀
    
    # 4. 거리순 정렬 (가까운 순)
    nearby_list.sort(key=lambda x: x['distance'])

    return {
        "target": TourInfoOut.model_validate(target_spot),
        "nearby_spots": nearby_list
    }

# 최종 상세 정보 조회 (페이지 2용)
def get_spot_detail(contentid: str, db: Session):
    spot = db.query(RecommendTourInfo).filter(RecommendTourInfo.contentid == contentid).first()
    if not spot:
        return None
    return TourInfoOut.model_validate(spot)