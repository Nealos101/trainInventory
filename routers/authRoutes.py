#THIS FILE HOLDS THE AUTH ROUTERS OF THE WEB APP, THE MAIN COMPONENTS SUPPORTING AUTHENTIFICATION

#CORE IMPORTS
from fastapi import (
    Depends,
    HTTPException,
    status,
    APIRouter,
    Request)
from fastapi.responses import JSONResponse

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

routerRefreshToken = APIRouter(
    prefix="/refreshToken",
    tags=["refreshToken"]
)

routerPerm = APIRouter(
    prefix="/perm",
    tags=["permissions"]
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
    accessTokenExpires = timedelta(minutes=settings.accessTokenExpireMinutes)
    # refreshTokenExpires = timedelta(days=settings.refreshTokenExpireDays)
    accessToken = vAuthService.createAccessToken(
        data={"sub": str(owner.ownerId)}, accessExpiresDelta=accessTokenExpires
    )
    refreshToken = vAuthService.createRefreshToken(
        data={"sub": str(owner.ownerId)}
        # , refreshExpiresDelta=refreshTokenExpires
    )
    response = JSONResponse(content={
    "access_token": accessToken,
    "token_type": "bearer"
    })
    response.set_cookie(
        key="refreshToken",
        value=refreshToken,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/refreshToken"
    )
    return response
 

@routerRefreshToken.post("/")
async def refreshToken(request: Request):
    refreshToken = request.cookies.get("refreshToken")
    if not refreshToken:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    
    payload = vAuthService.verifyToken(refreshToken)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    newAccessToken = vAuthService.createAccessToken({"sub": payload["sub"]})
    return {"access_token": newAccessToken, "token_type": "bearer"}

#PERMISSIONS ROUTES
@routerPerm.post("/")
def create_permissions(
    *,
    session: Session = Depends(vDbService.getSession),
    vPermission: vAuthSchema.PermissionsCreate
):
    vDbPerm = vAuthSchema.Permissions.model_validate(vPermission)
    session.add(vDbPerm)
    session.commit()
    session.refresh(vDbPerm)
    return vDbPerm