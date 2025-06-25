#THIS FILE HOLDS THE DB MODELS OF THE WEB APP, THE MAIN BACKEND COMPONENTS SUPPORTING DATA EXCHANGE

#NON  FASTAPI IMPORTS
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import date
from enum import Enum

#IMPORT CLASSES
from schemas.authSchema import Permissions
from core.constants import commonMaterials

#DB OWNER CLASSESES
class ownerBase(SQLModel):
    name: str = Field(index=True)
    username: str
    age: int | None = Field(default=None, index=True)
    disabled: bool | None = None

class owner(ownerBase, table=True):
    ownerId: int | None = Field(default=None, primary_key=True)
    hashedPassword: str = Field()

    Permissions: list["Permissions"] = Relationship(back_populates="owner")
    Inventory: list["Inventory"] = Relationship(back_populates="owner")

class ownerCreate(ownerBase):
    password: str

class ownerPublic(ownerBase):
    ownerId: int

class ownerUpdate(ownerBase):
    name: str | None = None
    age: int | None = None
    username: str | None = None
    password: str | None = None

#ENUM OBJECTS (DEFINED LISTS FOR DB)
#1. INVENTORY MATERIAL TYPES
class wheelType(str, Enum):
    notPres = commonMaterials["notPres"]
    notReq = commonMaterials["notRequired"]
    customJob = commonMaterials["customJob"]
    removed = commonMaterials["removed"]
    metal = commonMaterials["metal"]
    plastic = commonMaterials["plastic"]

#2.INVENTORY COUPLER TYPES
class couplerType(str, Enum):
    notPres = commonMaterials["notPres"]
    notReq = commonMaterials["notRequired"]
    customJob = commonMaterials["customJob"]
    removed = commonMaterials["removed"]
    hornH = "Hornhook"
    sprungMagKn = "Sprung Knuckle"
    ezKn = "Plastic Flash Knuckle"
    solidKn = "Solid Knuckle"
    damagedKn = "Damaged"
    missingKn = "Missing"

#3. POWER CLASS
class powerClass(str, Enum):
    notPres = commonMaterials["notPres"]
    notReq = commonMaterials["notRequired"]
    customJob = commonMaterials["customJob"]
    removed = commonMaterials["removed"]
    batt = "Battery"
    aC = "AC"
    dC = "DC"
    dccReady = "DCC Ready"
    dccSilent = "DCC Silent"
    dccSound = "DCC Sound"

#4. STOCK TYPE CLASS
class stockClass(str, Enum):
    loco = "Locomotive"
    wagon = "Wagon"
    coach = "Coach"
    auto = "Automobile"

#DB INVENTORY TABLE CLASSES
class InventoryBase(SQLModel):

    #REQUIRED FIELDS
    clientId: str = Field(index=True)
    stockType: stockClass
    stockName: str
    stockRoadNumber: str = Field(index=True)

    #OPTIONAL FIELDS
    stockBrand: Optional[str] = None
    stockRailroad: Optional[str] = None
    stockLivery: Optional[str] = None
    stockPower: Optional[powerClass] = None
    purchaseCost: Optional[float] = None
    purchaseDate: Optional[date] = None
    stockWheelType: Optional[wheelType] = None
    stockCouplerType: Optional[couplerType] = None
    stockComments: Optional[str] = None
    prototypeStart: Optional[date] = Field(default=None, index=True)
    prototypeEnd: Optional[date] = Field(default=None, index=True)

    #RELATIONSHIP
    ownerId: Optional[int] = Field(default=None, foreign_key="owner.ownerId")

class Inventory(InventoryBase, table=True):
    invId: int | None = Field(default=None, primary_key=True)

    owner: Optional["owner"] = Relationship(back_populates="Inventory")

class InventoryCreate(InventoryBase):
    pass

class InventoryPublic(InventoryBase):
    invId: int

class InventoryUpdate(InventoryBase):
    clientId: str | None = None
    stockBrand: str | None = None
    stockType: stockClass | None = None
    stockName: str | None = None
    stockRoadNumber: str | None = None
    stockrailroad: str | None = None
    stocklivery: str | None = None
    stockpower: powerClass | None = None
    purchaseCost: float | None = None
    purchasedate: date | None = None
    stockWheelType: wheelType | None = None
    stockCouplerType: couplerType | None = None
    stockComments: str | None = None
    prototypeStart: date | None = None
    prototypeEnd: date | None = None




