#THIS FILE HOLDS THE DB MODELS OF THE WEB APP, THE MAIN BACKEND COMPONENTS SUPPORTING DATA EXCHANGE

#NON  FASTAPI IMPORTS
from sqlmodel import Field, SQLModel

#AUTH CLASSES
class ownerBase(SQLModel):
    name: str = Field(index=True)
    username: str
    age: int | None = Field(default=None, index=True)
    disabled: bool | None = None

class owner(ownerBase, table=True):
    ownerId: int | None = Field(default=None, primary_key=True)
    hashedPassword: str = Field()

class ownerCreate(ownerBase):
    password: str

class ownerPublic(ownerBase):
    ownerId: int

class ownerUpdate(ownerBase):
    name: str | None = None
    age: int | None = None
    username: str | None = None
    password: str | None = None