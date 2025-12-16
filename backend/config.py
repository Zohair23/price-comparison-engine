# config.py - app settings
# loads database url and other config from .env file

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # default values, can be overwritten by .env file
    database_url: str = "postgresql://postgres:password@localhost:5432/price_comparison"
    secret_key: str = "your-secret-key-here-change-in-production"
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # eBay API credentials for real-time product data
    ebay_client_id: str = ""
    ebay_client_secret: str = ""
    
    # SerpAPI for Amazon, Walmart, Google Shopping
    serpapi_key: str = ""

    # PriceAPI for real product data
    priceapi_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
