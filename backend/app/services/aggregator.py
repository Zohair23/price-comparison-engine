# aggregator.py - eBay Price Tracker using Browse API
# Caches results to minimize API calls (5000/day limit)

from app.services.business import ProductService, PriceHistoryService
from config import settings
from sqlalchemy.orm import Session
import httpx
import base64
import time

# Token cache
_token_cache = {"token": None, "expires": 0}


class DataAggregationService:
    """eBay Browse API integration with caching"""
    
    @staticmethod
    def get_token():
        """Get OAuth token (cached to minimize calls)"""
        global _token_cache
        
        # Return cached token if still valid
        if _token_cache["token"] and time.time() < _token_cache["expires"]:
            return _token_cache["token"]
        
        credentials = f'{settings.ebay_client_id}:{settings.ebay_client_secret}'
        encoded = base64.b64encode(credentials.encode()).decode()
        
        resp = httpx.post(
            'https://api.ebay.com/identity/v1/oauth2/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {encoded}'
            },
            data={
                'grant_type': 'client_credentials',
                'scope': 'https://api.ebay.com/oauth/api_scope'
            },
            timeout=15
        )
        
        if resp.status_code == 200:
            data = resp.json()
            _token_cache["token"] = data["access_token"]
            # Cache for 1 hour (token valid for 2 hours)
            _token_cache["expires"] = time.time() + 3600
            return _token_cache["token"]
        
        print(f"Token error: {resp.status_code}")
        return None

    @staticmethod
    def search_ebay(query: str, limit: int = 5):
        """Search eBay Browse API - returns items with prices"""
        token = DataAggregationService.get_token()
        if not token:
            return []
        
        resp = httpx.get(
            'https://api.ebay.com/buy/browse/v1/item_summary/search',
            headers={
                'Authorization': f'Bearer {token}',
                'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
            },
            params={
                'q': query,
                'limit': limit,
                'filter': 'buyingOptions:{FIXED_PRICE}'  # Only Buy It Now
            },
            timeout=15
        )
        
        if resp.status_code == 200:
            return resp.json().get('itemSummaries', [])
        
        print(f"Search error: {resp.status_code} - {resp.text[:100]}")
        return []

    @staticmethod
    def save_ebay_item(db: Session, item: dict):
        """Save an eBay item to database"""
        try:
            title = item.get('title', '')[:200]
            price_info = item.get('price', {})
            price = float(price_info.get('value', 0))
            currency = price_info.get('currency', 'USD')
            image = item.get('image', {}).get('imageUrl', '')
            link = item.get('itemWebUrl', '')
            condition = item.get('condition', '')
            
            if not title or price <= 0:
                return None
            
            # Create product
            product = ProductService.create_product(
                db,
                name=title,
                description=f"Condition: {condition}" if condition else "eBay Listing",
                category="eBay",
                image_url=image
            )
            
            # Add price
            PriceHistoryService.add_price_record(
                db,
                product_id=product.id,
                retailer="eBay",
                price=price,
                original_price=None,
                url=link,
                in_stock="in_stock"
            )
            
            return product
        except Exception as e:
            print(f"Save error: {e}")
            return None

    @staticmethod
    def get_trending_products(db: Session):
        """Get products - use cached DB data if available"""
        existing = ProductService.get_all_products(db)
        
        # Return cached if we have enough
        if existing and len(existing) >= 3:
            return existing
        
        # Only fetch from eBay if DB is empty (saves API calls)
        print("Fetching from eBay API (1 call)...")
        items = DataAggregationService.search_ebay("electronics", limit=5)
        
        saved = []
        for item in items:
            product = DataAggregationService.save_ebay_item(db, item)
            if product:
                saved.append(product)
        
        return saved if saved else existing or []

    @staticmethod
    def search_products(search_term: str, db: Session):
        """Search - check local DB first, then eBay if needed"""
        # First check local DB
        local = ProductService.search_products(db, search_term)
        if local:
            return local
        
        # If nothing local, search eBay (1 API call)
        print(f"Searching eBay for: {search_term} (1 call)")
        items = DataAggregationService.search_ebay(search_term, limit=5)
        
        saved = []
        for item in items:
            product = DataAggregationService.save_ebay_item(db, item)
            if product:
                saved.append(product)
        
        return saved
