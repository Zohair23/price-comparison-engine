# product.py - defines the shape of product data for api
# pydantic validates that data matches these fields

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# for creating a new product
class ProductCreateSchema(BaseModel):
    name: str
    description: str
    category: str
    image_url: Optional[str] = None


# for returning product data
class ProductSchema(ProductCreateSchema):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
