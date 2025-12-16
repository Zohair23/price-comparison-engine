
# ...existing code...

# DEBUG: Return all products and their price histories as seen by the API
@router.get("/debug/all-products", response_model=list)
def debug_all_products(db: Session = Depends(get_db)):
    products = db.query(ProductService.__dict__["__globals__"]["Product"]).all()
    result = []
    for product in products:
        price_histories = db.query(ProductService.__dict__["__globals__"]["PriceHistory"]).filter_by(product_id=product.id).all()
        result.append({
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "brand": product.brand,
            "price_histories": [
                {
                    "id": ph.id,
                    "retailer": ph.retailer,
                    "price": ph.price,
                    "in_stock": ph.in_stock,
                    "created_at": str(ph.created_at)
                } for ph in price_histories
            ]
        })
    return result
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from app.models.price_history import PriceHistory
from database import get_db
from app.services.business import ProductService
from app.services.aggregator import DataAggregationService
from app.schemas.product import ProductSchema, ProductCreateSchema
from typing import List

# Define router before any route decorators
# router definition only, no stray code
router = APIRouter(prefix="/api/products", tags=["products"])
# products.py - api endpoints for products

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.services.business import ProductService
from app.services.aggregator import DataAggregationService
from app.schemas.product import ProductSchema, ProductCreateSchema
from typing import List

router = APIRouter(prefix="/api/products", tags=["products"])



# returns all products, normalized for frontend
@router.get("/", response_model=list)
def get_all_products(db: Session = Depends(get_db)):
    products = ProductService.get_all_products(db)
    result = []
    for product in products:
        # Get latest price per retailer for this product
        price_entries = db.query(PriceHistory).filter(PriceHistory.product_id == product.id).order_by(PriceHistory.created_at.desc()).all()
        prices_by_retailer = {}
        for price in price_entries:
            if price.retailer not in prices_by_retailer:
                prices_by_retailer[price.retailer] = price
        prices = []
        for price in prices_by_retailer.values():
            prices.append({
                "sellerId": price.retailer,
                "price": price.price,
                "stock": 1 if price.in_stock == "in_stock" else 0,
                "condition": "new",  # or map from price/retailer if available
                "originalPrice": price.original_price,
                "shipping": None,  # Add if available
                "deliveryDays": None  # Add if available
            })
        # Compose normalized product dict
        result.append({
            "id": str(product.id),
            "name": product.name,
            "brand": product.brand or "",
            "category": product.category,
            "image": product.image_url or "",
            "description": product.description,
            "rating": product.rating or 0,
            "reviewCount": 0,  # Add if available
            "prices": prices,
            "features": [],  # Add if available
            "specs": {},  # Add if available
            "tags": (product.tags.split(",") if product.tags else []),
        })
    return result


# get trending products from eBay
@router.get("/trending", response_model=List[ProductSchema])
def get_trending_products(db: Session = Depends(get_db)):
    """
    Get trending/popular products from eBay.
    """
    products = DataAggregationService.get_trending_products(db)
    return products


# search products by name or category (local search)
@router.get("/search", response_model=List[ProductSchema])
def search_products(q: str = "", category: str = None, db: Session = Depends(get_db)):
    products = ProductService.search_products(db, q, category)
    return products


# search eBay and add products - this triggers scraping
@router.post("/search-add", response_model=List[ProductSchema])
def search_and_add_products(q: str, db: Session = Depends(get_db)):
    """
    Search eBay for products matching the query.
    Scrapes real products and adds to database.
    """
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Search query too short")
    
    products = DataAggregationService.search_products(q, db)
    return products


# get one product by id
@router.get("/{product_id}", response_model=ProductSchema)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# create a new product
@router.post("/", response_model=ProductSchema)
def create_product(product: ProductCreateSchema, db: Session = Depends(get_db)):
    new_product = ProductService.create_product(
        db,
        name=product.name,
        description=product.description,
        category=product.category,
        image_url=product.image_url
    )
    return new_product
