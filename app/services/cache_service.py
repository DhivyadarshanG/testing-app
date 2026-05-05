"""Cache service with intentional bugs."""

import json
from typing import Optional, Any
import redis
from app.config import get_settings, is_bug_enabled

settings = get_settings()

# Global Redis connection pool (correct approach)
_redis_pool = None


def get_redis_pool():
    """Get or create Redis connection pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool.from_url(settings.redis_url)
    return _redis_pool


def get_cached_data(key: str) -> Optional[Any]:
    """
    Get data from cache.
    
    BUG-012: Redis Connection Pool Exhaustion
    When enabled, creates new Redis client each call.
    """
    if is_bug_enabled("012"):
        # BUGGY: Creates new Redis client every time - exhausts connection pool
        r = redis.Redis.from_url(settings.redis_url)
        data = r.get(key)
        if data:
            return json.loads(data)
        return None
    else:
        # CORRECT: Reuse connection pool
        pool = get_redis_pool()
        r = redis.Redis(connection_pool=pool)
        data = r.get(key)
        if data:
            return json.loads(data)
        return None


def set_cached_data(key: str, value: Any, expire: int = 300) -> bool:
    """
    Set data in cache with expiration.
    
    Args:
        key: Cache key
        value: Value to cache
        expire: Expiration time in seconds (default 5 minutes)
    """
    try:
        pool = get_redis_pool()
        r = redis.Redis(connection_pool=pool)
        r.setex(key, expire, json.dumps(value))
        return True
    except Exception:
        return False


def invalidate_cache(key: str) -> bool:
    """Delete a key from cache."""
    try:
        pool = get_redis_pool()
        r = redis.Redis(connection_pool=pool)
        r.delete(key)
        return True
    except Exception:
        return False


def update_user_cache(user_id: int, user_data: dict, db_commit_callback=None) -> bool:
    """
    Update user cache.
    
    BUG-010: Cache Invalidation Race
    When enabled, updates cache before DB commit.
    """
    cache_key = f"user:{user_id}"
    
    if is_bug_enabled("010"):
        # BUGGY: Update cache before DB commit - can lead to stale data
        set_cached_data(cache_key, user_data)
        
        # Then commit to DB
        if db_commit_callback:
            db_commit_callback()
        
        return True
    else:
        # CORRECT: Commit to DB first, then update cache
        if db_commit_callback:
            db_commit_callback()
        
        # Invalidate cache after DB commit to force refresh
        invalidate_cache(cache_key)
        
        return True

# Made with Bob
