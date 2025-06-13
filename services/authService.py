#THIS FILE SUPPORTS THE AUTH ROUTES OF THE WEB APP, THE MAIN COMPONENTS SUPPORTING AUTHENTIFICATION

#CORE IMPORTS
from fastapi import Depends, HTTPException, status

#NON  FASTAPI IMPORTS
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated, Optional
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer

#IMPORT CLASSES
from schemas import authSchema, dbSchema
from services import dbService
from core import security
from core.config import settings

#IMPORT FILES VARIABLE BRIDGES
vAuthSchema = authSchema
vSecurity = security
vSetting = settings
vDbSchemas = dbSchema
vDbService = dbService

#FAKE DB
fakeUsersDb = {
    "johndoe": {
        "username": "johndoe",
        "fullName": "John Doe",
        "email": "johndoe@example.com",
        "hashedPassword": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

#OAUTH2 HANDLING FUNCTIONS
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="token")

@staticmethod
def verifyPassword(plainPassword, hashedPassword):
    return vSecurity.pwdContext.verify(plainPassword, hashedPassword)

def getPasswordHash(password):
    return vSecurity.pwdContext.hash(password)

def getUser(db, username: str):
    if username in db:
        userDict = db[username]
        return vAuthSchema.userInDb(**userDict)

def authenticateOwner(
        db,
        username: str,
        password: str
) -> Optional[vDbSchemas.owner]:
    owner = vDbService.getOwnerByUsername(db, username)
    if not owner:
        return None
    if not verifyPassword(password, owner.hashedPassword):
        return None
    return owner

def createAccessToken(data: dict, expires_delta: timedelta | None = None):
    toEncode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    toEncode.update({"exp": expire})
    encodedJwt = jwt.encode(toEncode, vSetting.secretKey, algorithm=vSetting.algorithm)
    return encodedJwt

async def getCurrentUser(token: Annotated[str, Depends(oauth2Scheme)]):
    credentialsException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.secretKey, algorithms=[settings.algorithm])
        vUsername: str = payload.get("sub")
        if vUsername is None:
            raise credentialsException
        vTokenData = vAuthSchema.tokenData(username=vUsername)
    except InvalidTokenError:
        raise credentialsException
    user = vDbService.getOwnerByUsername(username=vTokenData.username)
    if user is None:
        raise credentialsException
    return user

async def getCurrentActiveUser(
    currentUser: Annotated[vAuthSchema.user, Depends(getCurrentUser)]):
    if currentUser.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return currentUser