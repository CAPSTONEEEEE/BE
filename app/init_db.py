# app/init_db.py
from app.database import engine
from app.models.common_models import Base

# 모델 등록 보장을 위해 명시 import
import app.models.market_models      # noqa: F401
import app.models.festival_models    # noqa: F401
import app.models.recommend_models   # noqa: F401

def init():
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created.")

if __name__ == "__main__":
    init()

