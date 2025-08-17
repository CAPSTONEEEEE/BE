# app/models/market_models.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, conint, conlist, confloat
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Numeric, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

# 공통 Base가 common_models.py에 있다고 가정
# (없다면 from sqlalchemy.orm import declarative_base 후 Base = declarative_base()로 대체)
from app.models.common_models import Base  # Base, TimestampMixin 등이 있다면 가져다 쓰세요.


class ProductStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    OUT_OF_STOCK = "OUT_OF_STOCK"


class Region(Base):
    __tablename__ = "regions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # 예: '전라남도 함평군' 등 풀네임
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    # 행정코드(선택)
    code: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)

    markets: Mapped[List["Market"]] = relationship("Market", back_populates="region")


class Market(Base):
    __tablename__ = "markets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # 주소/좌표 (필요 시 분리)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Numeric(10, 6), nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Numeric(10, 6), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey("regions.id"), nullable=True, index=True)
    region: Mapped[Optional[Region]] = relationship("Region", back_populates="markets")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    products: Mapped[List["Product"]] = relationship("Product", back_populates="market", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    # 예: 곡물, 수산, 과일, 가공식품 등
    slug: Mapped[Optional[str]] = mapped_column(String(60), unique=True, nullable=True)

    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(140), nullable=False, index=True)
    summary: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, index=True)
    stock: Mapped[int] = mapped_column(Integer, default=0, index=True)
    unit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # 예: '1kg', '500g', '1박스'
    image_urls: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 콤마로 join하여 저장 (간단 구현)
    status: Mapped[str] = mapped_column(String(20), default=ProductStatus.ACTIVE.value, index=True)

    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"), nullable=False, index=True)
    market: Mapped[Market] = relationship("Market", back_populates="products")

    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True, index=True)
    category: Mapped[Optional[Category]] = relationship("Category", back_populates="products")

    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey("regions.id"), nullable=True, index=True)
    region: Mapped[Optional[Region]] = relationship("Region")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

Index("idx_products_search", Product.name, Product.status, Product.price)


# -------------------------
# Pydantic Schemas (I/O)
# -------------------------

class RegionOut(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    class Config:
        from_attributes = True


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: Optional[str] = None
    class Config:
        from_attributes = True


class MarketBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[confloat(ge=-90, le=90)] = None
    lng: Optional[confloat(ge=-180, le=180)] = None
    phone: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    region_id: Optional[int] = None
    is_active: bool = True


class MarketCreate(MarketBase):
    pass


class MarketUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[confloat(ge=-90, le=90)] = None
    lng: Optional[confloat(ge=-180, le=180)] = None
    phone: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    region_id: Optional[int] = None
    is_active: Optional[bool] = None


class MarketOut(MarketBase):
    id: int
    region: Optional[RegionOut] = None
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1)
    summary: Optional[str] = None
    description: Optional[str] = None
    price: confloat(gt=0) = Field(..., description="판매가")
    stock: conint(ge=0) = 0
    unit: Optional[str] = None
    image_urls: Optional[conlist(HttpUrl, min_items=1)] = None
    status: ProductStatus = ProductStatus.ACTIVE
    market_id: int
    category_id: Optional[int] = None
    region_id: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    price: Optional[confloat(gt=0)] = None
    stock: Optional[conint(ge=0)] = None
    unit: Optional[str] = None
    image_urls: Optional[conlist(HttpUrl, min_items=1)] = None
    status: Optional[ProductStatus] = None
    category_id: Optional[int] = None
    region_id: Optional[int] = None


class ProductOut(BaseModel):
    id: int
    name: str
    summary: Optional[str] = None
    description: Optional[str] = None
    price: float
    stock: int
    unit: Optional[str] = None
    image_urls: Optional[list[HttpUrl]] = None
    status: ProductStatus
    market: MarketOut
    category: Optional[CategoryOut] = None
    region: Optional[RegionOut] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
