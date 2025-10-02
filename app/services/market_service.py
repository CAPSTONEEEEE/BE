from __future__ import annotations
from typing import Optional, Tuple, List

from sqlalchemy.orm import Session
from sqlalchemy import select, func, asc, desc, or_, and_, delete

from app.models.market_models import (
    Market, Product, Category, Region,
    MarketCreate, MarketUpdate, ProductCreate, ProductUpdate, ProductStatus,
    CartItem, WishlistItem, CartItemCreate, CartItemUpdate
)

# ---------- Market ----------
def create_market(db: Session, data: MarketCreate) -> Market:
    obj = Market(
        name=data.name,
        description=data.description,
        address=data.address,
        lat=data.lat,
        lng=data.lng,
        phone=data.phone,
        image_url=str(data.image_url) if data.image_url else None,
        region_id=data.region_id,
        is_active=data.is_active,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_market(db: Session, market_id: int, data: MarketUpdate) -> Optional[Market]:
    obj: Market | None = db.get(Market, market_id)
    if not obj:
        return None
    for field, value in data.dict(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj

def get_market(db: Session, market_id: int) -> Optional[Market]:
    return db.get(Market, market_id)

def list_markets(
    db: Session,
    q: Optional[str] = None,
    region_id: Optional[int] = None,
    is_active: Optional[bool] = True,
    page: int = 1,
    size: int = 12,
    order_by: str = "recent",  # name|recent
) -> Tuple[List[Market], int]:
    stmt = select(Market)
    conds = []
    if is_active is not None:
        conds.append(Market.is_active == is_active)
    if region_id:
        conds.append(Market.region_id == region_id)
    if q:
        like = f"%{q}%"
        conds.append(or_(Market.name.ilike(like), Market.description.ilike(like)))
    if conds:
        stmt = stmt.where(and_(*conds))

    if order_by == "name":
        stmt = stmt.order_by(asc(Market.name))
    else:
        stmt = stmt.order_by(desc(Market.created_at))

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.execute(stmt.offset((page - 1) * size).limit(size)).scalars().all()
    return rows, total


# ---------- Product ----------
def create_product(db: Session, data: ProductCreate) -> Product:
    obj = Product(
        name=data.name,
        summary=data.summary,
        description=data.description,
        price=data.price,
        stock=data.stock,
        unit=data.unit,
        # ⚠️ image_urls는 JSON 컬럼이므로 리스트 그대로 저장
        image_urls=[str(u) for u in (data.image_urls or [])],
        status=data.status if isinstance(data.status, ProductStatus) else ProductStatus(data.status),
        market_id=data.market_id,
        category_id=data.category_id,
        region_id=data.region_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_product(db: Session, product_id: int, data: ProductUpdate) -> Optional[Product]:
    obj: Product | None = db.get(Product, product_id)
    if not obj:
        return None
    payload = data.dict(exclude_unset=True)
    if "status" in payload:
        payload["status"] = payload["status"] if isinstance(payload["status"], ProductStatus) else ProductStatus(payload["status"])
    # JSON 컬럼: 리스트 그대로 세팅
    for k, v in payload.items():
        if k == "image_urls" and v is not None:
            v = [str(u) for u in v]
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.get(Product, product_id)

def delete_product(db: Session, product_id: int) -> bool:
    obj = db.get(Product, product_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

def list_products(
    db: Session,
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    region_id: Optional[int] = None,
    market_id: Optional[int] = None,
    status: Optional[str] = "ACTIVE",
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    page: int = 1,
    size: int = 12,
    sort: str = "recent",  # recent|price_asc|price_desc|name
) -> Tuple[List[Product], int]:
    stmt = select(Product)
    conds = []
    if q:
        like = f"%{q}%"
        conds.append(or_(Product.name.ilike(like), Product.summary.ilike(like)))
    if category_id:
        conds.append(Product.category_id == category_id)
    if region_id:
        conds.append(Product.region_id == region_id)
    if market_id:
        conds.append(Product.market_id == market_id)
    if status:
        conds.append(Product.status == status)
    if price_min is not None:
        conds.append(Product.price >= price_min)
    if price_max is not None:
        conds.append(Product.price <= price_max)
    if conds:
        stmt = stmt.where(and_(*conds))

    if sort == "price_asc":
        stmt = stmt.order_by(asc(Product.price))
    elif sort == "price_desc":
        stmt = stmt.order_by(desc(Product.price))
    elif sort == "name":
        stmt = stmt.order_by(asc(Product.name))
    else:
        stmt = stmt.order_by(desc(Product.created_at))

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.execute(stmt.offset((page - 1) * size).limit(size)).scalars().all()
    return rows, total


# ---------- Cart ----------
def add_to_cart(db: Session, data: CartItemCreate):
    existing = db.execute(
        select(CartItem).where(CartItem.user_id == data.user_id, CartItem.product_id == data.product_id)
    ).scalar_one_or_none()
    if existing:
        existing.quantity += data.quantity
        db.commit(); db.refresh(existing)
        return existing
    obj = CartItem(user_id=data.user_id, product_id=data.product_id, quantity=data.quantity)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def update_cart_item(db: Session, cart_id: int, data: CartItemUpdate):
    obj = db.get(CartItem, cart_id)
    if not obj:
        return None
    obj.quantity = data.quantity
    db.commit(); db.refresh(obj)
    return obj

def remove_cart_item(db: Session, cart_id: int) -> bool:
    obj = db.get(CartItem, cart_id)
    if not obj: return False
    db.delete(obj); db.commit()
    return True

def clear_cart(db: Session, user_id: int):
    db.execute(delete(CartItem).where(CartItem.user_id == user_id))
    db.commit()
    return True

def list_cart(db: Session, user_id: int, page: int, size: int):
    stmt = select(CartItem).where(CartItem.user_id == user_id).order_by(CartItem.id.desc())
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.execute(stmt.offset((page-1)*size).limit(size)).scalars().all()
    return items, int(total or 0)


# ---------- Wishlist ----------
def add_wishlist(db: Session, user_id: int, product_id: int):
    existing = db.execute(
        select(WishlistItem).where(WishlistItem.user_id == user_id, WishlistItem.product_id == product_id)
    ).scalar_one_or_none()
    if existing:
        return existing
    obj = WishlistItem(user_id=user_id, product_id=product_id)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def remove_wishlist(db: Session, user_id: int, product_id: int) -> bool:
    obj = db.execute(
        select(WishlistItem).where(WishlistItem.user_id == user_id, WishlistItem.product_id == product_id)
    ).scalar_one_or_none()
    if not obj: return False
    db.delete(obj); db.commit()
    return True

def list_wishlist(db: Session, user_id: int, page: int, size: int):
    stmt = select(WishlistItem).where(WishlistItem.user_id == user_id).order_by(WishlistItem.id.desc())
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.execute(stmt.offset((page-1)*size).limit(size)).scalars().all()
    return items, int(total or 0)
