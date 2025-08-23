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
    stmt = select(Festival)
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
        stmt = stmt.where(and_(*conds))

    if order_by == "title":
        stmt = stmt.order_by(asc(Festival.title))
    elif order_by == "recent":
        stmt = stmt.order_by(desc(Festival.created_at))
    else:  # "start"
        # SQLite에서 NULLS LAST를 지원하지 않으므로, 이와 유사한 동작을 하도록 수정
        # NULL 값을 먼저 정렬하고, 그 다음에 오름차순으로 정렬합니다.
        # 즉, NULL인 경우 1, 아닌 경우 0으로 만들어 정렬 우선순위를 줍니다.
        stmt = stmt.order_by(
            asc(Festival.event_start_date.is_(None)),
            asc(Festival.event_start_date)
        )
    
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    stmt = stmt.offset((page - 1) * size).limit(size)
    items = db.execute(stmt).scalars().all()
    return items, total


def get_festival_by_id(db: Session, festival_id: int) -> Optional[Festival]:
    return db.get(Festival, festival_id)


def create_festival(db: Session, data: FestivalCreate) -> Festival:
    obj = Festival(
        title=data.title,
        location=data.location,
        region_id=data.region_id,
        event_start_date=data.start_date,
        event_end_date=data.end_date,
        description=data.description,
        image_url=str(data.image_url) if data.image_url else None,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_festival(db: Session, festival_id: int, data: FestivalUpdate) -> Optional[Festival]:
    obj = db.get(Festival, festival_id)
    if not obj:
        return None
    for k, v in data.dict(exclude_unset=True).items():
        if k == "start_date":
            setattr(obj, "event_start_date", v)
        elif k == "end_date":
            setattr(obj, "event_end_date", v)
        else:
            setattr(obj, k, v)
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