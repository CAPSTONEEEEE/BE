# app/router/market_router.py
from __future__ import annotations
from typing import Optional, Any
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.services.common_service import get_db  # DB 세션 의존성 (경로 다르면 수정)
from app.services import market_service as svc
from app.models.market_models import (
    MarketCreate, MarketUpdate, MarketOut,
    ProductCreate, ProductUpdate, ProductOut
)

router = APIRouter(prefix="/market", tags=["market"])

# ---------- Market ----------
@router.get("/stores", response_model=dict, summary="가게 리스트")
def list_markets(
    q: Optional[str] = Query(None, description="가게명/설명 검색어"),
    region_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(True),
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    order_by: str = Query("recent", pattern="^(recent|name)$"),
    db: Session = Depends(get_db),
):
    items, total = svc.list_markets(
        db, q=q, region_id=region_id, is_active=is_active,
        page=page, size=size, order_by=order_by
    )
    return {
        "items": [MarketOut.model_validate(i) for i in items],
        "page": page,
        "size": size,
        "total": total,
        "total_pages": ceil(total / size) if size else 1
    }

@router.get("/stores/{market_id}", response_model=MarketOut, summary="가게 상세")
def get_market(market_id: int, db: Session = Depends(get_db)):
    obj = svc.get_market(db, market_id)
    if not obj:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")
    return obj

@router.post("/stores", response_model=MarketOut, status_code=status.HTTP_201_CREATED, summary="가게 생성")
def create_market(payload: MarketCreate, db: Session = Depends(get_db)):
    obj = svc.create_market(db, payload)
    return obj

@router.patch("/stores/{market_id}", response_model=MarketOut, summary="가게 수정")
def update_market(market_id: int, payload: MarketUpdate, db: Session = Depends(get_db)):
    obj = svc.update_market(db, market_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")
    return obj


# ---------- Product ----------
@router.get("/products", response_model=dict, summary="상품 리스트")
def list_products(
    q: Optional[str] = Query(None, description="상품명/요약 검색어"),
    category_id: Optional[int] = Query(None),
    region_id: Optional[int] = Query(None),
    market_id: Optional[int] = Query(None),
    status: Optional[str] = Query("ACTIVE"),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    sort: str = Query("recent", pattern="^(recent|price_asc|price_desc|name)$"),
    db: Session = Depends(get_db),
):
    items, total = svc.list_products(
        db, q=q, category_id=category_id, region_id=region_id, market_id=market_id,
        status=status, price_min=price_min, price_max=price_max, page=page, size=size, sort=sort
    )
    # ProductOut로 직렬화 (image_urls 등 변환 반영)
    return {
        "items": [ProductOut.model_validate(i) for i in items],
        "page": page,
        "size": size,
        "total": total,
        "total_pages": ceil(total / size) if size else 1
    }

@router.get("/products/{product_id}", response_model=ProductOut, summary="상품 상세")
def get_product(product_id: int, db: Session = Depends(get_db)):
    obj = svc.get_product(db, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    # 서비스에서 image_urls를 리스트로 복구하지 않았다면 여기서 처리 가능
    return ProductOut.model_validate(obj)

@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED, summary="상품 생성")
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    obj = svc.create_product(db, payload)
    return ProductOut.model_validate(obj)

@router.patch("/products/{product_id}", response_model=ProductOut, summary="상품 수정")
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    obj = svc.update_product(db, product_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    return ProductOut.model_validate(obj)

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="상품 삭제")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    ok = svc.delete_product(db, product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    return
