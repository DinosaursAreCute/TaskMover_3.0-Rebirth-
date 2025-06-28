"""
Multi-level Cache Manager

Provides efficient caching for pattern matching results and frequently
accessed data with TTL support and memory management.
"""

import time
import threading
from typing import Any, Dict, Optional, Set
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from ..interfaces import BasePatternComponent, ICacheManager
from ..exceptions import CacheError


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    created_at: float
    expires_at: Optional[float] = None
    hit_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    size_bytes: int = 0


class MultiLevelCacheManager(BasePatternComponent, ICacheManager):
    """
    Multi-level cache manager with LRU eviction and TTL support.
    
    Features:
    - Memory cache with LRU eviction
    - TTL (time-to-live) support
    - Cache statistics and monitoring
    - Thread-safe operations
    - Memory usage tracking
    """
    
    def __init__(self, 
                 max_memory_entries: int = 1000,
                 default_ttl_seconds: int = 300,
                 cleanup_interval_seconds: int = 60,
                 max_memory_mb: float = 50.0):
        super().__init__("cache_manager")
        
        # Configuration
        self._max_memory_entries = max_memory_entries
        self._default_ttl_seconds = default_ttl_seconds
        self._cleanup_interval_seconds = cleanup_interval_seconds
        self._max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        
        # Memory cache with ordered dict for LRU
        self._memory_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired': 0,
            'memory_usage_bytes': 0,
            'total_entries': 0
        }
        
        # Cleanup thread
        self._cleanup_thread = None
        self._shutdown_event = threading.Event()
        
        self._start_cleanup_thread()
        
        self._logger.info(f"MultiLevelCacheManager initialized with {max_memory_entries} max entries")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        with self._lock:
            try:
                entry = self._memory_cache.get(key)
                
                if entry is None:
                    self._stats['misses'] += 1
                    return None
                
                # Check if expired
                current_time = time.time()
                if entry.expires_at and current_time > entry.expires_at:
                    self._remove_entry(key)
                    self._stats['expired'] += 1
                    self._stats['misses'] += 1
                    return None
                
                # Update access statistics
                entry.hit_count += 1
                entry.last_accessed = current_time
                
                # Move to end (most recently used)
                self._memory_cache.move_to_end(key)
                
                self._stats['hits'] += 1
                return entry.value
                
            except Exception as e:
                self._log_error(e, "cache_get", key=key)
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store value in cache with optional TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self._lock:
            try:
                current_time = time.time()
                
                # Calculate expiration time
                if ttl is None:
                    ttl = self._default_ttl_seconds
                
                expires_at = current_time + ttl if ttl > 0 else None
                
                # Estimate size
                size_bytes = self._estimate_size(value)
                
                # Check if we need to make room
                self._ensure_capacity(size_bytes)
                
                # Create cache entry
                entry = CacheEntry(
                    value=value,
                    created_at=current_time,
                    expires_at=expires_at,
                    size_bytes=size_bytes
                )
                
                # Remove existing entry if present
                if key in self._memory_cache:
                    old_entry = self._memory_cache[key]
                    self._stats['memory_usage_bytes'] -= old_entry.size_bytes
                
                # Add new entry
                self._memory_cache[key] = entry
                self._stats['memory_usage_bytes'] += size_bytes
                self._stats['total_entries'] = len(self._memory_cache)
                
                self._logger.debug(f"Cached key '{key}' with {size_bytes} bytes, TTL: {ttl}s")
                
            except Exception as e:
                self._log_error(e, "cache_set", key=key)
    
    def invalidate(self, key: str) -> None:
        """
        Remove value from cache.
        
        Args:
            key: Cache key to remove
        """
        with self._lock:
            try:
                if key in self._memory_cache:
                    self._remove_entry(key)
                    self._logger.debug(f"Invalidated cache key: {key}")
                
            except Exception as e:
                self._log_error(e, "cache_invalidate", key=key)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            try:
                self._memory_cache.clear()
                self._stats['memory_usage_bytes'] = 0
                self._stats['total_entries'] = 0
                self._logger.info("Cache cleared")
                
            except Exception as e:
                self._log_error(e, "cache_clear")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self._stats.copy(),
                'hit_rate_percent': round(hit_rate, 2),
                'total_requests': total_requests,
                'memory_usage_mb': round(self._stats['memory_usage_bytes'] / (1024 * 1024), 2),
                'memory_utilization_percent': round(
                    self._stats['memory_usage_bytes'] / self._max_memory_bytes * 100, 2
                ) if self._max_memory_bytes > 0 else 0
            }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information."""
        with self._lock:
            current_time = time.time()
            
            entries_info = []
            for key, entry in self._memory_cache.items():
                is_expired = entry.expires_at and current_time > entry.expires_at
                age_seconds = current_time - entry.created_at
                
                entries_info.append({
                    'key': key,
                    'size_bytes': entry.size_bytes,
                    'hit_count': entry.hit_count,
                    'age_seconds': round(age_seconds, 2),
                    'is_expired': is_expired,
                    'expires_in_seconds': round(entry.expires_at - current_time, 2) if entry.expires_at else None
                })
            
            return {
                'configuration': {
                    'max_memory_entries': self._max_memory_entries,
                    'default_ttl_seconds': self._default_ttl_seconds,
                    'max_memory_mb': self._max_memory_bytes / (1024 * 1024),
                    'cleanup_interval_seconds': self._cleanup_interval_seconds
                },
                'statistics': self.get_stats(),
                'entries': entries_info
            }
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        with self._lock:
            try:
                current_time = time.time()
                expired_keys = []
                
                for key, entry in self._memory_cache.items():
                    if entry.expires_at and current_time > entry.expires_at:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    self._remove_entry(key)
                    self._stats['expired'] += 1
                
                if expired_keys:
                    self._logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                
                return len(expired_keys)
                
            except Exception as e:
                self._log_error(e, "cleanup_expired")
                return 0
    
    def shutdown(self) -> None:
        """Shutdown the cache manager and cleanup resources."""
        try:
            self._shutdown_event.set()
            
            if self._cleanup_thread and self._cleanup_thread.is_alive():
                self._cleanup_thread.join(timeout=5.0)
            
            self.clear()
            self._logger.info("Cache manager shutdown complete")
            
        except Exception as e:
            self._log_error(e, "shutdown")
    
    def _ensure_capacity(self, new_entry_size: int) -> None:
        """Ensure cache has capacity for new entry."""
        # Check memory limit
        while (self._stats['memory_usage_bytes'] + new_entry_size > self._max_memory_bytes or
               len(self._memory_cache) >= self._max_memory_entries):
            
            if not self._memory_cache:
                break
            
            # Remove least recently used entry
            lru_key = next(iter(self._memory_cache))
            self._remove_entry(lru_key)
            self._stats['evictions'] += 1
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry and update statistics."""
        if key in self._memory_cache:
            entry = self._memory_cache.pop(key)
            self._stats['memory_usage_bytes'] -= entry.size_bytes
            self._stats['total_entries'] = len(self._memory_cache)
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of a value."""
        try:
            import sys
            
            # Basic size estimation
            if isinstance(value, str):
                return sys.getsizeof(value)
            elif isinstance(value, (list, tuple)):
                return sys.getsizeof(value) + sum(sys.getsizeof(item) for item in value)
            elif isinstance(value, dict):
                return sys.getsizeof(value) + sum(
                    sys.getsizeof(k) + sys.getsizeof(v) for k, v in value.items()
                )
            else:
                return sys.getsizeof(value)
                
        except Exception:
            # Fallback estimation
            return 1024  # 1KB default
    
    def _start_cleanup_thread(self) -> None:
        """Start the background cleanup thread."""
        def cleanup_worker():
            while not self._shutdown_event.is_set():
                try:
                    self.cleanup_expired()
                    self._shutdown_event.wait(self._cleanup_interval_seconds)
                except Exception as e:
                    self._log_error(e, "cleanup_worker")
                    self._shutdown_event.wait(self._cleanup_interval_seconds)
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        self._logger.debug("Cache cleanup thread started")


class SimpleCacheManager(BasePatternComponent, ICacheManager):
    """
    Simple in-memory cache implementation for basic use cases.
    
    Provides basic caching without advanced features like LRU eviction
    or memory management.
    """
    
    def __init__(self, default_ttl_seconds: int = 300):
        super().__init__("simple_cache")
        
        self._default_ttl_seconds = default_ttl_seconds
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        
        self._logger.info("SimpleCacheManager initialized")
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                return None
            
            # Check if expired
            current_time = time.time()
            if entry.expires_at and current_time > entry.expires_at:
                del self._cache[key]
                return None
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache."""
        with self._lock:
            current_time = time.time()
            
            if ttl is None:
                ttl = self._default_ttl_seconds
            
            expires_at = current_time + ttl if ttl > 0 else None
            
            self._cache[key] = CacheEntry(
                value=value,
                created_at=current_time,
                expires_at=expires_at
            )
    
    def invalidate(self, key: str) -> None:
        """Remove value from cache."""
        with self._lock:
            self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
