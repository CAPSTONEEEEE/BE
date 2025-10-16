from __future__ import annotations
from typing import List, Dict, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status, Depends, Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.market_service import (
    # Market / Product
    create_market, update_market, get_market, list_markets,
    create_product, update_product, get_product, delete_product, list_products,
    # Cart & Wishlist
    add_to_cart, update_cart_item, remove_cart_item, clear_cart, list_cart,
    add_wishlist, remove_wishlist, list_wishlist,
)
from app.models.market_models import (
    MarketCreate, MarketUpdate, MarketOut,
    ProductCreate as ProductIn, ProductUpdate as ProductInUpdate, ProductOut,
    CartItemCreate, CartItemUpdate, CartItemOut,
    WishlistItemCreate, WishlistItemOut,
)
from pydantic import BaseModel, Field, conint, ConfigDict

router = APIRouter(prefix="/markets", tags=["markets"])

# ------------------------------------------------------
# 공통 페이지네이션 응답 스키마
# ------------------------------------------------------
class ProductListResponse(BaseModel):
    items: List[ProductOut]
    total: int
    page: int
    size: int
    model_config = ConfigDict(from_attributes=True)

class MarketListResponse(BaseModel):
    items: List[MarketOut]
    total: int
    page: int
    size: int
    model_config = ConfigDict(from_attributes=True)

class PageCart(BaseModel):
    items: List[CartItemOut]
    total: int
    page: int
    size: int
    model_config = ConfigDict(from_attributes=True)

class PageWishlist(BaseModel):
    items: List[WishlistItemOut]
    total: int
    page: int
    size: int
    model_config = ConfigDict(from_attributes=True)

# ======================================================
# ===============  상품 (DB 연동 CRUD)  ================
#   ⚠️ 라우트 우선순위 때문에 고정/세부 경로를 먼저 선언
# ======================================================

@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED, summary="상품 등록")
def create_product_api(payload: ProductIn, db: Session = Depends(get_db)):
    return create_product(db, payload)

@router.get("/products", response_model=ProductListResponse, summary="상품 목록")
def list_products_api(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="상품명/요약 검색어"),
    market_id: Optional[int] = Query(None, description="특정 마켓 필터"),
    category_id: Optional[int] = Query(None, description="카테고리"),
    region_id: Optional[int] = Query(None, description="지역"),
    status: Optional[str] = Query("ACTIVE", description="상태: ACTIVE/INACTIVE/OUT_OF_STOCK"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort: str = Query("recent", pattern="^(recent|price_asc|price_desc|name)$"),
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
):
    items, total = list_products(
        db,
        q=q,
        category_id=category_id,
        region_id=region_id,
        market_id=market_id,
        status=status,
        price_min=min_price,
        price_max=max_price,
        page=page,
        size=size,
        sort=sort,
    )
    return {"items": items, "total": total, "page": page, "size": size}

