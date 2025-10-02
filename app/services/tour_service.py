# app/services/tour_service.py

import os
import requests
from dotenv import load_dotenv
from urllib.parse import unquote # <--- 이 줄이 있는지 확인

class TourService:
    def __init__(self):
        load_dotenv()
        self.service_key = unquote(os.getenv("TOUR_API_KEY"))
        self.base_url = os.getenv("TOUR_API_BASE_URL")
        self.default_params = {
            "serviceKey": self.service_key,
            "MobileOS": "ETC",
            "MobileApp": "YourApp",
            "_type": "json"
        }
    
    # 이 함수가 반드시 TourService 클래스 안에 있어야 합니다.
    def get_area_codes(self, page_no: int = 1, num_of_rows: int = 10):
        """
        전국 시/도 지역 코드 목록을 가져옵니다.
        """
        params = {
            "pageNo": page_no,
            "numOfRows": num_of_rows
        }
        
        full_params = {**self.default_params, **params}
        
        try:
            response = requests.get(self.base_url, params=full_params)
            response.raise_for_status()
            
            response_data = response.json()
            items = response_data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            
            if isinstance(items, dict):
                items = [items]
            
            return items
            
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to TourAPI: {e}")
            return None