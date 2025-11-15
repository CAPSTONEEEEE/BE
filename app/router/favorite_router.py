from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# DB 세션 및 인증, 스키마, 서비스 import (경로에 맞게 수정 필요)
from app.db.database import get_db 
from app.schemas import UserRead # 사용자 정보 스키마 
from app.schemas import FavoriteRequest, FavoriteListResponse
from app.security import get_current_user # JWT 인증 디펜던시
from app.services.favorite_services import FavoriteService 

# 라우터 설정
router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
)

# ----------------------------------------------------
# 1. 찜 상태 토글 (POST /api/v1/favorites)
# ----------------------------------------------------
@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    # Dict[str, Union[str, bool]] 대신 명시적인 스키마 사용 가능
    response_model=dict, 
    description="찜 항목을 추가하거나 제거합니다."
)
def toggle_favorite_endpoint(
    request: FavoriteRequest,
    db: Session = Depends(get_db),
    # 인증 필수: 현재 로그인된 사용자 정보를 가져옵니다.
    current_user: UserRead = Depends(get_current_user), 
):
    service = FavoriteService(db)
    try:
        # 서비스의 toggle_favorite 호출
        result = service.toggle_favorite(current_user.id, request)
        return result
    except ValueError as e:
        # 유효성 검사 실패 (항목 없음, 이미 찜됨 등)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"찜 토글 중 서버 오류 발생: {str(e)}"
        )

# ----------------------------------------------------
# 2. 전체 찜 목록 조회 (GET /api/v1/favorites)
# ----------------------------------------------------
@router.get(
    "/",
    response_model=FavoriteListResponse, 
    description="사용자가 찜한 전체 목록을 타입별로 조회합니다."
)
def get_favorites_endpoint(
    db: Session = Depends(get_db),
    # 인증 필수: 현재 로그인된 사용자 정보를 가져옵니다.
    current_user: UserRead = Depends(get_current_user),
):
    service = FavoriteService(db)
    try:
        # 서비스의 get_user_favorites 호출
        favorites_list = service.get_user_favorites(current_user.id)
        return favorites_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"찜 목록 조회 중 서버 오류 발생: {str(e)}"
        )