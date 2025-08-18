from __future__ import annotations
from typing import Optional
from math import ceil
from datetime import date

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

router = APIRouter(prefix="/festivals", tags=["festival"])

# ---------- Mock Data ----------
class Festival(BaseModel):
    id: int
    title: str
    location: str
    start_date: date
    end_date: date
    region_id: int

# 임시 mock 데이터 (DB 대신 사용)
mock_festivals = [
    Festival(id=1, title="서울 불꽃축제", location="서울 여의도", start_date=date(2025, 10, 5), end_date=date(2025, 10, 5), region_id=1),
    Festival(id=2, title="부산 바다축제", location="부산 해운대", start_date=date(2025, 8, 1), end_date=date(2025, 8, 7), region_id=2),
    Festival(id=3, title="춘천 마임축제", location="강원 춘천", start_date=date(2025, 5, 25), end_date=date(2025, 5, 31), region_id=3),
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
    items = mock_festivals

    # 검색어 필터
    if q:
        items = [f for f in items if q.lower() in f.title.lower() or q.lower() in f.location.lower()]

    # 지역 필터
    if region_id:
        items = [f for f in items if f.region_id == region_id]

    # 날짜 필터
    if start_date:
        items = [f for f in items if f.start_date >= start_date]
    if end_date:
        items = [f for f in items if f.end_date <= end_date]

    total = len(items)
    start = (page - 1) * size
    end = start + size
    items = items[start:end]

    return {
        "items": items,
        "page": page,
        "size": size,
        "total": total,
        "total_pages": ceil(total / size) if size else 1,
    }

# ---------- Retrieve ----------
@router.get("/{festival_id}", response_model=Festival, summary="축제 상세 조회")
def get_festival(festival_id: int):
    for f in mock_festivals:
        if f.id == festival_id:
            return f
    raise HTTPException(status_code=404, detail="Festival not found")

# ---------- Create ----------
class FestivalCreate(BaseModel):
    title: str
    location: str
    start_date: date
    end_date: date
    region_id: int

@router.post("/", response_model=Festival, status_code=status.HTTP_201_CREATED, summary="축제 생성")
def create_festival(payload: FestivalCreate):
    new_id = max(f.id for f in mock_festivals) + 1 if mock_festivals else 1
    new_festival = Festival(id=new_id, **payload.dict())
    mock_festivals.append(new_festival)
    return new_festival

# ---------- Update ----------
class FestivalUpdate(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    region_id: Optional[int] = None

@router.patch("/{festival_id}", response_model=Festival, summary="축제 수정")
def update_festival(festival_id: int, payload: FestivalUpdate):
    for idx, f in enumerate(mock_festivals):
        if f.id == festival_id:
            updated = f.copy(update=payload.dict(exclude_unset=True))
            mock_festivals[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="Festival not found")

# ---------- Delete ----------
@router.delete("/{festival_id}", status_code=status.HTTP_204_NO_CONTENT, summary="축제 삭제")
def delete_festival(festival_id: int):
    for idx, f in enumerate(mock_festivals):
        if f.id == festival_id:
            mock_festivals.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Festival not found")
