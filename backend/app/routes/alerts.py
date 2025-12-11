# alerts.py - api endpoints for price alerts

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.services.business import AlertService, ProductService
from app.schemas.alert import AlertSchema, AlertCreateSchema
from typing import List

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


# get all active alerts
@router.get("/", response_model=List[AlertSchema])
def get_all_alerts(db: Session = Depends(get_db)):
    alerts = AlertService.get_active_alerts(db)
    return alerts


# create a new price alert
@router.post("/", response_model=AlertSchema)
def create_alert(alert_data: AlertCreateSchema, db: Session = Depends(get_db)):
    product = ProductService.get_product_by_id(db, alert_data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    alert = AlertService.create_alert(
        db,
        product_id=alert_data.product_id,
        price_threshold=alert_data.price_threshold,
        target_retailer=alert_data.target_retailer
    )
    return alert


# check if any alerts should trigger
@router.post("/check")
def check_alerts(db: Session = Depends(get_db)):
    triggered = AlertService.check_alerts(db)
    return {
        "status": "success",
        "triggered_count": len(triggered),
        "alerts": [
            {
                "id": alert.id,
                "product_id": alert.product_id,
                "threshold": alert.price_threshold
            }
            for alert in triggered
        ]
    }


# turn off an alert
@router.delete("/{alert_id}")
def deactivate_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = AlertService.deactivate_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"status": "success", "message": "Alert deactivated"}
