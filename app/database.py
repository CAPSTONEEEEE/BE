# app/database.py (예상되는 전체 내용)

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.common_models import Base # Base 모델 임포트 (가정)

# 1. DB 연결 URL 설정
# .env 파일에서 가져오는 것이 좋지만, 우선은 하드코딩된 SQLite 경로를 사용합니다.
# 실제 프로젝트에서는 os.getenv('DATABASE_URL')을 사용해야 합니다.
DATABASE_URL = "sqlite:///./tour_data.db" 

# 2. Engine 생성 (DB 연결)
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # SQLite 전용 설정 (FastAPI용)
)

# 3. SessionLocal 생성 (세션 공장)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. FastAPI DI용 함수
def get_db() -> Generator[Session, None, None]:
    """FastAPI 의존성 주입용 DB 세션 생성기"""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()