import requests
import httpx
from typing import List, Dict, Any, Tuple
from app.core.config import get_settings

# 설정 파일에서 TourAPI 관련 설정을 가져옵니다.
settings = get_settings()

class TourAPIClient:
    """
    한국관광공사 TourAPI와의 통신을 담당하는 클라이언트 클래스
    """
    BASE_URL = "https://apis.data.go.kr/B551011/KorService2"

    def __init__(self):
        self.service_key = settings.TOUR_API_KEY # .env 파일에 저장된 키를 가져옵니다.
        if not self.service_key:
            raise ValueError("TourAPI 서비스 키가 설정되지 않았습니다.")

    async def _send_request(self, endpoint: str, params: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], int]:
        """
        API 요청을 보내고 결과를 파싱하는 내부 메소드
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # 모든 요청에 공통으로 필요한 파라미터를 추가합니다.
        common_params = {
            'serviceKey': self.service_key,
            'MobileOS': 'ETC',
            'MobileApp': 'SosoHaeng',
            '_type': 'json'
        }
        params.update(common_params)

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, params=params)
            
            data = response.json()
            response_body = data.get('response', {}).get('body', {})
            items = response_body.get('items', {}).get('item', [])
            total_count = response_body.get('totalCount', 0) # totalCount를 가져옵니다.
            
            # items가 딕셔너리(단일 항목)인 경우 리스트로 변환합니다.
            processed_items = items if isinstance(items, list) else [items]
            
            # 성공적으로 두 개의 값을 튜플로 반환합니다.
            return processed_items, total_count
        
        except requests.exceptions.RequestException as e:
            print(f"API 요청 중 오류 발생: {e}")
            return []
        except Exception as e:
            print(f"데이터 처리 중 오류 발생: {e}")
            return []

    async def get_festivals(self, start_date: str, end_date: str, num_of_rows: int = 100, page_no: int = 1) -> List[Dict[str, Any]]:
        """
        지정된 시작일 이후의 축제 정보를 가져옵니다.
        """
        endpoint = "searchFestival2"
        params = {
            'eventStartDate': start_date,
            'eventEndDate': end_date,
            'numOfRows': num_of_rows,
            'pageNo': page_no,
            'arrange': 'C', #수정일순 저장
        }
        return await self._send_request(endpoint, params)
    
    # app/clients/tour_api_client.py 파일 내

    # tour_api_client.py 파일 내 get_recommends 함수 수정

    async def get_recommends(self, area_code: str = None, content_type_id: str = None, page_no: int = 1, num_of_rows: int = 100) -> Tuple[List[Dict[str, Any]], int]:
        """
        TourAPI에서 지역 기반 관광 정보(areaBasedList2)를 비동기로 가져옵니다.
        """
        
        # 지역 기반 관광정보 조회 API 엔드포인트
        endpoint = "areaBasedList2" 
        
        # API 요청에 필요한 파라미터 정의
        params = {
            'pageNo': page_no,
            'numOfRows': num_of_rows,
            'arrange': 'D',       # D=생성일순으로 정렬
            'contentTypeId': content_type_id, # 👈 이 매개변수를 사용하도록 추가/수정
            'areaCode': area_code, 
        }
        
        # 🌟 핵심: None인 파라미터는 요청에서 제거하여 검색 조건을 완화합니다.
        # 이렇게 해야 areaCode와 contentTypeId에 None을 넘겨도 API가 전국/전체 타입을 검색합니다.
        if params.get('areaCode') is None:
            del params['areaCode']
        
        if params.get('contentTypeId') is None:
            del params['contentTypeId']
            
        # _send_request 함수가 (raw_items, api_total_count) 튜플을 반환하도록 처리
        return await self._send_request(endpoint, params)
        
    # TourAPIClient 클래스의 정의 부분이라고 가정



# 다른 파일에서 쉽게 가져다 쓸 수 있도록 인스턴스를 만들어 둡니다.
tour_api_client = TourAPIClient()
