# app/services/user_service.py

from sqlalchemy.orm import Session
from app.models.users_models import MarketUser # User -> MarketUser
from app.schemas import MarketUserCreate, MarketUserLogin # schemas_.user_schemas -> schemas
from app.security import get_password_hash, verify_password 

def get_user_by_email(db: Session, email: str) -> MarketUser | None:
    """이메일을 사용해 데이터베이스에서 사용자를 조회합니다."""
    return db.query(MarketUser).filter(MarketUser.email == email).first()

def create_user(db: Session, user_create: MarketUserCreate):
    plain_password = user_create.password
    # 여기서도 비밀번호를 72바이트로 잘라줍니다.
    truncated_password = plain_password.encode('utf-8')[:72].decode('utf-8', 'ignore')
    
    hashed_password = get_password_hash(truncated_password)
    
    # 2. 암호화된 비밀번호로 DB 모델 객체를 만듭니다.
    # MarketUser 모델에 맞게 필드 전송
    db_user = MarketUser(
        email=user_create.email,
        username=user_create.username,
        hashed_password=hashed_password,
        is_seller=user_create.is_seller,
        business_number=user_create.business_number
    )
    
    # 3. DB에 추가하고 변경사항을 저장합니다.
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, user_login: MarketUserLogin):
    user = get_user_by_email(db, email=user_login.email)
    if not user:
        return None
        
    # 비밀번호를 72바이트로 잘라서 전달
    plain_password = user_login.password
    truncated_password_bytes = plain_password.encode('utf-8')[:72]
    
    # ▼▼▼ 디버깅 코드 수정 ▼▼▼
    # print(f"검증할 비밀번호(bytes): {truncated_password_bytes}")
    # print(f"길이(bytes): {len(truncated_password_bytes)}")
    # ▲▲▲ 디버깅 코드 수정 ▲▲▲

    if not verify_password(truncated_password_bytes, user.hashed_password):
        return None
    return user