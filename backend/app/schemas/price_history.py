# price_history.py - defines the shape of price data for api

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# price record with retailer info
class PriceHistorySchema(BaseModel):
    id: int
    product_id: int
    retailer: str
    price: float
    original_price: Optional[float] = None
    discount_percent: float
    url: Optional[str] = None
    in_stock: str
    rating: Optional[float] = None
    review_count: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
