# backend/app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv

# ★ 정적 파일 제공
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

# CORS
from fastapi.middleware.cors import CORSMiddleware

# models 관련 (기존 그대로)
from app.db.database import engine
from app.db.database import Base
import app.models.market_models      # noqa
import app.models.festival_models    # noqa
import app.models.recommend_models   # noqa

from app.router import recommend_router
from app.router import market_router
from app.router import festival_router
from app.router import users_router

load_dotenv()

app = FastAPI(
    title="소소행 API",
    description="소도시 여행 추천 및 지역 콘텐츠 제공을 위한 RESTful API",
    version="1.0.0"
)

# ===== CORS (그대로 유지) =====
origins = ["*"]  # 내부망/디바이스 접근용 임시 전체 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ============================

# ======= 정적 mock 데이터 마운트 (기존 유지) =======
BASE_DIR = Path(__file__).resolve().parent.parent  # BE/app -> parent == BE
MOCK_DIR = BASE_DIR / "mock_data"
app.mount("/mock_data", StaticFiles(directory=str(MOCK_DIR)), name="mock_data")

# ======= 업로드 정적 파일 마운트 (★ 최소 추가) =======
APP_DIR = Path(__file__).resolve().parent  # app/
STATIC_DIR = APP_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
# 예: http://<LAN IP>:8000/static/uploads/xxxxx.jpg
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
# =============================================

# 기능 라우터
app.include_router(recommend_router.router, prefix="/api/v1")
app.include_router(market_router.router, prefix="/api/v1")
app.include_router(festival_router.router, prefix="/api/v1")
app.include_router(users_router.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Sosohaeng Backend Mock API is running"}
