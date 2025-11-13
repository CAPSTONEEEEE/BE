import os
import sys
import asyncio
from dotenv import load_dotenv
from datetime import datetime, date

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from sqlalchemy.exc import OperationalError

# ====================================================================
# .env 경로 강제 지정 및 로드
# ====================================================================
# 1. PYTHONPATH에 현재 BE 폴더를 추가하여 app.* 모듈을 인식하도록 함
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# 2. .env 파일 로드를 위해 현재 위치를 프로젝트 루트로 강제 이동 및 로드
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    # 현재 디렉토리를 프로젝트 루트 (BE)로 변경하여 .env 파일을 찾도록 함
    os.chdir(project_root)
except FileNotFoundError:
    pass 
# 3. .env 로드
load_dotenv()
# ====================================================================


from app.db.database import SessionLocal, engine, test_db_connection 
from app.models.festival_models import Festival
from app.clients.tour_api_client import TourAPIClient


# --- 1. 데이터베이스 모델 설정 (테이블 확인용) ---
def create_db_tables():
    # Workbench에서 이미 테이블을 생성했으므로, 여기서는 모델을 로드하는 역할만 합니다.
    pass


# --- 2. TourAPI 데이터 동기화 함수 ---
async def run_db_sync():
    """
    TourAPI에서 모든 축제 데이터를 가져와 RDS에 저장(Upsert)합니다.
    """
    # NOTE: TourAPIClient의 get_festivals 함수는 이제 end_date 인자를 받도록 수정되어야 합니다.
    client = TourAPIClient()
    db: Session = SessionLocal()
    
    # 1년치 데이터 전체를 가져오기 위한 시작/종료일 설정
    start_date_range = "20250101" 
    end_date_range = "20251231"
    
    print("="*50)
    print("TourAPI 축제 데이터 동기화 시작")
    print(f"기간: {start_date_range} ~ {end_date_range}")
    print("="*50)
    
    current_page = 1
    total_count = 0
    total_processed_count = 0
    
    # DB에 이미 존재하는 contentid를 한 번에 가져와 메모리에 저장 (N+1 문제 방지)
    try:
        existing_content_ids = {str(id_) for id_ in db.execute(select(Festival.contentid)).scalars().all()}
    except Exception as e:
        print(f"DB 조회 오류: 테이블이 생성되지 않았거나 권한 문제입니다. 상세: {e}")
        db.close()
        return

    while True:
        # DB 연결이 끊겼을 경우를 대비하여 세션 재활용
        if not db.is_active:
            db = SessionLocal()
            
        try:
            # API 클라이언트를 통해 1페이지 분량의 축제 데이터를 비동기로 가져옴
            raw_items, api_total_count = await client.get_festivals(
                start_date=start_date_range,
                end_date=end_date_range,
                page_no=current_page,
                num_of_rows=100
            )
            if api_total_count == 0 and current_page == 1:
                print("API 응답에 totalCount가 0입니다. 동기화를 종료합니다.")
                break
            
            if current_page == 1:
                total_count = api_total_count
                print(f"총 {total_count}건의 데이터를 처리할 예정입니다.")

            if not raw_items:
                print(f"Page {current_page} - 더 이상 아이템이 없습니다. 동기화 완료.")
                break
            
            new_items_count = 0
            updated_items_count = 0
            
            # --- 3. 데이터 처리 및 저장 로직 (Upsert) ---
            for item in raw_items:
                content_id = item.get('contentid')
                
                # 데이터 유효성 검사 및 변환
                try:
                    data_to_save = {
                        'contentid': str(content_id),
                        'title': item.get('title'),
                        'location': item.get('addr1'), # DB 모델의 location 필드에 매핑
                        'event_start_date': item.get('eventstartdate'), 
                        'event_end_date': item.get('eventenddate'),
                        'mapx': float(item.get('mapx', 0.0)),
                        'mapy': float(item.get('mapy', 0.0)),
                        'image_url': item.get('firstimage', None),
                    }
                except Exception as e:
                    print(f"데이터 변환 오류: {e}, ContentID: {content_id}")
                    continue


                if content_id in existing_content_ids:
                    # UPDATE 로직 (이미 존재하는 데이터)
                    db.execute(
                        update(Festival)
                        .where(Festival.contentid == content_id)
                        .values(data_to_save)
                    )
                    updated_items_count += 1
                else:
                    # INSERT 로직 (새로운 데이터)
                    new_festival = Festival(**data_to_save)
                    db.add(new_festival)
                    existing_content_ids.add(content_id) 
                    new_items_count += 1
            
            db.commit() # 페이지 단위로 커밋
            total_processed_count += len(raw_items)
            
            print(f"Page {current_page} 처리 완료 | 삽입: {new_items_count}건, 업데이트: {updated_items_count}건")

            # 전체 아이템 수를 다 가져왔다면 루프 종료
            if total_processed_count >= total_count and total_count > 0:
                print(f"모든 데이터 ({total_processed_count}건) 수집 및 저장 완료.")
                break
            
            current_page += 1 # 다음 페이지로 이동

        except OperationalError as e:
            print(f"DB 연결 오류 (재시도 필요): RDS 인스턴스가 실행 중인지, IP가 열려있는지 확인하세요. 상세: {e}")
            break
        except Exception as e:
            # API 호출 오류 (JSON 파싱, 500 오류 등) 처리
            print(f"API 호출 또는 저장 중 알 수 없는 오류: {e}")
            break

    db.close()


if __name__ == "__main__":
    # 데이터베이스가 시작 상태인지 확인하고, 비동기 함수 실행
    
    # 1. DB 연결 테스트
    if test_db_connection():
        # 2. 비동기 함수 실행
        try:
            asyncio.run(run_db_sync())
        except Exception as e:
            print(f"스크립트 실행 중 치명적 오류: {e}")
    else:
        # DB 연결 테스트 실패 시 메시지는 test_db_connection 내부에서 출력됨
        pass