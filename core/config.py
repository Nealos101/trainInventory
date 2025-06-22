#TRAININVENTORY CONFIG

#NON  FASTAPI IMPORTS
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secretKey: str
    algorithm: str
    accessTokenExpireMinutes: int
    refreshTokenExpireDays: int

    class Config:
        env_file = ".env"

settings = Settings()