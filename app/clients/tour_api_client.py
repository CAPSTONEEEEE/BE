import requests
from typing import List, Dict, Any
from app.core.config import get_settings

# 설정 파일에서 TourAPI 관련 설정을 가져옵니다.
settings = get_settings()

class TourAPIClient:
    """
    한국관광공사 TourAPI와의 통신을 담당하는 클라이언트 클래스
    """
    BASE_URL = "http://apis.data.go.kr/B551011/KorService"

    def __init__(self):
        self.service_key = settings.TOUR_API_KEY # .env 파일에 저장된 키를 가져옵니다.
        if not self.service_key:
            raise ValueError("TourAPI 서비스 키가 설정되지 않았습니다.")

    def _send_request(self, endpoint: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
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
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # 200 OK가 아니면 오류를 발생시킵니다.
            
            data = response.json()
            items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            return items if isinstance(items, list) else [items]

        except requests.exceptions.RequestException as e:
            print(f"API 요청 중 오류 발생: {e}")
            return []
        except Exception as e:
            print(f"데이터 처리 중 오류 발생: {e}")
            return []

    def get_festivals(self, start_date: str, num_of_rows: int = 100, page_no: int = 1) -> List[Dict[str, Any]]:
        """
        지정된 시작일 이후의 축제 정보를 가져옵니다.
        """
        endpoint = "searchFestival"
        params = {
            'eventStartDate': start_date,
            'numOfRows': num_of_rows,
            'pageNo': page_no
        }
        return self._send_request(endpoint, params)
    
    # 나중에 여행지 정보가 필요하면 아래와 같이 메소드를 추가하면 됩니다.
    # def get_travel_spots(self, ...):
    #     ...

# 다른 파일에서 쉽게 가져다 쓸 수 있도록 인스턴스를 만들어 둡니다.
tour_api_client = TourAPIClient()