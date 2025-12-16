from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import Settings
from app.api.v1 import users as users_router
from app.api.v1 import auth as auth_router
from app.db import connect_to_db, close_db_connection

settings = Settings()


# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Application startup: Initializing resources...")
    await connect_to_db()

    yield
    # Shutdown logic
    print("Application shutdown: Cleaning up resources...")
    await close_db_connection()


app = FastAPI(title=settings.app_name, lifespan=lifespan)


app.include_router(auth_router.router, prefix=settings.api_v1_prefix, tags=["auth"])
app.include_router(users_router.router, prefix=settings.api_v1_prefix, tags=["users"])


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI Project with MongoDB"}
