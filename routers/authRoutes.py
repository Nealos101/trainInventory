#THIS FILE SUPPORTS THE AUTH ROUTES OF THE WEB APP, THE MAIN COMPONENTS SUPPORTING AUTHENTIFICATION

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
from schemas import authSchema
from services import authService, dbService

#IMPORT FILES VARIABLE BRIDGES
vAuthSchema = authSchema
vAuthService = authService
vDbService = dbService

#IMPORT CONFIGS
from core.config import settings


#DEFINE ROUTERS
routerToken = APIRouter(
    prefix="/token",
    tags=["token"]
)

routerMe = APIRouter(
    prefix="/users/me",
    tags=["usersMe"]
)

routerMeItems = APIRouter(
    prefix="/users/me/items",
    tags=["usersMeItems"]
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
        data={"sub": owner.ownerId}, expiresDelta=accessTokenExpires)
    return vAuthSchema.token(accessToken=accessToken, tokenType="bearer")

@routerMe.get("/", response_model=vAuthSchema.user)
async def readUsersMe(
    current_user: Annotated[vAuthSchema.user, Depends(vAuthService.getCurrentActiveUser)]):
    return current_user

@routerMeItems.get("/")
async def readOwnItems(
    current_user: Annotated[vAuthSchema.user, Depends(vAuthService.getCurrentActiveUser)]):
    return [{"itemId": "Foo", "owner": current_user.username}]