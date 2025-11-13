from __future__ import annotations
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from sqlalchemy import Column, Integer, String, Float, Text, Index, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from app.db.database import Base # RDS 연결을 위한 Base 임포트

Base = declarative_base()

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
    
    modified_time = Column(String(14))
    
    @classmethod
    def distance_col(cls, user_lat: float, user_lon: float):
        """
        사용자 위치로부터 축제 장소까지의 거리를 계산하는 SQLAlchemy 표현식을 반환합니다.
        (cls.mapy: 위도, cls.mapx: 경도 사용)
        """
        # 지구의 반경 (R)을 6371km로 사용합니다.
        R_KM = 6371.0

        return (
            R_KM * func.acos(
                func.cos(func.radians(user_lat)) * func.cos(func.radians(cls.mapy)) # <--- Festival의 위도(mapy) 컬럼
                * func.cos(func.radians(cls.mapx) - func.radians(user_lon)) # <--- Festival의 경도(mapx) 컬럼
                + func.sin(func.radians(user_lat)) * func.sin(func.radians(cls.mapy))
            )
        ).label('distance')
# 위치 기반 검색을 위한 인덱스 유지
Index("idx_festivals_title_date", Festival.title, Festival.event_start_date)


# -------------------------
# Pydantic Schemas (mapx, mapy 반영)
# -------------------------
class FestivalBase(BaseModel):
    title: str
    location: Optional[str] = None
    event_start_date: str # DB와 동일하게 String으로 변경
    event_end_date: str # DB와 동일하게 String으로 변경
    image_url: Optional[str] = None
    
    mapx: float
    mapy: float
    modified_time: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True,
    )


class FestivalCreate(FestivalBase):
    contentid: str # API 연동시 필요

class FestivalUpdate(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    event_start_date: Optional[str] = None
    event_end_date: Optional[str] = None
    image_url: Optional[str] = None
    mapx: Optional[float] = None
    mapy: Optional[float] = None
    modified_time: Optional[str] = None

    model_config = ConfigDict(validate_by_name=True)
