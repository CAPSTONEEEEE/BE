# 🚄 SoSoHaeng (소소행) — Backend

**[English](#english) · [한국어](#한국어)**

---

## English

Backend API server for **SoSoHaeng (소소행)**, a RAG-based travel recommendation service for small cities in Korea, built as a capstone project by a team of 3.
It is built with **FastAPI + SQLAlchemy** and includes an AI recommendation engine using **LangChain & OpenAI**, plus a data pipeline for the Korea Tourism Organization's **TourAPI**.

### Features
- **RAG-based travel recommendations** (LangChain, FAISS, OpenAI GPT-4o)
- **Location-based festival search** using the Haversine formula (radius filtering, e.g. 10 km)
- **Local market API** for regional specialties (products, Q&A)
- **Async TourAPI ingestion pipeline** (httpx + SQLAlchemy `AsyncSession`)

### Highlights
- **Evaluation:** on a 50-question set against a GPT-4o baseline, hallucinated places dropped from 18% to 2% and small-city coverage rose from 40% to 96%.
- **Performance:** response latency improved from 4.5s to 1.8s (target < 3s) under a 50-user JMeter load test.
- **Query optimization:** N+1 queries removed in the market service; distance filtering handled in database queries.

### Tech stack
| Category | Technology |
| --- | --- |
| **Framework** | FastAPI (Python 3.13+) |
| **Database** | MySQL (AWS RDS), SQLite (development), SQLAlchemy ORM |
| **AI / RAG** | LangChain, OpenAI API (GPT-4o), FAISS (vector search) |
| **Data pipeline** | TourAPI (Korea Tourism Organization), httpx (async) |
| **Migration** | Alembic |
| **Validation** | Pydantic |

### Key modules
- `app/services/recommend_service.py`: LangChain RAG pipeline
- `app/services/festival_services.py`: Haversine distance calculation and filtering
- `app/services/market_service.py`: product queries and N+1 optimization
- `app/services/tour_api_service.py`: async TourAPI collection and loading
- `scripts/sync_festivals.py`: festival data sync script

The full directory tree is in the Korean section below.

### Getting started
```bash
git clone https://github.com/CAPSTONEEEEE/BE.git
cd BE

python -m venv venv
source venv/bin/activate      # Mac/Linux
# venv\Scripts\activate       # Windows

pip install -r requirements.txt

cp .env.example .env          # then fill in your own API keys and DB settings
alembic upgrade head          # apply DB migrations

uvicorn app.main:app --host 0.0.0.0
```
Once the server is running, the interactive API docs are available at `http://localhost:8000/docs`.

---

## 한국어

# 🚄 소소행 (SoSoHaeng) — BE (FastAPI · Python)

RAG 기반 여행지 추천, 지역 축제 정보 수집, 로컬 마켓 거래 기능을 제공하는 **소소행** 프로젝트의 백엔드 API 서버 레포지토리입니다.
**FastAPI + SQLAlchemy**를 기반으로 구축되었으며, **LangChain & OpenAI**를 활용한 AI 추천 엔진과 **TourAPI** 데이터 파이프라인을 포함하고 있습니다.

### 주요 기능
- **RAG 기반 AI 여행지 추천**: LangChain, FAISS, GPT-4o
- **GPS 기반 내 주변 축제 조회**: Haversine 공식으로 반경(예: 10km) 필터링
- **지역 특산물 마켓**: 상품 조회와 Q&A API
- **TourAPI 비동기 수집 파이프라인**: httpx + SQLAlchemy `AsyncSession`

### 성과 요약
- **평가:** 50개 문항 평가셋에서 GPT-4o 단독 응답과 비교해 존재하지 않는 장소 추천 비율이 18%에서 2%로, 소도시 커버리지가 40%에서 96%로 개선되었습니다.
- **성능:** 사용자 50명 JMeter 부하 테스트에서 응답 지연이 4.5초에서 1.8초로 줄었습니다(목표 3초 이내).
- **쿼리 최적화:** 마켓 서비스의 N+1 쿼리를 제거하고, 거리 필터링을 DB 쿼리에서 처리합니다.

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
├── collect_tour_data.py      # TourAPI 데이터 수집 스크립트
├── .env.example              # 환경 변수 예시 파일
├── requirements.txt          # 프로젝트 의존성 패키지 목록
└── alembic.ini               # Alembic 설정 파일
```

---

## 빠른 시작 (로컬 실행)

### 1. 레포지토리 클론
```bash
git clone https://github.com/CAPSTONEEEEE/BE.git
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

### 3. 환경 변수 설정
`.env.example`을 복사해 `.env`를 만들고, 본인의 API 키와 DB 설정을 입력합니다.
```bash
cp .env.example .env
```

### 4. DB 마이그레이션
```bash
alembic upgrade head
```

### 5. 서버 실행
```bash
uvicorn app.main:app --host 0.0.0.0
```
서버 실행 후 `http://localhost:8000/docs`에서 API 문서(Swagger UI)를 확인할 수 있습니다.

---

## License
This project is developed for an academic capstone course.
All rights reserved unless otherwise specified.

- **No commercial use** without explicit permission from the project team.
- **No redistribution** of source code or assets without permission.
- If you need to reuse any part of this repository (code, UI, images, icons), please contact the maintainers first.
