"""
Caching utility for frequently accessed data
"""
import time
from functools import wraps

class Cache:
    """Simple in-memory cache with TTL support"""
    _cache = {}
    
    @classmethod
    def get(cls, key):
        """Get value from cache if not expired"""
        if key in cls._cache:
            value, expiry = cls._cache[key]
            if time.time() < expiry:
                return value
            else:
                del cls._cache[key]
        return None
    
    @classmethod
    def set(cls, key, value, ttl=300):
        """Store value with TTL (default 5 minutes)"""
        cls._cache[key] = (value, time.time() + ttl)
    
    @classmethod
    def clear(cls, key=None):
        """Clear specific key or all cache"""
        if key:
            cls._cache.pop(key, None)
        else:
            cls._cache.clear()

def cache_result(ttl=300, key_prefix=None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix or func.__name__}:{args}:{kwargs}"
            
            # Try to get from cache
            result = Cache.get(cache_key)
            if result is not None:
                return result
            
            # Compute and cache
            result = func(*args, **kwargs)
            Cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
