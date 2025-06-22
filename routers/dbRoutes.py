#THIS FILE HOLDS THE DB ROUTERS OF THE WEB APP, THE MAIN BACKEND COMPONENTS SUPPORTING DATA EXCHANGE

#MAIN FASTAPI IMPORTS
from fastapi import Depends, HTTPException, Query, APIRouter, status

#NON  FASTAPI IMPORTS
from sqlmodel import Session, select

#IMPORT FILES
from core import security
from schemas import dbSchema, authSchema
from services import dbService, authService

#IMPORT FILES VARIABLE BRIDGES
vCoreSecurity = security
vDbSchema = dbSchema
vDbService = dbService
vAuthService = authService
vAuthSchema = authSchema

routerOwners = APIRouter(
    prefix="/owners",
    tags=["owners"]
)

routerUser = APIRouter(
    prefix="/user",
    tags=["user"]
)

@routerOwners.post("/", response_model=vDbSchema.ownerPublic)
def create_an_account(
    *,
    session: Session = Depends(vDbService.getSession),
    owner: vDbSchema.ownerCreate
):
    
    #ASSURES UNIQUE USERNAME
    existingOwner = session.query(vDbSchema.owner).filter_by(username=owner.username).first()
    if existingOwner:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    #CREATES THE NEW USER
    hashedPassword = vCoreSecurity.hashPassword(owner.password)
    extraData = {"hashedPassword": hashedPassword}
    dbOwner = vDbSchema.owner.model_validate(owner, update=extraData)
    session.add(dbOwner)
    session.commit()
    session.refresh(dbOwner)

    #APPLIES THE DEFAULT PERMISSIONS        
    vAuthService.assignDefaultPermissions(session, dbOwner.ownerId)
        
    return dbOwner

@routerOwners.get("/", response_model=list[vDbSchema.ownerPublic])
def fetch_all_accounts(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("admin")),
    session: Session = Depends(vDbService.getSession),
    offset: int = 0,
    # limit: int = Query(default=100, le=100)
):
    owners = session.exec(select(vDbSchema.owner).offset(offset))
    return owners

@routerOwners.get("/{ownerId}", response_model=vDbSchema.ownerPublic)
def fetch_an_account(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("readOnly", "ownerPerm", "admin")),
    session: Session = Depends(vDbService.getSession),
    ownerId: int,
    currentUser: vDbSchema.owner = Depends(vAuthService.getCurrentActiveUser)
):
    owner = session.get(vDbSchema.owner, ownerId)
    permissionOwner = vAuthService.isAdmin(session, currentUser.ownerId)

    if not owner:
        raise HTTPException(status_code=404, detail="owner not found")
    if not (owner.ownerId == currentUser.ownerId or permissionOwner):
        raise HTTPException(status_code=403, detail="Not authorized to access this owner")   
    
    return owner

@routerUser.get("/me")
def fetch_my_account(
    *,
    session: Session = Depends(vDbService.getSession),
    currentUser: vDbSchema.owner = Depends(vAuthService.getCurrentActiveUser)
):
    
    permissions = (
        session.query(vAuthSchema.Permissions)
        .filter_by(ownerId=currentUser.ownerId)
        .first()
    )

    if not permissions:
        raise HTTPException(status_code=404, detail="Permissions not found")

    return {
        "user": currentUser,
        "permissions": {
            "readOnly": permissions.readOnly,
            "ownerPerm": permissions.ownerPerm,
            "admin": permissions.admin}
    }

@routerOwners.patch("/admin/{ownerId}", response_model=vDbSchema.ownerPublic)
def update_an_account(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("admin")),
    session: Session = Depends(vDbService.getSession),
    ownerId: int,
    owner: vDbSchema.ownerUpdate
):
    with Session(vDbService.engine) as session:
       dbOwner = session.get(vDbSchema.owner, ownerId)
    if not dbOwner:
        raise HTTPException(status_code=404, detail="owner not found")

    ownerData = owner.model_dump(exclude_unset=True)
    extraData = {}
    if "password" in ownerData:
        password = ownerData["password"]
        hashedPassword = vCoreSecurity.hashPassword(password)
        extraData["hashedPassword"] = hashedPassword
    dbOwner.sqlmodel_update(ownerData, update=extraData)
    session.add(dbOwner)
    session.commit()
    session.refresh(dbOwner)
    return dbOwner

