# user_preference.py - database model for user settings
# stores preferred retailers and email for alerts

from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True)
    preferred_retailers = Column(String(500), default="")
    price_alert_email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id})>"
