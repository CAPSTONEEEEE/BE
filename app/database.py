# app/database.py
import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# .env 로드 (DATABASE_URL 우선)
load_dotenv()

# 우선순위: .env -> 기본 SQLite 파일
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# 엔진 옵션: DB 엔진별로 안전 설정
engine_kwargs = {
    "pool_pre_ping": True,  # 끊어진 커넥션 자동 감지
}

# SQLite는 스레드 체크 옵션 필요
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    """FastAPI 의존성 주입용 DB 세션 생성기"""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
