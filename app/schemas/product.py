from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[int] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    average_rating: Optional[float] = None


class ProductRead(ProductBase):
    id: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
