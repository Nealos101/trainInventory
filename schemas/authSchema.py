#THIS FILE HOLDS THE MODEL INFORMATION SUPPORTING THE AUTH FUNCTIONS OF THE WEB APP, THE MAIN COMPONENTS SUPPORTING AUTHENTIFICATION

#NON  FASTAPI IMPORTS
from pydantic import BaseModel

#AUTH CLASSES
class token(BaseModel):
    access_token: str
    token_type: str

class tokenData(BaseModel):
    userId: str | None = None