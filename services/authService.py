#THIS FILE HOLDS THE AUTH SERVICES OF THE WEB APP, THE MAIN COMPONENTS SUPPORTING AUTHENTIFICATION

#CORE IMPORTS
from fastapi import Depends, HTTPException, status

#NON  FASTAPI IMPORTS
import jwt
from sqlmodel import Session, select
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

#OAUTH2 LOGIN SERVICES
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

#JWT TOKEN SERVICES (INCLUDING EXPIRABLE ACCESS AND EXTENDED REFRESH TOKEN)
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

#MAIN FUNCTIONS TO RETRIEVE CURRENT USER FROM FRONT END
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

#PERMISSIONS RETREIVER TO SUPPORT PERMISSIONS CHECKS
def requireAnyPermission(*perms: str):
    def permissionChecker(
        ownerPerm: vDbSchemas.owner = Depends(getCurrentActiveUser),
        session: Session = Depends(vDbService.getSession)
):
        permission = session.exec(
            select(vDbSchemas.Permissions).where(vDbSchemas.Permissions.ownerId == ownerPerm.ownerId)
        ).first()

        if not permission:
            raise HTTPException(status_code=403, detail="No permissions assigned to this user!")
        
        if not any(getattr(permission, perm, False) for perm in perms):
            raise HTTPException(
                status_code=403,
                detail=f"Requires one of the following permissions: {', '.join(perms)}"
            )
        
        return ownerPerm
    
    return permissionChecker

#ADD A DEFAULT LIST OF PERMISSIONS
def assignDefaultPermissions(session: Session, ownerId: int):
    existing = session.query(vAuthSchema.Permissions).filter_by(ownerId=ownerId).first()
    if existing:
        return
    
    defaultPerms = vAuthSchema.Permissions(
        ownerId=ownerId,
        readOnly=False,
        ownerPerm=True,
        admin=False
    )
    session.add(defaultPerms)
    session.commit()