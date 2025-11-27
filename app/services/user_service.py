import uuid
from typing import List, Optional

from app.schemas.user import UserCreate, UserRead


class UserService:
    """Simple in-memory user service for demo. Replace with DB calls later."""

    def __init__(self):
        self._users: dict[str, dict] = {}

    async def list_users(self) -> List[UserRead]:
        return [UserRead(id=k, **v) for k, v in self._users.items()]

    async def create_user(self, payload: UserCreate) -> UserRead:
        uid = str(uuid.uuid4())
        data = payload.dict()
        self._users[uid] = data
        return UserRead(id=uid, **data)

    async def get_user(self, user_id: str) -> Optional[UserRead]:
        if user_id in self._users:
            return UserRead(id=user_id, **self._users[user_id])
        return None
