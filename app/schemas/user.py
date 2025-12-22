from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Annotated
from datetime import datetime

PyObjectId = Annotated[str, BeforeValidator(str)]


class UserBase(BaseModel):
    email: str = Field(..., example="user@example.com")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="password123")
    name: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None


class UserInDB(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: Optional[str] = None
    hashed_password: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserRead(UserBase):
    id: str
    name: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class UserCurrent(UserBase):
    id: str
    name: Optional[str] = None
