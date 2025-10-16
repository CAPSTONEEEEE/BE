from sqlalchemy.orm import Session
from app.models.users_models import User
from app.schemas_ import user_schemas
from app.security import get_password_hash, verify_password 

def get_user_by_email(db: Session, email: str) -> User | None:
    """이메일을 사용해 데이터베이스에서 사용자를 조회합니다."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: user_schemas.UserCreate) -> User:
    """새로운 사용자를 생성하고 데이터베이스에 저장합니다."""
    print("🔍 [DEBUG] password type:", type(user.password))
    print("🔍 [DEBUG] password value:", user.password)
    # 1. 비밀번호를 암호화(해시)합니다.
    hashed_password = get_password_hash(user.password)
    
    # 2. 암호화된 비밀번호로 DB 모델 객체를 만듭니다.
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    
    # 3. DB에 추가하고 변경사항을 저장합니다.
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, user_login: user_schemas.UserLogin) -> User | None:
    """사용자 이메일과 비밀번호를 검증하여 인증합니다."""
    # 1. 이메일로 사용자를 먼저 찾습니다.
    db_user = get_user_by_email(db, email=user_login.email)
    
    # 2. 사용자가 없거나, 비밀번호가 틀리면 None을 반환합니다.
    if not db_user or not verify_password(user_login.password, db_user.hashed_password):
        return None
        
    # 3. 인증에 성공하면 사용자 객체를 반환합니다.
    return db_user

