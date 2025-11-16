# app/services/market_service.py

from __future__ import annotations
from typing import Optional, Tuple, List
import shutil
from pathlib import Path

from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, func, asc, desc, or_, and_, delete

# 새 ORM 모델 임포트
from app.models.market_models import (
    MarketProduct, MarketProductImage, MarketQna, MarketWishlist
)
from app.models.users_models import MarketUser

# 새 Pydantic 스키마 임포트 (schemas.py에서 정의)
from app.schemas import (
    MarketProductCreateSchema, MarketProductUpdateSchema,
    MarketQnaCreateSchema, MarketQnaUpdateSchema
)


# ---------- Product (상품) ----------
def create_product(
    db: Session, 
    data: MarketProductCreateSchema, 
    seller: MarketUser,
    image_files: List[Path] # 저장된 이미지 파일 경로 리스트
) -> MarketProduct:
    
    # 1. MarketProduct 객체 생성 (이미지 제외)
    db_product = MarketProduct(
        user_id=seller.id,
        title=data.title,
        price=data.price,
        shop_name=data.shop_name,
        location=data.location,
        summary=data.summary,
        seller_note=data.seller_note,
        delivery_info=data.delivery_info,
        region=data.region
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product) # product.id가 확정됨

    # 2. 이미지 파일 경로를 DB에 저장
    db_images = []
    for i, file_path in enumerate(image_files):
        # /static/uploads/filename.jpg 형태의 URL로 변환
        image_url = f"/static/uploads/{file_path.name}"
        db_img = MarketProductImage(
            product_id=db_product.id,
            image_url=image_url,
            is_thumbnail=(i == 0) # 첫 번째 이미지를 썸네일로 지정
        )
        db_images.append(db_img)

    if db_images:
        db.add_all(db_images)
        db.commit()
        db.refresh(db_product) # product.images 관계를 리프레시

    return db_product


def list_products(
    db: Session,
    q: Optional[str] = None,
    region: Optional[str] = None,
    sort: str = "likes",  # FE 코드 기준: '인기순'(likes), '후기순'(rating), '최신순'(recent)
    page: int = 1,
    size: int = 20,
) -> Tuple[List[MarketProduct], int]:
    
    stmt = (
        select(MarketProduct)
        .options(
            # ▼▼▼ [핵심 수정] Eager Loading 방식을 selectinload -> joinedload로 변경 ▼▼▼
            joinedload(MarketProduct.images), # 이미지를 Eager load (JOIN)
            # ▲▲▲ [핵심 수정] ▲▲▲
            joinedload(MarketProduct.seller)   # 판매자 정보를 Eager load
        )
    )
    
    conds = []
    if q:
        like = f"%{q}%"
        conds.append(or_(
            MarketProduct.title.ilike(like), 
            MarketProduct.summary.ilike(like),
            MarketProduct.location.ilike(like)
        ))
    if region and region != '전체':
        conds.append(MarketProduct.region == region)
    
    if conds:
        stmt = stmt.where(and_(*conds))

    # 정렬 (MarketHome.js 기준)
    if sort == '인기순':
        stmt = stmt.order_by(desc(MarketProduct.likes), desc(MarketProduct.rating))
    elif sort == '후기순':
        stmt = stmt.order_by(desc(MarketProduct.rating), desc(MarketProduct.likes))
    else: # '최신순' (기본값)
        stmt = stmt.order_by(desc(MarketProduct.created_at))

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.execute(
        stmt.offset((page - 1) * size).limit(size)
    ).scalars().unique().all() # unique()로 joinedload 중복 제거
    
    return rows, (total or 0)


def get_product(db: Session, product_id: int) -> Optional[MarketProduct]:
    # 상품 1개 조회 시, 모든 관련 정보(이미지, Q&A, 판매자)를 함께 로드
    stmt = (
        select(MarketProduct)
        .where(MarketProduct.id == product_id)
        .options(
            selectinload(MarketProduct.images),
            selectinload(MarketProduct.qna_list).joinedload(MarketQna.author),
            joinedload(MarketProduct.seller)
        )
    )
    return db.execute(stmt).scalar_one_or_none()


# ---------- QnA (상품 문의) ----------
def create_qna(db: Session, data: MarketQnaCreateSchema, product_id: int, author: MarketUser) -> MarketQna:
    db_qna = MarketQna(
        product_id=product_id,
        author_id=author.id,
        title=data.title,
        body=data.body
    )
    db.add(db_qna)
    db.commit()
    db.refresh(db_qna)
    return db_qna

def list_qna_for_product(db: Session, product_id: int) -> List[MarketQna]:
    stmt = (
        select(MarketQna)
        .where(MarketQna.product_id == product_id)
        .options(
            joinedload(MarketQna.author), # 질문 작성자 Eager Load
            joinedload(MarketQna.answerer) # 답변자 Eager Load
        )
        .order_by(desc(MarketQna.created_at))
    )
    return db.execute(stmt).scalars().all()


# ---------- Wishlist (찜하기) ----------
def add_wishlist(db: Session, user_id: int, product_id: int) -> Optional[MarketWishlist]:
    # 1. 상품이 존재하는지 확인
    product = db.get(MarketProduct, product_id)
    if not product:
        raise ValueError("Product not found")

    # 2. 이미 찜했는지 확인
    existing = db.execute(
        select(MarketWishlist).where(
            MarketWishlist.user_id == user_id, 
            MarketWishlist.product_id == product_id
        )
    ).scalar_one_or_none()
    
    if existing:
        return existing # 이미 찜한 상태면 그냥 반환

    # 3. 찜 목록에 추가
    db_wishlist = MarketWishlist(user_id=user_id, product_id=product_id)
    db.add(db_wishlist)
    
    # 4. 상품 'likes' 카운트 증가
    product.likes = (product.likes or 0) + 1
    
    db.commit()
    db.refresh(db_wishlist)
    return db_wishlist


def remove_wishlist(db: Session, user_id: int, product_id: int) -> bool:
    # 1. 찜 내역 조회
    existing = db.execute(
        select(MarketWishlist).where(
            MarketWishlist.user_id == user_id, 
            MarketWishlist.product_id == product_id
        )
    ).scalar_one_or_none()
    
    if not existing:
        return False # 삭제할 대상이 없음

    # 2. 찜 내역 삭제
    db.delete(existing)
    
    # 3. 상품 'likes' 카운트 감소
    product = db.get(MarketProduct, product_id)
    if product and (product.likes or 0) > 0:
        product.likes -= 1
        
    db.commit()
    return True


def list_wishlist(db: Session, user_id: int) -> List[MarketWishlist]:
    stmt = (
        select(MarketWishlist)
        .where(MarketWishlist.user_id == user_id)
        .options(
            joinedload(MarketWishlist.product) # 찜한 상품 정보 Eager Load
            .selectinload(MarketProduct.images) # 상품의 이미지까지 Eager Load
        )
        .order_by(desc(MarketWishlist.created_at))
    )
    return db.execute(stmt).scalars().all()