from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base # Base 임포트

# User 모델 임포트는 순환 참조를 피하기 위해 문자열로 참조합니다.
# from app.models.users_models import User 

class UserFavorite(Base):
    """
    통합 찜 목록을 위한 모델.
    축제, 상품, 추천 여행지 등 모든 찜 항목을 이 단일 테이블에 저장합니다.
    """
    __tablename__ = "user_favorite"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 찜을 한 사용자 ID (users 테이블의 id를 참조)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 찜 항목의 종류 (FESTIVAL, PRODUCT, SPOT 등)
    # 이 문자열 값은 FE/BE가 통일해야 하는 핵심 약속입니다.
    item_type = Column(String(50), nullable=False)
    
    # 찜 항목의 고유 ID (예: Festival.id, Product.id)
    item_id = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # 사용자 관계 정의
    user = relationship("User", back_populates="favorites")
