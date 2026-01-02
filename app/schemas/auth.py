from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="password123")


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    id: Optional[str] = None


class RefreshTokenInDB(BaseModel):
    token: str
    user_id: str
    expires_at: datetime
    created_at: datetime
    revoked_at: Optional[datetime] = None


class RefreshTokenRevoke(BaseModel):
    refresh_token: str = Field(..., description="The refresh token to revoke")


class UserCreateWithPassword(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="password123")
    name: Optional[str] = None
