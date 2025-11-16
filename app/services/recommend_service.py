# app/services/recommend_service.py (수정)

from __future__ import annotations
import os
import json
from typing import List, Optional, Dict, Any
# from dotenv import load_dotenv # 데모 모드에서는 필요 없음
# from openai import AsyncOpenAI # 데모 모드에서는 필요 없음
from fastapi import HTTPException
from json import JSONDecodeError 

# =========================
# AI 클라이언트 초기화 (데모 모드)
# =========================

# 1. 전역 변수 초기 선언
openai_client = None 

# ⚠️ 데모 모드: OpenAI API 호출을 하지 않도록 클라이언트를 None으로 설정합니다.
print("=================================================")
print("==  WARNING: DEMO MODE ACTIVE (NO AI CALLS)  ==")
print("=================================================")
        
# try:
#     openai_api_key = os.getenv("OPENAI_API_KEY")
#     if openai_api_key:
#         openai_client = AsyncOpenAI(api_key=openai_api_key)
#     else:
#         print("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. AI 서비스가 비활성화됩니다.")
# except Exception as e:
#     print(f"Error initializing OpenAI client: {e}")

# =========================
# 헬퍼 함수: 최종 응답 파싱
# =========================
# ⚠️ 데모 모드: 이 함수는 FINAL 모드에서 더 이상 사용되지 않지만,
#              혹시 모를 의존성을 위해 남겨둡니다.
def parse_final_response(content: str) -> Dict[str, Any]:
    """
    AI가 생성한 최종 응답 텍스트에서 자연어 부분과 JSON 부분을 분리하여 반환합니다.
    (사용자 지정 출력 형식에 맞춰 파싱)
    """
    JSON_HEADER = "2. 출력(JSON 스키마)"
    DISCLAIMER_HEADER = "3. 최종 한 줄 안내:"
    
    response_text = content
    recommendations = []
    
    try:
        # 1. JSON 블록의 경계 찾기
        json_header_index = content.find(JSON_HEADER)
        disclaimer_header_index = content.find(DISCLAIMER_HEADER)
        
        if json_header_index == -1 or disclaimer_header_index == -1:
            return {"response_text": content, "recommendations": []}
            
        # 2. Raw JSON 문자열 후보 추출
        json_start = json_header_index + len(JSON_HEADER)
        json_string_candidate = content[json_start:disclaimer_header_index].strip()
        
        # 3. JSON 문자열 정리 및 추출 (첫 '{'부터 마지막 '}'까지)
        start_brace = json_string_candidate.find('{')
        end_brace = json_string_candidate.rfind('}')
        
        if start_brace == -1 or end_brace == -1:
             return {"response_text": content, "recommendations": []}

        json_string_clean = json_string_candidate[start_brace : end_brace + 1].strip('`').strip()
        
        # 4. JSON 파싱
        json_data = json.loads(json_string_clean)
        recommendations = json_data.get("results", [])
        
        # 5. 최종 자연어 텍스트 부분 조합
        summary_text = content[:json_start].strip()
        disclaimer_text = content[disclaimer_header_index:].strip()
        response_text = f"{summary_text}\n\n{disclaimer_text}"

        return {
            "response_text": response_text, 
            "recommendations": recommendations,
        }

    except JSONDecodeError:
        print(f"Inner JSON parsing failed for: {json_string_clean[:100]}...")
        return {"response_text": content, "recommendations": []}
    except Exception as e:
        print(f"Error during final response parsing: {e}")
        return {"response_text": content, "recommendations": []}


# =========================
# ⚠️ 데모 모드용 상수 정의
# =========================
DEMO_QUESTIONS = [
    "자연 힐링이 좋으시군요! '여유로운 여행', '자연 탐방', '미식' 중 어떤 테마를 가장 선호하시나요?",
    "여유로운 여행에 관심이 많으시군요! 여행 시기는 언제로 생각하고 계신가요? (예: 한겨울이나 따뜻한 봄 등과 같이 작성해주세요!)",
    "선선한 가을 여행을 계획 중이시군요. 여행을 함께 가는 사람들과 관계는 어떻게 되시나요? (예: 친구, 가족, 연인 등)",
    "혼자 여행을 선호하시는군요! 주로 이용할 교통수단은 대중교통인가요, 아니면 자가용/차량인가요?",
]

# 프론트엔드에 표시될 최종 텍스트 (추천 카드 부분은 제외)
DEMO_FINAL_TEXT = (
    "당신은 자연 힐링 스타일을 선호하며, 선선한 가을 동안 혼자과 대중교통을 이용하는 여행을 계획 중이시군요. 사용자님의 취향에 맞춰 '고즈넉한 산책', '조용한 호수', '소도시 감성' 키워드를 확장했습니다.\n\n"
    "이러한 조건에 가장 적합한 소도시 3곳을 추천해 드립니다. 아래 버튼을 선택해 해당 도시의 상세 정보를 확인해 보세요.\n\n"
    "※ 일부 정보는 운영 상황에 따라 변동될 수 있으니 방문 전 최신 안내를 확인해 주세요."
)

