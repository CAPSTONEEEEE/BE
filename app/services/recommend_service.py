# app/services/recommend_service.py (수정)

from __future__ import annotations
import os
import json
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI
from fastapi import HTTPException
from json import JSONDecodeError 

# =========================
# AI 클라이언트 초기화 (함수 외부 - 전역 스코프)
# =========================

# 1. 전역 변수 초기 선언: NameError를 방지하기 위해 먼저 None으로 할당
openai_client = None 

try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if openai_api_key:
        # 2. 환경 변수가 있을 때만 클라이언트 객체 할당
        openai_client = AsyncOpenAI(api_key=openai_api_key)
    else:
        # API 키가 없는 경우 None을 유지하며 경고 출력
        print("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. AI 서비스가 비활성화됩니다.")
        
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    # 예외 발생 시 None 유지 (이미 초기화됨)

# =========================
# 헬퍼 함수: 최종 응답 파싱
# =========================
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
            # 마커가 없는 경우, 전체를 자연어 텍스트로 반환하고 구조화된 데이터는 포기
            return {"response_text": content, "recommendations": []}
            
        # 2. Raw JSON 문자열 후보 추출
        # JSON HEADER 이후부터 DISCLAIMER HEADER 전까지
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
        # 텍스트 = 요약 부분 + 최종 안내 부분
        
        # JSON HEADER 전까지 (요약 섹션)
        summary_text = content[:json_start].strip()
        # 최종 안내 부분
        disclaimer_text = content[disclaimer_header_index:].strip()

        # 최종적으로 사용자에게 보여줄 자연어 텍스트
        response_text = f"{summary_text}\n\n{disclaimer_text}"

        return {
            "response_text": response_text, 
            "recommendations": recommendations,
        }

    except JSONDecodeError:
        print(f"Inner JSON parsing failed for: {json_string_clean[:100]}...")
        # 파싱 실패 시, 전체 Raw Content를 텍스트로 반환
        return {"response_text": content, "recommendations": []}
    except Exception as e:
        print(f"Error during final response parsing: {e}")
        return {"response_text": content, "recommendations": []}


