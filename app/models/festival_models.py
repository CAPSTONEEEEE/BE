from __future__ import annotations
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from sqlalchemy import Integer, String, Text, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.common_models import Base


# -------------------------
# SQLAlchemy ORM Model
# -------------------------
class Festival(Base):
    __tablename__ = "festivals"
    
    # 1. id를 Primary Key로 사용하고, contentid는 고유값(unique)으로 설정
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 2. contentid도 mapped_column 스타일로 통일하고, primary_key=True는 제거
    contentid: Mapped[str] = mapped_column(String, unique=True, index=True)
    
    title: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey("regions.id"), nullable=True, index=True)
    event_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    event_end_date: Mapped[date] = mapped_column(Date, nullable=False)
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
    title: str
    location: Optional[str] = None
    region_id: Optional[int] = None
    start_date: Optional[date] = Field(None, alias="event_start_date")
    end_date: Optional[date] = Field(None, alias="event_end_date")
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None

    # ✅ Pydantic v2 설정
    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True,  # (v1: allow_population_by_field_name)
    )


class FestivalCreate(FestivalBase):
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

    # ✅ Pydantic v2 설정 (별도 from_attributes 불필요)
    model_config = ConfigDict(validate_by_name=True)


class FestivalOut(FestivalBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    # ✅ Pydantic v2 설정
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)
