# BE/app/router/common_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

# --- ProductCreateScreen.js 권한 확인을 위한 임시 함수 ---
# (market_router.py에 있던 get_current_user를 common_router로 이동)
from app.models.users_models import MarketUser
from app.schemas import MarketUserOut # Pydantic 모델 임포트
def get_current_user_dummy(db: Session = Depends(get_db)) -> MarketUser:
    """
    임시 더미 함수: 실제 JWT 토큰 검증 대신
    DB에서 1번 유저를 가져오거나, 없으면 생성해서 반환합니다.
    """
    user = db.get(MarketUser, 1) 
    if not user:
        # 1번 유저가 없다면(DB가 비어있다면) 임시 생성
        # (id=1을 강제하지 않고 DB가 자동 생성하도록 함)
        user = MarketUser(
            email="seller@test.com", 
            username="임시판매자", 
            hashed_password="dummy_password_bcrypt_hash", # 실제 해시값
            is_seller=True, # 판매자여야 등록 화면 접근 가능
            seller_status="approved",
            business_number="111-22-33333"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
# --------------------------------------------------


# prefix="" -> prefix="/api/v1"은 main.py에서 적용됨
router = APIRouter(prefix="", tags=["Common"])


@router.get("/")
def read_root():
    return {"message": "Welcome to Sosoheng API v1!"}

@router.get("/health")
def health_check():
    return {"status": "ok"}

# ▼▼▼ [추가] GET /me 엔드포인트 ▼▼▼
@router.get(
    "/me", 
    response_model=MarketUserOut,
    summary="현재 로그인된 사용자 정보 확인 (ProductCreateScreen.js용)"
)
def read_users_me(current_user: MarketUser = Depends(get_current_user_dummy)):
    """
    ProductCreateScreen.js가 권한 확인을 위해 호출하는 API.
    현재는 더미 유저(1번 유저) 정보를 반환합니다.
    """
    # 1번 유저가 "사업자 미등록" 상태라면, "사업자 전용 기능" 화면이 뜹니다.
    # user = db.get(MarketUser, 1)
    # user.is_seller = False
    # user.business_number = None
    # db.commit()
    
    return current_user