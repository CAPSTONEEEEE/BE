# backend/app/services/common_service.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite 데이터베이스 파일 경로 정의
# `../`는 `app/services` 디렉토리에서 `backend` 디렉토리로 이동한 뒤,
# `database.db` 파일을 찾는 것을 의미합니다.
DATABASE_URL = "sqlite:///../database.db"

# SQLAlchemy 엔진 생성
# connect_args={"check_same_thread": False}는 SQLite 사용 시 필수적입니다.
# FastAPI의 Request는 단일 스레드에서 처리되지만, SQLAlchemy는 기본적으로
# 세션을 여러 스레드에서 공유하는 것을 막기 때문에 이 옵션을 추가합니다.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 데이터베이스 세션 생성
# autocommit=False: 커밋을 직접 호출해야만 변경 사항이 저장됩니다.
# autoflush=False: 자동으로 세션을 플러시하지 않아 성능을 최적화할 수 있습니다.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 모델의 기본 클래스를 생성
# 이 클래스를 상속받아 모든 데이터베이스 테이블 클래스를 만듭니다.
Base = declarative_base()


def get_db():
    """
    API 엔드포인트에 데이터베이스 세션을 제공하는 의존성 주입 함수.
    `yield`를 사용하여 요청이 끝난 후 자동으로 세션을 닫습니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
