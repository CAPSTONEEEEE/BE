# app/services/festival_services.py
from __future__ import annotations
from typing import Optional, Tuple, List
from datetime import date

from sqlalchemy import select, func, asc, desc, and_, or_
from sqlalchemy.orm import Session

from app.models.festival_models import (
    Festival,
    FestivalCreate,  
    FestivalUpdate,  
)
def list_festivals(
    db: Session,
    q: Optional[str] = None,
    region_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    size: int = 20,
    order_by: str = "start",
) -> Tuple[List[Festival], int]:
    
    # 1. 필터링 조건을 먼저 구성합니다.
    stmt_for_filtering = select(Festival)
    conds = []
    if q:
        like = f"%{q}%"
        conds.append(or_(Festival.title.ilike(like), Festival.location.ilike(like)))
    if region_id:
        conds.append(Festival.region_id == region_id)
    if start_date:
        conds.append(Festival.event_end_date >= start_date)
    if end_date:
        conds.append(Festival.event_start_date <= end_date)
    
    if conds:
        stmt_for_filtering = stmt_for_filtering.where(and_(*conds))

    # 2. 필터링된 결과의 전체 개수를 먼저 효율적으로 계산합니다.
    total = db.scalar(select(func.count()).select_from(stmt_for_filtering.subquery()))
    
    # 3. 그 다음에 정렬과 페이징을 적용하여 실제 데이터를 가져옵니다.
    stmt_for_data = stmt_for_filtering
    if order_by == "title":
        stmt_for_data = stmt_for_data.order_by(asc(Festival.title))
    elif order_by == "recent":
        stmt_for_data = stmt_for_data.order_by(desc(Festival.created_at))
    else:  # "start"
        stmt_for_data = stmt_for_data.order_by(
            asc(Festival.event_start_date.is_(None)),
            asc(Festival.event_start_date)
        )
    
    stmt_for_data = stmt_for_data.offset((page - 1) * size).limit(size)
    items = db.execute(stmt_for_data).scalars().all()
    
    return items, total


def get_festival_by_id(db: Session, festival_id: int) -> Optional[Festival]:
    return db.get(Festival, festival_id)


def create_festival(db: Session, data: FestivalCreate) -> Festival:
    # **data.dict()를 사용하여 코드를 간결하게 만듭니다.
    obj = Festival(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_festival(db: Session, festival_id: int, data: FestivalUpdate) -> Optional[Festival]:
    obj = db.get(Festival, festival_id)
    if not obj:
        return None
    
    # Pydantic과 SQLAlchemy 모델의 필드명이 일치한다고 가정하고 코드를 간결하게 만듭니다.
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(obj, key, value)
        
    db.commit()
    db.refresh(obj)
    return obj


def delete_festival(db: Session, festival_id: int) -> bool:
    obj = db.get(Festival, festival_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True