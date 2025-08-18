# app/models/festival_models.py
from __future__ import annotations
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import Integer, String, Text, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.common_models import Base  # 공통 DeclarativeBase


# -------------------------
# SQLAlchemy ORM Models
# -------------------------
class Festival(Base):
    """
    지역 축제/행사: TourAPI 연동 결과를 수용할 수 있도록 구성.
    - 기간형(event_start/end_date), 위치, 소개, 대표 이미지 등
    """
    __tablename__ = "festivals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False, index=True)  # 기존 name -> title 통일
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # 주소 또는 장소명
    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey("regions.id"), nullable=True, index=True)

    event_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    event_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # 관계 (Region 모델은 market_models.py에 정의되어 있음)
    region = relationship("Region")

# 검색 최적화 인덱스
Index("idx_festivals_title_date", Festival.title, Festival.event_start_date)


# -------------------------
# Pydantic Schemas (I/O)
# -------------------------
class FestivalBase(BaseModel):
    title: str = Field(..., description="축제/행사명")
    location: Optional[str] = Field(None, description="장소/주소")
    region_id: Optional[int] = Field(None, description="지역 식별자(Regions)")
    event_start_date: Optional[date] = Field(None, description="행사 시작일")
    event_end_date: Optional[date] = Field(None, description="행사 종료일")
    description: Optional[str] = Field(None, description="소개/설명")
    image_url: Optional[HttpUrl] = Field(None, description="대표 이미지 URL")

class FestivalCreate(FestivalBase):
    """신규 축제 생성 요청 스키마"""
    pass

class FestivalUpdate(BaseModel):
    """축제 수정 요청 스키마(부분 업데이트 허용)"""
    title: Optional[str] = None
    location: Optional[str] = None
    region_id: Optional[int] = None
    event_start_date: Optional[date] = None
    event_end_date: Optional[date] = None
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None

class FestivalOut(FestivalBase):
    """축제 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
