from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    email: str = Field(..., example="user@example.com")


class UserCreate(UserBase):
    name: Optional[str] = None


class UserRead(UserBase):
    id: str
    name: Optional[str] = None

    class Config:
        orm_mode = True
