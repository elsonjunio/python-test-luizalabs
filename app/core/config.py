from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    ENV: str = 'dev'

    AUTHORIZATION_URL: str = ''
    TOKEN_URL: str = ''
    JWKS_URI: str = ''
    REDIS_HOST: str = ''
    REDIS_PORT: int = 0
    LOGLEVE: str = 'INFO'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
