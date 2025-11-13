# app/models/market_models.py

from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Integer, String, Text, DateTime, Boolean, ForeignKey,
    Numeric, Index, CheckConstraint, UniqueConstraint, JSON
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.database import Base
from app.models.users_models import MarketUser # 수정된 MarketUser 임포트

# --- market.sql 스키마에 맞춘 새 ORM 모델 ---

class MarketProduct(Base):
    __tablename__ = "market_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("market_users.id"), nullable=False) # 판매자 ID
    
    # ProductCreateScreen.js 폼 필드
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    shop_name: Mapped[Optional[str]] = mapped_column(String(100))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    seller_note: Mapped[Optional[str]] = mapped_column(Text)
    delivery_info: Mapped[Optional[str]] = mapped_column(String(255))
    
    # MarketHome.js 필터링/정렬 필드
    region: Mapped[Optional[str]] = mapped_column(String(50))
    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=0.00)
    likes: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # --- 관계 설정 ---
    # 1. 판매자 (User)
    seller: Mapped[MarketUser] = relationship("MarketUser", lazy="joined")
    
    # 2. 이 상품에 달린 이미지들 (1:N)
    images: Mapped[List["MarketProductImage"]] = relationship(
        "MarketProductImage", 
        back_populates="product", 
        cascade="all, delete-orphan",
        lazy="selectin" # Eager Loading
    )
    
    # 3. 이 상품에 달린 Q&A (1:N)
    qna_list: Mapped[List["MarketQna"]] = relationship(
        "MarketQna",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="subquery" # Eager Loading
    )
    
    # 4. 이 상품을 찜한 내역 (1:N)
    wishlist_items: Mapped[List["MarketWishlist"]] = relationship(
        "MarketWishlist",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    __table_args__ = (
        Index("idx_products_region", "region"),
        Index("idx_products_likes", "likes"),
    )


class MarketProductImage(Base):
    __tablename__ = "market_product_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("market_products.id", ondelete="CASCADE"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_thumbnail: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # --- 관계 설정 ---
    product: Mapped[MarketProduct] = relationship("MarketProduct", back_populates="images")


class MarketQna(Base):
    __tablename__ = "market_qna"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("market_products.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("market_users.id"), nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    
    answer_body: Mapped[Optional[str]] = mapped_column(Text)
    answered_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("market_users.id"))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # --- 관계 설정 ---
    product: Mapped[MarketProduct] = relationship("MarketProduct", back_populates="qna_list")
    author: Mapped[MarketUser] = relationship("MarketUser", foreign_keys=[author_id], lazy="joined")
    answerer: Mapped[Optional[MarketUser]] = relationship("MarketUser", foreign_keys=[answered_by_id], lazy="joined")


class MarketWishlist(Base):
    __tablename__ = "market_wishlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("market_users.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("market_products.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # --- 관계 설정 ---
    user: Mapped[MarketUser] = relationship("MarketUser", lazy="joined")
    product: Mapped[MarketProduct] = relationship("MarketProduct", back_populates="wishlist_items", lazy="joined")
    
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_product_wishlist"),
    )