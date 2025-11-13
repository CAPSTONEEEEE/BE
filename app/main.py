# BE/app/main.py
import os

from fastapi import FastAPI
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(project_root, ".env"))

from fastapi.staticfiles import StaticFiles
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware


from app.router import recommend_router
from app.router import market_router
from app.router import festival_router

# --- DB 및 모델 임포트 (Alembic/Uvicorn이 인식하도록) ---
from app.db.database import Base, engine, test_db_connection
# 아래 noqa 임포트는 app/models/__init__.py에서 처리하므로 주석 처리
# import app.models.market_models      # noqa
# import app.models.festival_models    # noqa
# import app.models.recommend_models   # noqa
import app.models # __init__.py를 임포트

# --- API 라우터 임포트 ---
from app.api import api_router # ◀◀◀ main.py가 직접 임포트하던 것을 api.py로 교체



app = FastAPI(
    title="소소행 API",
    description="소도시 여행 추천 및 지역 콘텐츠 제공을 위한 RESTful API",
    version="1.0.0"
)

# ===== CORS (그대로 유지) =====
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ============================

# ======= 정적 파일 마운트 (mock_data 및 uploads) =======
BASE_DIR = Path(__file__).resolve().parent.parent  # BE/app -> parent == BE
MOCK_DIR = BASE_DIR / "mock_data"
STATIC_DIR = BASE_DIR / "app" / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# /mock_data 경로는 /api/v1과 별개로 루트에서 접근
app.mount("/mock_data", StaticFiles(directory=str(MOCK_DIR)), name="mock_data")
# /static 경로는 /api/v1과 별개로 루트에서 접근
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
# =============================================


# 기능 라우터
app.include_router(recommend_router.router, prefix="/api/v1")
app.include_router(market_router.router, prefix="/api/v1")
app.include_router(festival_router.router, prefix="/api/v1")
app.include_router(api_router, prefix="/api/v1") 

@app.on_event("startup")
def startup_event():
    """
    서버 시작 시 DB 연결을 테스트하여 환경 변수 오류를 즉시 감지합니다.
    """
    test_db_connection()

@app.get("/")
def root():
    # 이 엔드포인트는 common_router.py의 "/"와 겹치므로
    # common_router.py의 "/"가 /api/v1/ 로 등록됩니다.
    return {"message": "Sosohaeng Backend API Root"}