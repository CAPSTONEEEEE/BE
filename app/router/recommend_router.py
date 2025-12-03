# app/router/recommend_router.py

# 1. 필요한 라이브러리 및 스키마 임포트
from fastapi import APIRouter, HTTPException, Depends  # [수정] Depends 추가
from sqlalchemy.orm import Session  # [수정] Session 타입 힌트 추가

from app.schemas import (
    ChatbotRequest,       
    RandomRecommendRequest,
    RandomRecommendResponse,
    ChatRecommendResponse,
)

from app.services.recommend_service import (
    get_chatbot_search_keywords_and_recommendations,
    get_nearby_spots,
    get_spot_detail
)

from app.db.database import get_db 

# 2. APIRouter 인스턴스 정의
router = APIRouter(tags=["추천"])

# 3. 라우터 엔드포인트 정의
# AI 챗봇 엔드포인트
@router.post("/chatbot", summary="RAG 기반 AI 챗봇 추천", response_model=ChatRecommendResponse)
async def chatbot_endpoint(
    request: ChatbotRequest, 
    db: Session = Depends(get_db) # [수정] FastAPI 의존성 주입으로 db 세션 획득
):
    try:
        # [수정] 서비스 함수 호출 시 db 인자 전달
        result = await get_chatbot_search_keywords_and_recommendations(request.message, db)
        
        # result는 dict 형태로 {"ai_response_text": ..., "db_recommendations": ...}를 포함함
        return ChatRecommendResponse(
            response=result["ai_response_text"],
            recommendations=result["db_recommendations"] 
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"챗봇 라우터 내부 오류: {e}")
        # 상세 에러 로그를 출력하여 디버깅 용이하게 함
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500, 
            detail=f"챗봇 서비스 처리 중 알 수 없는 서버 오류가 발생했습니다."
        )

# 랜덤 추천 엔드포인트 (기존 코드 유지)
@router.post("/random_recommendations", summary="랜덤 여행지 추천", response_model=RandomRecommendResponse)
def get_random_recommendations(request: RandomRecommendRequest):
    # 만약 get_random_recommendations_from_db 함수도 DB를 쓰도록 바꿨다면 
    # 여기도 위와 똑같이 db: Session = Depends(get_db)를 추가해야 합니다.
    # 현재 코드 기준으로는 그대로 둡니다.
    try:
        # 주의: 이 함수가 어디서 임포트되었는지 코드상에는 안 보이지만, 
        # 만약 db가 필요하다면 위 chatbot_endpoint처럼 수정해야 합니다.
        from app.services.recommend_service import get_random_recommendations_from_db # 가상의 임포트
        recommendations = get_random_recommendations_from_db(themes=request.themes)
        
        return RandomRecommendResponse(
            message="랜덤 여행지 추천이 완료되었습니다.",
            recommendations=recommendations
        )
    except HTTPException as e:
        raise e
    except ImportError:
         # 임시 처리 (랜덤 추천 함수가 없어서 에러날 경우를 대비)
         return RandomRecommendResponse(
            message="랜덤 추천 기능 준비 중",
            recommendations=[]
        )
         

# 1. [페이지 1용] 주변 관광지 리스트 조회
@router.get("/nearby/{contentid}", summary="반경 20km 주변 관광지 조회")
def get_nearby_places(contentid: str, db: Session = Depends(get_db)):
    print(f"==========================================")
    print(f"🚀 [API 요청 도착] ID: {contentid}")
    print(f"==========================================")
    
    try:
        result = get_nearby_spots(contentid, db)
        
        if not result["target"]:
            print(f"❌ [DB 조회 실패] 해당 ID({contentid})를 DB에서 찾을 수 없습니다.")
            raise HTTPException(status_code=404, detail="해당 여행지를 찾을 수 없습니다.")
        
        print(f"✅ [DB 조회 성공] 주변 여행지 개수: {len(result['nearby_spots'])}")
        return result
    except Exception as e:
        print(f"Error fetching nearby spots: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="주변 관광지 조회 실패")

# 2. [페이지 2용] 특정 관광지 상세 정보 조회
@router.get("/detail/{contentid}", summary="특정 관광지 상세 정보 조회")
def get_place_detail(contentid: str, db: Session = Depends(get_db)):
    spot = get_spot_detail(contentid, db)
    if not spot:
        raise HTTPException(status_code=404, detail="여행지 정보를 찾을 수 없습니다.")
    return spot