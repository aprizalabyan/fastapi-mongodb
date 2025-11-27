from typing import List
from fastapi import APIRouter, HTTPException

from app.schemas.user import UserRead, UserCreate
from app.services.user_service import UserService

router = APIRouter()

service = UserService()


@router.get("/users", response_model=List[UserRead])
async def list_users():
    return await service.list_users()


@router.post("/users", response_model=UserRead, status_code=201)
async def create_user(payload: UserCreate):
    return await service.create_user(payload)


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(user_id: str):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
