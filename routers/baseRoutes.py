#THIS FILE SUPPORTS THE BASE HTML ROUTES OF THE WEB APP, ALLOWING FOR PAGE NAVIGATION, A VERY BASIC MODULE OF FRONT END.

#CORE IMPORTS
from fastapi import Request
from fastapi import APIRouter

#SUBCORE IMPORTS
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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

templates = Jinja2Templates(directory="Scenes")

#ROUTES
@routerHome.get("/", response_class=HTMLResponse)
async def openHome(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@routerAccount.get("/", response_class=HTMLResponse)
async def openAccount(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})

@routerInventory.get("/", response_class=HTMLResponse)
async def openInventory(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

@routerGuides.get("/")
async def openGuides(request: Request):
    return templates.TemplateResponse(
        "guides.html", {"request": request})