from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.db.database import Base 
from datetime import datetime

# 핵심 인증용 사용자 모델 (MarketUser와 분리)
class User(Base):
    """
    로그인 및 인증에 필요한 최소한의 사용자 정보를 담는 기본 모델입니다.
    기존 MarketUser가 상속받아 사용하거나, MarketUser와 독립적으로 사용할 수 있습니다.
    """
    __tablename__ = "users" # 새로운 테이블 이름 사용 (예: users)

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String, nullable=False) 
    hashed_password = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True) # 계정 활성화 상태
    is_business = Column(Boolean, default=False) #사업자 여부
    business_registration_number = Column(String(10), unique=True, index=True, nullable=True)
    favorites = relationship(
        "UserFavorite", 
        back_populates="user", 
        cascade="all, delete-orphan" # 사용자가 삭제되면 찜 기록도 삭제
    )
