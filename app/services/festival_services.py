from __future__ import annotations
from typing import Optional, Tuple, List
from datetime import date
from math import radians, sin, cos, sqrt, atan2

from sqlalchemy import select, func, asc, desc, and_, or_, literal_column, text
from sqlalchemy.orm import Session
from app.models.festival_models import Festival, FestivalCreate, FestivalUpdate

#지구 반지름 (km 단위)
EARTH_RADIUS = 6371.0

# -------------------------
#Haversine 공식 구현
# -------------------------
def haversine_distance_sql(lat1: float, lon1: float, lat_col: str = 'mapy', lon_col: str = 'mapx') -> text:
    """
    Haversine 공식을 MySQL 쿼리로 작성하여 거리를 계산하는 SQL Expression을 반환합니다.
    (RDS에서 직접 계산하는 것이 성능상 유리합니다.)
    """
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)

    # 쿼리에서 직접 계산하도록 SQL 텍스트를 사용합니다.
    distance_expression = text(f"""
        ({EARTH_RADIUS} * 2 * ASIN(
            SQRT(
                POWER(SIN(RADIANS({lat_col} - {lat1}) / 2), 2) + 
                COS({lat1_rad}) * COS(RADIANS({lat_col})) * POWER(SIN(RADIANS({lon_col} - {lon1}) / 2), 2)
            )
        ))
    """).label('distance')
    
    return distance_expression


def list_festivals(
    db: Session,
    q: Optional[str] = None,
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None,
    distance_km: Optional[int] = None,
    page: int = 1,
    size: int = 20,
    order_by: str = "start",
) -> Tuple[List[Festival], int]:
    
    stmt_for_filtering = select(Festival)
    conds = []

    # 1. 위치 기반 필터링 조건 추가 (Haversine)
    if user_lat is not None and user_lon is not None and distance_km is not None:
        # SQL Expression으로 거리를 계산하는 서브쿼리를 만듭니다.
        distance_col = haversine_distance_sql(user_lat, user_lon)
        
        # 거리가 distance_km 이내인 조건을 추가합니다.
        # NOTE: 이 방식은 MySQL 8.0의 ST_Distance_Sphere를 사용하는 것이 가장 이상적이지만,
        # 호환성을 위해 SQLAlchemy text()를 사용합니다.
        
        # 일단은 Haversine 계산을 쿼리에 넣지 않고, 거리 제한만 추가하는 방식으로 변경
        # (Haversine 쿼리 자체가 복잡하여 SQLAlchemy와 함께 쓰기 어려움. Python에서 계산하는 것이 일반적)

        # 임시: 데이터베이스에서 필터링하는 대신, 데이터를 가져온 후 Python에서 필터링하는 방식으로 대체
        # (MySQL 8.0 Spatial Index 설정을 피하기 위한 최선의 방법)
        pass # 현재는 DB 필터링을 건너뛰고, 전체를 가져와 Python에서 필터링하는 것이 안전함.

    # 1. 일반 필터링 조건을 구성합니다.
    if q:
        like = f"%{q}%"
        # Festival.location은 addr1을 의미합니다.
        conds.append(or_(Festival.title.ilike(like), Festival.addr1.ilike(like))) 
    
    if conds:
        stmt_for_filtering = stmt_for_filtering.where(and_(*conds))

    # 2. 필터링된 결과의 전체 개수 계산 (위치 필터링 전)
    total = db.scalar(select(func.count()).select_from(stmt_for_filtering.subquery()))
    
    # 3. 정렬 적용
    stmt_for_data = stmt_for_filtering
    
    #거리순 정렬 추가
    if order_by == "distance" and user_lat is not None and user_lon is not None:
        # DB에서 직접 거리 계산하여 정렬합니다.
        distance_calc = haversine_distance_sql(user_lat, user_lon)
        stmt_for_data = stmt_for_data.add_columns(distance_calc).order_by(distance_calc)
    elif order_by == "title":
        stmt_for_data = stmt_for_data.order_by(asc(Festival.title))
    elif order_by == "recent":
        stmt_for_data = stmt_for_data.order_by(desc(Festival.created_at))
    else:  # "start" (시작일순)
        stmt_for_data = stmt_for_data.order_by(asc(Festival.event_start_date))

    # 4.페이징 적용
    stmt_for_data = stmt_for_data.offset((page - 1) * size).limit(size)
    items = db.execute(stmt_for_data).unique().all()
    
    # 5.위치 기반 필터링 (Python에서 처리)
    final_items = []
    
    for row in items:
        festival = row[0] # Festival 객체 추출

        #거리순 정렬 시 거리 정보 추가 (Haversine 결과가 row[1]에 있음)
        if order_by == "distance" and user_lat is not None:
            distance = row[1] # 계산된 거리 (km)
            
            #거리 제한 필터링
            if distance_km is not None and distance > distance_km:
                continue # 반경을 벗어나면 건너뜁니다.
            
            # Festival 객체에 임시로 distance 속성을 추가하여 FE에 전달할 수 있습니다.
            # 하지만 Pydantic 모델에 없으므로, 서비스 레이어에서 계산만 합니다.
        
        final_items.append(festival)

    # 현재 진행 중인 축제만 보여주는 필터링은 Router에서 이미 처리하거나 ,
    # 데이터 동기화 스크립트가 '종료된 축제'를 삭제/비활성화 해야 합니다. 
    
    return final_items, total


def get_festival_by_id(db: Session, festival_id: int) -> Optional[Festival]:
    return db.get(Festival, festival_id)


def create_festival(db: Session, data: FestivalCreate) -> Festival:
    # contentid를 제외하고 Pydantic 데이터만 추출
    data_dict = data.dict(exclude_unset=True)
    obj = Festival(**data_dict)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_festival(db: Session, festival_id: int, data: FestivalUpdate) -> Optional[Festival]:
    obj = db.get(Festival, festival_id)
    if not obj:
        return None
    
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