# 프론트엔드 RecommendationCard 렌더링에 사용될 구조화된 데이터
DEMO_RECOMMENDATIONS = [
    {
        "contentid": "DEMO_1", # React Native의 key prop 및 찜하기/상세보기용
        "title": "정선(강원도)",
        "reason": "깊은 산자락과 맑은 계곡이 어우러진 정선은 가을 단풍과 고즈넉한 산책길이 매력적입니다. 대중교통 접근성도 좋아 혼자 힐링 여행에 적합합니다.",
        "activity": "고즈넉한 산책, 가을 단풍 감상", # 스키마에 맞춰 임의 생성
        "mapping": "고즈넉한 산책" # 스키마에 맞춰 임의 생성
    },
    {
        "contentid": "DEMO_2",
        "title": "담양(전라남도)",
        "reason": "메타세쿼이아길과 죽녹원이 대표적인 담양은 조용한 숲 산책과 여유로운 분위기가 특징입니다. 자연 속에서 혼자만의 시간을 보내기 좋은 가을 여행지입니다.",
        "activity": "메타세쿼이아길 산책, 죽녹원",
        "mapping": "조용한 호수"
    },
    {
        "contentid": "DEMO_3",
        "title": "완주(전라북도)",
        "reason": "대둔산과 소양고택 등 자연과 전통이 공존하는 완주는 소도시 감성이 돋보이며, 대중교통으로도 편히 방문할 수 있어 가을 힐링 여행지로 알맞습니다.",
        "activity": "소양고택, 대둔산 등반",
        "mapping": "소도시 감성"
    }
]


# =========================
# 핵심 AI 추천 서비스 로직 (⚠️ 데모 모드)
# =========================
async def get_chatbot_search_keywords_and_recommendations(user_message: str):
    """
    [데모 모드]
    OpenAI API를 호출하는 대신, 턴 카운트에 따라 미리 정의된 질문(DEMO_QUESTIONS) 또는 
    최종 답변(DEMO_FINAL_TEXT, DEMO_RECOMMENDATIONS)을 반환합니다.
    """
    
    current_profile = {}
    turn_count = 0
    
    # ⚠️ NOTE: 클라이언트가 JSON 형태로 {message, profile, count}를 보낸다고 가정하고 파싱
    try:
        # 1. user_message가 JSON 문자열 형태로 왔을 경우 파싱
        input_data = json.loads(user_message)
        raw_user_input = input_data.get("message", user_message)
        current_profile = input_data.get("current_profile", {})
        turn_count = input_data.get("turn_count", 0) # 0, 1, 2, 3, ...
        
    except (JSONDecodeError, AttributeError):
        # 2. JSON이 아니거나 초기 요청일 경우, 턴 카운트 0, 프로필 빈 값으로 시작
        pass
    
    # 3. 턴 카운트에 따라 데모 질문 또는 최종 답변 분기
    
    # 3-1. QUESTION 모드 (데모 질문이 남아있는 경우)
    # (turn_count 0, 1, 2, 3일 때 실행)
    if turn_count < len(DEMO_QUESTIONS):
        question_text = DEMO_QUESTIONS[turn_count]
        new_turn_count = turn_count + 1 # 프론트엔드가 다음 턴에 사용할 카운트
        
        # ⚠️ NOTE: 프론트엔드가 파싱할 수 있도록 
        #               원래 AI의 QUESTION 모드 응답 형식을 그대로 모방합니다.
        
        # 프로필은 데모에서 중요하지 않으므로 그냥 받은 값을 다시 보냅니다.
        new_profile = current_profile 
        
        # 클라이언트가 다음 요청에 보낼 JSON 구조
        next_request_data = {
            "next_question": question_text,
            "current_profile": new_profile,
            "turn_count": new_turn_count
        }
        
        # JSON을 문자열로 직렬화하여 클라이언트에 전달 (프론트엔드에서 파싱해야 함)
        formatted_response = (
            f"{question_text}\n\n"
            f"---PROFILE_UPDATE---\n"
            f"{json.dumps(next_request_data, ensure_ascii=False)}\n"
            f"---END_PROFILE---"
        )
        
        return {
            "ai_response_text": formatted_response,
            "db_recommendations": []
        }

    # 3-2. FINAL 모드 (모든 데모 질문이 소진된 경우)
    # (turn_count 4일 때 실행)
    else:
        # ⚠️ NOTE: 프론트엔드가 기대하는 
        #               'ai_response_text'와 'db_recommendations'를 반환합니다.
        
        return {
            "ai_response_text": DEMO_FINAL_TEXT, 
            "db_recommendations": DEMO_RECOMMENDATIONS
        }

    # ⚠️ (원래 코드) OpenAI API 호출 로직은 모두 제거됨
    # try:
    #     response = await openai_client.chat.completions.create(...)
    # ...
    # except Exception as e:
    # ...