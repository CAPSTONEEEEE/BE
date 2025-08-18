# backend/app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv

# 다른 라우터 모듈을 가져옵니다.
from app.router import users_router, content_router
# 새로 만든 recommend_router를 임포트합니다.
from app.router import recommend_router
# 새로 만든 market_router를 임포트합니다.
from app.router import market_router

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
#app.include_router(content_router.router)

# 각 기능별 router를 포함시킵니다.
app.include_router(recommend_router.router)

# 라우터 등록
app.include_router(market_router.router)

# 기본 root 엔드포인트
@app.get("/")
def root():
    return {"message": "Sosohaeng Backend Mock API is running"}