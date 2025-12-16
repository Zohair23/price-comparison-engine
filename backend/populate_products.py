
"""
populate_products.py (TEST DATA MODE)
Temporarily generates 20+ products with unique, diverse filterable fields for robust filter testing.
Revert to original logic when done testing.
"""

from app.services.business import ProductService
from app.models.price_history import PriceHistory
from database import SessionLocal
from random import randint, uniform, choice
from datetime import datetime, timedelta

SELLERS = [f"Seller{i}" for i in range(1, 6)]
CATEGORIES = ["Laptops", "Phones", "Headphones", "Monitors", "Cameras"]
DELIVERY_INFOS = ["Free delivery", "Next day", "Standard", "Express", "Pickup"]

def main():
    db = SessionLocal()
    for i in range(1, 25):
        name = f"Test Product {i}"
        description = f"Description for product {i}"
        category = choice(CATEGORIES)
        brand = f"Brand{i%5+1}"
        image_url = f"https://dummyimage.com/400x400/000/fff&text=Product+{i}"
        tags = f"tag{i},test"
        rating = round(uniform(2.5, 5.0), 1)
        review_count = randint(0, 5000)
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
        # Add 1-3 offers per product
        for j in range(randint(1, 3)):
            retailer = choice(SELLERS)
            price = round(uniform(50, 2000), 2)
            original_price = price + round(uniform(10, 200), 2)
            discount_percent = round((original_price - price) / original_price * 100, 2)
            url = f"https://store.com/product/{i}/offer/{j}"
            in_stock = choice(["in_stock", "out_of_stock"])
            offer_rating = round(uniform(2.5, 5.0), 1)
            offer_review_count = randint(0, 5000)
            delivery_info = choice(DELIVERY_INFOS)
            created_at = datetime.utcnow() - timedelta(days=randint(0, 30))
            price_history = PriceHistory(
                product_id=product.id,
                retailer=retailer,
                price=price,
                original_price=original_price,
                discount_percent=discount_percent,
                url=url + f"?delivery={delivery_info.replace(' ', '+')}",
                in_stock=in_stock,
                rating=offer_rating,
                review_count=offer_review_count,
                created_at=created_at
            )
            db.add(price_history)
        db.commit()
    print("Inserted 20+ unique test products with diverse offers.")

if __name__ == "__main__":
    main()
    db.close()
    print(f"Imported {total_imported} products with offers.")



if __name__ == "__main__":
    main()
