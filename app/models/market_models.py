# app/models/market_models.py
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    ConfigDict,
    conint,
    confloat,
    field_validator,
)
from sqlalchemy import (
    Integer, String, Text, DateTime, Boolean, ForeignKey,
    Numeric, Index, CheckConstraint, UniqueConstraint, Enum as SAEnum, JSON
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.common_models import Base  # DeclarativeBase


# =========================
# SQLAlchemy ORM Models
# =========================

class ProductStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    OUT_OF_STOCK = "OUT_OF_STOCK"


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # 예: "전라남도 함평군"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 행정코드/커스텀코드(선택)
    code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)

    markets: Mapped[List["Market"]] = relationship(
        "Market",
        back_populates="region",
        cascade="save-update",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("name", name="uq_regions_name"),
    )

    def __repr__(self) -> str:
        return f"<Region id={self.id} name={self.name!r}>"


class Market(Base):
    __tablename__ = "markets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # 위경도: Numeric(10,6) 은 SQLite/MySQL/Postgres 모두 호환
    lat: Mapped[Optional[float]] = mapped_column(Numeric(10, 6), nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Numeric(10, 6), nullable=True)

    phone: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    region_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("regions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    region: Mapped[Optional[Region]] = relationship(
        "Region",
        back_populates="markets",
        lazy="joined",
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="market",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    __table_args__ = (
        # 같은 지역 내 동일 상호 중복 방지(지역 미지정 시 None 허용)
        UniqueConstraint("name", "region_id", name="uq_markets_name_region"),
        Index("idx_markets_active_region", "is_active", "region_id"),
    )

    def __repr__(self) -> str:
        return f"<Market id={self.id} name={self.name!r} is_active={self.is_active}>"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # 예: 곡물, 수산, 과일
    name: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    slug: Mapped[Optional[str]] = mapped_column(String(60), nullable=True, unique=True)

    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category",
        cascade="save-update",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(140), nullable=False, index=True)
    summary: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 가격/재고 제약
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, index=True)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)

    unit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # 예: 1kg, 500g

    # 여러 이미지: JSON 배열로 저장(모든 주요 DB에서 호환)
    image_urls: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)

    status: Mapped[ProductStatus] = mapped_column(
        SAEnum(ProductStatus, native_enum=False, validate_strings=True, length=20),
        default=ProductStatus.ACTIVE,
        index=True,
        nullable=False,
    )

    market_id: Mapped[int] = mapped_column(
        ForeignKey("markets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    market: Mapped[Market] = relationship(
        "Market", back_populates="products", lazy="joined"
    )

    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    category: Mapped[Optional[Category]] = relationship(
        "Category", back_populates="products", lazy="joined"
    )

    # 지역과도 직접 연결해두면 지역 필터/추천에 유용
    region_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("regions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    region: Mapped[Optional[Region]] = relationship("Region", lazy="joined")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        # 가격/재고 유효성 보장
        CheckConstraint("price >= 0", name="ck_products_price_nonnegative"),
        CheckConstraint("stock >= 0", name="ck_products_stock_nonnegative"),
        Index("idx_products_search", "name", "status", "price"),
        Index("idx_products_market_category", "market_id", "category_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name!r} status={self.status} price={self.price}>"


# =========================
# Pydantic Schemas (I/O)
# =========================

# ---- Region
class RegionCreate(BaseModel):
    name: str = Field(..., max_length=100)
    code: Optional[str] = Field(None, max_length=20)


class RegionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    code: Optional[str] = Field(None, max_length=20)


class RegionOut(BaseModel):
    id: int
    name: str
    code: Optional[str] = None

    # ✅ Pydantic v2
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)


# ---- Category
class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=60)
    slug: Optional[str] = Field(None, max_length=60)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=60)
    slug: Optional[str] = Field(None, max_length=60)


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: Optional[str] = None

    # ✅ Pydantic v2
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)


