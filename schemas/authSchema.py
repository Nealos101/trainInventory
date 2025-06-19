#THIS FILE HOLDS THE MODEL INFORMATION SUPPORTING THE AUTH FUNCTIONS OF THE WEB APP, THE MAIN COMPONENTS SUPPORTING AUTHENTIFICATION

#NON  FASTAPI IMPORTS
from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship

#IMPORT CLASSES
if TYPE_CHECKING:
    from schemas.dbSchema import owner

#TOKEN CLASSES
class token(BaseModel):
    access_token: str
    token_type: str

class tokenData(BaseModel):
    userId: str | None = None


#AUTH (PERMISSIONS) DB CLASSES
class PermissionsBase(SQLModel):
    readOnly: bool
    ownerPerm: bool
    admin: bool

    ownerId: Optional[int] = Field(default=None, foreign_key="owner.ownerId")

class Permissions(PermissionsBase, table=True):
    permId: int | None = Field(default=None, primary_key=True)

    owner: Optional["owner"] = Relationship(back_populates="Permissions")

class PermissionsCreate(PermissionsBase):
    pass

class PermissionsPublic(PermissionsBase):
    permID: int

class PermissionsUpdate(SQLModel):
    readOnly: Optional[bool] = None
    ownerPerm: Optional[bool] = None
    admin: Optional[bool] = None
    ownerId: Optional[int] = None
