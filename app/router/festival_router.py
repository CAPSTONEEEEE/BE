# app/router/festival_router.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy.orm import Session # (DB 연결 제거)
# from app.db.database import get_db # (DB 연결 제거)
import datetime
from datetime import date
from app.models.festival_models import FestivalCreate, FestivalUpdate, FestivalOut
# from app.services.festival_services import ( # (DB 서비스 제거)
#     list_festivals,
#     get_festival_by_id,
#     create_festival,
#     update_festival,
#     delete_festival,
# )

# --- 데모용 목데이터 로드를 위한 모듈 임포트 ---
import json
import os
# ---

router = APIRouter(prefix="/festivals", tags=["festival"])

# --- 데모용 목데이터 파일 경로 ---
# 이 파일(festival_router.py)은 app/router/ 안에 있으므로, 
# 상위 폴더(BE)로 두 번 올라가서 mock_data/mock_festivals.json을 찾아야 합니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK_DATA_PATH = os.path.join(BASE_DIR, "../mock_data/mock_festivals.json")

def load_mock_data():
    """목데이터 JSON 파일을 읽어오는 헬퍼 함수"""
    try:
        with open(MOCK_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 목 데이터 로드 실패: {e}")
        # 실패 시 비상용 데이터 반환
        return [
            {
                "contentid": "99999",
                "title": "[데모] 목데이터 로드 실패",
                "location": "BE/mock_data/mock_festivals.json 경로 확인 필요",
                "event_start_date": "20250101",
                "event_end_date": "20250101",
                "mapx": 0,
                "mapy": 0,
                "image_url": "",
                # FestivalOut 스키마에 맞는 다른 필드들도 채워주세요. (id 등)
                "id": 1 
            }
        ]

# ---------- List (핵심 수정) ----------
@router.get("/", summary="축제 목록 조회 [데모 모드]")
def list_festivals_api(
    # --- DB 관련 파라미터 모두 제거 ---
    # q: str | None = Query(None, description="축제명/장소 검색어"),
    # region_id: int | None = Query(None, description="지역 ID"),
    # start_date: date | None = None,
    # end_date: date | None = None,
    # page: int = Query(1, ge=1),
    # size: int = Query(20, ge=1, le=100),
    # order_by: str = Query("start", pattern="^(start|recent|title)$"),
    # db: Session = Depends(get_db),
):
    print("--- ⚠️  [데모 모드] DB가 아닌 목데이터를 반환합니다. (GET /festivals/) ---")
    # DB 서비스 호출 대신 목데이터 로드
    # items, _ = list_festivals(db, q, region_id, start_date, end_date, page, size, order_by)
    
    items = load_mock_data()
    
    # *** 중요 ***
    # mock_festivals.json의 데이터가 FestivalOut 스키마와 다를 수 있습니다.
    # 예를 들어, JSON에는 'id'가 없는데 스키마에는 'id'가 필요할 수 있습니다.
    # 이 경우, 데이터를 변환해야 합니다.
    # (간단한 데모를 위해 JSON과 스키마가 일치한다고 가정합니다)
    return items

# ---------- Retrieve (수정) ----------
@router.get("/{festival_id}", summary="축제 상세 조회 [데모 모드]")
def get_festival_api(
    festival_id: str, 
    # db: Session = Depends(get_db) # (DB 연결 제거)
):
    print(f"--- ⚠️  [데모 모드] 목데이터에서 ID {festival_id}를 찾습니다. ---")
    # festival = get_festival_by_id(db, festival_id)
    
    all_festivals = load_mock_data()
    
    # contentid가 문자열일 수 있으므로 str()로 비교 (혹은 festival_id를 str로 받기)
    festival = next((f for f in all_festivals if str(f.get('contentid')) == str(festival_id)), None)
    
    if not festival:
        raise HTTPException(status_code=404, detail="[데모] Festival not found")
    
    # 1. 'id' 필드 추가 (임시 값)
    #    (contentid의 해시값이나 다른 고유한 int를 사용할 수 있지만, 데모용으론 999도 충분)
    festival['id'] = 999  # 또는 hash(festival['contentid']) % 100000
    
    # 2. 'created_at', 'updated_at' 필드 추가 (임시 값)
    now = datetime.datetime.now()
    festival['created_at'] = festival.get('created_at', now)
    festival['updated_at'] = festival.get('updated_at', now)
    return festival

# ---------- Create (데모용 임시) ----------
@router.post("/", response_model=FestivalOut, status_code=status.HTTP_201_CREATED, summary="축제 생성 [데모 - 저장 안 됨]")
def create_festival_api(
    payload: FestivalCreate, 
    # db: Session = Depends(get_db) # (DB 연결 제거)
):
    print("--- ⚠️  [데모 모드] 축제 생성 요청 수신 (실제 저장 안 됨) ---")
    # return create_festival(db, payload)
    
    # 받은 데이터를 스키마에 맞게 '척'만 해서 반환
    demo_response = payload.model_dump()
    demo_response["id"] = 999 # 임시 ID
    demo_response["contentid"] = "DEMO" + str(demo_response.get("title", "T"))[:3]
    return demo_response

# ---------- Update (데모용 임시) ----------
@router.put("/{festival_id}", response_model=FestivalOut, summary="축제 수정 [데모 - 저장 안 됨]")
def update_festival_api(
    festival_id: str, 
    payload: FestivalUpdate, 
    # db: Session = Depends(get_db) # (DB 연결 제거)
):
    print(f"--- ⚠️  [데모 모드] 축제 {festival_id} 수정 요청 (실제 저장 안 됨) ---")
    # festival = update_festival(db, festival_id, payload)
    # if not festival:
    #     raise HTTPException(status_code=404, detail="Festival not found")

    # 그냥 받은 데이터에 ID만 붙여서 반환
    demo_response = payload.model_dump(exclude_unset=True) # 변경된 부분만
    demo_response["id"] = 999
    demo_response["title"] = demo_response.get("title", "[데모] 수정됨")
    
    now = datetime.datetime.now()
    demo_response['created_at'] = now
    demo_response['updated_at'] = now
    return demo_response

# ---------- Delete (데모용 임시) ----------
@router.delete("/{festival_id}", status_code=status.HTTP_204_NO_CONTENT, summary="축제 삭제 [데모 - 삭제 안 됨]")
def delete_festival_api(
    festival_id: str, 
    # db: Session = Depends(get_db) # (DB 연결 제거)
):
    print(f"--- ⚠️  [데모 모드] 축제 {festival_id} 삭제 요청 (실제 삭제 안 됨) ---")
    # success = delete_festival(db, festival_id)
    # if not success:
    #     raise HTTPException(status_code=404, detail="Festival not found")
    return # 204 응답은 바디가 없음
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from datetime import date
from app.models.festival_models import FestivalCreate, FestivalUpdate, FestivalOut
from app.services.festival_services import (
    list_festivals,
    get_festival_by_id,
    create_festival,
    update_festival,
    delete_festival,
)

router = APIRouter(prefix="/festivals", tags=["festival"])

# ---------- List ----------
@router.get("/", response_model=List[FestivalOut], summary="축제 목록 조회")
def list_festivals_api(
    q: str | None = Query(None, description="축제명/장소 검색어"),
    region_id: int | None = Query(None, description="지역 ID"),
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    order_by: str = Query("start", pattern="^(start|recent|title)$"),
    db: Session = Depends(get_db),
):
    items, _ = list_festivals(db, q, region_id, start_date, end_date, page, size, order_by)
    return items

# ---------- Retrieve ----------
@router.get("/{festival_id}", response_model=FestivalOut, summary="축제 상세 조회")
def get_festival_api(festival_id: int, db: Session = Depends(get_db)):
    festival = get_festival_by_id(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    return festival

# ---------- Create ----------
@router.post("/", response_model=FestivalOut, status_code=status.HTTP_201_CREATED, summary="축제 생성")
def create_festival_api(payload: FestivalCreate, db: Session = Depends(get_db)):
    return create_festival(db, payload)

# ---------- Update ----------
@router.put("/{festival_id}", response_model=FestivalOut, summary="축제 수정")
def update_festival_api(festival_id: int, payload: FestivalUpdate, db: Session = Depends(get_db)):
    festival = update_festival(db, festival_id, payload)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    return festival

# ---------- Delete ----------
@router.delete("/{festival_id}", status_code=status.HTTP_204_NO_CONTENT, summary="축제 삭제")
def delete_festival_api(festival_id: int, db: Session = Depends(get_db)):
    success = delete_festival(db, festival_id)
    if not success:
        raise HTTPException(status_code=404, detail="Festival not found")
"""