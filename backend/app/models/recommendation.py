# recommendation.py - database model for product recommendations
# stores similar products that might interest the user

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    recommended_product_id = Column(Integer, index=True)
    recommendation_type = Column(String(50))
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # link to product table
    product = relationship("Product", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation(product_id={self.product_id}, type={self.recommendation_type})>"
