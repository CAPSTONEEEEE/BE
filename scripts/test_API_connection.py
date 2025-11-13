import os
import sys
import asyncio
from dotenv import load_dotenv
import httpx
from typing import List, Dict, Any

# PYTHONPATH에 현재 BE 폴더를 추가하여 app.* 모듈을 인식하도록 함
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# .env 파일 로드 (경로 재확인)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    os.chdir(project_root)
except FileNotFoundError:
    pass
load_dotenv()

# app/clients/tour_api_client.py 의존성을 피하고 핵심 변수만 로드
TOUR_API_BASE_URL = "https://apis.data.go.kr/B551011"
TOUR_API_KEY = os.getenv("TOUR_API_KEY")

if not TOUR_API_KEY:
    print("❌ [오류] TOUR_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
    sys.exit(1)


async def test_tour_api_connection():
    """TourAPI에 요청을 보내 응답 상태를 확인하는 테스트 함수"""
    
    # searchFestival2 엔드포인트 사용 (가장 많은 데이터를 요구하는 기능으로 테스트)
    operation = "/KorService2/searchFestival2"
    
    # 최소한의 필수 파라미터와 짧은 기간(11월)을 사용
    params = {
        "serviceKey": TOUR_API_KEY,
        "MobileOS": "ETC",
        "MobileApp": "TestApp",
        "pageNo": 1,
        "numOfRows": 1, # 1건만 요청
        "_type": "json",
        "eventStartDate": "20251101",
        "eventEndDate": "20251231",
    }
    
    url = f"{TOUR_API_BASE_URL}{operation}"

    print("="*50)
    print("🚀 TourAPI 연결 및 키 유효성 테스트 시작...")
    print(f"URL: {url}")
    print("="*50)

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            
        # 1. HTTP 상태 코드 확인 (401, 403, 500 등 오류 확인)
        response.raise_for_status() 
        
        # 2. JSON 파싱 및 데이터 확인
        data = response.json()
        total_count = data.get('response', {}).get('body', {}).get('totalCount', 0)
        
        if total_count > 0:
            print(f"🎉 API 연결 성공! 응답 코드: {response.status_code} OK")
            print(f"   [유효성 확인] 11~12월 축제 총 {total_count}건 조회됨.")
            return True
        else:
            print(f"⚠️ API 연결은 성공했으나, 데이터가 조회되지 않음. 응답 코드: {response.status_code} OK")
            print("   (파라미터 문제일 수 있음. 키 자체는 유효할 가능성이 높음)")
            return True

    except httpx.HTTPStatusError as e:
        print(f"❌ API 연결 실패: HTTP 상태 오류 {e.response.status_code}")
        print(f"   오류 상세: {e.response.text}")
        print("   (원인: 키 유효성, 권한, 또는 API 서버 내부 오류일 수 있습니다.)")
        return False
    except httpx.RequestError as e:
        print(f"❌ API 연결 실패: 네트워크 요청 오류")
        print(f"   오류 상세: {e}")
        return False
    except Exception as e:
        print(f"❌ 데이터 처리 중 알 수 없는 오류: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_tour_api_connection())