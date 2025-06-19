#THIS FILE HOLDS THE DB ROUTERS OF THE WEB APP, THE MAIN BACKEND COMPONENTS SUPPORTING DATA EXCHANGE

#MAIN FASTAPI IMPORTS
from fastapi import Depends, HTTPException, Query, APIRouter, status

#NON  FASTAPI IMPORTS
from sqlmodel import Session, select

#IMPORT FILES
from core import security
from schemas import dbSchema
from services import dbService, authService

#IMPORT FILES VARIABLE BRIDGES
vCoreSecurity = security
vDbSchemas = dbSchema
vDbService = dbService
vAuthService = authService

routerOwners = APIRouter(
    prefix="/owners",
    tags=["owners"]
)

@routerOwners.post("/", response_model=vDbSchemas.ownerPublic)
def createOwner(
    *,
    session: Session = Depends(vDbService.getSession),
    owner: vDbSchemas.ownerCreate
):
    
    #ASSURES UNIQUE USERNAME
    existingOwner = session.query(vDbSchemas.owner).filter_by(username=owner.username).first()
    if existingOwner:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    #CREATES THE NEW USER
    hashedPassword = vCoreSecurity.hashPassword(owner.password)
    extraData = {"hashedPassword": hashedPassword}
    dbOwner = vDbSchemas.owner.model_validate(owner, update=extraData)
    session.add(dbOwner)
    session.commit()
    session.refresh(dbOwner)

    #APPLIES THE DEFAULT PERMISSIONS        
    vAuthService.assignDefaultPermissions(session, dbOwner.ownerId)
        
    return dbOwner

@routerOwners.get("/", response_model=list[vDbSchemas.ownerPublic])
def readOwners(
    *,
    ownerPerm: vDbSchemas.owner = Depends(vAuthService.requireAnyPermission("admin")),
    session: Session = Depends(vDbService.getSession),
    offset: int = 0,
    limit: int = Query(default=100, le=100)
):
    owners = session.exec(select(vDbSchemas.owner).offset(offset).limit(limit)).all()
    return owners

@routerOwners.get("/{ownerId}", response_model=vDbSchemas.ownerPublic)
def readOwner(
    *,
    ownerPerm: vDbSchemas.owner = Depends(vAuthService.requireAnyPermission("readOnly", "ownerPerm", "admin")),
    session: Session = Depends(vDbService.getSession),
    ownerId: int,
    currentUser: vDbSchemas.owner = Depends(vAuthService.getCurrentActiveUser)
):
    owner = session.get(vDbSchemas.owner, ownerId)
    if not owner:
        raise HTTPException(status_code=404, detail="owner not found")
    if owner.ownerId != currentUser.ownerId:
        raise HTTPException(status_code=403, detail="Not authorized to access this owner")   
    
    return owner

@routerOwners.patch("/{ownerId}", response_model=vDbSchemas.ownerPublic)
def update_owner(
    *,
    ownerPerm: vDbSchemas.owner = Depends(vAuthService.requireAnyPermission("ownerPerm", "admin")),
    session: Session = Depends(vDbService.getSession),
    ownerId: int,
    owner: vDbSchemas.ownerUpdate,
    currentUser: vDbSchemas.owner = Depends(vAuthService.getCurrentActiveUser)
):
    with Session(vDbService.engine) as session:
       dbOwner = session.get(vDbSchemas.owner, ownerId)
    if not dbOwner:
        raise HTTPException(status_code=404, detail="owner not found")
    if dbOwner.ownerId != currentUser.ownerId:
        raise HTTPException(status_code=403, detail="Not authorized to access this owner")
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

@routerOwners.delete("/{ownerId}")
def deleteOwner(
    *,
    ownerPerm: vDbSchemas.owner = Depends(vAuthService.requireAnyPermission("ownerPerm", "admin")),
    session: Session = Depends(vDbService.getSession), ownerId: int,
    currentUser: vDbSchemas.owner = Depends(vAuthService.getCurrentActiveUser)
):
    owner = session.get(vDbSchemas.owner, ownerId)
    if not owner:
        raise HTTPException(status_code=404, detail="owner not found")
    if owner.ownerId != currentUser.ownerId:
        raise HTTPException(status_code=403, detail="Not authorized to access this owner")
    session.delete(owner)
    session.commit()
    return {"ok": True}