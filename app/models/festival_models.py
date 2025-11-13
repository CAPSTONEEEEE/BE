from __future__ import annotations
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base

from app.db.database import Base # RDS 연결을 위한 Base 임포트


# -------------------------
# SQLAlchemy ORM Model
# -------------------------
class Festival(Base):
    __tablename__ = "festivals"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # API의 contentid와 매핑되며 고유해야 함
    contentid = Column(String(30), unique=True, nullable=False) 
    
    title = Column(String(255), nullable=False)
    
    # API의 addr1을 저장하기 위한 필드 (오류 해결)
    location = Column(String(255)) 
    
    # TourAPI는 날짜를 YYYYMMDD 문자열로 제공하므로 String(8)로 처리
    event_start_date = Column(String(8)) 
    event_end_date = Column(String(8))
    
    mapx = Column(Float) # 경도
    mapy = Column(Float) # 위도
    
    image_url = Column(Text) # URL을 저장
    
    # TourAPI에는 없으나 DB 관리를 위해 추가 (스크립트에서 값을 넣지 않아도 DB가 처리)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 🟢 위치 기반 검색을 위한 인덱스 유지
Index("idx_festivals_title_date", Festival.title, Festival.event_start_date)


# -------------------------
# Pydantic Schemas (mapx, mapy 반영)
# -------------------------
class FestivalBase(BaseModel):
    title: str
    location: Optional[str] = None
    # region_id: Optional[int] = None # ⚠️ Region 필드 제거
    event_start_date: str # DB와 동일하게 String으로 변경
    event_end_date: str # DB와 동일하게 String으로 변경
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    
    # 🟢 위치 정보 추가
    mapx: float
    mapy: float

    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True,
    )


class FestivalCreate(FestivalBase):
    contentid: str # API 연동시 필요

class FestivalUpdate(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    # region_id: Optional[int] = None # ⚠️ Region 필드 제거
    event_start_date: Optional[str] = None
    event_end_date: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    mapx: Optional[float] = None
    mapy: Optional[float] = None

    model_config = ConfigDict(validate_by_name=True)


class FestivalOut(FestivalBase):
    id: int
    contentid: str # TourAPI ID 추가
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True, validate_by_name=True)