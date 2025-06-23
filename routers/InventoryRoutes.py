#THIS FILE HOLDS THE INVENTORY DB ROUTERS OF THE WEB APP, THE MAIN BACKEND COMPONENTS SUPPORTING THE CORE FUNCTIONS OF THE WEB APP

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

#DEFINE ROUTERS
routerInv = APIRouter(
    prefix="/inventory",
    tags=["inventory"]
)

@routerInv.get("/all", response_model=list[vDbSchema.InventoryPublic])
def fetch_all_inventory(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("admin")),
    session: Session = Depends(vDbService.getSession),
    offset: int = 0,
    # limit: int = Query(default=100, le=100)
):
    inventory = session.exec(select(vDbSchema.Inventory).offset(offset))
    return inventory

@routerInv.get("/{ownerId}", response_model=vDbSchema.InventoryPublic)
def fetch_an_inventory(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("readOnly", "ownerPerm", "admin")),
    session: Session = Depends(vDbService.getSession),
    ownerId: int,
    currentUser: vDbSchema.owner = Depends(vAuthService.getCurrentActiveUser)
):
    inventory = session.get(vDbSchema.Inventory, ownerId)
    permissionOwner = vAuthService.isAdmin(session, currentUser.ownerId)

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    if not (inventory.ownerId == currentUser.ownerId or permissionOwner):
        raise HTTPException(status_code=403, detail="Not authorized to access this Inventory")   
    
    return inventory

@routerInv.get("/{ownerId}/{invId}", response_model=vDbSchema.InventoryPublic)
def fetch_an_inventory_record(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("readOnly", "ownerPerm", "admin")),
    session: Session = Depends(vDbService.getSession),
    ownerId: int,
    invId: int,
    currentUser: vDbSchema.owner = Depends(vAuthService.getCurrentActiveUser)
):
    inventory = session.get(vDbSchema.Inventory, invId)
    permissionOwner = vAuthService.isAdmin(session, currentUser.ownerId)

    #IF RECORD NOT FOUND
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    
    #IF FOUND, BUT INV.OWNER IS NOT DEFINED OWNERID
    if not (inventory.ownerId == ownerId):
        raise HTTPException(status_code=403, detail="Given owner not authorized to access this Inventory") 
    
    #IF NOT ADMIN, AND INV.OWNER IS NOT THE CURRENT OWNER
    if not (inventory.ownerId == currentUser.ownerId or permissionOwner):
        raise HTTPException(status_code=403, detail="Not authorized to access this Inventory")   
    
    return inventory

@routerInv.post("/", response_model=vDbSchema.InventoryPublic)
def create_an_inventory_record(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("ownerPerm", "admin")),
    session: Session = Depends(vDbService.getSession),
    inventory: vDbSchema.InventoryCreate,
    currentUser: vDbSchema.owner = Depends(vAuthService.getCurrentActiveUser)
):
    
    #ASSURES UNIQUE CLIENTID
    existingInv = (
        session.query(vDbSchema.Inventory)
        .filter_by(clientId=inventory.clientId, ownerId=inventory.ownerId)
        .first()
    )

    # PULL PERMISSIONS
    targetPermissions = (
        session.query(vAuthSchema.Permissions)
        .filter_by(ownerId=inventory.ownerId)
        .first()
    )

    #STOPS AN ADMIN FROM TRYING TO ADD A RECORD TO A FELLOW ADMIN'S INVENTORY
    if (targetPermissions and targetPermissions.admin and inventory.ownerId != currentUser.ownerId):
        raise HTTPException(
            status_code=403,
            detail="You cannot add a record to this Inventory."
        )

    if existingInv:
        raise HTTPException(
            status_code=400,
            detail="Your chosen clientId already exists, please choose another."
        )
    
    #CREATES THE INVENTORY
    dbInv = vDbSchema.Inventory.model_validate(inventory)
    session.add(dbInv)
    session.commit()
    session.refresh(dbInv)
    return vDbSchema.InventoryPublic.model_validate(dbInv)

