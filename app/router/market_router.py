# BE/app/router/market_router.py

from __future__ import annotations
from typing import List, Dict, Optional
import uuid, os, shutil
from pathlib import Path

from fastapi import (
    APIRouter, HTTPException, Query, status, Depends, Response, 
    Request, UploadFile, Form, File
)
from sqlalchemy.orm import Session

from app.db.database import get_db
# 새 서비스 함수 임포트
from app.services.market_service import (
    create_product, list_products, get_product,
    create_qna, list_qna_for_product,
    add_wishlist, remove_wishlist, list_wishlist
)
# 새 Pydantic 스키마 임포트
from app.schemas import (
    MarketProductOut, MarketProductCreateSchema,
    MarketQnaOut, MarketQnaCreateSchema,
    MarketWishlistOut
)
from app.models.users_models import MarketUser
# ▼▼▼ [수정] common_router에 정의된 더미 함수 임포트 ▼▼▼
from app.router.common_router import get_current_user_dummy


# ------------------------------------------------------
# 업로드 경로 (app/static/uploads) 준비 (기존과 동일)
# ------------------------------------------------------
APP_DIR = Path(__file__).resolve().parents[1]   # app/
STATIC_DIR = APP_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# prefix를 '/products'로 변경 (FE 코드 기준)
router = APIRouter(prefix="/products", tags=["market_products"])


# ======================================================
# ===============  상품 (Products)  ====================
# ======================================================

@router.post(
    "", # POST /products
    response_model=MarketProductOut, 
    status_code=status.HTTP_201_CREATED, 
    summary="상품 등록 (ProductCreateScreen.js)"
)
async def create_product_api(
    # ... (Form 필드들은 기존과 동일) ...
    title: str = Form(...),
    price: int = Form(...),
    shop_name: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    seller_note: Optional[str] = Form(None),
    delivery_info: Optional[str] = Form(None),
    region: Optional[str] = Form(None),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    # ▼▼▼ [수정] Depends(get_current_user) -> Depends(get_current_user_dummy) ▼▼▼
    current_user: MarketUser = Depends(get_current_user_dummy) # 판매자 권한 확인
):
    """
    ProductCreateScreen.js에서 'multipart/form-data'로 전송한 상품 정보를 등록합니다.
    """
    # ... (기존 create_product_api 로직은 동일) ...
    
    # 0. (추가) 더미 함수가 반환한 유저가 판매자인지 다시 확인
    if not current_user.is_seller:
         raise HTTPException(status_code=403, detail="판매자 권한이 없습니다.")

    # 1. Pydantic 스키마로 폼 데이터 검증
    try:
        data = MarketProductCreateSchema(
            title=title, price=price, shop_name=shop_name, location=location,
            summary=summary, seller_note=seller_note, delivery_info=delivery_info,
            region=region
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"폼 데이터 오류: {e}")

    # 2. 이미지 파일 저장
    saved_files: List[Path] = []
    try:
        for file in images:
            if not file.filename: continue
            _, ext = os.path.splitext(file.filename)
            filename = f"{uuid.uuid4().hex}{ext.lower() or '.jpg'}"
            save_path = UPLOAD_DIR / filename
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(save_path)
    except Exception as e:
        for path in saved_files:
            if path.exists(): os.remove(path)
        raise HTTPException(status_code=500, detail=f"이미지 저장 실패: {e}")
    
    # 3. 서비스 로직 호출
    try:
        product = create_product(db, data, current_user, saved_files)
        return product
    except Exception as e:
        for path in saved_files:
            if path.exists(): os.remove(path)
        raise HTTPException(status_code=500, detail=f"DB 저장 실패: {e}")


@router.get(
    "", # GET /products
    response_model=List[MarketProductOut], 
    summary="상품 목록 조회 (MarketHome.js)"
)
def list_products_api(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="상품명/설명/위치 검색어"),
    region: Optional[str] = Query('전체', description="지역 필터"),
    sort: Optional[str] = Query('인기순', description="정렬: 인기순, 후기순, 최신순"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    """
    MarketHome.js의 목록 조회 API
    """
    items, total = list_products(
        db, q=q, region=region, sort=sort, page=page, size=size
    )
    return items 


@router.get(
    "/{product_id}", # GET /products/{product_id}
    response_model=MarketProductOut, 
    summary="상품 상세 정보"
)
def get_product_api(product_id: int, db: Session = Depends(get_db)):
    obj = get_product(db, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return obj


# ======================================================
# ============  상품 Q&A (ProductQnAScreen.js)  =========
# ======================================================

@router.post(
    "/{product_id}/qna", # POST /products/{product_id}/qna
    response_model=MarketQnaOut, 
    status_code=status.HTTP_201_CREATED, 
    summary="상품 문의 등록 (ProductQnAScreen.js)"
)
def create_qna_api(
    product_id: int,
    payload: MarketQnaCreateSchema,
    db: Session = Depends(get_db),
    # ▼▼▼ [수정] Depends(get_current_user) -> Depends(get_current_user_dummy) ▼▼▼
    current_user: MarketUser = Depends(get_current_user_dummy) # 질문자
):
    try:
        return create_qna(db, payload, product_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"문의 등록 실패: {e}")


@router.get(
    "/{product_id}/qna", # GET /products/{product_id}/qna
    response_model=List[MarketQnaOut], 
    summary="상품 문의 목록 (ProductQnAScreen.js)"
)
def list_qna_api(product_id: int, db: Session = Depends(get_db)):
    return list_qna_for_product(db, product_id)


# ======================================================
# ============  찜하기 (WishlistScreen.js)  ============
# ======================================================

# Wishlist 라우터를 별도로 생성 (prefix=/wishlist)
router_wishlist = APIRouter(prefix="/wishlist", tags=["market_wishlist"])

@router_wishlist.post(
    "", # POST /wishlist
    response_model=MarketWishlistOut,
    status_code=status.HTTP_201_CREATED,
    summary="찜하기 추가 (WishlistScreen.js)"
)
def add_wishlist_api(
    payload: dict,
    db: Session = Depends(get_db),
    # ▼▼▼ [수정] Depends(get_current_user) -> Depends(get_current_user_dummy) ▼▼▼
    current_user: MarketUser = Depends(get_current_user_dummy) # 찜한 유저
):
    product_id = payload.get("id") or payload.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id가 필요합니다.")
    try:
        wishlist_item = add_wishlist(db, user_id=current_user.id, product_id=int(product_id))
        return wishlist_item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"처리 중 오류: {e}")


@router_wishlist.delete(
    "/{product_id}", # DELETE /wishlist/{product_id}
    status_code=status.HTTP_204_NO_CONTENT,
    summary="찜하기 취소 (WishlistScreen.js)"
)
def remove_wishlist_api(
    product_id: int,
    db: Session = Depends(get_db),
    # ▼▼▼ [수정] Depends(get_current_user) -> Depends(get_current_user_dummy) ▼▼▼
    current_user: MarketUser = Depends(get_current_user_dummy) # 찜한 유저
):
    ok = remove_wishlist(db, user_id=current_user.id, product_id=product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router_wishlist.get(
    "", # GET /wishlist
    response_model=List[MarketWishlistOut],
    summary="내 찜 목록 (WishlistScreen.js)"
)
def list_my_wishlist_api(
    db: Session = Depends(get_db),
    # ▼▼▼ [수정] Depends(get_current_user) -> Depends(get_current_user_dummy) ▼▼▼
    current_user: MarketUser = Depends(get_current_user_dummy)
):
    return list_wishlist(db, user_id=current_user.id)