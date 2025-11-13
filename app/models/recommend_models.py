from __future__ import annotations
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from sqlalchemy import Column, Integer, String, Float, Index, Text
from sqlalchemy.ext.declarative import declarative_base # (사용하는 경우)

from app.db.database import Base # RDS 연결을 위한 Base 임포트


# -------------------------
# SQLAlchemy ORM Model
# -------------------------
class RecommendTourInfo(Base):
    """
    TourAPI의 '지역 기반 관광정보' 응답을 저장하는 테이블 모델
    테이블명: recommend_tourInfo
    """
    __tablename__ = "recommend_tourInfo"
    
    # ⚠️ NOTE: 테이블 스키마에 id가 없지만, SQLAlchemy는 기본적으로 PK가 필요합니다.
    # 만약 contentid를 PK로 사용한다면 id 필드는 제거하고 contentid에 primary_key=True를 부여합니다.
    # 제공해주신 sync_recommends.py에서 contentid를 PK로 사용하고 있으므로, 그에 맞춥니다.
    
    contentid = Column(String(20), primary_key=True, index=True)  # VARCHAR(20) & Primary Key
    
    contenttypeid = Column(String(10)) # VARCHAR(10)
    title = Column(String(255), nullable=False) # VARCHAR(255)
    addr1 = Column(String(255)) # VARCHAR(255)
    addr2 = Column(String(255)) # VARCHAR(255)
    zipcode = Column(String(10)) # VARCHAR(10)
    
    areacode = Column(String(10)) # VARCHAR(10)
    sigungucode = Column(String(10)) # VARCHAR(10)
    
    cat1 = Column(String(10)) # VARCHAR(10)
    cat2 = Column(String(10)) # VARCHAR(10)
    cat3 = Column(String(10)) # VARCHAR(10)
    tel = Column(String(50)) # VARCHAR(50)
    
    firstimage = Column(String(500)) # firstimage URL
    firstimage2 = Column(String(500)) # firstimage2 URL
    
    # DB 스키마는 DECIMAL이지만, SQLAlchemy에서 Float 또는 Numeric으로 매핑합니다. 
    # sync_recommends.py에 맞추어 Float을 사용합니다.
    mapx = Column(Float) # 경도 (DECIMAL)
    mapy = Column(Float) # 위도 (DECIMAL)
    
    mlevel = Column(Integer) # INT (API 응답은 string이지만, DB는 INT이므로 변환 필요)
    
    # 시간 정보는 API 응답에서 YYYYMMDDHHMMSS 문자열로 오므로 String(14)로 처리
    createdtime = Column(String(14)) # VARCHAR(14)
    modifiedtime = Column(String(14)) # VARCHAR(14)

# -------------------------
# Pydantic Schemas (API 입출력용)
# -------------------------
class TourInfoBase(BaseModel):
    contentid: str = Field(..., description="콘텐츠 ID")
    contenttypeid: Optional[str] = Field(None, description="콘텐츠 타입 ID")
    title: str = Field(..., description="관광지 이름")
    addr1: Optional[str] = Field(None, description="주소 1")
    addr2: Optional[str] = Field(None, description="주소 2")
    zipcode: Optional[str] = Field(None, description="우편번호")
    
    areacode: Optional[str] = Field(None, description="지역 코드")
    sigungucode: Optional[str] = Field(None, description="시군구 코드")
    
    cat1: Optional[str] = Field(None, description="대분류")
    cat2: Optional[str] = Field(None, description="중분류")
    cat3: Optional[str] = Field(None, description="소분류")
    tel: Optional[str] = Field(None, description="전화번호")
    
    firstimage: Optional[HttpUrl] = Field(None, description="대표 이미지 URL")
    firstimage2: Optional[HttpUrl] = Field(None, description="썸네일 이미지 URL")
    
    mapx: Optional[float] = Field(None, description="경도(X)")
    mapy: Optional[float] = Field(None, description="위도(Y)")
    mlevel: Optional[int] = Field(None, description="지도 레벨")
    
    createdtime: Optional[str] = Field(None, description="생성 시간 (YYYYMMDDHHMMSS)")
    modifiedtime: Optional[str] = Field(None, description="수정 시간 (YYYYMMDDHHMMSS)")
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True,
    )


class TourInfoCreate(TourInfoBase):
    # 생성 시 필수 필드를 명시할 수 있지만, 여기서는 Base와 동일하게 설정
    pass

class TourInfoUpdate(BaseModel):
    # 업데이트 시 모든 필드를 Optional로 설정
    title: Optional[str] = None
    addr1: Optional[str] = None
    tel: Optional[str] = None
    mapx: Optional[float] = None
    mapy: Optional[float] = None
    modifiedtime: Optional[str] = None
    
    model_config = ConfigDict(validate_by_name=True)


class TourInfoOut(TourInfoBase):
    # 출력 시 필드 변화는 없지만, 스키마 명시
    pass