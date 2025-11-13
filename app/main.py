# backend/app/main.py
import os
from fastapi import FastAPI
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(project_root, ".env"))

# ★ 추가: 정적 파일 제공
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# CORS
from fastapi.middleware.cors import CORSMiddleware

# models 관련 수정
from app.db.database import engine, test_db_connection
from app.db.database import Base
import app.models.market_models      # noqa
import app.models.festival_models    # noqa
import app.models.recommend_models   # noqa

from app.router import recommend_router
from app.router import market_router
from app.router import festival_router


app = FastAPI(
    title="소소행 API",
    description="소도시 여행 추천 및 지역 콘텐츠 제공을 위한 RESTful API",
    version="1.0.0"
)
origins = ["*"] # 모든 출처를 허용 (개발용)

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

# ======= 정적 mock 데이터 마운트 (핵심) =======
# 이 파일(app/main.py)의 상위(= BE) 폴더에 있는 mock_data 폴더를 가리킵니다.
BASE_DIR = Path(__file__).resolve().parent.parent  # BE/app -> parent == BE
MOCK_DIR = BASE_DIR / "mock_data"

# /mock_data 경로로 정적 파일을 서비스하도록 마운트
# 예: http://<LAN IP>:8000/mock_data/mock_markets.json
app.mount("/mock_data", StaticFiles(directory=str(MOCK_DIR)), name="mock_data")
# =============================================

# 기능 라우터
app.include_router(recommend_router.router, prefix="/api/v1")
app.include_router(market_router.router, prefix="/api/v1")
app.include_router(festival_router.router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    """
    서버 시작 시 DB 연결을 테스트하여 환경 변수 오류를 즉시 감지합니다.
    """
    test_db_connection()

@app.get("/")
def root():
    return {"message": "Sosohaeng Backend Mock API is running"}
