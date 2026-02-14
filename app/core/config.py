from typing import Optional
from fastapi_mail import ConnectionConfig
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    MONGO_URL: str
    MONGO_DB: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ALGORITHM : str
    SECRET_KEY : str
    REFRESH_SECRET_KEY : str
    
    class Config:
        env_file = ".env"
        extra = "allow"
        
@lru_cache
def get_settings():
    return Settings()

def clear_settings_cache():
    get_settings.cache_clear()
    
    
conf = ConnectionConfig(
    MAIL_USERNAME="prabhamuruganantham06@gmail.com",
    MAIL_PASSWORD="ptyt oscx cego mthh",
    MAIL_FROM="prabhamuruganantham06@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,    
    MAIL_SSL_TLS=False,    
    USE_CREDENTIALS=True
)
