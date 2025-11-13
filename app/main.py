# BE/app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from fastapi.middleware.cors import CORSMiddleware

# --- DB 및 모델 임포트 (Alembic/Uvicorn이 인식하도록) ---
from app.db.database import Base, engine
# 아래 noqa 임포트는 app/models/__init__.py에서 처리하므로 주석 처리
# import app.models.market_models      # noqa
# import app.models.festival_models    # noqa
# import app.models.recommend_models   # noqa
import app.models # __init__.py를 임포트

# --- API 라우터 임포트 ---
from app.api import api_router # ◀◀◀ main.py가 직접 임포트하던 것을 api.py로 교체

load_dotenv()

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

# ======= 메인 API 라우터 등록 =======
# api.py에 정의된 모든 라우터 (market, festival, common 등)를
# /api/v1 접두사와 함께 등록합니다.
app.include_router(api_router, prefix="/api/v1") 
# ===================================

@app.get("/")
def root():
    # 이 엔드포인트는 common_router.py의 "/"와 겹치므로
    # common_router.py의 "/"가 /api/v1/ 로 등록됩니다.
    return {"message": "Sosohaeng Backend API Root"}