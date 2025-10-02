import requests
import sys
import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from time import sleep

# 현재 디렉터리를 Python 경로에 추가하여 모듈을 임포트할 수 있게 합니다.
# 이 스크립트가 backend/ 디렉토리 밖에서 실행된다고 가정합니다.
# 만약 backend/app/ 밑에서 실행한다면 이 부분은 수정해야 합니다.
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 임포트 오류가 발생하면 이 부분을 수정해야 합니다.
try:
    from app.services.tour_api_service import get_api_params, COMMON_INFO_URL
    from app.models.tour_models import TourData
    from app.database import SessionLocal 
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure you are running this script from the correct directory or adjust sys.path.")
    sys.exit(1)


# 수집할 콘텐츠 타입 ID 목록 (관광공사 기준)
# 12: 관광지, 14: 문화시설, 15: 축제/공연/행사, 28: 레포츠, 32: 숙박, 38: 쇼핑, 39: 음식점
CONTENT_TYPE_IDS = ["12", "14", "28", "38", "39"] # 주요 여행지, 문화, 레포츠, 쇼핑, 음식점


def fetch_tour_data(page_no: int, content_type_id: str):
    """관광공사 API에서 데이터를 가져옵니다."""
    try:
        params = get_api_params(page_no, content_type_id)
        print(f"  -> Calling API for Content Type {content_type_id}, Page {page_no}...")
        
        # API 호출
        response = requests.get(COMMON_INFO_URL, params=params)
        response.raise_for_status() # HTTP 에러 발생 시 예외 처리
        
        data = response.json()
        
        # 전체 데이터 개수와 현재 페이지의 아이템 개수 확인
        body = data.get("response", {}).get("body", {})
        total_count = body.get("totalCount", 0)
        items = body.get("items", {}).get("item", [])
        
        # item이 하나만 있을 경우 리스트가 아닌 딕셔너리로 반환되는 경우를 처리
        if isinstance(items, dict):
            items = [items]
            
        print(f"  -> Total: {total_count}, Items fetched this page: {len(items)}")
        
        return items, total_count
        
    except requests.exceptions.HTTPError as e:
        print(f"  [ERROR] HTTP Error occurred: {e}. Check API key or URL.")
        return [], 0
    except Exception as e:
        print(f"  [ERROR] An unexpected error occurred: {e}")
        return [], 0


def save_data_to_db(db: Session, items):
    """가져온 아이템 목록을 DB에 저장합니다."""
    new_count = 0
    
    for item in items:
        # DB에 이미 존재하는 contentid인지 확인
        existing_item = db.query(TourData).filter(TourData.contentid == str(item.get("contentid"))).first()
        
        if existing_item:
            # print(f"  - Skipping existing item: {item.get('title')}")
            continue

        try:
            # TourData 모델에 맞게 데이터 정제 및 객체 생성
            tour_data = TourData(
                contentid=str(item.get("contentid")), # 문자열로 변환
                contenttypeid=str(item.get("contenttypeid")), # 문자열로 변환
                title=item.get("title"),
                addr1=item.get("addr1"),
                addr2=item.get("addr2"),
                areacode=item.get("areacode"),
                sigungucode=item.get("sigungucode"),
                tel=item.get("tel"),
                firstimage=item.get("firstimage"),
                firstimage2=item.get("firstimage2"),
                mapx=float(item.get("mapx")) if item.get("mapx") else None,
                mapy=float(item.get("mapy")) if item.get("mapy") else None,
                overview=item.get("overview"), # overview는 이 API에서 제공 안될 수 있음 (나중에 디테일 API 필요)
                homepage=item.get("homepage"),
                cat1=item.get("cat1"),
                cat2=item.get("cat2"),
                cat3=item.get("cat3"),
                booktour=item.get("booktour"),
                zipcode=item.get("zipcode"),
            )
            db.add(tour_data)
            new_count += 1
            
        except Exception as e:
            print(f"  [ERROR] Failed to process item {item.get('contentid')}: {e}")
            
    try:
        db.commit()
        print(f"  [SUCCESS] Successfully saved {new_count} new items.")
    except IntegrityError:
        db.rollback()
        print("  [WARNING] IntegrityError occurred (duplicate primary key/unique constraint). Rolling back.")
    except Exception as e:
        db.rollback()
        print(f"  [ERROR] Database commit failed: {e}")


def main():
    """메인 데이터 수집 루틴"""
    print("==============================================")
    print("       Starting Tour API Data Collection      ")
    print("==============================================")
    
    # DB 세션 생성
    db: Session = SessionLocal()
    
    for content_type_id in CONTENT_TYPE_IDS:
        print(f"\n[SECTION] Collecting data for Content Type ID: {content_type_id}")
        page = 1
        has_more_data = True
        
        while has_more_data:
            print(f"\n  Processing Page {page}...")
            
            items, total_count = fetch_tour_data(page, content_type_id)
            
            if not items:
                has_more_data = False
                print("  -> Finished fetching. No more items returned.")
                continue
                
            # DB에 데이터 저장
            save_data_to_db(db, items)

            # 다음 페이지로 이동
            page += 1
            
            # API 호출 간격 유지 (Too Many Requests 방지)
            sleep(0.5) 
            
            # API 제한에 따라 10페이지까지만 수집하도록 제한하거나 (선택사항)
            # if page > 10: 
            #     print("Reached page limit for this type. Moving to next content type.")
            #     break

    db.close()
    print("\n==============================================")
    print("    Tour API Data Collection FINISHED       ")
    print("==============================================")


if __name__ == "__main__":
    main()
