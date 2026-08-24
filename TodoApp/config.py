from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL:str
    SECRET_KEY: str
    DEBUG: bool = False
    PORT:int =8000
    ALGORITHM :str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    model_config = SettingsConfigDict(env_file=".env",env_file_encoding="utf-8")

@lru_cache
def get_settings():
    return Settings()