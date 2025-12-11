# product.py - database model for products
# stores product info like name, description, category

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Product(Base):
    __tablename__ = "products"

    # basic product info
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(Text)
    category = Column(String(100), index=True)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # links to other tables
    price_histories = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="product", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name})>"
