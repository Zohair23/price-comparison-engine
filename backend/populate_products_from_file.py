# This script loads product data from a local JSON file (products.json) and populates the database.
# Use this as a workaround if direct API access fails due to SSL issues.

import json
from app.services.business import ProductService, PriceHistoryService
from database import SessionLocal

PRODUCTS_FILE = "products.json"


def main():
    db = SessionLocal()
    print(f"Loading products from {PRODUCTS_FILE}...")
    with open(PRODUCTS_FILE, "r") as f:
        data = json.load(f)
    products = data.get("products", data)  # handle both {products: [...]} and [...] formats
    for item in products:
        name = item.get("name") or item.get("title") or "Unnamed Product"
        description = item.get("description") or "No description"
        category = item.get("category") or "Uncategorized"
        brand = item.get("brand") or None
        image_url = item.get("image") or item.get("image_url") or None
        tags = item.get("tags")
        if isinstance(tags, list):
            tags = ",".join(tags)
        elif not tags:
            tags = None
        rating = item.get("rating")
        try:
            rating = float(rating) if rating is not None else None
        except Exception:
            rating = None
        # Insert product
        product = ProductService.create_product(
            db,
            name=name[:255],
            description=description,
            category=category,
            image_url=image_url,
            brand=brand,
            tags=tags,
            rating=rating
        )
        # Insert price(s)
        prices = item.get("prices") or [item]  # handle both nested and flat
        for price_entry in prices:
            retailer = price_entry.get("retailer") or price_entry.get("seller") or "Unknown"
            price = float(price_entry.get("price") or price_entry.get("value") or 0)
            original_price = price_entry.get("original_price")
            url = price_entry.get("url") or price_entry.get("link")
            in_stock = str(price_entry.get("in_stock", "in_stock"))
            if price > 0:
                PriceHistoryService.add_price_record(
                    db,
                    product_id=product.id,
                    retailer=retailer,
                    price=price,
                    original_price=original_price,
                    url=url,
                    in_stock=in_stock
                )
        print(f"Added: {name} [{category}]")
    db.close()

if __name__ == "__main__":
    main()
