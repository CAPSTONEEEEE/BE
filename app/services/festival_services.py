from __future__ import annotations
from typing import Optional, Tuple, List, Any
import datetime
from math import radians, sin, cos, sqrt, atan2

from sqlalchemy import select, func, asc, desc, and_, or_, literal_column, text, extract
from sqlalchemy.orm import Session
from app.models.festival_models import Festival
#지구 반지름 (km 단위)
EARTH_RADIUS = 6371.0

def list_festivals(
    db: Session,
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None,
    distance_km: Optional[float] = None,
    page: int = 1,
    size: int = 20,
    order_by: str = "distance",
) -> Tuple[List[Any], int]:
    
    # 1. 기본 쿼리 설정
    query = db.query(Festival)
    
    # 2. 종료된 축제 제외 필터 추가 (오늘 날짜 이후이거나 오늘 진행 중인 축제만 표시)
    today_str = datetime.date.today().strftime('%Y%m%d')
    query = query.filter(Festival.event_end_date >= today_str)
    
    # 3. 거리 계산 및 필터링/정렬 준비
    distance_col = None
    if user_lat is not None and user_lon is not None:
        # Festival 모델에 정의된 올바른 Haversine 컬럼 생성 함수를 사용합니다.
        distance_col = Festival.distance_col(user_lat, user_lon)
        
        # 쿼리에 distance 컬럼을 추가 (정렬 및 결과 표시를 위함)
        query = query.add_columns(distance_col)

        # 거리 필터링: distance_km이 제공되면 해당 범위 내의 축제만 필터링합니다.
        if distance_km is not None and distance_km > 0:
            query = query.filter(distance_col <= distance_km)

    # 4. 정렬 (order_by)
    if order_by == 'distance' and distance_col is not None:
        # 거리(distance_col)를 기준으로 오름차순 정렬합니다.
        query = query.order_by(distance_col.asc())
    elif order_by == 'title':
        # 제목을 기준으로 오름차순 정렬합니다.
        query = query.order_by(Festival.title.asc())
    else:
        if distance_col is not None:
            query = query.order_by(distance_col.asc())
        else:
            # 거리 정보가 없을 경우 (예: user_lat/lon 미제공) ID 오름차순 등으로 대체
            query = query.order_by(Festival.id.asc())
            
    # 5. 총 개수 (페이지네이션을 위해)
    total_count = query.count()

    # 6. 페이지네이션 적용
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    
    # 7. 결과 반환 시, distance 컬럼이 추가된 경우 Festival 객체와 거리를 분리하여 반환해야 함.
    return items, total_count