#MAIN FASTAPI IMPORTS
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

#NON  FASTAPI IMPORTS
from pathlib import Path
from contextlib import asynccontextmanager

#IMPORT FILES
from routers import authRoutes, baseRoutes, dbRoutes
from services import dbService

#IMPORT FILES VARIABLE BRIDGES
vBaseRoute = baseRoutes
vAuthRoute = authRoutes
vDbService = dbService
vDbRoute = dbRoutes

#DEPRECIATED CODE FROM FASTAPI DOCUMENTATION
# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()

#NEW VERSION
@asynccontextmanager
async def lifespan(app: FastAPI):
    vDbService.createDbAndTables()
    yield

#APP DEFINE
app = FastAPI(lifespan=lifespan)


#APP ROUTERS BASE_ROUTES
for vBaseRoute in [
    vBaseRoute.routerHome,
    vBaseRoute.routerInventory,
    vBaseRoute.routerAccount,
    vBaseRoute.routerHelp,
    vBaseRoute.routerGuides

]:
    app.include_router(vBaseRoute)

#APP ROUTERS AUTH_ROUTES
for vAuthRoute in [
    vAuthRoute.routerToken,
    vAuthRoute.routerMe,
    vAuthRoute.routerMeItems
]:
    app.include_router(vAuthRoute)

#APP ROUTERS DB_ROUTES
for vDbRoute in [
    vDbRoute.routerOwners
]:
    app.include_router(vDbRoute)

# app.include_router(auth_routes.routerToken)
# app.include_router(auth_routes.routerMe)
# app.include_router(auth_routes.routerMeItems)

#JINJA2 TEMPLATING
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)