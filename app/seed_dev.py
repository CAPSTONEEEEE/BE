# BE/app/seed_dev.py
from sqlalchemy.orm import Session
from datetime import date
import json

from app.database import SessionLocal
from app.models.market_models import Region, Market, Category, Product, ProductStatus
from app.models.festival_models import Festival
from app.models.recommend_models import Recommendation


def get_or_create(session: Session, model, *, lookup: dict, defaults: dict | None = None):
    """
    lookup 필드로 우선 검색하고 없으면 defaults를 포함해 생성
    """
    inst = session.query(model).filter_by(**lookup).first()
    if inst:
        return inst, False
    params = {**lookup}
    if defaults:
        params.update(defaults)
    inst = model(**params)
    session.add(inst)
    session.commit()
    session.refresh(inst)
    return inst, True


def seed_markets(session: Session):
    # 기존 market_models.py 시딩 로직 (변경 없음)
    jeonnam, _ = get_or_create(session, Region,
                               lookup={"name": "전라남도 함평군"},
                               defaults={"code": "JN-HP"})
    grain, _ = get_or_create(session, Category,
                             lookup={"name": "곡물"},
                             defaults={"slug": "grain"})

    market, _ = get_or_create(
        session, Market,
        lookup={"name": "함평 나비쌀 마켓", "region_id": jeonnam.id},
        defaults={
            "description": "전남 함평의 대표 특산물 판매",
            "address": "전라남도 함평군 함평읍 ○○로 123",
            "phone": "061-000-0000",
            "image_url": "https://example.com/hampyeong_market.jpg",
            "is_active": True,
        }
    )

    get_or_create(
        session, Product,
        lookup={"name": "함평 나비쌀 10kg", "market_id": market.id},
        defaults={
            "summary": "올해 수확한 신선한 쌀",
            "description": "청정 지역 함평에서 재배한 쌀로 밥맛이 뛰어납니다.",
            "price": 35000,
            "stock": 25,
            "unit": "10kg",
            "image_urls": ["https://example.com/rice10.jpg"],
            "status": ProductStatus.ACTIVE,
            "category_id": grain.id,
            "region_id": jeonnam.id,
        }
    )
    get_or_create(
        session, Product,
        lookup={"name": "함평 나비쌀 20kg", "market_id": market.id},
        defaults={
            "summary": "가성비 대용량",
            "description": "가정용/업소용 모두 추천",
            "price": 65000,
            "stock": 12,
            "unit": "20kg",
            "image_urls": ["https://example.com/rice20.jpg"],
            "status": ProductStatus.ACTIVE,
            "category_id": grain.id,
            "region_id": jeonnam.id,
        }
    )


def seed_festivals(session: Session):
    # 기존 festival_models.py 시딩 로직 (변경 없음)
    get_or_create(
        session, Festival,
        lookup={"title": "보령 머드 축제"},
        defaults={
            "region_id": None,
            "event_start_date": date(2025, 7, 20),
            "event_end_date": date(2025, 7, 28),
            "location": "충남 보령",
            "description": "머드 체험과 공연이 있는 여름 대표 축제",
            "image_url": "https://example.com/boryeong.jpg",
        }
    )
    get_or_create(
        session, Festival,
        lookup={"title": "전주 한옥마을 투어"},
        defaults={
            "region_id": None,
            "event_start_date": date(2025, 5, 1),
            "event_end_date": date(2025, 12, 31),
            "location": "전북 전주",
            "description": "전통과 현대가 공존하는 전주 한옥마을 투어 프로그램",
            "image_url": "https://example.com/jeonju.jpg",
        }
    )
    get_or_create(
        session, Festival,
        lookup={"title": "담양 죽녹원 산책"},
        defaults={
            "region_id": None,
            "event_start_date": date(2025, 4, 1),
            "event_end_date": date(2025, 10, 31),
            "location": "전남 담양",
            "description": "대나무 숲 힐링 산책",
            "image_url": "https://example.com/damyang.jpg",
        }
    )
    get_or_create(
        session, Festival,
        lookup={"title": "거제도 외도 보타니아"},
        defaults={
            "region_id": None,
            "event_start_date": date(2025, 3, 1),
            "event_end_date": date(2025, 11, 30),
            "location": "경남 거제",
            "description": "바다 위 정원 섬 투어",
            "image_url": "https://example.com/geoje.jpg",
        }
    )


def seed_recommendation(session: Session):
    """
    Recommendation 테이블에 더미 데이터를 추가합니다.
    """
    # JSON 직렬화된 tags와 reason을 사용
    get_or_create(
        session, Recommendation,
        lookup={"title": "부산 감천문화마을"},
        defaults={
            "description": "형형색색의 집들이 모여있는 예술 마을",
            "reason": json.dumps(["아름다운 풍경", "예술 감상", "사진 명소"]),
            "tags": json.dumps(["예술", "문화", "사진"]),
            "image_url": "https://example.com/gamcheon.jpg"
        }
    )
    get_or_create(
        session, Recommendation,
        lookup={"title": "단양 패러글라이딩"},
        defaults={
            "description": "하늘을 나는 짜릿한 경험",
            "reason": json.dumps(["짜릿한 경험", "멋진 경치", "액티비티"]),
            "tags": json.dumps(["액티비티", "스릴", "경치"]),
            "image_url": "https://example.com/danyang.jpg"
        }
    )
    get_or_create(
        session, Recommendation,
        lookup={"title": "경주 불국사"},
        defaults={
            "description": "신라 시대의 역사와 문화를 느낄 수 있는 곳",
            "reason": json.dumps(["역사 공부", "고요한 분위기", "문화유적"]),
            "tags": json.dumps(["역사", "문화", "유적"]),
            "image_url": "https://example.com/bulguksa.jpg"
        }
    )
    get_or_create(
        session, Recommendation,
        lookup={"title": "전주 한옥마을"},
        defaults={
            "description": "한국의 전통 가옥과 문화가 살아있는 곳",
            "reason": json.dumps(["전통 체험", "한옥 구경", "맛집 탐방"]),
            "tags": json.dumps(["전통", "문화", "한옥"]),
            "image_url": "https://example.com/jeonju-hanok.jpg"
        }
    )
    get_or_create(
        session, Recommendation,
        lookup={"title": "제주도 서귀포"},
        defaults={
            "description": "아름다운 해변과 조용한 분위기의 휴양지",
            "reason": json.dumps(["아름다운 해변", "조용한 분위기", "힐링"]),
            "tags": json.dumps(["바다", "자연", "휴양"]),
            "image_url": "https://example.com/seogwipo.jpg"
        }
    )


def main():
    session = SessionLocal()
    try:
        seed_markets(session)
        seed_festivals(session)
        seed_recommendation(session)
        print("✅ Dev seed completed.")
    finally:
        session.close()


if __name__ == "__main__":
    main()

