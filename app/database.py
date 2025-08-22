# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ▶ SQLite (로컬 파일)
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

# SQLite는 멀티스레드 접근 시 추가 옵션 필요
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

