#중요 API키들 모아두는 파일
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 기존 변수들
    TOUR_API_KEY: str
    OPENAI_API_KEY: str
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    # .env 파일에 추가된 변수들도 여기에 선언해주어야 합니다.
    environment: str
    database_url: str
    cors_origins: str
    openai_model: str
    
    model_config = SettingsConfigDict(env_file=".env", extra='ignore') # 👈 extra='ignore' 추가

@lru_cache
def get_settings():
    """
    Settings 객체를 생성하고 캐싱하여 재사용합니다.
    이렇게 하면 설정 파일을 매번 읽지 않아 효율적입니다.
    """
    return Settings()