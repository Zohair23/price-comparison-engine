# alert.py - defines the shape of alert data for api

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# for creating a new alert
class AlertCreateSchema(BaseModel):
    product_id: int
    price_threshold: float
    target_retailer: Optional[str] = None


# for returning alert data
class AlertSchema(AlertCreateSchema):
    id: int
    is_active: bool
    triggered: bool
    created_at: datetime
    triggered_at: Optional[datetime] = None

    class Config:
        from_attributes = True
