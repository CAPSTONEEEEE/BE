# BE/app/api.py
from fastapi import APIRouter

# 개별 라우터 임포트
from app.router.market_router import router as market_router
from app.router.festival_router import router as festival_router
from app.router.recommend_router import router as recommend_router
from app.router.common_router import router as common_router
from app.router.users_router import router as users_router
from app.router.favorite_router import router as favorite_router

api_router = APIRouter()

# 기능별 라우터 등록
api_router.include_router(market_router)
api_router.include_router(festival_router)
api_router.include_router(recommend_router)
api_router.include_router(common_router)
api_router.include_router(users_router)  
api_router.include_router(favorite_router) 