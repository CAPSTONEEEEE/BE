from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db # DB 세션 임포트
from app.models.festival_models import FestivalCreate, FestivalUpdate, FestivalOut

from app.services.festival_services import (
    list_festivals,
    get_festival_by_id,
    create_festival,
    update_festival,
    delete_festival,
)

router = APIRouter(prefix="/festivals", tags=["festival"])


@router.get("/", response_model=List[FestivalOut], summary="축제 목록 조회 및 위치 기반 필터링")
def list_festivals_api(
    # Haversine 공식에 필요한 파라미터 추가
    user_lat: float = Query(None, description="사용자 위도 (mapy)"),
    user_lon: float = Query(None, description="사용자 경도 (mapx)"),
    distance_km: int = Query(None, description="반경 (km)"),
    
    q: str | None = Query(None, description="축제명/장소 검색어"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    order_by: str = Query("start", pattern="^(start|recent|title|distance)$", description="정렬 기준"),
    db: Session = Depends(get_db), # DB 세션 의존성 주입
):
    items, _ = list_festivals(
        db, 
        q=q,
        user_lat=user_lat,
        user_lon=user_lon,
        distance_km=distance_km,
        page=page, 
        size=size, 
        order_by=order_by
    )
    return items

# ---------- Retrieve ----------
@router.get("/{festival_id}", response_model=FestivalOut, summary="축제 상세 조회 (DB 기반)")
def get_festival_api(festival_id: int, db: Session = Depends(get_db)):
    festival = get_festival_by_id(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found in DB")
    return festival
