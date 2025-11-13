import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Column, Integer, String, Numeric, DateTime, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column

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

# --- 5. recommend_tourInfo 테이블 모델 정의 (수정) ---
class TourInfo(Base):
    __tablename__ = "recommend_tourInfo"
    
    # primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True) # Type: INT
    
    # API 응답에서 매핑될 컬럼
    contentid: Mapped[str] = mapped_column(String(10), unique=True, index=True) # Type: VARCHAR(10)
    title: Mapped[str] = mapped_column(String(255))                             # Type: VARCHAR(255)
    addr1: Mapped[str] = mapped_column(String(255))                             # Type: VARCHAR(255)
    
    # 날짜 필드: VARCHAR(8)에 맞춤
    event_start_date: Mapped[str] = mapped_column(String(8), nullable=True)     # Type: VARCHAR(8)
    event_end_date: Mapped[str] = mapped_column(String(8), nullable=True)       # Type: VARCHAR(8)
    
    # 지도 좌표: DECIMAL(12, 7)에 맞춤 (Numeric 사용)
    mapx: Mapped[float] = mapped_column(Numeric(12, 7), nullable=True)          # Type: DECIMAL
    mapy: Mapped[float] = mapped_column(Numeric(12, 7), nullable=True)          # Type: DECIMAL
    
    # 이미지 URL
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)          # Type: VARCHAR(500)
    
    # 자동 생성되는 시간 정보
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now()) # Type: DATETIME
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now()) # Type: DATETIME
    
    def __repr__(self) -> str:
        return f"TourInfo(id={self.id!r}, title={self.title!r})"