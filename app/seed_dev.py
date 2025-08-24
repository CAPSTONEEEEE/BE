# app/seed_dev.py
from sqlalchemy.orm import Session
from datetime import date

from app.database import SessionLocal
from app.models.market_models import Region, Market, Category, Product, ProductStatus
from app.models.festival_models import Festival  # ← 팀원 모델 사용 (title, event_* 컬럼)

def get_or_create(session: Session, model, *, lookup: dict, defaults: dict | None = None):
    """lookup 필드로 우선 검색하고 없으면 defaults를 포함해 생성"""
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
    # Region
    jeonnam, _ = get_or_create(session, Region,
                               lookup={"name": "전라남도 함평군"},
                               defaults={"code": "JN-HP"})
    # Category
    grain, _ = get_or_create(session, Category,
                             lookup={"name": "곡물"},
                             defaults={"slug": "grain"})

    # Market
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

    # Products
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
    # ※ Festival 필드명: title, event_start_date, event_end_date, location, description
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

def main():
    session = SessionLocal()
    try:
        seed_markets(session)
        seed_festivals(session)
        print("✅ Dev seed completed.")
    finally:
        session.close()

if __name__ == "__main__":
    main()
