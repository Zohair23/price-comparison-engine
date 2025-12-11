# recommendations.py - api endpoints for product recommendations
# not used in the frontend right now but kept for future

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.services.business import RecommendationService, ProductService
from app.schemas.recommendation import RecommendationSchema
from typing import List

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


# get recommendations for a product
@router.get("/{product_id}")
def get_recommendations(product_id: int, db: Session = Depends(get_db)):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    recommendations = RecommendationService.get_recommendations_for_product(db, product_id)
    return recommendations


# generate new recommendations for a product
@router.post("/generate/{product_id}")
def generate_recommendations(product_id: int, limit: int = 5, db: Session = Depends(get_db)):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    recs = RecommendationService.generate_recommendations(db, product_id, limit)
    return {
        "status": "success",
        "product_id": product_id,
        "count": len(recs),
        "recommendations": [
            {
                "id": rec.id,
                "type": rec.recommendation_type,
                "score": rec.score,
                "recommended_product_id": rec.recommended_product_id
            }
            for rec in recs
        ]
    }
