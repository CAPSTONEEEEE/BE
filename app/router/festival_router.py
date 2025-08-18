# app/router/festival_router.py
from __future__ import annotations
from typing import Optional
from math import ceil
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.services.common_service import get_db
from app.services import festival_service as svc
from app.models.festival_models import (
    FestivalCreate,
    FestivalUpdate,
    FestivalOut,
)

router = APIRouter(prefix="/festivals", tags=["festival"])

# ---------- List ----------
@router.get("/", response_model=dict, summary="축제 목록 조회")
def list_festivals(
    q: Optional[str] = Query(None, description="축제명/장소 검색어"),
    region_id: Optional[int] = Query(None, description="지역 ID(Regions)"),
    start_date: Optional[date] = Query(None, description="행사 시작일(이후) 필터"),
    end_date: Optional[date] = Query(None, description="행사 종료일(이전) 필터"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    order_by: str = Query("start", pattern="^(start|recent|title)$"),
    db: Session = Depends(get_db),
):
    """
    축제/행사 목록을 검색/필터/정렬/페이지네이션하여 반환합니다.
    """
    try:
        items, total = svc.list_festivals(
            db=db,
            q=q,
            region_id=region_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            size=size,
            order_by=order_by,
        )
        return {
            "items": [FestivalOut.model_validate(i) for i in items],
            "page": page,
            "size": size,
            "total": total,
            "total_pages": ceil(total / size) if size else 1,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"list_festivals failed: {e}")

# ---------- Retrieve ----------
@router.get("/{festival_id}", response_model=FestivalOut, summary="축제 상세 조회")
def get_festival(festival_id: int, db: Session = Depends(get_db)):
    try:
        obj = svc.get_festival_by_id(db=db, festival_id=festival_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Festival not found")
        return FestivalOut.model_validate(obj)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_festival failed: {e}")

# ---------- Create ----------
@router.post(
    "/",
    response_model=FestivalOut,
    status_code=status.HTTP_201_CREATED,
    summary="축제 생성",
)
def create_festival(payload: FestivalCreate, db: Session = Depends(get_db)):
    try:
        obj = svc.create_festival(db=db, data=payload)
        return FestivalOut.model_validate(obj)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"create_festival failed: {e}")

# ---------- Update (partial) ----------
@router.patch(
    "/{festival_id}",
    response_model=FestivalOut,
    summary="축제 수정",
)
def update_festival(
    festival_id: int, payload: FestivalUpdate, db: Session = Depends(get_db)
):
    try:
        obj = svc.update_festival(db=db, festival_id=festival_id, data=payload)
        if not obj:
            raise HTTPException(status_code=404, detail="Festival not found")
        return FestivalOut.model_validate(obj)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"update_festival failed: {e}")

# ---------- Delete ----------
@router.delete(
    "/{festival_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="축제 삭제",
)
def delete_festival(festival_id: int, db: Session = Depends(get_db)):
    try:
        ok = svc.delete_festival(db=db, festival_id=festival_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Festival not found")
        return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"delete_festival failed: {e}")
