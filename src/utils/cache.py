"""
Caching utility for frequently accessed data
"""
import time
import threading
from functools import wraps

class Cache:
    """Simple in-memory cache with TTL support"""
    _cache = {}
    _lock = threading.Lock()
    
    @classmethod
    def get(cls, key):
        """Get value from cache if not expired"""
        with cls._lock:
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
        with cls._lock:
            # Basic memory management: Clear expired items if cache gets too big
            if len(cls._cache) > 1000:
                now = time.time()
                expired_keys = [k for k, v in cls._cache.items() if v[1] < now]
                for k in expired_keys:
                    del cls._cache[k]
            
            cls._cache[key] = (value, time.time() + ttl)
    
    @classmethod
    def clear(cls, key=None):
        """Clear specific key or all cache"""
        with cls._lock:
            if key:
                cls._cache.pop(key, None)
            else:
                cls._cache.clear()

    @classmethod
    def invalidate_prefix(cls, prefix):
        """Clear all keys starting with a specific prefix"""
        with cls._lock:
            keys_to_remove = [k for k in cls._cache if k.startswith(prefix)]
            for k in keys_to_remove:
                del cls._cache[k]

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
