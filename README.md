# 🚄 소소행 (SoSoHaeng) — BE (FastAPI · Python)

RAG 기반 여행지 추천, 지역 축제 정보 수집, 로컬 마켓 거래 기능을 제공하는 **소소행** 프로젝트의 백엔드 API 서버 레포지토리입니다.  
**FastAPI + SQLAlchemy**를 기반으로 구축되었으며, **LangChain & OpenAI**를 활용한 AI 추천 엔진과 **TourAPI** 데이터 파이프라인을 포함하고 있습니다.

---

## 기술 스택

| Category | Technology |
| --- | --- |
| **Framework** | FastAPI (Python 3.13+) |
| **Database** | MySQL (AWS RDS), SQLite (Dev), SQLAlchemy ORM |
| **AI / RAG** | LangChain, OpenAI API (GPT-4o), FAISS (Vector Search) |
| **Data Pipeline** | TourAPI (한국관광공사), AsyncSession (httpx) |
| **Migration** | Alembic |
| **Validation** | Pydantic |

---

## 폴더 구조

프로젝트의 주요 디렉토리 구조입니다.

```bash
BE/
├── app/                      # 메인 애플리케이션 코어
│   ├── core/                 # 설정(config) 및 의존성 관리
│   ├── db/                   # DB 세션 설정 및 연결
│   ├── models/               # SQLAlchemy ORM 모델 (DB 테이블 정의)
│   │   ├── festival_models.py
│   │   ├── market_models.py
│   │   ├── recommend_models.py
│   │   └── ...
│   ├── router/               # API 엔드포인트 라우팅 (Controller 역할)
│   │   ├── recommend_router.py # RAG 기반 AI 여행지 추천 API
│   │   ├── festival_router.py  # [LBS] GPS 기반 내 주변 축제 조회 API
│   │   ├── market_router.py    # 지역 특산물 마켓 상품/Q&A API
│   │   └── ...
│   ├── schemas/              # Pydantic 데이터 검증 스키마 (DTO)
│   ├── services/             # 비즈니스 로직 (Service Layer)
│   │   ├── recommend_service.py # LangChain 활용 RAG 파이프라인 로직
│   │   ├── festival_services.py # [LBS] Haversine 공식 적용 거리 계산 및 필터링
│   │   ├── market_service.py    # [Optimization] 상품 조회/정렬 및 N+1 쿼리 최적화
│   │   ├── tour_api_service.py  # TourAPI 비동기 데이터 수집 및 적재
│   │   └── ...
│   ├── clients/              # 외부 API 호출 클라이언트
│   └── main.py               # FastAPI 앱 진입점
├── migrations/               # Alembic DB 마이그레이션 스크립트
├── scripts/                  # 데이터 동기화 및 유틸리티 스크립트
│   ├── sync_festivals.py     # 축제 데이터 최신화 스크립트
│   └── ...
├── mock_data/                # 테스트용 Mock 데이터 (JSON)
├── requirements.txt          # 프로젝트 의존성 패키지 목록
└── alembic.ini               # Alembic 설정 파일
```

---

## 빠른 시작 (로컬 실행)

### 1. 레포지토리 클론
```bash
git clone [https://github.com/CAPSTONEEEEE/BE.git](https://github.com/CAPSTONEEEEE/BE.git)
cd BE
```

### 2. 가상 환경 설정 및 패키지 설치
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 3. 서버 실행
```bash
uvicorn app.main:app --host 0.0.0.0
```

---

## License
This project is developed for an academic capstone course.  
All rights reserved unless otherwise specified.

- **No commercial use** without explicit permission from the project team.
- **No redistribution** of source code or assets without permission.
- If you need to reuse any part of this repository (code, UI, images, icons), please contact the maintainers first.
