import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# --- 1. .env 파일에서 데이터베이스 URL 로드 ---
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
load_dotenv(os.path.join(project_root, ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# --- 2. 데이터베이스 엔진 및 세션 설정 ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 3. Alembic을 위한 Naming Convention 설정 ---
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# --- 4. 통합된 Base 클래스 ---
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

def get_db():
    """FastAPI 의존성 주입(Dependency Injection)을 위한 DB 세션 생성기"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

