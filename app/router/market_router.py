# app/router/market_router.py
from __future__ import annotations
from typing import List, Dict, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field, conint, confloat

router = APIRouter(prefix="/markets", tags=["markets"])

# ---------------------------
# Pydantic Schemas (Mock)
# ---------------------------
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

class ProductCreate(BaseModel):
    name: str
    price: confloat(gt=0)
    stock: conint(ge=0) = 0
    summary: Optional[str] = None
    market_id: Optional[int] = Field(None, description="연결할 마켓 ID (선택)")

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[confloat(gt=0)] = None
    stock: Optional[conint(ge=0)] = None
    summary: Optional[str] = None
    market_id: Optional[int] = None

class ProductOut(ProductCreate):
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

# ---------------------------
# In-Memory Mock Stores
# ---------------------------
_mock_markets: List[Dict] = [
    {
        "id": 1,
        "name": "함평 나비쌀 마켓",
        "description": "전남 함평의 대표 특산물 판매",
        "address": "전라남도 함평군 함평읍",
        "phone": "061-123-4567",
        "region_id": 1,
        "is_active": True,
    },
    {
        "id": 2,
        "name": "부산 어묵 마켓",
        "description": "부산 명물 어묵 판매",
        "address": "부산광역시 중구",
        "phone": "051-987-6543",
        "region_id": 2,
        "is_active": True,
    },
]

_mock_products: List[Dict] = [
    {"id": 1, "name": "나비쌀 10kg", "price": 35000.0, "stock": 50, "summary": "함평쌀", "market_id": 1},
    {"id": 2, "name": "나비쌀 20kg", "price": 65000.0, "stock": 30, "summary": "특가", "market_id": 1},
    {"id": 3, "name": "부산 어묵 세트", "price": 20000.0, "stock": 100, "summary": "명물", "market_id": 2},
    {"id": 4, "name": "특선 어묵 모듬", "price": 30000.0, "stock": 80, "summary": "모듬", "market_id": 2},
]

_mock_sellers: List[Dict] = []  # {id, seller_name, phone, market_name, address}
_mock_reviews: List[Dict] = []  # {id, product_id, user_id, rating, comment, created_at}

_next_seller_id = 1
_next_product_id = 5
_next_review_id = 1

# ---------------------------
# Markets (목록/상세)
# ---------------------------
@router.get("", summary="마켓 목록")  # GET /markets/
def list_markets():
    # 각 마켓에 소속 상품을 붙여서 보기 좋게 반환
    items = []
    for m in _mock_markets:
        products = [p for p in _mock_products if p.get("market_id") == m["id"]]
        items.append({**m, "products": products})
    return items

@router.get("/{market_id}", summary="마켓 상세")  # GET /markets/{id}
def get_market(market_id: int):
    m = next((x for x in _mock_markets if x["id"] == market_id), None)
    if not m:
        raise HTTPException(status_code=404, detail="Market not found")
    products = [p for p in _mock_products if p.get("market_id") == market_id]
    return {**m, "products": products}

# ---------------------------
# Seller (등록/수정/삭제)
# ---------------------------
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
    return

# ---------------------------
# Products (등록/조회/수정/삭제)
# ---------------------------
@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED, summary="상품 등록")
def create_product(payload: ProductCreate):
    global _next_product_id
    obj = {"id": _next_product_id, **payload.dict()}
    _mock_products.append(obj)
    _next_product_id += 1
    return obj

@router.get("/products", summary="상품 목록")
def list_products(
    q: Optional[str] = Query(None, description="상품명/요약 검색어"),
    market_id: Optional[int] = Query(None, description="특정 마켓 필터"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
):
    items = _mock_products[:]
    if q:
        ql = q.lower()
        items = [p for p in items if ql in p["name"].lower() or ql in (p.get("summary") or "").lower()]
    if market_id is not None:
        items = [p for p in items if p.get("market_id") == market_id]
    if min_price is not None:
        items = [p for p in items if float(p["price"]) >= min_price]
    if max_price is not None:
        items = [p for p in items if float(p["price"]) <= max_price]
    return {"items": items, "total": len(items)}

@router.get("/products/{product_id}", response_model=ProductOut, summary="상품 상세 정보")
def get_product(product_id: int):
    obj = next((p for p in _mock_products if p["id"] == product_id), None)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return obj

@router.patch("/products/{product_id}", response_model=ProductOut, summary="상품 수정")
def update_product(product_id: int, payload: ProductUpdate):
    obj = next((p for p in _mock_products if p["id"] == product_id), None)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    obj.update({k: v for k, v in payload.dict(exclude_unset=True).items()})
    return obj

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="상품 삭제")
def delete_product(product_id: int):
    idx = next((i for i, p in enumerate(_mock_products) if p["id"] == product_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Product not found")
    _mock_products.pop(idx)
    return

# ---------------------------
# Contact (실시간 채팅 시작 / mock)
# ---------------------------
@router.post("/products/{product_id}/contact", response_model=ContactResponse, summary="실시간 채팅 시작(문의)")
def start_contact(product_id: int, payload: ContactRequest):
    if not next((p for p in _mock_products if p["id"] == product_id), None):
        raise HTTPException(status_code=404, detail="Product not found")
    return ContactResponse(
        ok=True,
        chat_room_id=f"chat_{product_id}_{payload.user_id}",
        product_id=product_id,
        created_at=datetime.utcnow(),
    )

# ---------------------------
# Reviews (생성/목록)
# ---------------------------
@router.post("/products/{product_id}/review", response_model=ReviewOut, status_code=status.HTTP_201_CREATED, summary="거래 후기 및 평가")
def add_review(product_id: int, payload: ReviewCreate):
    global _next_review_id
    if not next((p for p in _mock_products if p["id"] == product_id), None):
        raise HTTPException(status_code=404, detail="Product not found")
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
