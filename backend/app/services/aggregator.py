# aggregator.py - Multi-Source Price Tracker
# Sources: eBay Browse API (5000/day) + SerpAPI (100/month for Amazon, Walmart, etc.)
# Caches results to minimize API calls

from app.services.business import ProductService, PriceHistoryService
from config import settings
from sqlalchemy.orm import Session
import httpx
import base64
import time

# Token cache
_token_cache = {"token": None, "expires": 0}


class DataAggregationService:
    """Multi-source price aggregation: eBay + SerpAPI (Amazon, Walmart, Google Shopping)"""
    
    # ==================== EBAY API (5000 calls/day) ====================
    
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

    # ==================== SERPAPI (100 calls/month) ====================
    # Use sparingly! Each call searches Amazon, Walmart, or Google Shopping
    
    @staticmethod
    def search_amazon(query: str, limit: int = 5):
        """Search Amazon via SerpAPI - USE SPARINGLY (100/month total)"""
        if not settings.serpapi_key:
            print("SerpAPI key not configured")
            return []
        
        resp = httpx.get(
            'https://serpapi.com/search.json',
            params={
                'engine': 'amazon',
                'amazon_domain': 'amazon.com',
                'k': query,
                'api_key': settings.serpapi_key
            },
            timeout=20
        )
        
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('organic_results', [])[:limit]
            return results
        
        print(f"Amazon search error: {resp.status_code}")
        return []

    @staticmethod
    def search_walmart(query: str, limit: int = 5):
        """Search Walmart via SerpAPI - USE SPARINGLY (100/month total)"""
        if not settings.serpapi_key:
            print("SerpAPI key not configured")
            return []
        
        resp = httpx.get(
            'https://serpapi.com/search.json',
            params={
                'engine': 'walmart',
                'query': query,
                'api_key': settings.serpapi_key
            },
            timeout=20
        )
        
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('organic_results', [])[:limit]
            return results
        
        print(f"Walmart search error: {resp.status_code}")
        return []

    @staticmethod
    def search_google_shopping(query: str, limit: int = 5):
        """Search Google Shopping via SerpAPI - USE SPARINGLY (100/month total)"""
        if not settings.serpapi_key:
            print("SerpAPI key not configured")
            return []
        
        resp = httpx.get(
            'https://serpapi.com/search.json',
            params={
                'engine': 'google_shopping',
                'q': query,
                'api_key': settings.serpapi_key
            },
            timeout=20
        )
        
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('shopping_results', [])[:limit]
            return results
        
        print(f"Google Shopping search error: {resp.status_code}")
        return []

    # ==================== SAVE TO DATABASE ====================

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
    def save_amazon_item(db: Session, item: dict):
        """Save an Amazon item from SerpAPI to database"""
        try:
            title = item.get('title', '')[:200]
            price = item.get('price', {}).get('raw', '') if isinstance(item.get('price'), dict) else item.get('price', '')
            
            # Parse price (can be "$29.99" or similar)
            if isinstance(price, str):
                price = float(price.replace('$', '').replace(',', '').strip() or 0)
            else:
                price = float(price or 0)
            
            image = item.get('thumbnail', '')
            link = item.get('link', '')
            rating = item.get('rating', '')
            
            if not title or price <= 0:
                return None
            
            product = ProductService.create_product(
                db,
                name=title,
                description=f"Rating: {rating}" if rating else "Amazon Listing",
                category="Amazon",
                image_url=image
            )
            
            PriceHistoryService.add_price_record(
                db,
                product_id=product.id,
                retailer="Amazon",
                price=price,
                original_price=None,
                url=link,
                in_stock="in_stock"
            )
            
            return product
        except Exception as e:
            print(f"Amazon save error: {e}")
            return None

    @staticmethod
    def save_walmart_item(db: Session, item: dict):
        """Save a Walmart item from SerpAPI to database"""
        try:
            title = item.get('title', '')[:200]
            price = item.get('primary_offer', {}).get('offer_price', 0)
            if not price:
                price = item.get('price', 0)
            
            if isinstance(price, str):
                price = float(price.replace('$', '').replace(',', '').strip() or 0)
            else:
                price = float(price or 0)
            
            image = item.get('thumbnail', '')
            link = item.get('product_page_url', '')
            rating = item.get('rating', '')
            
            if not title or price <= 0:
                return None
            
            product = ProductService.create_product(
                db,
                name=title,
                description=f"Rating: {rating}" if rating else "Walmart Listing",
                category="Walmart",
                image_url=image
            )
            
            PriceHistoryService.add_price_record(
                db,
                product_id=product.id,
                retailer="Walmart",
                price=price,
                original_price=None,
                url=link,
                in_stock="in_stock"
            )
            
            return product
        except Exception as e:
            print(f"Walmart save error: {e}")
            return None

    # ==================== HIGH-LEVEL METHODS ====================

    @staticmethod
    def get_trending_products(db: Session):
        """Get trending consumer electronics products (phones, laptops, headphones, etc.)
        Uses cached DB data if available, otherwise fetches from eBay by category."""
        existing = ProductService.get_all_products(db)
        # Return cached if we have enough
        if existing and len(existing) >= 3:
            return existing

        # Only fetch from eBay if DB is empty (saves API calls)
        print("Fetching trending consumer electronics from eBay API (1 call per category, only if DB empty)...")
        categories = ["phones", "laptops", "headphones", "tablets", "smartwatch", "camera", "monitor", "gaming console"]
        saved = []
        for cat in categories:
            items = DataAggregationService.search_ebay(cat, limit=2)
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

    @staticmethod
    def compare_prices(query: str, db: Session, use_serpapi: bool = False):
        """
        Compare prices across retailers for the same product.
        - Always uses eBay (free, 5000/day)
        - Optionally uses SerpAPI for Amazon/Walmart (costs 1 call from 100/month limit)
        """
        results = {
            "query": query,
            "retailers": {}
        }
        
        # Always get eBay prices (free)
        ebay_items = DataAggregationService.search_ebay(query, limit=3)
        if ebay_items:
            results["retailers"]["eBay"] = []
            for item in ebay_items:
                price_info = item.get('price', {})
                results["retailers"]["eBay"].append({
                    "title": item.get('title', '')[:100],
                    "price": float(price_info.get('value', 0)),
                    "url": item.get('itemWebUrl', ''),
                    "image": item.get('image', {}).get('imageUrl', '')
                })
        
        # Only use SerpAPI if explicitly requested (saves your 100/month)
        if use_serpapi and settings.serpapi_key:
            print("Using SerpAPI (1 call from 100/month)...")
            
            # Amazon
            amazon_items = DataAggregationService.search_amazon(query, limit=3)
            if amazon_items:
                results["retailers"]["Amazon"] = []
                for item in amazon_items:
                    price = item.get('price', {})
                    if isinstance(price, dict):
                        price = price.get('raw', '$0')
                    price_val = float(str(price).replace('$', '').replace(',', '') or 0)
                    results["retailers"]["Amazon"].append({
                        "title": item.get('title', '')[:100],
                        "price": price_val,
                        "url": item.get('link', ''),
                        "image": item.get('thumbnail', '')
                    })
        
        return results
