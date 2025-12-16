import os
import requests
from app.services.business import ProductService
from app.models.price_history import PriceHistory
from database import SessionLocal
from datetime import datetime

PRICEAPI_KEY = os.getenv("PRICEAPI_KEY")

# Example: Fetch laptops from PriceAPI (adjust endpoint/params as needed)
API_URL = "https://priceapi.com/api/v2/products"
PARAMS = {
    "q": "laptop",
    "country": "us",
    "key": PRICEAPI_KEY,
    "source": "google-shopping",
    "page": 1,
    "per_page": 20
}

def fetch_products():
    resp = requests.get(API_URL, params=PARAMS)
    resp.raise_for_status()
    return resp.json().get("products", [])

def main():
    db = SessionLocal()
    products = fetch_products()
    for p in products:
        # Map PriceAPI fields to your DB schema as needed
        name = p.get("name")
        description = p.get("description", "")
        category = p.get("category", "Other")
        image_url = p.get("image_url", "")
        brand = p.get("brand", "Unknown")
        tags = ",".join(p.get("tags", []))
        rating = p.get("rating", 0)
        # Create product
        product = ProductService.create_product(
            db,
            name=name,
            description=description,
            category=category,
            image_url=image_url,
            brand=brand,
            tags=tags,
            rating=rating
        )
        # Add offers (example, adjust as needed)
        for offer in p.get("offers", []):
            price_history = PriceHistory(
                product_id=product.id,
                retailer=offer.get("seller", "Unknown"),
                price=offer.get("price", 0),
                original_price=offer.get("original_price", 0),
                discount_percent=offer.get("discount_percent", 0),
                url=offer.get("url", ""),
                in_stock=offer.get("in_stock", True),
                rating=offer.get("rating", 0),
                review_count=offer.get("review_count", 0),
                created_at=datetime.utcnow()
            )
            db.add(price_history)
        db.commit()
    print(f"Imported {len(products)} products from PriceAPI.")

if __name__ == "__main__":
    main()
