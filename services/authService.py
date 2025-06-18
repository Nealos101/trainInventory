#THIS FILE HOLDS THE AUTH SERVICES OF THE WEB APP, THE MAIN COMPONENTS SUPPORTING AUTHENTIFICATION

#CORE IMPORTS
from fastapi import Depends, HTTPException, status

#NON  FASTAPI IMPORTS
import jwt
from sqlmodel import Session
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

#OAUTH2 HANDLING FUNCTIONS
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="/token")

@staticmethod
def verifyPassword(plainPassword, hashedPassword):
    return vSecurity.pwdContext.verify(plainPassword, hashedPassword)

def getPasswordHash(password):
    return vSecurity.pwdContext.hash(password)

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

def createAccessToken(data: dict, accessExpiresDelta: timedelta | None = None):
    toEncode = data.copy()
    if accessExpiresDelta:
        expire = datetime.now(timezone.utc) + accessExpiresDelta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=vSetting.accessTokenExpireMinutes)
    toEncode.update({"exp": expire})
    encodedJwt = jwt.encode(toEncode, vSetting.secretKey, algorithm=vSetting.algorithm)
    return encodedJwt

def createRefreshToken(data: dict):
    refreshExpiresDelta = datetime.now(timezone.utc) + timedelta(days=vSetting.refreshTokenExpireDays)
    toEncode = data.copy()
    toEncode.update({"exp": refreshExpiresDelta})
    return jwt.encode(toEncode, vSetting.secretKey, algorithm=vSetting.algorithm)

def verifyToken(token: str):
    payload = jwt.decode(token, vSetting.secretKey, algorithms=vSetting.algorithm)
    return payload

async def getCurrentUser(
        token: Annotated[str, Depends(oauth2Scheme)],
        session: Session = Depends(vDbService.getSession)
):
    credentialsException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, vSetting.secretKey, algorithms=[vSetting.algorithm])
        userId: str = payload.get("sub")
        if userId is None:
            raise credentialsException
        tokenData = vAuthSchema.tokenData(userId=userId)
    except InvalidTokenError:
        raise credentialsException
    user = session.query(vDbSchemas.owner).filter_by(ownerId=tokenData.userId).first()
    if user is None:
        raise credentialsException
    return user

async def getCurrentActiveUser(
    currentUser: Annotated[vDbSchemas.owner, Depends(getCurrentUser)]):
    if currentUser.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return currentUser