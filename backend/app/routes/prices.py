# prices.py - api endpoints for price data

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.services.business import PriceHistoryService, ProductService
from app.schemas.price_history import PriceHistorySchema
from typing import List

router = APIRouter(prefix="/api/prices", tags=["prices"])


# get prices from all stores for one product
@router.get("/comparison/{product_id}", response_model=List[PriceHistorySchema])
def get_price_comparison(product_id: int, db: Session = Depends(get_db)):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    prices = PriceHistoryService.get_price_comparison(db, product_id)
    return prices


# get price changes over time
@router.get("/history/{product_id}", response_model=List[PriceHistorySchema])
def get_price_history(product_id: int, days: int = 30, db: Session = Depends(get_db)):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    history = PriceHistoryService.get_price_history(db, product_id, days)
    return history


# find the cheapest price
@router.get("/lowest/{product_id}", response_model=PriceHistorySchema)
def get_lowest_price(product_id: int, db: Session = Depends(get_db)):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    lowest = PriceHistoryService.get_lowest_price(db, product_id)
    if not lowest:
        raise HTTPException(status_code=404, detail="No price data available")
    
    return lowest


# find the biggest discount
@router.get("/best-deal/{product_id}", response_model=PriceHistorySchema)
def get_best_deal(product_id: int, db: Session = Depends(get_db)):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    best = PriceHistoryService.get_best_deal(db, product_id)
    if not best:
        raise HTTPException(status_code=404, detail="No price data available")
    
    return best
