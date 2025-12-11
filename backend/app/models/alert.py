# alert.py - database model for price alerts
# stores the target price user wants to be notified at

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Alert(Base):
    __tablename__ = "alerts"

    # each alert has an id, product, and target price
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    price_threshold = Column(Float)
    target_retailer = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime, nullable=True)

    # link to product table 
    product = relationship("Product", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(product_id={self.product_id}, threshold={self.price_threshold})>"
