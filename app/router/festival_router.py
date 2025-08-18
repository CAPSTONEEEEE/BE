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

# ---------------- Mock Data ----------------
mock_festivals = [
    {
        "id": 1,
        "title": "서울 불꽃축제",
        "region_id": 11,
        "location": "서울 여의도 한강공원",
        "start_date": "2025-09-01",
        "end_date": "2025-09-03",
        "description": "서울에서 열리는 불꽃놀이 축제",
    },
    {
        "id": 2,
        "title": "부산 국제영화제",
        "region_id": 26,
        "location": "부산 해운대",
        "start_date": "2025-10-05",
        "end_date": "2025-10-12",
        "description": "아시아 최대 영화제",
    },
]

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
    
):
    filtered = mock_festivals
    if q:
        filtered = [f for f in filtered if q.lower() in f["title"].lower() or q in f["location"]]
    if region_id:
        filtered = [f for f in filtered if f["region_id"] == region_id]

    total = len(filtered)
    start = (page - 1) * size
    end = start + size
    items = filtered[start:end]

    return {
        "items": [FestivalOut(**i) for i in items],
        "page": page,
        "size": size,
        "total": total,
        "total_pages": ceil(total / size) if size else 1,
    }

# ---------- Retrieve ----------
@router.get("/{festival_id}", response_model=FestivalOut, summary="축제 상세 조회")
def get_festival(festival_id: int):
    for f in mock_festivals:
        if f["id"] == festival_id:
            return FestivalOut(**f)
    raise HTTPException(status_code=404, detail="Festival not found") 

# ---------- Create ----------
@router.post(
    "/",
    response_model=FestivalOut,
    status_code=status.HTTP_201_CREATED,
    summary="축제 생성",
)
def create_festival(payload: FestivalCreate):
    new_id = max(f["id"] for f in mock_festivals) + 1 if mock_festivals else 1
    new_festival = payload.dict()
    new_festival["id"] = new_id
    mock_festivals.append(new_festival)
    return FestivalOut(**new_festival)

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
def delete_festival(festival_id: int):
    global mock_festivals
    mock_festivals = [f for f in mock_festivals if f["id"] != festival_id]
    return