# migrations/env.py
# -----------------------------------------------
# Alembic 환경설정
# - .env(DATABASE_URL)에서 DB URL을 읽어들임
# - 앱의 Base 메타데이터를 연결하여 autogenerate 사용
# - 모든 모델 모듈을 강제 import하여 테이블 인식 보장
# - SQLite: render_as_batch=True 로 안전한 스키마 변경
# - 타입/기본값 변경 감지(compare_type / compare_server_default)
# -----------------------------------------------

from __future__ import annotations

import os
import sys
import app.models.tour_models
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from dotenv import load_dotenv

# Alembic 설정 객체(로깅 포함)
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------
# 앱 모듈 import 가능하도록 경로 추가
# (현재 파일: BE/migrations/env.py → 상위(BE)로 올라가서 sys.path에 추가)
# ---------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# ---------------------------
# 앱의 Base 메타데이터 로드
# ※ autogenerate가 모든 테이블을 인식하려면
#    각 모델 모듈을 반드시 import 해야 함
# ---------------------------
from app.models.common_models import Base  # noqa: E402

# 모든 모델 강제 import (테이블 등록 보장)
import app.models.market_models  # noqa: F401,E402
import app.models.festival_models  # noqa: F401,E402
import app.models.recommend_models  # noqa: F401,E402

target_metadata = Base.metadata

# ---------------------------
# .env에서 DATABASE_URL 로드
# ---------------------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# SQLite 여부 판단 (배치 모드 필요)
IS_SQLITE = DATABASE_URL.startswith("sqlite")


def run_migrations_offline() -> None:
    """오프라인 모드: DB 커넥션 없이 SQL 스크립트 생성."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,               # 타입 변경 감지
        compare_server_default=True,     # 서버 기본값 변경 감지
        render_as_batch=IS_SQLITE,       # SQLite 테이블 재작성 모드
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """온라인 모드: 실제 DB 커넥션으로 마이그레이션 적용."""
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,               # 타입 변경 감지
            compare_server_default=True,     # 서버 기본값 변경 감지
            render_as_batch=IS_SQLITE,       # SQLite 테이블 재작성 모드
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
