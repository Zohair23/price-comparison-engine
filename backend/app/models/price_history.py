# price_history.py - database model for price records
# stores price from each retailer at a point in time

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class PriceHistory(Base):
    __tablename__ = "price_histories"

    # price info for one product at one retailer
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    retailer = Column(String(100), index=True)
    price = Column(Float)
    original_price = Column(Float, nullable=True)
    discount_percent = Column(Float, default=0)
    url = Column(String(500), nullable=True)
    in_stock = Column(String(20), default="in_stock")
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # link to product table
    product = relationship("Product", back_populates="price_histories")

    __table_args__ = (
        UniqueConstraint("product_id", "retailer", "created_at", name="uq_product_retailer_date"),
    )

    def __repr__(self):
        return f"<PriceHistory(product_id={self.product_id}, retailer={self.retailer}, price={self.price})>"