@routerInv.patch("/{ownerId}/{invId}", response_model=vDbSchema.InventoryPublic)
def update_an_inventory_record(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("ownerPerm", "admin")),
    session: Session = Depends(vDbService.getSession),
    ownerId: int,
    invId: int,
    inventory: vDbSchema.InventoryUpdate,
    currentUser: vDbSchema.owner = Depends(vAuthService.getCurrentActiveUser)
):

    #FETCH THE RECORD
    dbInv = session.get(vDbSchema.Inventory, invId)
    if not dbInv:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found"
        )

    #ENSURE PROVIDED RECORD BELONGS TO THE CORRECT OWNER
    if dbInv.ownerId != ownerId:
        raise HTTPException(
            status_code=400,
            detail="Inventory record does not belong to this owner"
        )
    
    #ENSURES ONLY THE OWNER OF THE RECORD OR AN ADMIN IS MAKING THE UPDATE
    isAdmin = vAuthService.isAdmin(session, currentUser.ownerId)
    if not (dbInv.ownerId == currentUser.ownerId or isAdmin):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this Inventory record"
        )

    invData = inventory.model_dump(exclude_unset=True)

    #CLIENTID UNIQUENESS CHECK
    if "clientId" in invData:
        newClientId = invData["clientId"]
        if newClientId != dbInv.clientId:
            existingInv = (
                session.query(vDbSchema.Inventory)
                .filter_by(clientId=newClientId, ownerId=dbInv.ownerId)
                .first()
            )
            if existingInv:
                raise HTTPException(
                    status_code=400,
                    detail="This clientId already exists in this owner's Inventory."
                )
            
    # PULL PERMISSIONS
    targetPermissions = (
        session.query(vAuthSchema.Permissions)
        .filter_by(ownerId=ownerId)
        .first()
    )

    #STOPS AN ADMIN FROM TRYING TO UPDATE A FELLOW ADMIN'S INVENTORY RECORDS
    if (targetPermissions and targetPermissions.admin and ownerId != currentUser.ownerId):
        raise HTTPException(
            status_code=403,
            detail="You cannot delete a fellow Admin's Inventory."
        )

    dbInv.sqlmodel_update(invData)
    session.add(dbInv)
    session.commit()
    session.refresh(dbInv)
    return vDbSchema.InventoryPublic.model_validate(dbInv)

@routerInv.delete("/{ownerId}/{invId}")
def delete_an_owner(
    *,
    ownerPerm: vDbSchema.owner = Depends(vAuthService.requireAnyPermission("ownerPerm", "admin")),
    session: Session = Depends(vDbService.getSession),
    currentUser: vDbSchema.owner = Depends(vAuthService.getCurrentActiveUser),
    ownerId: int,
    invId: int,
):
    
    #FETCH THE RECORD / ENSURE IT EXISTS
    dbInv = session.get(vDbSchema.Inventory, invId)
    if not dbInv:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found"
        )
    
    #ENSURE PROVIDED RECORD BELONGS TO THE CORRECT OWNER
    if dbInv.ownerId != ownerId:
        raise HTTPException(
            status_code=400,
            detail="Inventory record does not belong to this owner"
        )
    
    #ENSURES ONLY THE OWNER OF THE RECORD OR AN ADMIN IS MAKING THE UPDATE
    isAdmin = vAuthService.isAdmin(session, currentUser.ownerId)
    if not (dbInv.ownerId == currentUser.ownerId or isAdmin):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this Inventory record"
        )

    # TO SEE IF OWNER EXISTS (BACKEND PROTECTION LOGIC)
    owner = session.get(vDbSchema.owner, ownerId)
    if not owner:
        raise HTTPException(status_code=404, detail="owner not found")
    
    # PULL PERMISSIONS
    targetPermissions = (
        session.query(vAuthSchema.Permissions)
        .filter_by(ownerId=ownerId)
        .first()
    )

    #STOPS AN ADMIN FROM TRYING TO DELETE A FELLOW ADMIN'S INVENTORY RECORDS
    if (targetPermissions and targetPermissions.admin and ownerId != currentUser.ownerId):
        raise HTTPException(
            status_code=403,
            detail="You cannot delete a fellow Admin's Inventory."
        )

    session.delete(dbInv)
    session.commit()
    return {
        "ok": True,
        "Message": f"Inventory with clientId {dbInv.clientId} was successfully deleted"
    }