# app/models/common_models.py
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

# 제약조건 이름 규칙 (Naming Convention)
# Alembic autogenerate 시 일관된 이름이 생성되도록 보장
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",                        # 인덱스
    "uq": "uq_%(table_name)s_%(column_0_name)s",          # 유니크 제약조건
    "ck": "ck_%(table_name)s_%(constraint_name)s",        # 체크 제약조건
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # 외래키
    "pk": "pk_%(table_name)s",                            # 기본키
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
