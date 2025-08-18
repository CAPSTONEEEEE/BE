# backend/app/router/common_router.py

from fastapi import APIRouter

# APIRouter 객체 생성
# prefix='/', tags=['Common']는 이 라우터의 모든 엔드포인트가
# 기본 경로('/')를 사용하고 'Common' 태그로 그룹화되도록 설정합니다.
router = APIRouter(prefix="", tags=["Common"])


# GET / 엔드포인트: 루트 경로를 위한 간단한 환영 메시지를 반환합니다.
@router.get("/")
def read_root():
    return {"message": "Welcome to Sosoheng API!"}

# GET /health 엔드포인트: 서버 상태를 확인하는 데 사용됩니다.
# 데이터베이스 연결 상태, API 키 유효성 등 더 복잡한 로직을 추가할 수 있습니다.
@router.get("/health")
def health_check():
    return {"status": "ok"}
