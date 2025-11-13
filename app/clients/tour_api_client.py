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
    # 나중에 여행지 정보가 필요하면 아래와 같이 메소드를 추가하면 됩니다.
    # def get_travel_spots(self, ...):
    #     ...

# 다른 파일에서 쉽게 가져다 쓸 수 있도록 인스턴스를 만들어 둡니다.
tour_api_client = TourAPIClient()
