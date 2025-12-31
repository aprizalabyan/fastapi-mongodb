from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    comment: Optional[str] = None
    rating: Optional[int] = None


class ReviewUpdate(BaseModel):
    comment: Optional[str] = None
    rating: Optional[int] = None


class ReviewRead(ReviewBase):
    id: str
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    reviewer_name: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    isEditable: bool = False
