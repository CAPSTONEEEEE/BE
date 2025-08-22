from fastapi import APIRouter

from app.router.users_router import router as users_router
from app.router.market_router import router as market_router
from app.router.festival_router import router as festival_router
from app.router.recommend_router import router as recommend_router
from app.router.content_router import router as content_router

api_router = APIRouter()
api_router.include_router(users_router)
api_router.include_router(market_router)
api_router.include_router(festival_router)
api_router.include_router(recommend_router)
api_router.include_router(content_router)
