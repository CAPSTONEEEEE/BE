# 실제 비즈니스 로직과 외부 API 연동을 담당

import random
import asyncio
from typing import List
from .recommend_models import (
    RandomRecommendRequest,
    RandomRecommendResponse,
    ChatRecommendRequest,
    ChatRecommendResponse,
    TravelDestination,
)
from openai import AsyncOpenAI  # 비동기 OpenAI 클라이언트 사용

# OpenAI API 클라이언트 초기화
# 실제 환경에서는 환경 변수에서 API 키를 불러와야 합니다.
client = AsyncOpenAI(api_key="YOUR_OPENAI_API_KEY")

class RecommendationService:
    """
    여행지 추천 로직을 처리하는 서비스 클래스
    """

    # RAG 기술을 모방하기 위한 임시 데이터셋
    # 실제로는 데이터베이스나 외부 저장소에서 불러와야 합니다.
    DUMMY_DATA = {
        "휴양": [
            {"title": "제주도 서귀포", "description": "아름다운 해변과 조용한 분위기를 즐길 수 있는 휴양지입니다."},
            {"title": "강릉 경포호", "description": "호수와 바다가 어우러져 평화로운 산책을 즐길 수 있습니다."},
            {"title": "여수 돌산도", "description": "밤바다 야경이 아름다운 곳으로 휴식에 제격입니다."},
        ],
        "액티비티": [
            {"title": "속초 설악산", "description": "등산과 케이블카를 이용한 짜릿한 액티비티를 경험할 수 있습니다."},
            {"title": "양양 서핑 해변", "description": "파도가 좋아 서핑을 즐기기에 최적의 장소입니다."},
            {"title": "단양 패러글라이딩", "description": "하늘을 날며 남한강의 아름다운 풍경을 한눈에 담을 수 있습니다."},
        ],
        "전시/관람형": [
            {"title": "서울 예술의전당", "description": "다양한 공연과 전시를 관람할 수 있는 복합 문화 공간입니다."},
            {"title": "전주 한옥마을", "description": "전통적인 한옥 건축물을 감상하며 한국의 아름다움을 느낄 수 있습니다."},
            {"title": "부산 영화의 전당", "description": "국제영화제 개최지로 다양한 영화를 즐길 수 있습니다."},
        ],
        "이색 체험": [
            {"title": "담양 죽녹원", "description": "대나무 숲길을 걸으며 힐링하고 이색적인 사진을 남길 수 있습니다."},
            {"title": "평창 양떼목장", "description": "드넓은 초원에서 양들과 교감하는 특별한 체험을 할 수 있습니다."},
            {"title": "안동 하회마을", "description": "전통적인 민속마을에서 고즈넉한 시간을 보낼 수 있습니다."},
        ]
    }

    async def get_random_recommendations(
        self, request: RandomRecommendRequest
    ) -> RandomRecommendResponse:
        """
        사용자 테마 기반으로 랜덤 여행지를 추천합니다. (약 5개)
        """
        # 1. RAG 기술 적용: 사용자 테마에 맞는 정보 가져오기 (여기서는 임시 데이터 사용)
        candidate_destinations = []
        for theme in request.themes:
            if theme in self.DUMMY_DATA:
                for dest in self.DUMMY_DATA[theme]:
                    candidate_destinations.append(
                        TravelDestination(
                            title=dest["title"],
                            description=dest["description"],
                            reason=[theme]
                        )
                    )

        # 2. 충분한 후보가 있을 경우, 무작위로 5개 선택
        if len(candidate_destinations) < 5:
            # 후보가 부족하면 전체 데이터에서 랜덤으로 채웁니다.
            all_destinations = [
                TravelDestination(title=item['title'], description=item['description'])
                for theme_list in self.DUMMY_DATA.values() for item in theme_list
            ]
            final_recommendations = random.sample(all_destinations, k=5)
        else:
            final_recommendations = random.sample(candidate_destinations, k=5)

        return RandomRecommendResponse(
            message="랜덤 여행지 추천이 완료되었습니다.",
            recommendations=final_recommendations
        )

    async def get_chat_recommendations(
        self, request: ChatRecommendRequest
    ) -> ChatRecommendResponse:
        """
        챗봇 대화를 기반으로 맞춤형 여행지를 추천합니다. (약 3개)
        """
        # 1. OpenAI API 호출을 위한 프롬프트 구성
        # 챗봇과의 대화를 통해 얻은 정보를 프롬프트에 담아 정확한 추천을 유도합니다.
        # 이 예시에서는 사용자의 마지막 메시지를 기반으로 프롬프트를 만듭니다.
        user_message = request.conversation[-1].content if request.conversation else ""

        # OpenAI API 호출 (실제 API 호출 코드는 여기에 위치)
        # 이 코드는 실제 API 호출을 시뮬레이션합니다.
        try:
            # API 호출 프롬프트 예시:
            # "사용자의 대화: '{user_message}'을 기반으로 사용자의 취향을 파악하여
            # 한국 내 여행지 3곳을 추천해줘. 추천 이유를 각 여행지마다 1~2줄로 설명해줘.
            # 응답은 JSON 형식으로 [{title: "", description: ""}] 형태로 줘."

            # 임시로 API 응답을 시뮬레이션합니다.
            await asyncio.sleep(1) # API 호출 대기 시간 시뮬레이션
            
            # OpenAI API의 응답을 가정
            dummy_api_response_content = """
            [
                {
                    "title": "서울 익선동 한옥마을",
                    "description": "복고풍의 분위기와 현대적인 감성이 공존하는 한옥마을로, 다양한 맛집과 카페를 탐방하기 좋습니다.",
                    "reason": ["도시", "레트로", "맛집 탐방"]
                },
                {
                    "title": "인제 자작나무 숲",
                    "description": "사계절 내내 아름다운 자작나무 숲을 거닐며 자연 속에서 힐링을 할 수 있는 곳입니다.",
                    "reason": ["자연", "힐링", "산책"]
                },
                {
                    "title": "군산 근대역사박물관",
                    "description": "일제강점기 시대의 역사와 문화를 배울 수 있는 곳으로, 역사에 관심이 많은 분께 추천합니다.",
                    "reason": ["역사", "교육", "실내"]
                }
            ]
            """
            import json
            api_result = json.loads(dummy_api_response_content)
            
            recommendations = [
                TravelDestination(
                    title=item["title"],
                    description=item["description"],
                    reason=item.get("reason", [])
                )
                for item in api_result
            ]

        except Exception as e:
            # API 호출 실패 시 에러 처리
            print(f"OpenAI API 호출 실패: {e}")
            raise HTTPException(status_code=500, detail="추천 기능에 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")

        return ChatRecommendResponse(
            message="대화 기반 맞춤형 여행지 추천이 완료되었습니다.",
            recommendations=recommendations
        )