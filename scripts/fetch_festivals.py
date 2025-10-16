# scripts/fetch_festivals.py
import requests
import json
import pandas as pd
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app import database
from app.models import festival_models
from datetime import datetime

def fetch_and_store_festivals():
    """
    TourAPI 또는 로컬 목(Mock) 데이터로부터 축제 데이터를 가져와 DB에 저장합니다.
    """
    settings = get_settings()
    db: Session = next(database.get_db())
    
    # --- 1. DB에 이미 있는 데이터의 ID 목록을 가져옵니다. ---
    try:
        existing_ids_query = db.query(festival_models.Festival.contentid).all()
        existing_ids = {str(id_tuple[0]) for id_tuple in existing_ids_query}
    except Exception as e:
        print(f"DB 조회 중 오류 발생: {e}")
        db.close()
        return
    # --- 2. 데이터 가져오기 ---
    # TourAPI가 정상일 때는 아래 주석을 풀고, '목 데이터 로직' 부분을 주석 처리하세요.
    
    """
    # ===============================================================
    #  (1) 실제 TourAPI 호출 로직 (현재는 주석 처리됨)
    # ===============================================================
    items = []
    url = 'http://apis.data.go.kr/B551011/KorService/searchFestival'
    page = 1

    while True:
        print(f"{page} 페이지 수집 중...")
        params = {
            'MobileOS': 'ETC',
            'MobileApp': 'SosoHaeng',
            'serviceKey': settings.TOUR_API_KEY,
            'eventStartDate': '20250101',
            'numOfRows': 100,
            'pageNo': page
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            items_raw = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            
            if isinstance(items_raw, list):
                items.extend(items_raw) # 여러 페이지 데이터를 누적
            elif items_raw: # 단일 아이템일 경우
                items.append(items_raw)

            # 마지막 페이지인지 확인 (가져온 아이템 수가 numOfRows보다 적으면 마지막 페이지)
            if len(items_raw) < params['numOfRows']:
                print("✅ 모든 데이터 수집 완료.")
                break
        
        except Exception as e:
            print(f"API 요청 또는 데이터 처리 중 오류 발생: {e}")
            break # 오류 발생 시 중단
        
        page += 1
    """

    # ===============================================================
    #  (2) 목(Mock) 데이터 로직 (현재 활성화됨)
    # ===============================================================
    items = []
    try:
        with open('mock_data/mock_festivals.json', 'r', encoding='utf-8') as f:
            items = json.load(f)
        print(f"✅ 목 데이터 파일에서 {len(items)}개의 아이템을 성공적으로 불러왔습니다.")
    except FileNotFoundError:
        print("❌ 에러: 'BE/mock_data/mock_festivals.json' 파일을 찾을 수 없습니다.")
        db.close()
        return
    except json.JSONDecodeError:
        print("❌ 에러: JSON 파일 형식이 잘못되었습니다.")
        db.close()
        return
    # ===============================================================
    if not items:
        print("저장할 데이터가 없습니다.")
        db.close()
        return

    # --- 3. Pandas DataFrame으로 변환 및 DB 저장 ---
    df = pd.json_normalize(items)

    festivals_to_create = []
    festivals_to_update = []
    

    for _, row in df.iterrows():
        content_id = str(row.get('contentid'))
        
        festival_data = {
            'contentid': content_id,
            'title': row.get('title'),
            'location': row.get('addr1'),
            'event_start_date': row.get('eventstartdate'),
            'event_end_date': row.get('eventenddate'),
            'mapx': float(row.get('mapx', 0)),
            'mapy': float(row.get('mapy', 0)),
            'image_url': row.get('firstimage')
        }
        
        if content_id in existing_ids:
            festivals_to_update.append(festival_data)
        else:
            festivals_to_create.append(festival_data)
    try:
        if festivals_to_create:
            for data in festivals_to_create:
                db_obj = festival_models.Festival(**data)
                db.add(db_obj)
            print(f"{len(festivals_to_create)}건의 신규 데이터를 추가했습니다.")

        if festivals_to_update:
            for data in festivals_to_update:
                db.query(festival_models.Festival).filter(
                    festival_models.Festival.contentid == data['contentid']
                ).update({k: v for k, v in data.items() if v is not None}) # None 값은 업데이트에서 제외
            print(f"{len(festivals_to_update)}건의 기존 데이터를 업데이트했습니다.")
        
        db.commit()
        #page += 1
    except Exception as e:
        print(f"DB 저장 중 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()
        print("DB 저장 완료")

if __name__ == "__main__":
    fetch_and_store_festivals()
    