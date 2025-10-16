# backend/app/models/tour_models.py

from __future__ import annotations
from typing import List, Optional
from sqlalchemy import Integer, String, Text, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from app.db.database import Base


class TourData(Base):
    """
    관광공사 API의 여행 데이터를 저장하는 데이터베이스 테이블 모델.
    - 공통 정보 조회(search_common) API를 기반으로 설계되었습니다.
    """
    __tablename__ = "tour_data"

    # 기본키
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # 콘텐츠 ID (API에서 제공하는 고유 ID)
    contentid: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    # 콘텐츠 타입 ID (관광지, 문화시설 등)
    contenttypeid: Mapped[str] = mapped_column(String(5), nullable=False)

    # 주요 정보
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    addr1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    addr2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    areacode: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    sigungucode: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    tel: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    firstimage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    firstimage2: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mapx: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mapy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    homepage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 기타 정보
    cat1: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    cat2: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    cat3: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    booktour: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    zipcode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"TourData(id={self.id}, title='{self.title}')"