from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict
from app.schemas import FavoriteRequest, FavoriteListResponse, FavoriteItemOut
from app.models.favorite_models import UserFavorite 
from app.models.festival_models import Festival 
from app.models.market_models import MarketProduct 
from app.models.recommend_models import RecommendTourInfo

class FavoriteService:
    """찜 기능 관련 비즈니스 로직을 처리하는 서비스 클래스"""

    def __init__(self, db: Session):
        # FastAPI의 DI를 통해 주입받은 DB 세션을 저장합니다.
        self.db = db

    # ----------------------------------------------------
    # 1. 찜 상태 토글 (POST /favorites)
    # ----------------------------------------------------
    def toggle_favorite(self, user_id: int, request: FavoriteRequest):
        """
        찜 항목을 추가 또는 제거합니다 (토글).
        item_id는 DB의 VARCHAR 타입에 맞추어 String으로 처리합니다.
        """
        item_id_str = str(request.item_id)
        
        # 1. 항목 유효성 검사 (실제 항목이 존재하는지 확인)
        item = self._check_item_exists(request.item_type, item_id_str)
        if not item:
            # 404를 반환해야 하지만, 서비스에서는 예외를 발생시키고 라우터에서 처리합니다.
            raise ValueError(f"해당 ID({item_id_str})의 {request.item_type} 항목을 찾을 수 없습니다.")

        # 2. 기존 찜 기록 조회
        favorite = self.db.query(UserFavorite).filter(
            and_(
                UserFavorite.user_id == user_id,
                UserFavorite.item_type == request.item_type,
                UserFavorite.item_id == item_id_str,
            )
        ).first()

        if favorite:
            # 찜 해제
            self.db.delete(favorite)
            self.db.commit()
            return {"message": "Favorite removed successfully.", "is_added": False}
        else:
            # 찜 추가
            new_favorite = UserFavorite(
                user_id=user_id,
                item_type=request.item_type,
                item_id=item_id_str,
            )
            self.db.add(new_favorite)
            try:	
                self.db.add(new_favorite)	
                self.db.commit()	
                return {"message": "Favorite added successfully.", "is_added": True}	
            except Exception:	
                self.db.rollback() # 예외 발생 시 롤백	
                raise

    # ----------------------------------------------------
    # 2. 전체 찜 목록 조회 (GET /favorites)
    # ----------------------------------------------------
    def get_user_favorites(self, user_id: int) -> FavoriteListResponse:
        """
        사용자의 모든 찜 항목을 조회하고 Pydantic 스키마에 맞게 상세 정보를 반환합니다.
        """
        # 1. 사용자의 찜 목록 ID/타입 전체 조회
        favorites = self.db.query(UserFavorite).filter(UserFavorite.user_id == user_id).all()
        
        # 2. 타입별로 ID 목록 분리 
        favs_by_type = {
            "FESTIVAL": [f.item_id for f in favorites if f.item_type == "FESTIVAL"],
            "PRODUCT": [f.item_id for f in favorites if f.item_type == "PRODUCT"],
            "SPOT": [f.item_id for f in favorites if f.item_type == "SPOT"],
        }
        
        # 3. 각 항목 상세 정보 조회 
        # 축제 
        festival_ids_str = [i for i in favs_by_type["FESTIVAL"]]
        festivals_data = self.db.query(Festival).filter(Festival.contentid.in_(festival_ids_str)).all()
        
        # 마켓 상품
        product_ids_int = [int(i) for i in favs_by_type["PRODUCT"] if str(i).isdigit()]
        products_data = self.db.query(MarketProduct).filter(MarketProduct.id.in_(product_ids_int)).all()
        
        # 추천 여행지
        spot_ids_str = [i for i in favs_by_type["SPOT"]]
        spots_data = self.db.query(RecommendTourInfo).filter(RecommendTourInfo.contentid.in_(spot_ids_str)).all()

        # 4. Pydantic 응답 스키마에 맞게 데이터 변환 및 그룹화
        response_data = {
            "festivals": [self._map_to_favorite_item_out(item, "FESTIVAL") for item in festivals_data],
            "products": [self._map_to_favorite_item_out(item, "PRODUCT") for item in products_data],
            "spots": [self._map_to_favorite_item_out(item, "SPOT") for item in spots_data],
        }
        
        # 5. FavoriteListResponse 스키마에 맞게 반환
        return FavoriteListResponse(**response_data)
        
    # ----------------------------------------------------
    # 헬퍼 함수 
    # ----------------------------------------------------
    
    def _check_item_exists(self, item_type: str, item_id: str):
        try:
            item_id_int = int(item_id)
        except ValueError:
            return None # 숫자가 아닌 경우 유효하지 않은 ID로 처리
        """DB에서 해당 항목이 실제로 존재하는지 확인합니다."""
        if item_type == "FESTIVAL":
            return self.db.query(Festival).filter(Festival.contentid == item_id).first()
        elif item_type == "PRODUCT":
            return self.db.query(MarketProduct).filter(MarketProduct.id == int(item_id)).first()
        elif item_type == "SPOT":
            return self.db.query(RecommendTourInfo).filter(RecommendTourInfo.contentid == item_id).first()
        return None

    def _map_to_favorite_item_out(self, item: object, item_type: str) -> Dict:
        """DB 모델 객체를 찜 응답 스키마에 맞게 매핑"""

        title = getattr(item, 'title', '제목 없음')
        item_id_to_return = None
        
        image_url = None
        if item_type == "FESTIVAL":
             image_url = getattr(item, 'image_url', None)
             item_id_to_return = getattr(item, 'contentid', getattr(item, 'id'))
        elif item_type == "PRODUCT":
             image_url = None
             item_id_to_return = getattr(item, 'id')
        elif item_type == "SPOT":
             image_url = getattr(item, 'firstimage', None)
             item_id_to_return = getattr(item, 'contentid')
        else:
            return None
        
        return {
            "item_id": str(item_id_to_return),
            "item_type": item_type,
            "title": title,
            "image_url": image_url
        }