@router.get("/products/{product_id}", response_model=ProductOut, summary="상품 상세 정보")
def get_product_api(product_id: int, db: Session = Depends(get_db)):
    obj = get_product(db, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return obj

@router.patch("/products/{product_id}", response_model=ProductOut, summary="상품 수정")
def update_product_api(product_id: int, payload: ProductInUpdate, db: Session = Depends(get_db)):
    obj = update_product(db, product_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return obj

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="상품 삭제")
def delete_product_api(product_id: int, db: Session = Depends(get_db)):
    ok = delete_product(db, product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Product not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ======================================================
# ===============  장바구니 (DB 연동)  =================
#   ⚠️ 동적 경로("/{market_id}")보다 위에 둬야 함
# ======================================================

@router.get("/cart", response_model=PageCart, summary="장바구니 목록")
def list_cart_api(
    user_id: int = Query(..., description="사용자 ID"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = list_cart(db, user_id=user_id, page=page, size=size)
    return {"items": items, "total": total, "page": page, "size": size}

@router.post("/cart", response_model=CartItemOut, status_code=status.HTTP_201_CREATED, summary="장바구니 추가/누적")
def add_cart_api(payload: CartItemCreate, db: Session = Depends(get_db)):
    # 서비스에서 ValueError로 올려주는 에러를 404/400으로 변환
    try:
        return add_to_cart(db, payload)
    except ValueError as e:
        msg = str(e)
        if msg == "PRODUCT_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Product not found")
        raise HTTPException(status_code=400, detail="Invalid cart request")

@router.patch("/cart/{cart_id}", response_model=CartItemOut, summary="장바구니 수량 변경")
def update_cart_api(cart_id: int, payload: CartItemUpdate, db: Session = Depends(get_db)):
    obj = update_cart_item(db, cart_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return obj

@router.delete("/cart/{cart_id}", status_code=status.HTTP_204_NO_CONTENT, summary="장바구니 항목 삭제")
def delete_cart_api(cart_id: int, db: Session = Depends(get_db)):
    ok = remove_cart_item(db, cart_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/cart", status_code=status.HTTP_204_NO_CONTENT, summary="장바구니 비우기")
def clear_cart_api(user_id: int = Query(..., description="사용자 ID"), db: Session = Depends(get_db)):
    clear_cart(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ======================================================
# ===============  찜하기 (DB 연동)  ===================
#   ⚠️ 동적 경로("/{market_id}")보다 위에 둬야 함
# ======================================================

@router.get("/wishlist", response_model=PageWishlist, summary="찜 목록")
def list_wishlist_api(
    user_id: int = Query(..., description="사용자 ID"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = list_wishlist(db, user_id=user_id, page=page, size=size)
    return {"items": items, "total": total, "page": page, "size": size}

@router.post("/wishlist", response_model=WishlistItemOut, status_code=status.HTTP_201_CREATED, summary="찜 추가")
def add_wishlist_api(payload: WishlistItemCreate, db: Session = Depends(get_db)):
    try:
        return add_wishlist(db, payload.user_id, payload.product_id)
    except ValueError as e:
        msg = str(e)
        if msg == "PRODUCT_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Product not found")
        raise HTTPException(status_code=400, detail="Invalid wishlist request")

@router.delete("/wishlist", status_code=status.HTTP_204_NO_CONTENT, summary="찜 삭제")
def remove_wishlist_api(
    user_id: int = Query(..., description="사용자 ID"),
    product_id: int = Query(..., description="상품 ID"),
    db: Session = Depends(get_db),
):
    ok = remove_wishlist(db, user_id, product_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist item not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ======================================================
# ===============  마켓 (DB 연동 CRUD)  ================
#   ⚠️ 동적 경로는 항상 마지막 쪽에 배치
# ======================================================

@router.get("", response_model=MarketListResponse, summary="마켓 목록")
def list_markets_api(
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="마켓명/설명 검색어"),
    region_id: int | None = Query(None, description="지역 ID"),
    is_active: bool | None = Query(True, description="활성 여부"),
    order_by: str = Query("recent", pattern="^(recent|name)$"),
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
):
    items, total = list_markets(
        db,
        q=q,
        region_id=region_id,
        is_active=is_active,
        page=page,
        size=size,
        order_by=order_by,
    )
    return {"items": items, "total": total, "page": page, "size": size}

@router.post("", response_model=MarketOut, status_code=status.HTTP_201_CREATED, summary="마켓 생성")
def create_market_api(payload: MarketCreate, db: Session = Depends(get_db)):
    return create_market(db, payload)

@router.get("/{market_id}", response_model=MarketOut, summary="마켓 상세")
def get_market_api(market_id: int, db: Session = Depends(get_db)):
    obj = get_market(db, market_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Market not found")
    return obj

@router.patch("/{market_id}", response_model=MarketOut, summary="마켓 수정")
def update_market_api(market_id: int, payload: MarketUpdate, db: Session = Depends(get_db)):
    obj = update_market(db, market_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Market not found")
    return obj

# ======================================================
# ======  판매자/문의/후기 (기존 Mock 그대로 유지)  ======
# ======================================================

class SellerCreate(BaseModel):
    seller_name: str = Field(..., description="판매자 이름")
    phone: Optional[str] = Field(None, description="연락처")
    market_name: str = Field(..., description="마켓 이름")
    address: Optional[str] = Field(None, description="주소")

class SellerUpdate(BaseModel):
    seller_name: Optional[str] = None
    phone: Optional[str] = None
    market_name: Optional[str] = None
    address: Optional[str] = None

class SellerOut(SellerCreate):
    id: int

class ContactRequest(BaseModel):
    user_id: int
    message: str = Field(..., description="첫 메시지(문의 내용)")

class ContactResponse(BaseModel):
    ok: bool
    chat_room_id: str
    product_id: int
    created_at: datetime

class ReviewCreate(BaseModel):
    user_id: int
    rating: conint(ge=1, le=5)
    comment: Optional[str] = None

class ReviewOut(ReviewCreate):
    id: int
    product_id: int
    created_at: datetime

_mock_sellers: List[Dict] = []
_mock_reviews: List[Dict] = []
_next_seller_id = 1
_next_review_id = 1

@router.post("/seller", response_model=SellerOut, status_code=status.HTTP_201_CREATED, summary="판매자 등록")
def register_seller(payload: SellerCreate):
    global _next_seller_id
    obj = {"id": _next_seller_id, **payload.dict()}
    _mock_sellers.append(obj)
    _next_seller_id += 1
    return obj

@router.patch("/seller/{seller_id}", response_model=SellerOut, summary="판매자 수정")
def update_seller(seller_id: int, payload: SellerUpdate):
    s = next((x for x in _mock_sellers if x["id"] == seller_id), None)
    if not s:
        raise HTTPException(status_code=404, detail="Seller not found")
    s.update({k: v for k, v in payload.dict(exclude_unset=True).items()})
    return s

@router.delete("/seller/{seller_id}", status_code=status.HTTP_204_NO_CONTENT, summary="판매자 삭제")
def delete_seller(seller_id: int):
    idx = next((i for i, x in enumerate(_mock_sellers) if x["id"] == seller_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Seller not found")
    _mock_sellers.pop(idx)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/products/{product_id}/contact", response_model=ContactResponse, summary="실시간 채팅 시작(문의)")
def start_contact(product_id: int, payload: ContactRequest):
    return ContactResponse(
        ok=True,
        chat_room_id=f"chat_{product_id}_{payload.user_id}",
        product_id=product_id,
        created_at=datetime.utcnow(),
    )

@router.post("/products/{product_id}/review", response_model=ReviewOut, status_code=status.HTTP_201_CREATED, summary="거래 후기 및 평가")
def add_review(product_id: int, payload: ReviewCreate):
    global _next_review_id
    obj = {
        "id": _next_review_id,
        "product_id": product_id,
        "user_id": payload.user_id,
        "rating": payload.rating,
        "comment": payload.comment,
        "created_at": datetime.utcnow(),
    }
    _mock_reviews.append(obj)
    _next_review_id += 1
    return obj

@router.get("/products/{product_id}/reviews", response_model=List[ReviewOut], summary="상품 후기 목록")
def list_reviews(product_id: int):
    return [r for r in _mock_reviews if r["product_id"] == product_id]
