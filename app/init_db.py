# app/init_db.py
from app.database import engine
from app.models import Base  # __init__.py에서 모든 모델 import되게 해둠

def init():
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created.")

if __name__ == "__main__":
    init()

