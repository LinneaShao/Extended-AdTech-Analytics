"""
Simple in-memory caching for database queries.
"""

import time
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """In-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache if not expired."""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if time.time() > entry['expires_at']:
            del self._cache[key]
            return None
        
        logger.debug(f"Cache hit for key: {key}")
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set item in cache with TTL."""
        if ttl is None:
            ttl = self.default_ttl
        
        expires_at = time.time() + ttl
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at
        }
        
        logger.debug(f"Cache set for key: {key}, TTL: {ttl}s")
    
    def delete(self, key: str) -> bool:
        """Delete item from cache."""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache deleted for key: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        logger.debug("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"Removed {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        self.cleanup_expired()
        return {
            'total_entries': len(self._cache),
            'cache_keys': list(self._cache.keys())
        }
