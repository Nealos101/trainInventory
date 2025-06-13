#NON  FASTAPI IMPORTS
from pydantic_settings import BaseSettings

class settings(BaseSettings):
    secretKey: str
    algorithm: str
    accessTokenExpireHours: int

    class Config:
        env_file = ".env"

settings = settings()