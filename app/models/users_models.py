from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
# 'db' 경로를 추가하여 올바른 위치에서 Base를 가져옵니다.
from app.db.database import Base 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    
    