from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
import datetime
from datetime import date
from app.models.festival_models import FestivalCreate, FestivalUpdate, FestivalOut

# --- TourAPI 연동을 위한 모듈 임포트 ---
import httpx
import os
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# --- TourAPI 설정 ---
TOUR_API_BASE_URL = "https://apis.data.go.kr/B551011"
TOUR_API_KEY = os.getenv("TOUR_API_KEY")

if not TOUR_API_KEY:
    print("="*50)
    print("[치명적 오류] TOUR_API_KEY 환경 변수가 설정되지 않았습니다!")
    print("프로젝트 루트에 .env 파일을 만들고 TOUR_API_KEY=...를 설정하세요.")
    print("="*50)

router = APIRouter(prefix="/festivals", tags=["festival"])


# ---------- List (전체 조회 + 필터링) ----------
@router.get("/", response_model=List[FestivalOut], summary="축제 목록 조회 (2025년 전체 + 현재 진행중 필터링)")
async def list_festivals_api(
    # page, size 파라미터 제거 -> 무조건 "전체" 목록을 반환
):
    print(f"--- [TourAPI] 2025년 전체 축제 데이터 수집 시작... ---")
    
    operation = "/KorService2/searchFestival2"
    today = datetime.date.today() # 2025-11-11
    
    total_items_from_api = []
    current_page = 1
    total_count = 0 # TourAPI가 알려줄 전체 아이템 수

    while True:
        params = {
            "serviceKey": TOUR_API_KEY,
            "MobileOS": "ETC",
            "MobileApp": "AppTest",   
            "pageNo": current_page,
            "numOfRows": 100, # 한 번에 100개씩 (최대)
            "_type": "json",
            "arrange": "A", # (A=제목순, C=수정일순)
            "eventStartDate": "20250101", # 1년치 전체 조회
            "eventEndDate": "20251231",
        }
        
        print(f" TourAPI {current_page}페이지 호출 중...")

        try:
            # 1. API 호출
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{TOUR_API_BASE_URL}{operation}",
                    params=params,
                    timeout=10.0
                )
            response.raise_for_status()
            data = response.json()
            
            body = data.get("response", {}).get("body", {})
            if not body:
                print(" TourAPI body가 비어있음. 중단.")
                break
                
            items = body.get("items", {}).get("item", [])
            if not items:
                print(f"{current_page}페이지에 아이템이 없음. 수집 중단.")
                break # 아이템이 더이상 없으면 중단
            
            if isinstance(items, dict):
                items = [items]
            
            # (첫 페이지만) total_count 저장
            if current_page == 1:
                total_count = body.get("totalCount", 0)
                print(f"TourAPI 확인: 2025년 전체 축제 수 {total_count}건")

            total_items_from_api.extend(items)
            
            # 2. 종료 조건: 현재 가져온 아이템 수가 total_count보다 크거나 같으면
            if len(total_items_from_api) >= total_count:
                print(f"TourAPI 전체 데이터 수집 완료 (총 {len(total_items_from_api)}건).")
                break
            
            current_page += 1 # 다음 페이지로

        except httpx.HTTPStatusError as e:
            print(f" TourAPI HTTP 오류 ({current_page}페이지): {e}")
            break # 오류 발생 시 중단
        except Exception as e:
            print(f" API 호출 중 알 수 없는 오류 ({current_page}페이지): {e}")
            break

    # 3.  수집된 전체 목록을 "오늘 날짜" 기준으로 필터링
    print(f"--- [FastAPI] {len(total_items_from_api)}건 데이터 필터링 시작 (기준일: {today}) ---")
    
    final_filtered_list = []
    
    for item in total_items_from_api:
        try:
            # 3-1. 날짜 문자열 가져오기
            start_date_str = item.get("eventstartdate")
            end_date_str = item.get("eventenddate")

            if not end_date_str or len(end_date_str) != 8:
                 continue
            if not start_date_str or len(start_date_str) != 8:
                 continue

            # 3-2. 문자열("YYYYMMDD") -> 'date' 객체로 수동 변환
            start_date_obj = datetime.datetime.strptime(start_date_str, "%Y%m%d").date()
            end_date_obj = datetime.datetime.strptime(end_date_str, "%Y%m%d").date()

            # 3-3. "오늘 날짜" 기준으로 "이미 끝난" 축제 필터링
            if end_date_obj < today:
                # print(f" 필터링됨 (종료): {item.get('title')} (종료일: {end_date_obj})")
                continue
            
            # 3-4. Pydantic 모델로 최종 변환
            final_filtered_list.append(FestivalOut(
                id=int(item.get("contentid")), 
                contentid=item.get("contentid"),
                title=item.get("title"),
                location=item.get("addr1", ""),
                event_start_date=start_date_obj,
                event_end_date=end_date_obj,
                mapx=float(item.get("mapx", 0.0)),
                mapy=float(item.get("mapy", 0.0)),
                image_url=item.get("firstimage", ""),
                created_at=datetime.datetime.now(), 
                updated_at=datetime.datetime.now(),
            ))
        except Exception as e:
            print(f"데이터 처리/변환 오류: {e}, 항목: {item.get('title')}")
    
    print(f"FastAPI 필터링 완료. (총 {len(total_items_from_api)}건 중 {len(final_filtered_list)}건 반환)")
    return final_filtered_list


