#THIS FILE SUPPORTS THE BASE HTML ROUTES OF THE WEB APP, ALLOWING FOR PAGE NAVIGATION, A VERY BASIC MODULE OF FRONT END.

#CORE IMPORTS
from fastapi import Request
from fastapi import APIRouter

#SUBCORE IMPORTS
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

#IMPORT CLASSES
from schemas import dbSchema

#IMPORT FILES VARIABLE BRIDGES
vDbSchemas = dbSchema

#DEFINE ROUTERS
routerHome = APIRouter()

routerAccount = APIRouter(
    prefix="/account",
    tags=["account"]
)

routerInventory = APIRouter(
    prefix="/inventory",
    tags=["inventory"]
)

routerHelp = APIRouter(
    prefix="/help",
    tags=["help"]
)

routerGuides = APIRouter(
    prefix="/guides",
    tags=["guides"]
)

routerEnum = APIRouter(
    prefix="/enum",
    tags=["enum"]
)

baseDir = Path(___file___).resolve().parent
templates = Jinja2Templates(directory=str(baseDir / "scenes"))

#ROUTES
@routerHome.get("/", response_class=HTMLResponse)
async def open_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@routerAccount.get("/", response_class=HTMLResponse)
async def open_account(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})

@routerInventory.get("/", response_class=HTMLResponse)
async def open_inventory(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

@routerGuides.get("/")
async def open_guides(request: Request):
    return templates.TemplateResponse(
        "guides.html", {"request": request})

@routerEnum.get("/")
async def retrieve_all_enums():
    return {
        "wheelClasses": [e.value for e in vDbSchemas.wheelType],
        "couplerClasses": [e.value for e in vDbSchemas.couplerType],
        "powerClasses": [e.value for e in vDbSchemas.powerClass],
        "stockClasses": [e.value for e in vDbSchemas.stockClass]
    }