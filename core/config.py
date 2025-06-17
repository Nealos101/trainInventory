#TRAININVENTORY CONFIG

#NON  FASTAPI IMPORTS
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secretKey: str
    algorithm: str
    accessTokenExpireHours: int

    class Config:
        env_file = ".env"

settings = Settings()