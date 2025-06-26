#THIS IS THE MAIN FASTAPI FILE, THE APPLICATION ITSELF

#MAIN FASTAPI IMPORTS
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

#NON  FASTAPI IMPORTS
from pathlib import Path
from contextlib import asynccontextmanager

#IMPORT FILES
from routers import authRoutes, baseRoutes, dbRoutes, inventoryRoutes
from services import dbService

#IMPORT FILES VARIABLE BRIDGES
vBaseRoute = baseRoutes
vAuthRoute = authRoutes
vDbService = dbService
vDbRoute = dbRoutes
vInvRoute = inventoryRoutes

@asynccontextmanager
async def lifespan(app: FastAPI):
    vDbService.createDbAndTables()
    yield

#APP DEFINE
app = FastAPI(lifespan=lifespan)

#APP ROUTERS BASE ROUTES
for vBaseRoute in [
    vBaseRoute.routerHome,
    vBaseRoute.routerInventory,
    vBaseRoute.routerAccount,
    vBaseRoute.routerHelp,
    vBaseRoute.routerGuides,
    vBaseRoute.routerEnum

]:
    app.include_router(vBaseRoute)

#APP ROUTERS AUTH ROUTES
for vAuthRoute in [
    vAuthRoute.routerToken,
    vAuthRoute.routerRefreshToken,
    vAuthRoute.routerPerm
]:
    app.include_router(vAuthRoute)

#APP ROUTERS DB ROUTES
for vDbRoute in [
    vDbRoute.routerOwners,
    vDbRoute.routerUser
]:
    app.include_router(vDbRoute)

#APP ROUTERS INV ROUTES
for vInvRoute in [
    vInvRoute.routerInv
]:
    app.include_router(vInvRoute)

# app.include_router(auth_routes.routerToken)
# app.include_router(auth_routes.routerMe)
# app.include_router(auth_routes.routerMeItems)

#JINJA2 TEMPLATING
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)