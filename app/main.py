from fastapi import FastAPI

from app.core.config import Settings
from app.api.v1 import users as users_router

settings = Settings()

app = FastAPI(title=settings.app_name)

app.include_router(users_router.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI base project"}
