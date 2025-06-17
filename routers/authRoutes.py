#THIS FILE HOLDS THE AUTH ROUTERS OF THE WEB APP, THE MAIN COMPONENTS SUPPORTING AUTHENTIFICATION

#CORE IMPORTS
from fastapi import Depends, HTTPException, status
from fastapi import APIRouter

#SUBCORE IMPORTS
from fastapi.security import OAuth2PasswordRequestForm

#NON  FASTAPI IMPORTS
from typing import Annotated
from datetime import timedelta
from sqlmodel import Session


#IMPORT FILES
from schemas import authSchema, dbSchema
from services import authService, dbService

#IMPORT FILES VARIABLE BRIDGES
vAuthSchema = authSchema
vAuthService = authService
vDbService = dbService
vDbSchema = dbSchema

#IMPORT CONFIGS
from core.config import settings


#DEFINE ROUTERS
routerToken = APIRouter(
    prefix="/token",
    tags=["token"]
)

#AUTH ROUTERS
@routerToken.post("/")
async def loginForAccessToken(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(vDbService.getSession)
) -> vAuthSchema.token:
    owner = vAuthService.authenticateOwner(session, form_data.username, form_data.password)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"})
    accessTokenExpires = timedelta(hours=settings.accessTokenExpireHours)
    accessToken = vAuthService.createAccessToken(
        data={"sub": str(owner.ownerId)}, expiresDelta=accessTokenExpires)
    return vAuthSchema.token(access_token=accessToken, token_type="bearer")