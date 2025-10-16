from passlib.context import CryptContext

# 비밀번호 암호화를 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """입력된 비밀번호와 DB의 암호화된 비밀번호를 비교합니다."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """비밀번호를 해시화합니다."""
    if not isinstance(password, str):
        raise ValueError("Password must be a string")

    # bcrypt는 최대 72바이트까지만 지원하므로 잘라줍니다.
    password = password[:72]
    return pwd_context.hash(password)
