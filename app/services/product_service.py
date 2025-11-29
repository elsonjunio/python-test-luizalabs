import httpx
import json
from app.core.redis import redis

SHORT_TTL = 60 * 5       # 5 min
LONG_TTL = 60 * 60 * 24  # 24h


class ProductService:
    BASE_URL = 'http://challenge-api.luizalabs.com/api/product/{}'  # exemplo

    @staticmethod
    async def get_product(product_id: str):
        """Fetches a product using short cache, API fallback, and long cache.
        
        Args:
            product_id: Identifier of the product.

        Returns:
            A tuple with product data or None, and the source type.
        """
        short_key = f'product:{product_id}:short'
        long_key = f'product:{product_id}:long'

        # 1) get product from cache with ttl short
        cached = await redis.get(short_key)
        if cached:
            return json.loads(cached), 'cache_short'

        # 2) direct request
        try:
            async with httpx.AsyncClient(timeout=3) as c:
                r = await c.get(ProductService.BASE_URL.format(product_id))
                r.raise_for_status()
                data = r.json()

            # save to cache
            await redis.set(short_key, json.dumps(data), ex=SHORT_TTL)
            return data, 'api'

        except Exception:
            # 3) get product from cache with ttl long
            cached_long = await redis.get(long_key)
            if cached_long:
                return json.loads(cached_long), 'cache_long'

            return None, 'not_found'

    @staticmethod
    async def save_long_cache(product_id, data):
        """Stores product data in long cache.

        Args:
            product_id: Identifier of the product.
            data: Product data to be cached.
        """
        key = f'product:{product_id}:long'
        await redis.set(key, json.dumps(data), ex=LONG_TTL)
