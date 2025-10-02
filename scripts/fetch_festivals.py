# scripts/fetch_festivals.py

import requests
import pandas as pd
from sqlalchemy.orm import Session
# app 폴더 바로 아래의 database.py를 가져옵니다.
from app import database 

# app/models 폴더 아래의 필요한 모델 파일을 직접 가져옵니다.
# Festival 모델이 festival_models.py 안에 있다고 가정합니다.
from app.models import festival_models
from app.core.config import get_settings

def fetch_and_store_festivals():
    """TourAPI로부터 축제 데이터를 가져와 DB에 저장합니다."""
    
    settings = get_settings()
    db: Session = next(database.get_db())

    # --- 개선점 1: 기존 contentid를 미리 한번에 가져오기 ---
    existing_ids_query = db.query(festival_models.Festival.contentid).all()
    existing_ids = {str(id_[0]) for id_ in existing_ids_query} # 빠른 조회를 위해 set으로 변환
    # ---------------------------------------------------

    url = 'http://apis.data.go.kr/B551011/KorService2/searchFestival2'
    page = 1

    while True:
        print(f"{page} 페이지 수집 중...")

        # 'params' 딕셔너리를 먼저 정의합니다.
        #    page 변수가 매번 바뀌므로, params는 반드시 while 루프 안에 있어야 합니다.
        params = {
            'MobileOS': 'ETC',
            'MobileApp': 'SosoHaeng',
            'serviceKey': settings.TOUR_API_KEY,
            '_type': 'json',
            'eventStartDate': '20250101',
            'numOfRows': 100,
            'pageNo': page
        }
        items = [] # 미리 초기화
        try:
            # API 요청 자체를 try 블록 안으로 이동
            response = requests.get(url, params=params)
            response.raise_for_status() # 4xx/5xx 에러 발생 시 예외를 일으킴
            
            # --- 👇 디버깅을 위해 이 두 줄을 추가하세요 ---
            print("API 응답 상태 코드:", response.status_code)
            print("API 응답 내용:", response.text)
            # -----------------------------------------
            
            # 'response' 변수를 사용하여 JSON 파싱
            data = response.json()
            items_raw = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        
            #  API가 빈 문자열("") 등을 반환하는 경우를 대비해, 리스트가 아니면 빈 리스트로 처리
            if isinstance(items_raw, list):
                items = items_raw
        
        except Exception as e:
            # 이제 네트워크 오류, JSON 파싱 오류 등 모든 문제를 여기서 잡습니다.
            print(f"API 요청 또는 데이터 처리 중 오류 발생: {e}")
            break

        if not items:
            print("✅ 해당 페이지에 데이터가 없거나 모든 데이터 수집 완료.")
            break
    
        df = pd.json_normalize(items)

        # 👈 1. INSERT와 UPDATE할 데이터를 담을 빈 리스트를 미리 생성
        festivals_to_create = []
        festivals_to_update = []

        for _, row in df.iterrows():
            content_id = row.get('contentid')
        
            # API 응답 데이터를 SQLAlchemy 모델이 이해하는 딕셔너리 형태로 변환
            festival_data = {
                'contentid': content_id,
                'title': row.get('title'),
                'addr1': row.get('addr1'), # models.py에 addr1이 정의되어 있다고 가정
                'eventstartdate': row.get('eventstartdate'),
                'eventenddate': row.get('eventenddate'),
                'mapx': float(row.get('mapx', 0)),
                'mapy': float(row.get('mapy', 0)),
            }

            # 👈 2. DB 조회가 아닌, 메모리에서 판별하여 각 리스트에 추가
            if content_id in existing_ids:
                festivals_to_update.append(festival_data)
            else:
                festivals_to_create.append(festival_data)
    
        # 👈 3. 루프가 끝난 후, 수집된 데이터를 DB에 한 번에 처리
        if festivals_to_create:
            db.bulk_insert_mappings(festival_models.Festival, festivals_to_create)
            print(f"{len(festivals_to_create)}건의 신규 데이터를 추가했습니다.")

        if festivals_to_update:
            db.bulk_update_mappings(festival_models.Festival, festivals_to_update)
            print(f"{len(festivals_to_update)}건의 기존 데이터를 업데이트했습니다.")
    
        db.commit() # 모든 변경사항을 한 번에 커밋
        page += 1
        
        db.close()
        print("DB 저장 완료")

if __name__ == "__main__":
    fetch_and_store_festivals()