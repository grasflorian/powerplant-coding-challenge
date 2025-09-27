from fastapi import FastAPI

from .routers.powerplans import powerplans_router

app = FastAPI()
app.include_router(powerplans_router)
