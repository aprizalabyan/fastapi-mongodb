from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId

from app.schemas.user import UserCreate, UserRead, UserUpdate


class UserService:
    """User service with MongoDB backend."""

    collection_name = "users"

    def __init__(self, db):
        """Initialize service with database instance."""
        self.db = db

    async def list_users(self) -> List[UserRead]:
        """Fetch all users from MongoDB."""
        users = []
        async for doc in self.db[self.collection_name].find():
            users.append(self._doc_to_user_read(doc))
        return users

    async def create_user(self, payload: UserCreate) -> UserRead:
        """Insert new user into MongoDB and add timestamps."""
        now = datetime.now(timezone.utc)
        data = payload.model_dump()
        data["createdAt"] = now
        data["updatedAt"] = now
        result = await self.db[self.collection_name].insert_one(data)
        data["_id"] = result.inserted_id
        return self._doc_to_user_read(data)

    async def get_user(self, user_id: str) -> Optional[UserRead]:
        """Fetch single user by ID from MongoDB."""
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None

        doc = await self.db[self.collection_name].find_one({"_id": oid})
        if doc:
            return self._doc_to_user_read(doc)
        return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user by ID. Returns True if deleted."""
        try:
            oid = ObjectId(user_id)
        except Exception:
            return False

        result = await self.db[self.collection_name].delete_one({"_id": oid})
        return result.deleted_count == 1

    async def update_user(
        self, user_id: str, payload: UserUpdate
    ) -> Optional[UserRead]:
        """Update a user by ID. Returns updated user or None if not found."""
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None

        # Only update fields that are provided (not None)
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            # If no fields provided, just return the user as-is
            return await self.get_user(user_id)

        # Add updatedAt timestamp
        update_data["updatedAt"] = datetime.now(timezone.utc)

        result = await self.db[self.collection_name].find_one_and_update(
            {"_id": oid}, {"$set": update_data}, return_document=True
        )
        if result:
            return self._doc_to_user_read(result)
        return None

    @staticmethod
    def _doc_to_user_read(doc: dict) -> UserRead:
        """Convert MongoDB document to UserRead schema."""
        # ensure id field exists and is a str
        doc["id"] = str(doc["_id"]) if "_id" in doc else doc.get("id")
        return UserRead(**doc)
