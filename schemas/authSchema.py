#NON  FASTAPI IMPORTS
from pydantic import BaseModel

#AUTH CLASSES
class token(BaseModel):
    accessToken: str
    tokenType: str

class tokenData(BaseModel):
    username: str | None = None

class user(BaseModel):
    username: str
    email: str | None = None
    fullName: str | None = None
    disabled: bool | None = None

class userInDb(user):
    hashedPassword: str