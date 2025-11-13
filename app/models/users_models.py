# app/models/users_models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
# 'db' 경로를 추가하여 올바른 위치에서 Base를 가져옵니다.
from app.db.database import Base 

# User -> MarketUser로 변경하고, market.sql 스키마에 맞게 필드 추가
class MarketUser(Base):
    __tablename__ = "market_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    username = Column(String(100), nullable=False) # unique=True 제거 (이메일로 구분)
    
    # --- market.sql 스키마에 맞게 필드 추가 ---
    is_seller = Column(Boolean, default=False)
    business_number = Column(String(50), unique=True, nullable=True) # 사업자 등록번호
    seller_status = Column(String(20), default='pending') # (예: 'pending', 'approved')
    # ---
    
    # is_active는 seller_status로 대체 가능하므로 일단 주석 처리
    # is_active = Column(Boolean, default=True) 
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())