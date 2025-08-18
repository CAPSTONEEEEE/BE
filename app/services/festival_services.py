# app/services/festival_service.py
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

# -------------------------
# CRUD & Query
# -------------------------
def list_festivals(
    db: Session,
    q: Optional[str] = None,
    region_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    size: int = 20,
    order_by: str = "start",  # start|recent|title
) -> Tuple[List[Festival], int]:
    stmt = select(Festival)
    conds = []

    if q:
        like = f"%{q}%"
        conds.append(or_(Festival.title.ilike(like), Festival.location.ilike(like)))
    if region_id:
        conds.append(Festival.region_id == region_id)
    if start_date:
        conds.append(Festival.event_end_date == None) if start_date is None else None  # noqa: E711
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
        stmt = stmt.order_by(asc(Festival.event_start_date.nulls_last()))

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
        event_start_date=data.event_start_date,
        event_end_date=data.event_end_date,
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


# -------------------------
# (옵션) 초기 더미 데이터 시드
# -------------------------
def seed_festivals_if_empty(db: Session) -> int:
    """테이블이 비어있으면 몇 개의 더미 축제를 채워 넣는다. 반환: 추가 개수"""
    count = db.scalar(select(func.count()).select_from(Festival))
    if count and count > 0:
        return 0

    samples = [
        Festival(
            title="봄꽃 축제", location="서울", description="벚꽃과 함께하는 봄맞이 축제",
            event_start_date=date(2025, 4, 10), event_end_date=date(2025, 4, 14)
        ),
        Festival(
            title="여름 해변 음악제", location="부산", description="바닷가에서 열리는 음악 페스티벌",
            event_start_date=date(2025, 7, 20), event_end_date=date(2025, 7, 22)
        ),
        Festival(
            title="가을 단풍 축제", location="강원도", description="단풍과 함께하는 가을 축제",
            event_start_date=date(2025, 10, 15), event_end_date=date(2025, 10, 20)
        ),
    ]
    db.add_all(samples)
    db.commit()
    return len(samples)
