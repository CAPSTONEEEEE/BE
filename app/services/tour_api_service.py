import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("sNi2tlEh0+B9o0hig8eIQmwPR+tcLeZ46hmkrPWWk2vXNhWFvSpDizqGZy1CtB1tRV4Krz53LU3OHgKvtyihHg==")
BASE_URL = "http://api.visitkorea.or.kr/openapi/service/rest/KorService1"

# 공통 정보 조회 API 엔드포인트
COMMON_INFO_URL = f"{BASE_URL}/areaBasedList1"

def get_api_params(page_no: int, content_type_id: str):
    """API 호출에 필요한 기본 파라미터를 반환합니다."""
    # API 키가 없으면 에러 발생
    if not API_KEY:
        raise ValueError("TOUR_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
    return {
        "serviceKey": API_KEY,
        "numOfRows": 100,  # 한 페이지에 가져올 데이터 수
        "pageNo": page_no,
        "MobileOS": "ETC",
        "MobileApp": "sosoheng",
        "arrange": "A", # 제목순 정렬
        "contentTypeId": content_type_id,
        "_type": "json"  # JSON 형식으로 응답받기
    }
