# migrations/env.py
# -----------------------------------------------
# Alembic 환경설정
# - .env(DATABASE_URL)에서 DB URL을 읽어들임
# - 앱의 Base 메타데이터를 연결하여 autogenerate 사용
# - 모든 모델 모듈을 강제 import하여 테이블 인식 보장
# - 타입/기본값 변경 감지(compare_type / compare_server_default)
# -----------------------------------------------

import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

# --- 1. 경로 설정 ---
# 프로젝트의 루트 폴더(BE/)를 파이썬의 모듈 검색 경로에 추가합니다.
# 이렇게 해야 env.py에서 'app' 모듈을 찾을 수 있습니다.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# --- 2. 모델 및 Base 메타데이터 임포트 ---
# 이제 경로가 설정되었으므로 app 모듈을 정상적으로 가져올 수 있습니다.
# Alembic이 데이터베이스 스키마 변경을 감지하려면 모든 모델이 Base를 상속해야 합니다.
from app.db.database import Base
from app.models import * # User, Festival 등 모든 모델을 임포트해서 Base.metadata에 등록합니다.

# --- 3. .env 파일 로드 및 데이터베이스 URL 설정 ---
# 프로젝트 루트 폴더에 있는 .env 파일을 로드합니다.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# .env 파일에 DATABASE_URL이 있으면 그 값을 사용하고, 없으면 새로 조합합니다.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

IS_SQLITE = "sqlite" in str(DATABASE_URL)

# --- 4. Alembic 설정 ---
# Alembic 설정 객체를 가져와 실제 데이터베이스 URL을 설정합니다.
config = context.config
config.set_main_option("sqlalchemy.url", str(DATABASE_URL))

# 로깅 설정을 로드합니다.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembic이 참조할 메타데이터를 설정합니다.
target_metadata = Base.metadata

# --- 마이그레이션 함수들 ---

def run_migrations_offline() -> None:
    """오프라인 모드에서 마이그레이션을 실행합니다. (SQL 스크립트 생성)"""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=IS_SQLITE,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """온라인 모드에서 마이그레이션을 실행합니다. (DB에 직접 적용)"""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"), poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=IS_SQLITE,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
