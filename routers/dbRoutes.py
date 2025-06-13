#THIS FILE SUPPORTS THE DB ROUTES OF THE WEB APP, THE MAIN BACKEND COMPONENTS SUPPORTING DATA EXCHANGE

#MAIN FASTAPI IMPORTS
from fastapi import Depends, HTTPException, Query, APIRouter

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

# routerOwnersowner = APIRouter(
#     prefix="/owners",
#     tags=["ownersowner"]
# )

@routerOwners.post("/", response_model=vDbSchemas.ownerPublic)
def createOwner(*, session: Session = Depends(vDbService.getSession), owner: vDbSchemas.ownerCreate):
    hashedPassword = vCoreSecurity.hashPassword(owner.password)
    with Session(vDbService.engine) as session:
        extraData = {"hashedPassword": hashedPassword}
        dbOwner = vDbSchemas.owner.model_validate(owner, update=extraData)
        session.add(dbOwner)
        session.commit()
        session.refresh(dbOwner)
        return dbOwner

@routerOwners.get("/", response_model=list[vDbSchemas.ownerPublic])
def readOwners(
    *,
    session: Session = Depends(vDbService.getSession),
    offset: int = 0,limit: int = Query(default=100, le=100)
):
    with Session(vDbService.engine) as session:
        owners = session.exec(select(vDbSchemas.owner).offset(offset).limit(limit)).all()
        return owners

@routerOwners.get("/{ownerId}", response_model=vDbSchemas.ownerPublic)
def readOwner(
    *,
    session: Session = Depends(vDbService.getSession),
    ownerId: int,
    currentUser: vDbSchemas.owner = Depends(vAuthService.getCurrentUser)
):
    owner = session.get(vDbSchemas.owner, ownerId)
    if not owner:
        raise HTTPException(status_code=404, detail="owner not found")
    
    if owner.id != currentUser.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this owner")   
    
    return owner

@routerOwners.patch("/{ownerId}", response_model=vDbSchemas.ownerPublic)
def update_owner(*, session: Session = Depends(vDbService.getSession), ownerId: int, owner: vDbSchemas.ownerUpdate):
    with Session(vDbService.engine) as session:
        dbOwner = session.get(vDbSchemas.owner, ownerId)
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

@routerOwners.delete("/{ownerId}")
def deleteOwner(*, session: Session = Depends(vDbService.getSession), ownerId: int):
    owner = session.get(vDbSchemas.owner, ownerId)
    if not owner:
        raise HTTPException(status_code=404, detail="owner not found")
    session.delete(owner)
    session.commit()
    return {"ok": True}