from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db # DB 세션 임포트
from app.schemas import FestivalListResponse, FestivalRead
from app.models.festival_models import FestivalBase
from app.services.festival_services import list_festivals

router = APIRouter(prefix="/festivals", tags=["festival"])


@router.get(
    "/",
    response_model=FestivalListResponse,
    summary="축제 목록 조회 (거리 필터링 및 정렬 기본 적용)"
)
async def list_festivals_api(
    db: Session = Depends(get_db), # DB 세션 의존성 주입
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    # 기본 정렬을 'distance'로 설정하여 10km 필터와 함께 사용되도록 합니다.
    order_by: str = Query(
        "distance", 
        pattern="^(distance|title)$", # 'distance'와 'title'만 허용
        description="정렬 기준: 'distance' 또는 'title' 중 선택"
    ),
    
    user_lat: float = Query(
        ..., 
        description="사용자 현재 위치 위도 (필수)", 
        alias="user_lat"
    ),
    user_lon: float = Query(
        ..., 
        description="사용자 현재 위치 경도 (필수)", 
        alias="user_lon"
    ),
    
    # 기본 거리 필터링을 10km로 설정하여 기본 화면으로 제공합니다.
    distance_km: Optional[float] = Query(
        10.0, 
        ge=0.1, 
        description="거리 필터 (km 단위). None으로 설정 시 필터링 없음 (전체 목록)."
    ),
) -> Any:
    """
    사용자 위치 기반으로 현재 진행 중인 축제 목록을 조회합니다.
    - 기본적으로 10km 이내의 축제가 거리 순으로 정렬되어 표시됩니다.
    - 쿼리 파라미터 distance_km을 None으로 설정하거나 요청에 포함하지 않으면 거리 필터가 해제됩니다.
    """
    try:
        # 서비스 레이어 호출: items는 (Festival 객체, distance)의 튜플 리스트로 반환됩니다.
        items_with_distance, total_count = list_festivals(
            db=db,
            page=page,
            size=size,
            user_lat=user_lat,
            user_lon=user_lon,
            distance_km=distance_km,
            order_by=order_by
        )
        
        # Pydantic 스키마에 맞게 데이터 변환 및 거리 정보 포함
        festival_list = []
        for festival_obj, distance in items_with_distance:
                
                # FestivalRead 스키마에 거리 정보를 포함하여 생성
                festival_data = FestivalRead.model_validate(festival_obj)
                # 거리 정보를 추가 (소수점 둘째 자리까지 반올림)
                festival_data.distance = round(distance, 2)
                festival_list.append(festival_data)
                
        return FestivalListResponse(
            total=total_count,
            page=page,
            size=size,
            items=festival_list
        )

    except Exception as e:
        # 서버 에러 발생 시 500 응답 반환 및 에러 로깅
        print(f"API Error in list_festivals_api: {e}")
        # 사용자에게 상세한 에러 메시지를 노출하지 않기 위해 일반적인 메시지를 사용
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="서버 내부 오류가 발생했습니다. 로그를 확인해주세요."
        )