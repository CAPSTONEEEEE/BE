# BE/app/api.py
from fastapi import APIRouter

# 개별 라우터 임포트
from app.router.market_router import router as market_router
from app.router.festival_router import router as festival_router
from app.router.recommend_router import router as recommend_router
from app.router.common_router import router as common_router
from app.router.users_router import router as users_router
# ⚠️ content_router는 Review 모델 의존성 깨져 임시 제외
# from app.router.content_router import router as content_router

api_router = APIRouter()

# 기능별 라우터 등록
api_router.include_router(market_router)
api_router.include_router(festival_router)
api_router.include_router(recommend_router)
api_router.include_router(common_router)
api_router.include_router(users_router)  
# api_router.include_router(content_router)  # TODO: Review 스키마 정리 후 재활성화
