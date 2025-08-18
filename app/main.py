# backend/app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv

# 다른 라우터 모듈을 가져옵니다.
from app.router import users_router, content_router

# .env 파일에서 환경 변수를 불러옵니다.
load_dotenv()

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="소소행 API",
    description="소도시 여행 추천 및 지역 콘텐츠 제공을 위한 RESTful API",
    version="1.0.0"
)

# 각 라우터를 메인 애플리케이션에 포함시킵니다.
app.include_router(users_router.router)
app.include_router(content_router.router)

# 참고: /users/{user_id}/favorites 경로는 users_router와 content_router에
# 중복되어 정의될 수 있으므로, content_router에서 해당 경로를
# 적절한 접두사로 수정하거나, 하나의 라우터로 통합하는 것이 좋습니다.
