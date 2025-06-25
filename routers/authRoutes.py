#THIS FILE HOLDS THE AUTH ROUTERS OF THE WEB APP, THE MAIN COMPONENTS SUPPORTING AUTHENTIFICATION INCLUDING PERMISSIONS (WHICH SITS IN DB)

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
async def auth_a_token(
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
async def refresh_Token(request: Request):
    refreshToken = request.cookies.get("refreshToken")
    if not refreshToken:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    
    payload = vAuthService.verifyToken(refreshToken)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    newAccessToken = vAuthService.createAccessToken({"sub": payload["sub"]})
    return {"access_token": newAccessToken, "token_type": "bearer"}

#PERMISSIONS ROUTES
@routerPerm.post("/", include_in_schema=False)
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

@routerPerm.patch("/{ownerId}")
def update_permissions(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("admin")),
    session: Session = Depends(vDbService.getSession),
    vPermission: vAuthSchema.PermissionsUpdate,
    ownerId: int
):
    
    # ENSURES OWNER EXISTS
    dbOwner = session.get(vDbSchema.owner, ownerId)
    if not dbOwner:
        raise HTTPException(status_code=404, detail="owner not found")

    #ENSURES THE PERMISSIONS ROW EXISTS FOR THE OWNER
    dbPerm = session.query(authSchema.Permissions).filter_by(ownerId=ownerId).first()
    if not dbPerm:
        raise HTTPException(status_code=404, detail="Existing permissions not found")
    
    #ENSURES THERE ISN'T AN ADMIN DEMOTION
    if dbPerm.admin and not vPermission.admin:
        raise HTTPException(status_code=403, detail="Cannot remove admin rights from another admin")
    
    #PERFORMS THE UPDATE
    updateData = vPermission.model_dump(exclude_unset=True)
    for key, value in updateData.items():
        setattr(dbPerm, key, value)

    session.commit()
    session.refresh(dbPerm)

    return dbPerm

@routerPerm.delete("/{ownerId}")
def delete_Permissions(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("admin")),
    session: Session = Depends(vDbService.getSession),
    ownerId: int
):
   
    # TO STOP FELLOW ADMIN DELETE
    targetPermissions = (
        session.query(vAuthSchema.Permissions)
        .filter_by(ownerId=ownerId)
        .first()
    )
    if not targetPermissions:
        raise HTTPException(
            status_code=404,
            detail="permissions for this user not found"
        )

    if targetPermissions.admin:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete a user's permissions if they hold admin priviledges."
        )

    session.delete(targetPermissions)
    session.commit()
    return {"ok": True}