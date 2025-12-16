# business.py - all the database queries live here
# separated into classes: ProductService, PriceHistoryService, AlertService

from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.price_history import PriceHistory
from app.models.alert import Alert
from app.models.recommendation import Recommendation
from sqlalchemy import and_, desc
from datetime import datetime, timedelta
import random


# handles all product related queries
class ProductService:
    @staticmethod
    def search_products(db: Session, query: str, category: str = None):
        # search by name or description, filter by category if given
        q = db.query(Product)
        
        if query:
            q = q.filter(Product.name.ilike(f"%{query}%") | Product.description.ilike(f"%{query}%"))
        
        if category:
            q = q.filter(Product.category.ilike(f"%{category}%"))
        
        return q.all()

    @staticmethod
    def get_product_by_id(db: Session, product_id: int):
        # find one product by its id
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def create_product(db: Session, name: str, description: str, category: str, image_url: str = None, brand: str = None, tags: str = None, rating: float = None):
        # add a new product to the database
        product = Product(
            name=name,
            description=description,
            category=category,
            brand=brand,
            image_url=image_url,
            tags=tags,
            rating=rating
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def get_all_products(db: Session):
        # get every product in the database
        return db.query(Product).all()


# handles price data queries
class PriceHistoryService:
    @staticmethod
    def get_price_comparison(db: Session, product_id: int):
        # get latest price from each retailer for one product
        all_prices = db.query(PriceHistory).filter(
            PriceHistory.product_id == product_id
        ).order_by(PriceHistory.created_at.desc()).all()
        
        # keep only the latest price per retailer
        prices_by_retailer = {}
        for price_entry in all_prices:
            if price_entry.retailer not in prices_by_retailer:
                prices_by_retailer[price_entry.retailer] = price_entry
        
        return list(prices_by_retailer.values())

    @staticmethod
    def get_price_history(db: Session, product_id: int, days: int = 30):
        """Get historical prices for a product"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return db.query(PriceHistory).filter(
            and_(
                PriceHistory.product_id == product_id,
                PriceHistory.created_at >= cutoff_date
            )
        ).order_by(PriceHistory.created_at.asc()).all()

    @staticmethod
    def add_price_record(db: Session, product_id: int, retailer: str, price: float, 
                        original_price: float = None, url: str = None, in_stock: str = "in_stock"):
        """Add a price record for a product"""
        discount_percent = 0
        if original_price and original_price > 0:
            discount_percent = ((original_price - price) / original_price) * 100

        price_history = PriceHistory(
            product_id=product_id,
            retailer=retailer,
            price=price,
            original_price=original_price,
            discount_percent=discount_percent,
            url=url,
            in_stock=in_stock
        )
        db.add(price_history)
        db.commit()
        db.refresh(price_history)
        return price_history

    @staticmethod
    def get_lowest_price(db: Session, product_id: int):
        """Get the lowest current price"""
        latest = PriceHistoryService.get_price_comparison(db, product_id)
        if latest:
            return min(latest, key=lambda x: x.price)
        return None

    @staticmethod
    def get_best_deal(db: Session, product_id: int):
        """Get the best discount"""
        latest = PriceHistoryService.get_price_comparison(db, product_id)
        if latest:
            return max(latest, key=lambda x: x.discount_percent)
        return None


class AlertService:
    @staticmethod
    def create_alert(db: Session, product_id: int, price_threshold: float, target_retailer: str = None):
        """Create a price alert"""
        alert = Alert(
            product_id=product_id,
            price_threshold=price_threshold,
            target_retailer=target_retailer,
            is_active=True
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def get_active_alerts(db: Session):
        """Get all active alerts"""
        return db.query(Alert).filter(Alert.is_active == True).all()

    @staticmethod
    def check_alerts(db: Session):
        """Check if any alerts should be triggered"""
        active_alerts = AlertService.get_active_alerts(db)
        triggered_alerts = []
        
        for alert in active_alerts:
            # Get current prices for the product
            prices = PriceHistoryService.get_price_comparison(db, alert.product_id)
            
            for price_entry in prices:
                if alert.target_retailer and price_entry.retailer != alert.target_retailer:
                    continue
                
                if price_entry.price <= alert.price_threshold and not alert.triggered:
                    alert.triggered = True
                    alert.triggered_at = datetime.utcnow()
                    triggered_alerts.append(alert)
        
        db.commit()
        return triggered_alerts

    @staticmethod
    def deactivate_alert(db: Session, alert_id: int):
        """Deactivate an alert"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.is_active = False
            db.commit()
        return alert


class RecommendationService:
    @staticmethod
    def generate_recommendations(db: Session, product_id: int, limit: int = 5):
        """Generate recommendations for a product using simple collaborative filtering"""
        current_product = ProductService.get_product_by_id(db, product_id)
        if not current_product:
            return []
        
        # Find similar products in same category with similar price range
        prices = PriceHistoryService.get_price_comparison(db, product_id)
        if not prices:
            return []
        
        avg_price = sum(p.price for p in prices) / len(prices)
        price_range = (avg_price * 0.7, avg_price * 1.3)
        
        similar_products = db.query(Product).filter(
            and_(
                Product.category == current_product.category,
                Product.id != product_id
            )
        ).all()
        
        # Clear old recommendations
        db.query(Recommendation).filter(Recommendation.product_id == product_id).delete()
        
        recommendations = []
        for similar_product in similar_products[:limit]:
            similar_prices = PriceHistoryService.get_price_comparison(db, similar_product.id)
            if similar_prices:
                avg_similar_price = sum(p.price for p in similar_prices) / len(similar_prices)
                
                # Score based on price similarity and category match
                if price_range[0] <= avg_similar_price <= price_range[1]:
                    score = 0.9
                    rec_type = "similar"
                else:
                    score = 0.6
                    rec_type = "related"
                
                recommendation = Recommendation(
                    product_id=product_id,
                    recommended_product_id=similar_product.id,
                    recommendation_type=rec_type,
                    score=score
                )
                db.add(recommendation)
                recommendations.append(recommendation)
        
        db.commit()
        return recommendations

    @staticmethod
    def get_recommendations_for_product(db: Session, product_id: int):
        """Get stored recommendations for a product"""
        recommendations = db.query(Recommendation).filter(
            Recommendation.product_id == product_id
        ).order_by(desc(Recommendation.score)).all()
        
        result = []
        for rec in recommendations:
            product = ProductService.get_product_by_id(db, rec.recommended_product_id)
            if product:
                result.append({
                    "id": rec.id,
                    "product": product,
                    "type": rec.recommendation_type,
                    "score": rec.score
                })
        
        return result
