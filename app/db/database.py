# BE/app/db/database.py

import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, MetaData, text, Column, Integer, String, Numeric, DateTime, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.engine import URL 
from sqlalchemy.exc import OperationalError # DB 연결 오류 처리를 위해 추가

# 주의: main.py가 .env 로드를 책임지므로, 여기서는 경로 계산을 제거합니다.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(project_root, ".env"))

# RDS 접속 정보 (환경 변수에서 직접 로드)
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST") 
DB_NAME = os.getenv("DB_NAME") 

# 환경 변수 누락 시 ValueError 발생 (main.py 로드가 성공하면 발생하지 않음)
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    raise ValueError("RDS 접속 환경 변수(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)가 설정되지 않았습니다. .env 파일을 확인하세요.")

# MySQL URL 생성
DATABASE_URL_STR = URL.create(
    "mysql+pymysql", 
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database=DB_NAME,
).render_as_string(hide_password=False)

# --- 2. 데이터베이스 엔진 및 세션 설정 ---
engine = create_engine(DATABASE_URL_STR, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 3. Alembic을 위한 Naming Convention 설정 (기존과 동일) ---
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# --- 4. 통합된 Base 클래스 (기존과 동일) ---
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

def get_db():
    """FastAPI 의존성 주입(Dependency Injection)을 위한 DB 세션 생성기"""
    db = SessionLocal()
    try:
        # DB 연결 테스트 (인스턴스가 꺼져 있을 경우 대비)
        db.execute(text("SELECT 1")) 
        yield db
    except OperationalError as e:
        db.close()
        print(f"DB Operational Error: {e}")
        raise
    finally:
        db.close()


def test_db_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("DB 연결 테스트 성공.")
        return True
    except OperationalError as e:
        print("DB 연결 실패: RDS 인스턴스가 실행 중(Available)인지 확인하세요.")
        print(f"   오류 상세: {e}")
        return False

from app.models import tour_models
