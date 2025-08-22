# app/__init__.py
# 애플리케이션 초기 설정 및 메인 라우터 포함
from fastapi import FastAPI
from app.api import api_router

def create_app() -> FastAPI:
    """
    FastAPI 애플리케이션 인스턴스를 생성하고 설정합니다.
    """
    app = FastAPI(
        title="소소행 API",
        description="소도시 여행 추천 및 지역 콘텐츠 제공을 위한 RESTful API",
        version="1.0.0"
    )

    # API 라우터를 포함하여 엔드포인트를 등록합니다.
    app.include_router(api_router, prefix="/api")

    # 애플리케이션 시작 및 종료 시 수행할 이벤트 리스너를 추가할 수 있습니다.
    @app.on_event("startup")
    async def startup_event():
        print("애플리케이션 시작...")

    @app.on_event("shutdown")
    async def shutdown_event():
        print("애플리케이션 종료...")

    return app

# app/api/__init__.py
# 모든 API 라우터들을 하나로 모으는 역할을 합니다.
from fastapi import APIRouter
from .. import routes_recommend, routes_places, routes_market, routes_health, routes_users

api_router = APIRouter()

# 각 모듈의 라우터들을 메인 라우터에 포함시킵니다.
api_router.include_router(routes_recommend.router, tags=["추천"])
api_router.include_router(routes_places.router, tags=["장소"])
api_router.include_router(routes_market.router, tags=["마켓"])
api_router.include_router(routes_health.router, tags=["상태 확인"])
api_router.include_router(routes_users.router, tags=["회원"])

# app/models/__init__.py
# 모든 데이터 스키마들을 한 곳에서 쉽게 불러올 수 있게 합니다.
from .schemas_common import *
from .schemas_recommend import *
from .schemas_places import *
from .schemas_market import *

# app/services/__init__.py
# 모든 서비스 모듈을 한 곳에서 쉽게 불러올 수 있게 합니다.
from .tourapi_client import *
from .recommender import *
from .market_service import *

# app/core/__init__.py
# 공통 유틸리티 모듈들을 한 곳에서 불러올 수 있게 합니다.
from .config import *
from .cache import *
from .database import *