# ---------- Retrieve (상세 조회) ----------
@router.get("/{festival_id}", response_model=Any, summary="축제 상세 조회 [TourAPI 연동]")
async def get_festival_api(
    festival_id: str,
):
    print(f"---  [TourAPI] 'KorService2/detailCommon2' (MobileApp='AppTest') 호출 시작... (ID: {festival_id}) ---")
    
    operation = "/KorService2/detailCommon2"
    params = {
        "serviceKey": TOUR_API_KEY,
        "MobileOS": "ETC",
        "MobileApp": "AppTest", 
        "_type": "json",
        "contentId": festival_id,
        "contentTypeId": 15,
        "defaultYN": "Y",
        "firstImageYN": "Y",
        "addrinfoYN": "Y",
        "mapinfoYN": "Y",
        "overviewYN": "Y",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TOUR_API_BASE_URL}{operation}",
                params=params,
                timeout=10.0
            )
        response.raise_for_status()
        data = response.json()
        body = data.get("response", {}).get("body", {})
        if not body or body.get("totalCount", 0) == 0:
             raise HTTPException(status_code=404, detail="[TourAPI] Festival not found")
        items = body.get("items", {}).get("item", [])
        item = items[0] if isinstance(items, list) else items
        
        transformed_item = {
            "id": int(item.get("contentid")),
            "contentid": item.get("contentid"),
            "title": item.get("title"),
            "location": item.get("addr1", ""),
            "event_start_date": item.get("eventstartdate", "날짜정보없음"), 
            "event_end_date": item.get("eventenddate", "날짜정보없음"),
            "mapx": float(item.get("mapx", 0.0)),
            "mapy": float(item.get("mapy", 0.0)),
            "image_url": item.get("firstimage", ""),
            "created_at": item.get("createdtime", datetime.datetime.now().isoformat()),
            "updated_at": item.get("modifiedtime", datetime.datetime.now().isoformat()),
            "overview": item.get("overview", "설명 정보가 없습니다.")
        }
        return transformed_item
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
             raise HTTPException(status_code=404, detail="[TourAPI] Festival not found")
        raise HTTPException(status_code=e.response.status_code, detail=f"TourAPI Error: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail="TourAPI 연결에 실패했습니다")
    except json.JSONDecodeError as e:
        print(f"TourAPI JSON 파싱 오류 ('detailCommon2'): {e}, 응답: {response.text}")
        raise HTTPException(status_code=500, detail="TourAPI 'detailCommon2' 응답을 파싱할 수 없습니다.")