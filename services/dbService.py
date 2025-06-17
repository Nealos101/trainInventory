#THIS FILE HOLDS THE DB SERVICES OF THE WEB APP, THE MAIN COMPONENTS SUPPORTING DATA EXCHANGE

#MAIN FASTAPI IMPORTS
from fastapi import Depends, HTTPException

#NON  FASTAPI IMPORTS
from sqlmodel import Session, SQLModel, create_engine, select
from typing import Annotated, Optional

#IMPORT CLASSES
from schemas import dbSchema

#IMPORT FILES VARIABLE BRIDGES
vDbSchemas = dbSchema

#SQL MODEL
sqliteFileName = "database.db"
sqliteErl = f"sqlite:///{sqliteFileName}"

connectArgs = {"check_same_thread": False}
engine = create_engine(sqliteErl, connect_args=connectArgs)

def createDbAndTables():
    SQLModel.metadata.create_all(engine)

def getSession():
    with Session(engine) as session:
        yield session

def getOwnerByUsername(session: Session, username: str) -> Optional[vDbSchemas.owner]:
    statement = select(vDbSchemas.owner).where(vDbSchemas.owner.username == username)
    return session.exec(statement).first()

def deleteOwner(ownerId: int):
    with Session(engine) as session:
        owner = session.get(vDbSchemas.owner, ownerId)
        if not owner:
            raise HTTPException(status_code=404, detail="owner not found")
        session.delete(owner)
        session.commit()
        return {"ok": True}
    
SessionDep = Annotated[Session, Depends(getSession)]