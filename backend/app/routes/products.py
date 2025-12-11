# products.py - api endpoints for products

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.services.business import ProductService
from app.services.aggregator import DataAggregationService
from app.schemas.product import ProductSchema, ProductCreateSchema
from typing import List

router = APIRouter(prefix="/api/products", tags=["products"])


# returns all products
@router.get("/", response_model=List[ProductSchema])
def get_all_products(db: Session = Depends(get_db)):
    products = ProductService.get_all_products(db)
    return products


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