@routerOwners.get("/admin/{ownerId}")
def read_an_account(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("admin")),
    session: Session = Depends(vDbService.getSession),
    ownerId: int
):
    owner = session.get(vDbSchema.owner, ownerId)

    if not owner:
        raise HTTPException(status_code=404, detail="owner not found")
    
    permissions = (
        session.query(vAuthSchema.Permissions)
        .filter_by(ownerId=owner.ownerId)
        .first()
    )

    if not permissions:
        raise HTTPException(status_code=404, detail="Permissions not found")
    
    if permissions and permissions.admin:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to retreive an admin's full account dataset."
        )

    return {
        "user": owner,
        "permissions": {
            "readOnly": permissions.readOnly,
            "ownerPerm": permissions.ownerPerm,
            "admin": permissions.admin}
    }

@routerUser.patch("/me", response_model=vDbSchema.ownerPublic)
def update_my_account(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("readOnly", "ownerPerm", "admin")),
    session: Session = Depends(vDbService.getSession),
    owner: vDbSchema.ownerUpdate,
    currentUser: vDbSchema.owner = Depends(vAuthService.getCurrentActiveUser)
):
    ownerData = owner.model_dump(exclude_unset=True)
    #ASSURES UNIQUE USERNAME
    if "username" in ownerData:
        newUserName = ownerData["username"]
        if newUserName == currentUser.username:
            raise HTTPException(
                status_code=400,
                detail="This username is already your username"            
            )

    existingOwner = session.query(vDbSchema.owner).filter_by(username=owner.username).first()
    if existingOwner:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    with Session(vDbService.engine) as session:
       dbOwner = session.get(vDbSchema.owner, currentUser.ownerId)
    if not dbOwner:
        raise HTTPException(status_code=404, detail="owner not found")
    if dbOwner.ownerId != currentUser.ownerId:
        raise HTTPException(status_code=403, detail="Not authorized to access this owner")

    extraData = {}
    if "password" in ownerData:
        password = ownerData["password"]
        hashedPassword = vCoreSecurity.hashPassword(password)
        extraData["hashedPassword"] = hashedPassword
        
    dbOwner.sqlmodel_update(ownerData, update=extraData)
    session.add(dbOwner)
    session.commit()
    session.refresh(dbOwner)
    return dbOwner

@routerOwners.delete("/{ownerId}")
def delete_an_owner(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("admin")),
    session: Session = Depends(vDbService.getSession), ownerId: int,
    currentUser: vDbSchema.owner = Depends(vAuthService.getCurrentActiveUser)
):
    
    # TO SEE IF OWNER EXISTS (BACKEND PROTECTION LOGIC)
    owner = session.get(vDbSchema.owner, ownerId)
    if not owner:
        raise HTTPException(status_code=404, detail="owner not found")
    
    # TO STOP FELLOW ADMIN DELETE
    targetPermissions = (
        session.query(vAuthSchema.Permissions)
        .filter_by(ownerId=ownerId)
        .first()
    )

    if targetPermissions and targetPermissions.admin:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete a user with admin priviledges."
        )

    session.delete(owner)
    session.commit()
    return {"ok": True}

@routerUser.delete("/me")
def delete_my_account(
    *,
    session: Session = Depends(vDbService.getSession),
    currentUser: vDbSchema.owner = Depends(vAuthService.getCurrentActiveUser)
):
    owner = session.get(vDbSchema.owner, currentUser.ownerId)
    if not owner:
        raise HTTPException(status_code=404, detail="owner not found")
    
    session.delete(owner)
    session.commit()
    return {"ok": True}


@routerOwners.delete("/{ownerId}")
def delete_an_account(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("admin")),
    session: Session = Depends(vDbService.getSession), ownerId: int,
    currentUser: vDbSchema.owner = Depends(vAuthService.getCurrentActiveUser)
):
    
    # TO SEE IF OWNER EXISTS (BACKEND PROTECTION LOGIC)
    owner = session.get(vDbSchema.owner, ownerId)
    if not owner:
        raise HTTPException(status_code=404, detail="owner not found")
    
    # TO STOP FELLOW ADMIN DELETE
    targetPermissions = (
        session.query(vAuthSchema.Permissions)
        .filter_by(ownerId=ownerId)
        .first()
    )

    if targetPermissions and targetPermissions.admin:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete a user with admin priviledges."
        )

    session.delete(owner)
    session.commit()
    return {"ok": True}

@routerUser.delete("/perm/me")
def delete_my_permissions(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("ownerPerm", "admin")),
    session: Session = Depends(vDbService.getSession),
    currentUser: vDbSchema.owner = Depends(vAuthService.getCurrentActiveUser)
):
    targetPermissions = session.get(vAuthSchema.Permissions, currentUser.ownerId)
    if not targetPermissions:
        raise HTTPException(status_code=404, detail="owner not found")
    
    session.delete(targetPermissions)
    session.commit()
    return {"ok": True}