# ---- Market
class MarketBase(BaseModel):
    name: str = Field(..., max_length=120)
    description: Optional[str] = None
    address: Optional[str] = Field(None, max_length=255)
    lat: Optional[confloat(ge=-90, le=90)] = None
    lng: Optional[confloat(ge=-180, le=180)] = None
    phone: Optional[str] = Field(None, max_length=40)
    image_url: Optional[HttpUrl] = None
    region_id: Optional[int] = None
    is_active: bool = True


class MarketCreate(MarketBase):
    pass


class MarketUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    description: Optional[str] = None
    address: Optional[str] = Field(None, max_length=255)
    lat: Optional[confloat(ge=-90, le=90)] = None
    lng: Optional[confloat(ge=-180, le=180)] = None
    phone: Optional[str] = Field(None, max_length=40)
    image_url: Optional[HttpUrl] = None
    region_id: Optional[int] = None
    is_active: Optional[bool] = None


class MarketOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    address: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    phone: Optional[str]
    image_url: Optional[str]
    is_active: bool
    region: Optional[RegionOut]
    created_at: datetime
    updated_at: Optional[datetime]

    # ✅ Pydantic v2
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)


# ---- Product ----
class ProductBase(BaseModel):
    name: str = Field(..., max_length=140)
    summary: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    stock: conint(ge=0) = 0
    unit: Optional[str] = Field(None, max_length=30)
    image_urls: Optional[List[HttpUrl]] = None
    status: ProductStatus = ProductStatus.ACTIVE
    market_id: int
    category_id: Optional[int] = None
    region_id: Optional[int] = None

    # ✅ Pydantic v2: validator → field_validator
    @field_validator("image_urls", mode="before")
    @classmethod
    def _normalize_urls(cls, v):
        # 허용: None, [], 리스트/튜플/세트/콤마 문자열
        if v in (None, ""):
            return None
        if isinstance(v, str):
            parts = [p.strip() for p in v.split(",") if p.strip()]
            return parts or None
        if isinstance(v, (list, tuple, set)):
            return list(v) or None
        return None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=140)
    summary: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    stock: Optional[conint(ge=0)] = None
    unit: Optional[str] = Field(None, max_length=30)
    image_urls: Optional[List[HttpUrl]] = None
    status: Optional[ProductStatus] = None
    market_id: Optional[int] = None
    category_id: Optional[int] = None
    region_id: Optional[int] = None

    @field_validator("image_urls", mode="before")
    @classmethod
    def _normalize_urls(cls, v):
        if v in (None, ""):
            return None
        if isinstance(v, str):
            parts = [p.strip() for p in v.split(",") if p.strip()]
            return parts or None
        if isinstance(v, (list, tuple, set)):
            return list(v) or None
        return None


class ProductOut(BaseModel):
    id: int
    name: str
    summary: Optional[str]
    description: Optional[str]
    price: float
    stock: int
    unit: Optional[str]
    image_urls: Optional[List[str]]
    status: ProductStatus
    market: MarketOut
    category: Optional[CategoryOut]
    region: Optional[RegionOut]
    created_at: datetime
    updated_at: Optional[datetime]

    # ✅ Pydantic v2
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)


# --- 장바구니 & 찜 (추가) ---
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, conint
from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

class CartItem(Base):
    __tablename__ = "cart_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional["datetime"]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", lazy="joined")

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),
        CheckConstraint("quantity >= 1", name="ck_cart_quantity_ge_1"),
    )

class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", lazy="joined")

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),
    )

# ---- Pydantic (IO) ----
class CartItemCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: conint(ge=1) = 1

class CartItemUpdate(BaseModel):
    quantity: conint(ge=1)

class CartItemOut(BaseModel):
    id: int
    user_id: int
    quantity: int
    product: ProductOut
    model_config = ConfigDict(from_attributes=True)

class WishlistItemCreate(BaseModel):
    user_id: int
    product_id: int

class WishlistItemOut(BaseModel):
    id: int
    user_id: int
    product: ProductOut
    model_config = ConfigDict(from_attributes=True)
