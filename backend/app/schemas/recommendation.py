# recommendation.py - defines the shape of recommendation data for api

from pydantic import BaseModel
from datetime import datetime


class RecommendationSchema(BaseModel):
    id: int
    product_id: int
    recommended_product_id: int
    recommendation_type: str
    score: float
    created_at: datetime

    class Config:
        from_attributes = True
