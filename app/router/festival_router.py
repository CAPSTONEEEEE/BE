# app/router/festival_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from datetime import date
from app.models.festival_models import FestivalCreate, FestivalUpdate, FestivalOut
from app.services.festival_services import (
    list_festivals,
    get_festival_by_id,
    create_festival,
    update_festival,
    delete_festival,
)

router = APIRouter(prefix="/festivals", tags=["festival"])

# ---------- List ----------
@router.get("/", response_model=List[FestivalOut], summary="축제 목록 조회")
def list_festivals_api(
    q: str | None = Query(None, description="축제명/장소 검색어"),
    region_id: int | None = Query(None, description="지역 ID"),
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    order_by: str = Query("start", pattern="^(start|recent|title)$"),
    db: Session = Depends(get_db),
):
    items, _ = list_festivals(db, q, region_id, start_date, end_date, page, size, order_by)
    return items

# ---------- Retrieve ----------
@router.get("/{festival_id}", response_model=FestivalOut, summary="축제 상세 조회")
def get_festival_api(festival_id: int, db: Session = Depends(get_db)):
    festival = get_festival_by_id(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    return festival

# ---------- Create ----------
@router.post("/", response_model=FestivalOut, status_code=status.HTTP_201_CREATED, summary="축제 생성")
def create_festival_api(payload: FestivalCreate, db: Session = Depends(get_db)):
    return create_festival(db, payload)

# ---------- Update ----------
@router.put("/{festival_id}", response_model=FestivalOut, summary="축제 수정")
def update_festival_api(festival_id: int, payload: FestivalUpdate, db: Session = Depends(get_db)):
    festival = update_festival(db, festival_id, payload)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    return festival

# ---------- Delete ----------
@router.delete("/{festival_id}", status_code=status.HTTP_204_NO_CONTENT, summary="축제 삭제")
def delete_festival_api(festival_id: int, db: Session = Depends(get_db)):
    success = delete_festival(db, festival_id)
    if not success:
        raise HTTPException(status_code=404, detail="Festival not found")
