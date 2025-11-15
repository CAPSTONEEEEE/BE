# app/services/tour_api_service.py (기존 파일 수정/추가)

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.clients.tour_api_client import TourAPIClient 
from app.models.tour_models import TourInfo # ORM 모델

# 1. API 클라이언트 초기화 (서비스 파일 상단에 정의)
try:
    tour_api_client = TourAPIClient()
except ValueError as e:
    # API 키가 설정되지 않은 경우 처리
    print(f"TourAPIClient 초기화 오류: {e}")
    tour_api_client = None


async def save_attraction_data(db: AsyncSession, data_list: List[Dict[str, Any]]):
    """
    정제된 관광지 데이터 리스트를 DB에 저장(업데이트/삽입)합니다.
    """
    if not data_list or tour_api_client is None:
        return

    for item_data in data_list:
        content_id = item_data.get('contentid')
        if not content_id:
            continue
            
        # 💡 API 필드명을 DB 모델 속성명과 매핑 및 타입 변환
        data_to_save = {
            'contentid': content_id,
            'contenttypeid': item_data.get('contenttypeid'),
            'title': item_data.get('title'),
            'addr1': item_data.get('addr1'),
            'addr2': item_data.get('addr2'),
            'zipcode': item_data.get('zipcode'),
            'areacode': item_data.get('areacode'),
            'sigungucode': item_data.get('sigungucode'),
            'cat1': item_data.get('cat1'),
            'cat2': item_data.get('cat2'),
            'cat3': item_data.get('cat3'),
            'tel': item_data.get('tel'),
            'firstimage': item_data.get('firstimage'),
            'firstimage2': item_data.get('firstimage2'),
            
            # 타입 변환 (문자열 -> float/int)
            # None 또는 빈 문자열이 올 경우 처리
            'mapx': float(item_data['mapx']) if item_data.get('mapx') else None,
            'mapy': float(item_data['mapy']) if item_data.get('mapy') else None,
            'mlevel': int(item_data['mlevel']) if item_data.get('mlevel') else None,
            
            'createdtime': item_data.get('createdtime'),
            'modifiedtime': item_data.get('modifiedtime'),
        }

        # 1. DB에 이미 존재하는지 확인 (Primary Key로 조회)
        existing_attraction = await db.get(TourInfo, content_id)
        
        if existing_attraction:
            # 2. 존재하면 업데이트 (수정 시간이 다를 경우에만 업데이트하는 로직 추가 가능)
            for key, value in data_to_save.items():
                setattr(existing_attraction, key, value)
        else:
            # 3. 존재하지 않으면 새로 추가
            try:
                new_attraction = TourInfo(**data_to_save)
                db.add(new_attraction)
            except Exception as e:
                print(f"DB 객체 생성 오류 (ID: {content_id}): {e}")
                
    # 반복문이 끝난 후 한 번에 커밋
    await db.commit()


async def load_initial_attraction_data(db: AsyncSession):
    """
    TourAPI에서 모든 관광지 데이터를 가져와 DB에 적재하는 메인 함수입니다.
    이 함수는 서버 시작 시 또는 관리자 엔드포인트를 통해 호출되어야 합니다.
    """
    if tour_api_client is None:
        print("Tour API 클라이언트가 초기화되지 않아 데이터 적재를 건너뜁니다.")
        return

    print("--- 관광지 데이터 초기 적재 시작 (Area Based List) ---")
    
    # 예시: 전국 관광지(contentTypeId=12)만 가져오도록 설정
    content_type_tour = '12' 
    num_of_rows_per_page = 100
    current_page = 1
    
    # 1. 전체 데이터 개수 파악
    total_count = tour_api_client.get_total_count(area_code='', content_type_id=content_type_tour)
    if total_count == 0:
        print("Tour API에서 가져올 데이터가 0건입니다. (API 키나 설정 확인 필요)")
        return

    print(f"총 {total_count}개의 관광지 데이터를 가져올 예정입니다.")

    # 2. 페이지를 반복하며 데이터 적재
    while (current_page - 1) * num_of_rows_per_page < total_count:
        try:
            # API 호출
            data_items = tour_api_client.get_area_based_list(
                area_code='', # 전국(지역코드 생략)
                content_type_id=content_type_tour,
                num_of_rows=num_of_rows_per_page,
                page_no=current_page
            )

            if not data_items:
                break
            
            # DB 저장
            await save_attraction_data(db, data_items)
            
            print(f"페이지 {current_page} (총 {len(data_items)}건) 저장 완료.")
            
            current_page += 1

        except HTTPException as e:
            print(f"API 호출 또는 DB 저장 중 오류 발생: {e.detail}")
            break
        except Exception as e:
            print(f"예상치 못한 오류 발생: {e}")
            break
            
    print("--- 관광지 데이터 초기 적재 완료 ---")