# app/models/festival_models.py
from __future__ import annotations
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import Integer, String, Text, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.common_models import Base  # DeclarativeBase


# -------------------------
# SQLAlchemy ORM Model
# -------------------------
class Festival(Base):
    __tablename__ = "festivals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey("regions.id"), nullable=True, index=True)

    # DB 컬럼명 유지하되, Pydantic에서 alias로 start_date/end_date 사용
    event_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    event_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    region = relationship("Region")

Index("idx_festivals_title_date", Festival.title, Festival.event_start_date)


# -------------------------
# Pydantic Schemas
# -------------------------
class FestivalBase(BaseModel):
    title: str = Field(..., description="축제/행사명")
    location: Optional[str] = None
    region_id: Optional[int] = None
    start_date: Optional[date] = Field(None, alias="event_start_date")
    end_date: Optional[date] = Field(None, alias="event_end_date")
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True  # alias로 데이터 매핑 가능


class FestivalCreate(FestivalBase):
    """축제 생성 요청"""
    title: str
    start_date: date
    end_date: date


class FestivalUpdate(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    region_id: Optional[int] = None
    start_date: Optional[date] = Field(None, alias="event_start_date")
    end_date: Optional[date] = Field(None, alias="event_end_date")
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None

    class Config:
        allow_population_by_field_name = True


class FestivalOut(FestivalBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
