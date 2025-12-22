from typing import List
from fastapi import APIRouter, HTTPException, Depends

from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.services.user_service import UserService
from app.api.deps import get_db
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/users", dependencies=[Depends(get_current_user)])


async def get_user_service(db=Depends(get_db)):
    """Dependency to inject database into UserService."""
    return UserService(db)


@router.get("", response_model=List[UserRead])
async def list_users(
    service: UserService = Depends(get_user_service),
):
    return await service.list_users()


@router.post("", response_model=UserRead, status_code=201)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.create_user(payload)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service),
):
    user = await service.update_user(user_id, payload)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
):
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    # 204 No Content
    return None
