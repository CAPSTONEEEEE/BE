# app/models/tour_models.py (파일 이름이 tour_models.py로 가정)

from __future__ import annotations
from typing import Optional
from sqlalchemy import String, Float, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base 

class TourInfo(Base):
    """
    TourAPI의 지역기반 관광지 정보를 저장하는 데이터베이스 모델.
    """
    __tablename__ = "recommend_tourInfo" 
    __table_args__ = {'extend_existing': True}

    # 1. 핵심 식별자 (Primary Key)
    contentid: Mapped[str] = mapped_column(String(20), primary_key=True)
    contenttypeid: Mapped[str] = mapped_column(String(10), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # 2. 위치 및 주소 정보
    addr1: Mapped[Optional[str]] = mapped_column(String(255))
    addr2: Mapped[Optional[str]] = mapped_column(String(255))
    zipcode: Mapped[Optional[str]] = mapped_column(String(10))
    areacode: Mapped[Optional[str]] = mapped_column(String(10))
    sigungucode: Mapped[Optional[str]] = mapped_column(String(10))
    
    # 3. 카테고리 정보
    cat1: Mapped[Optional[str]] = mapped_column(String(10))
    cat2: Mapped[Optional[str]] = mapped_column(String(10))
    cat3: Mapped[Optional[str]] = mapped_column(String(10))
    
    # 4. 이미지 및 연락처
    tel: Mapped[Optional[str]] = mapped_column(String(50))
    firstimage: Mapped[Optional[str]] = mapped_column(String(500))
    firstimage2: Mapped[Optional[str]] = mapped_column(String(500))
    
    # 5. 지도 좌표
    mapx: Mapped[Optional[float]] = mapped_column(Float) # Decimal 대신 Float 사용
    mapy: Mapped[Optional[float]] = mapped_column(Float)
    mlevel: Mapped[Optional[int]] = mapped_column(Integer)
    
    # 6. 타임스탬프
    createdtime: Mapped[Optional[str]] = mapped_column(String(14))
    modifiedtime: Mapped[Optional[str]] = mapped_column(String(14))