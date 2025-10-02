# backend/app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv
import os

# .env 로드 (DATABASE_URL 등)
load_dotenv()

# DB & 모델 등록 (실서비스는 Alembic 권장)
from app.database import engine
from app.models.common_models import Base
import app.models.market_models      # noqa: F401
import app.models.festival_models    # noqa: F401
import app.models.recommend_models   # noqa: F401

# 통합 라우터 (각 기능 라우터를 app/api.py에서 묶음)
from app.api import api_router

app = FastAPI(
    title="소소행 API",
    description="소도시 여행 추천 및 지역 콘텐츠 제공을 위한 RESTful API",
    version="1.0.0",
)

# 개발 편의: DEV_AUTO_CREATE=true 일 때만 자동 테이블 생성
if os.getenv("DEV_AUTO_CREATE", "false").lower() in ("1", "true", "yes"):
    Base.metadata.create_all(bind=engine)

# 통합 라우터 연결 (recommend/market/festival 등 포함)
app.include_router(api_router)

@app.get("/", tags=["root"])
def root():
    return {"message": "Sosohaeng Backend API is running", "docs": "/docs"}



"""

# backend/app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv


# models 관련 수정
from app.database import engine
from app.models.common_models import Base
# 모델 등록(실서비스에선 Alembic 권장)
import app.models.market_models      # noqa
import app.models.festival_models    # noqa
import app.models.recommend_models   # noqa


# 다른 라우터 모듈을 가져옵니다.
# from app.router import users_router, content_router
# 새로 만든 recommend_router를 임포트합니다.
from app.router import recommend_router
# 새로 만든 market_router를 임포트합니다.
from app.router import market_router
# 새로 만든 festival_router를 임포트합니다.
from app.router import festival_router

# .env 파일에서 환경 변수를 불러옵니다.
load_dotenv()

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="소소행 API",
    description="소도시 여행 추천 및 지역 콘텐츠 제공을 위한 RESTful API",
    version="1.0.0"
)

# 각 라우터를 메인 애플리케이션에 포함시킵니다.
#app.include_router(users_router.router)

#app.include_router(content_router.router)

# 각 기능별 router 등록
app.include_router(recommend_router.router)
app.include_router(market_router.router)
app.include_router(festival_router.router)

# 기본 root 엔드포인트
@app.get("/")
def root():
    return {"message": "Sosohaeng Backend Mock API is running"}

"""