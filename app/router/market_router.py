# app/router/market_router.py

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
# 새 Pydantic 스키마 임포트 (schemas.py에서 정의)
from app.schemas import (
    MarketProductOut, MarketProductCreateSchema,
    MarketQnaOut, MarketQnaCreateSchema,
    MarketWishlistOut
)
# 인증 (JWT) - 임시로 MarketUser를 가져오는 함수 (실제로는 security.py에서 구현 필요)
from app.models.users_models import MarketUser
def get_current_user(db: Session = Depends(get_db)) -> MarketUser:
    # !!! 경고: 이것은 임시 더미 함수입니다.
    # 실제로는 security.py에서 JWT 토큰을 검증하고 사용자를 반환해야 합니다.
    # ProductCreateScreen.js의 'me?.isSeller' 체크를 통과시키기 위해
    # is_seller=True인 1번 유저를 임시로 반환합니다.
    user = db.get(MarketUser, 1) 
    if not user:
        # 1번 유저가 없다면(DB가 비어있다면) 임시 생성
        user = MarketUser(
            id=1,
            email="seller@test.com", 
            username="임시판매자", 
            hashed_password="dummy_password", 
            is_seller=True, 
            seller_status="approved"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    if not user.is_seller:
         raise HTTPException(status_code=403, detail="판매자 권한이 없습니다.")
    return user

# ------------------------------------------------------
# 업로드 경로 (app/static/uploads) 준비
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
    # ProductCreateScreen.js의 FormData()에 맞게 Form 필드들을 받음
    title: str = Form(...),
    price: int = Form(...),
    shop_name: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    seller_note: Optional[str] = Form(None),
    delivery_info: Optional[str] = Form(None),
    region: Optional[str] = Form(None), # 'region' 필드 추가 (MarketHome.js 필터링용)
    images: List[UploadFile] = File(...), # 여러 이미지 받기
    db: Session = Depends(get_db),
    current_user: MarketUser = Depends(get_current_user) # 판매자 권한 확인
):
    """
    ProductCreateScreen.js에서 'multipart/form-data'로 전송한 상품 정보를 등록합니다.
    """
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
            if not file.filename:
                continue
            
            # 파일명 중복 방지를 위해 UUID 사용
            _, ext = os.path.splitext(file.filename)
            filename = f"{uuid.uuid4().hex}{ext.lower() or '.jpg'}"
            save_path = UPLOAD_DIR / filename
            
            # 파일을 디스크에 저장
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            saved_files.append(save_path)
    except Exception as e:
        # 실패 시 저장했던 파일들 삭제
        for path in saved_files:
            if path.exists(): os.remove(path)
        raise HTTPException(status_code=500, detail=f"이미지 저장 실패: {e}")
    
    # 3. 서비스 로직 호출 (DB에 정보 및 파일 경로 저장)
    try:
        product = create_product(db, data, current_user, saved_files)
        return product
    except Exception as e:
        # 실패 시 저장했던 파일들 삭제
        for path in saved_files:
            if path.exists(): os.remove(path)
        raise HTTPException(status_code=500, detail=f"DB 저장 실패: {e}")


@router.get(
    "", # GET /products
    response_model=List[MarketProductOut], # MarketHome.js는 리스트만 받음
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
    - MarketHome.js는 { items: [], total: 0 } 형태가 아닌 리스트 자체를 받으므로 
      (const list = Array.isArray(json) ? json : (json.items ?? []))
      여기서는 리스트만 반환합니다.
    - MarketHome.js의 fetch 주소는 /products 입니다.
    """
    items, total = list_products(
        db, q=q, region=region, sort=sort, page=page, size=size
    )
    # FE가 리스트를 바로 사용하므로 items만 반환
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
    current_user: MarketUser = Depends(get_current_user) # 질문자
):
    # TODO: 실제 JWT 인증 로직으로 current_user를 가져와야 함
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
    """
    ProductQnAScreen.js에서 호출하는 API
    """
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
    payload: dict, # FE에서 { "id": "product_id" } 형태의 이상한 객체를 보낼 수 있음
    db: Session = Depends(get_db),
    current_user: MarketUser = Depends(get_current_user) # 찜한 유저
):
    # FE의 useFavoritesStore.js가 product 객체 전체 또는 { id: ... }를 보냄
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
    current_user: MarketUser = Depends(get_current_user) # 찜한 유저
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
    current_user: MarketUser = Depends(get_current_user)
):
    """
    WishlistScreen.js는 'favoritesArray'를 사용하며, 
    이 API는 서버와 동기화하는 용도로 사용될 수 있습니다.
    (현재 WishlistScreen.js 코드는 서버 API를 호출하지 않고 로컬 스토리지(zustand)만 사용합니다)
    -> API를 호출하도록 FE 수정이 필요하지만, BE는 준비해둡니다.
    """
    return list_wishlist(db, user_id=current_user.id)