# BE/app/main.py
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(project_root, ".env"))

from app.core.config import get_settings
settings = get_settings()

# --- DB 및 모델 임포트 (Alembic/Uvicorn이 인식하도록) ---
from app.db.database import Base, engine, test_db_connection
import app.models

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="소도시 여행 추천 및 지역 콘텐츠 제공을 위한 RESTful API",
    version="1.0.0"
)

# ===== CORS  =====
#CORS 미들웨어 설정 (보안 강화: settings.CORS_ORIGINS 사용)
if settings.CORS_ORIGINS:
    # 콤마로 구분된 문자열을 리스트로 변환
    origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(',')]
else:
    # 설정되지 않은 경우 (개발 환경에서만 사용 권장)
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print(f"CORS origins configured: {origins}")
# ============================

# --- API 라우터 임포트 ---
from app.api import api_router 
app.include_router(api_router, prefix=settings.API_V1_STR) 

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