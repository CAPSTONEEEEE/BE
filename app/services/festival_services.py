from typing import List, Optional
from festival_models import Festival

# Mock 데이터
mock_festivals = [
    Festival(id=1, name="봄꽃 축제", location="서울", date="2025-04-10", description="벚꽃과 함께하는 봄맞이 축제"),
    Festival(id=2, name="여름 해변 음악제", location="부산", date="2025-07-20", description="바닷가에서 열리는 음악 페스티벌"),
    Festival(id=3, name="가을 단풍 축제", location="강원도", date="2025-10-15", description="단풍과 함께하는 가을 축제"),
]

def get_all_festivals() -> List[Festival]:
    return mock_festivals

def get_festival_by_id(festival_id: int) -> Optional[Festival]:
    for festival in mock_festivals:
        if festival.id == festival_id:
            return festival
    return None