# =========================
# 핵심 AI 추천 서비스 로직
# =========================
async def get_chatbot_search_keywords_and_recommendations(user_message: str):
    if not openai_client:
        raise HTTPException(status_code=503, detail="AI 서비스 연결에 문제가 있습니다.")
    
    # --- [NEW] 턴 카운트 및 프로필 추출 로직 (프론트엔드 통신 가정) ---
    current_profile = {}
    turn_count = 0
    raw_user_input = user_message # API 요청이 단순 문자열일 경우를 대비하여 저장
    
    # ⚠️ NOTE: 클라이언트가 JSON 형태로 {message, profile, count}를 보낸다고 가정하고 파싱
    try:
        # 1. user_message가 JSON 문자열 형태로 왔을 경우 파싱
        input_data = json.loads(user_message)
        raw_user_input = input_data.get("message", user_message)
        current_profile = input_data.get("current_profile", {})
        turn_count = input_data.get("turn_count", 0)
        
    except (JSONDecodeError, AttributeError):
        # 2. JSON이 아니거나 초기 요청일 경우, 턴 카운트 0, 프로필 빈 값으로 시작
        pass
    
    # 3. 최대 턴 제한 상수 설정
    MAX_TURNS = 5 # 초기 질문 (턴 0) + 심화 질문 4회 = 총 5턴
    
    # 4. 턴 카운트 증가 (현재 요청은 새로운 턴이므로 +1)
    turn_count += 1 
    
    # 5. 최대 턴을 초과했거나 임박했을 경우 모드 강제
    FORCE_FINAL_MODE = turn_count >= MAX_TURNS

    # -------------------------------------------------------------

    profile_fields = ["relation", "people", "when", "period", "transportation", "style", "budget", "age"]
    recommend_count = 3
    
    # === system_prompt 재구성: 턴 카운트 및 질문 효율성 강화 ===
    system_prompt = (
        f"[역할]\n당신은 한국의 소도시 여행 큐레이션 전문가 '소소행'입니다. 현재 **대화 턴은 {turn_count}/{MAX_TURNS}** 입니다.\n"
        f"{'FORCE_FINAL_MODE가 True이므로 이 응답은 무조건 FINAL 모드여야 합니다.' if FORCE_FINAL_MODE else 'FINAL 모드가 아니라면, 질문 우선순위에 따라 다음 질문을 합니다.'}\n"
        "당신이 관리하는 프로필 필드는 {', '.join(profile_fields)} 입니다.\n\n"
        
        "[정보 파악 규칙]\n"
        "1. **반복 금지**: `current_profile`에 이미 값이 채워진 필드는 재차 질문하지 않습니다.\n"
        "2. **질문 조합**: 효율성을 위해, **비슷한 필드(예: 인원/관계, 시기/기간)는 하나의 질문으로 묶어** 파악합니다.\n"
        "3. **질문 우선순위**: 필드가 비어있고 FINAL 모드가 강제되지 않았다면 다음 순서로 질문합니다:\n"
        "   - **우선순위 1 (Style/키워드)**: `style`이 비어있다면, 사용자의 답변을 바탕으로 RAG 키워드 3개를 확장 제시하며 취향에 맞는 것을 선택하게 유도하는 질문을 먼저 합니다.\n"
        "   - **우선순위 2 (People/Relation)**: `people` 또는 `relation` 중 하나라도 비어있다면, '함께 여행하시는 **인원**은 몇 명이고, **관계**는 어떻게 되시나요?'를 질문합니다.\n"
        "   - **우선순위 3 (When/Period)**: `when` 또는 `period` 중 하나라도 비어있다면, '여행 **시기**와 **기간**은 어느 정도로 생각하고 계신가요?'를 질문합니다.\n"
        "   - **우선순위 4 (Transportation)**: `transportation`이 비어있다면, '주로 이용할 **교통수단**은 대중교통인가요, 아니면 자가용/차량인가요?'를 질문합니다.\n"
        "4. **자동 파악**: 사용자가 질문하지 않은 정보(예: `age`, `budget`)를 메시지에서 파악했다면, `current_profile`에 즉시 채웁니다.\n\n"
        
        "[행동 모드]\n"
        "현재까지 추출된 정보와 사용자 메시지를 기반으로, 다음 중 하나의 모드를 선택하세요.\n"
        
        "### [QUESTION 모드] (턴이 {MAX_TURNS} 미만일 때만 가능)\n"
        f"{'FORCE_FINAL_MODE가 True이므로 QUESTION 모드를 선택할 수 없습니다.' if FORCE_FINAL_MODE else ''}\n"
        "필요한 정보가 남아있고, 질문 횟수가 남아있는 경우 'QUESTION 모드'로 응답하세요.\n"
        "- **next_question**: 위 질문 우선순위를 따라 질문합니다. 질문은 반드시 1개만, 간결하게 제시하세요.\n"
        "- **current_profile**: **이전 프로필 ({current_profile})**과 **새로운 메시지**를 바탕으로 최신 정보로 프로필을 업데이트하세요. (모르는 필드는 null/None 유지)\n\n"
        
        "### [FINAL 모드]\n"
        f"{'FORCE_FINAL_MODE가 True이거나 핵심 정보가 파악된 경우 FINAL 모드를 선택해야 합니다.' if FORCE_FINAL_MODE else '핵심 정보(style, people, period)가 파악되었다면 FINAL 모드로 전환하세요.'}\n"
        "**최대 턴을 모두 사용**했거나, **핵심 정보가 파악**되었다면 'FINAL 모드'로 응답하여 최종 추천을 진행하세요.\n"
        "- **final_response_content**: 이 안에 최종 추천 결과 전체를 [최종 출력 형식]에 맞춰 담으세요.\n\n"
        
        "[최종 출력 형식 - FINAL 모드에서만 사용]\n"
        # ... (이하 최종 출력 형식 코드는 그대로 유지) ...
        f"1. 요약 섹션 (자연어)\n"
        f"\"{{주요 요구사항 요약}}에 맞는 여행을 선호하시는군요! {{요구사항}}을 위해 '{{확장 키워드1}}', '{{확장 키워드2}}'{{(선택) '확장 키워드3'}}로 키워드를 확장했습니다.\n"
        f"당신에게 꼭 맞는 여행지 {recommend_count}곳을 추천해드립니다.\"\n\n"
        f"2. 출력(JSON 스키마) - 여행지 정보는 파악된 프로필에 맞춰 가상의 더미 데이터를 생성하세요.\n"
        f"{{ \"results\": [ {{ \"title\": \"...\", \"reason\": \"...\", \"activity\": \"...\", \"mapping\": \"...\" }}, ... ], \"keywords\": [\"확장 키워드1\", \"확장 키워드2\"] }}\n\n"
        f"3. 최종 한 줄 안내:\n"
        f"\"※ 일부 정보는 운영 상황에 따라 변동될 수 있으니 방문 전 최신 안내를 확인해 주세요.\"\n\n"
        
        "[JSON 출력 스키마 - 반드시 이 스키마를 준수하여 출력하세요]\n"
        "```json\n"
        "{\n"
        f"  \"status\": \"<QUESTION 또는 FINAL>\",\n"
        f"  \"current_profile\": {{\n"
        f"    \"relation\": \"<파악된 값 또는 null>\",\n"
        f"    \"people\": \"<파악된 값 또는 null>\",\n"
        f"    \"when\": \"<파악된 값 또는 null>\",\n"
        f"    \"period\": \"<파악된 값 또는 null>\",\n"
        f"    \"transportation\": \"<파악된 값 또는 null>\",\n"
        f"    \"style\": \"<파악된 값 또는 null>\",\n"
        f"    \"budget\": \"<파악된 값 또는 null>\",\n"
        f"    \"age\": \"<파악된 값 또는 null>\"\n"
        f"  }},\n"
        f"  \"turn_count\": {turn_count},\n" # 새로운 턴 카운트 포함
        "  \"next_question\": \"<status가 QUESTION일 때만 다음 질문>\",\n"
        "  \"final_response_content\": \"<status가 FINAL일 때만 최종 추천 전체 텍스트>\"\n"
        "}\n"
        "```"
    )

    try:
        # 1. GPT API 호출 (JSON 응답 강제)
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": system_prompt},
                # AI에게는 사용자의 실제 답변만 전달
                {"role": "user", "content": raw_user_input} 
            ],
            temperature=0.7,
            response_format={"type": "json_object"} 
        )
        
        # ... (이하 GPT 응답 파싱 및 상태 확인 로직은 그대로 유지) ...
        raw_ai_content = response.choices[0].message.content
        
        try:
            ai_response_json: Dict[str, Any] = json.loads(raw_ai_content)
        except JSONDecodeError:
             raise HTTPException(
                status_code=500, 
                detail="AI가 유효하지 않은 JSON 형식을 반환했습니다."
            )
            
        status = ai_response_json.get("status")
        
        # FINAL 모드 처리 (로직 동일)
        if status == "FINAL":
            final_text_raw = ai_response_json.get("final_response_content", "")
            parsed_result = parse_final_response(final_text_raw)

            return {
                "ai_response_text": parsed_result["response_text"], 
                "db_recommendations": parsed_result["recommendations"]
            }
        
        # QUESTION 모드 처리
        elif status == "QUESTION":
            question_text = ai_response_json.get("next_question", "죄송합니다. 다음 질문을 생성하는 데 실패했습니다.")
            
            # ⚠️ NOTE: 턴 카운트와 프로필을 포함하여 클라이언트가 다음 요청에 사용할 수 있도록 응답해야 합니다.
            # 현재 ChatRecommendResponse 스키마가 이를 지원하지 않으므로, 
            # 다음 질문과 함께 새로운 프로필 정보를 포함한 JSON을 텍스트로 반환하는 임시 조치를 취합니다.
            
            # 클라이언트가 파싱하기 쉽도록 응답 텍스트를 구조화합니다.
            new_profile = ai_response_json.get("current_profile", {})
            
            # 클라이언트가 다음 요청에 보낼 JSON 구조
            next_request_data = {
                "next_question": question_text,
                "current_profile": new_profile,
                "turn_count": turn_count
            }
            
            # JSON을 문자열로 직렬화하여 클라이언트에 전달 (프론트엔드에서 파싱해야 함)
            # 클라이언트가 이 JSON을 파싱하여 다음 요청의 'current_profile'과 'turn_count'로 사용해야 합니다.
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

        else:
            raise HTTPException(status_code=500, detail=f"AI가 알 수 없는 상태(status: {status})를 반환했습니다.")

    except HTTPException:
        raise
    except Exception as e:
        print(f"AI 추천 처리 중 예상치 못한 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="AI 추천 처리 중 서버 오류가 발생했습니다.")