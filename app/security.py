from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone 
from typing import Optional, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db.database import get_db 

settings = get_settings()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") 

# ======================================================
# 1. 비밀번호 해싱 및 검증
# ======================================================
pwd_context = CryptContext(schemes=["argon2"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """입력된 비밀번호와 DB의 암호화된 비밀번호를 비교합니다."""
    # Argon2는 72바이트 제한이 없지만, 함수 구조를 유지합니다.
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """비밀번호를 해시화합니다."""
    # BCrypt 오류 회피 로직은 Argon2에서는 불필요하지만, 만약의 경우를 대비해 유지합니다.
    password_safe = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password_safe)

# ======================================================
# 2. JWT 토큰 생성 
# ======================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """주어진 데이터와 만료 시간으로 JWT 액세스 토큰을 생성합니다."""
    to_encode = data.copy()
    
    # 만료 시간 (exp) 및 발급 시점 (iat) 설정
    now = datetime.now(timezone.utc) 
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=15) 
        
    to_encode.update({"exp": expire})  # 만료 시점
    to_encode.update({"iat": now})     # 발급 시점
    
    # 토큰 인코딩 및 반환
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# JWT 토큰 디코딩 함수 
def decode_access_token(token: str) -> Optional[dict]:
    """JWT 토큰을 디코딩하여 payload를 추출합니다."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
# ======================================================
# 3. JWT 토큰 검증 및 현재 사용자 로직 
# ======================================================

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # 순환 참조 해결을 위해 함수 내부에서 임포트합니다.
    from app.services.user_service import get_user_by_email 
    """JWT 토큰을 검증하고 현재 로그인된 사용자 객체를 반환합니다."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # DB에서 사용자 정보 조회
    user = get_user_by_email(db, email=email)
    
    if user is None:
        raise credentials_exception
        
    return user # DB 모델 객체 반환 (User 모델)