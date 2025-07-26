"""
Multi-Level Cache Management System
==================================

Provides hierarchical caching with LRU eviction, TTL support,
and automatic invalidation for improved performance.
"""

import logging
import threading
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..exceptions import StorageException


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: Optional[int] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl_seconds is None:
            return False
        
        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now() > expiry_time
    
    @property
    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        return (datetime.now() - self.created_at).total_seconds()


@dataclass
class CacheStats:
    """Cache statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    entries: int = 0
    memory_usage: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0


class ICacheLevel(ABC):
    """Interface for cache levels."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        pass


class LRUCache(ICacheLevel):
    """
    LRU (Least Recently Used) cache implementation.
    
    Features:
    - Automatic eviction based on size
    - TTL support
    - Thread-safe operations
    - Statistics tracking
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds
        """
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats()
        self._logger = logging.getLogger(f"{__name__}.LRUCache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired:
                del self._cache[key]
                self._stats.misses += 1
                self._stats.entries -= 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            
            # Update access metadata
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            
            self._stats.hits += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        with self._lock:
            now = datetime.now()
            ttl_to_use = ttl if ttl is not None else self._default_ttl
            
            # Create new entry
            entry = CacheEntry(
                value=value,
                created_at=now,
                last_accessed=now,
                access_count=0,
                ttl_seconds=ttl_to_use
            )
            
            # Remove if already exists
            if key in self._cache:
                del self._cache[key]
                self._stats.entries -= 1
            
            # Add new entry
            self._cache[key] = entry
            self._stats.entries += 1
            
            # Evict if over capacity
            while len(self._cache) > self._max_size:
                self._evict_lru()
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.entries -= 1
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._stats.entries = 0
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                evictions=self._stats.evictions,
                entries=len(self._cache),
                memory_usage=self._estimate_memory_usage()
            )
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count."""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                self._stats.entries -= 1
            
            return len(expired_keys)
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self._cache:
            self._cache.popitem(last=False)  # Remove first (oldest) item
            self._stats.evictions += 1
            self._stats.entries -= 1
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes (rough approximation)."""
        # This is a simple estimation - could be enhanced
        total_size = 0
        for key, entry in self._cache.items():
            total_size += len(str(key)) * 2  # Assuming Unicode
            total_size += len(str(entry.value)) * 2  # Rough value size
            total_size += 200  # Overhead for entry metadata
        return total_size


class FileCache(ICacheLevel):
    """
    File-based cache for persistent storage.
    
    Features:
    - Persistent storage
    - Automatic cleanup
    - Size limits
    """
    
    def __init__(self, cache_dir: str, max_size_mb: int = 100):
        """
        Initialize file cache.
        
        Args:
            cache_dir: Directory for cache files
            max_size_mb: Maximum cache size in MB
        """
        import pickle
        from pathlib import Path
        
        self._cache_dir = Path(cache_dir)
        self._max_size_bytes = max_size_mb * 1024 * 1024
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._stats = CacheStats()
        self._logger = logging.getLogger(f"{__name__}.FileCache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from file cache."""
        with self._lock:
            file_path = self._get_file_path(key)
            
            if not file_path.exists():
                self._stats.misses += 1
                return None
            
            try:
                import pickle
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                
                # Check if expired
                if entry.is_expired:
                    file_path.unlink()
                    self._stats.misses += 1
                    return None
                
                # Update access time
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                
                # Save updated entry
                with open(file_path, 'wb') as f:
                    pickle.dump(entry, f)
                
                self._stats.hits += 1
                return entry.value
                
            except Exception as e:
                self._logger.warning(f"Failed to read cache file {file_path}: {e}")
                self._stats.misses += 1
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in file cache."""
        with self._lock:
            file_path = self._get_file_path(key)
            
            now = datetime.now()
            entry = CacheEntry(
                value=value,
                created_at=now,
                last_accessed=now,
                access_count=0,
                ttl_seconds=ttl
            )
            
            try:
                import pickle
                with open(file_path, 'wb') as f:
                    pickle.dump(entry, f)
                
                self._stats.entries += 1
                
                # Check size limits
                self._cleanup_if_needed()
                
            except Exception as e:
                self._logger.error(f"Failed to write cache file {file_path}: {e}")
    
    def delete(self, key: str) -> bool:
        """Delete value from file cache."""
        with self._lock:
            file_path = self._get_file_path(key)
            
            if file_path.exists():
                file_path.unlink()
                self._stats.entries -= 1
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache files."""
        with self._lock:
            for file_path in self._cache_dir.glob("*.cache"):
                file_path.unlink()
            self._stats.entries = 0
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            # Count actual files
            file_count = len(list(self._cache_dir.glob("*.cache")))
            total_size = sum(f.stat().st_size for f in self._cache_dir.glob("*.cache"))
            
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                evictions=self._stats.evictions,
                entries=file_count,
                memory_usage=total_size
            )
    
    def _get_file_path(self, key: str):
        """Get file path for cache key."""
        import hashlib
        # Use hash to handle special characters in keys
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self._cache_dir / f"{key_hash}.cache"
    
    def _cleanup_if_needed(self) -> None:
        """Clean up cache if size limit exceeded."""
        total_size = sum(f.stat().st_size for f in self._cache_dir.glob("*.cache"))
        
        if total_size > self._max_size_bytes:
            # Remove oldest files first
            files = [(f, f.stat().st_mtime) for f in self._cache_dir.glob("*.cache")]
            files.sort(key=lambda x: x[1])  # Sort by modification time
            
            for file_path, _ in files:
                file_path.unlink()
                self._stats.evictions += 1
                total_size -= file_path.stat().st_size
                
                if total_size <= self._max_size_bytes * 0.8:  # Leave some headroom
                    break


class MultiLevelCacheManager:
    """
    Multi-level cache manager coordinating L1 (memory) and L2 (file) caches.
    
    Features:
    - Automatic promotion/demotion between levels
    - Configurable cache levels
    - Statistics aggregation
    - Background cleanup
    """
    
    def __init__(self, 
                 l1_cache: Optional[ICacheLevel] = None,
                 l2_cache: Optional[ICacheLevel] = None,
                 auto_promote: bool = True):
        """
        Initialize multi-level cache manager.
        
        Args:
            l1_cache: L1 (memory) cache
            l2_cache: L2 (persistent) cache
            auto_promote: Automatically promote frequently accessed items to L1
        """
        self._l1_cache = l1_cache or LRUCache(max_size=500, default_ttl=300)
        self._l2_cache = l2_cache
        self._auto_promote = auto_promote
        self._lock = threading.RLock()
        self._logger = logging.getLogger(f"{__name__}.MultiLevelCacheManager")
        
        # Track promotion/demotion candidates
        self._access_counts: Dict[str, int] = {}
        self._promote_threshold = 3  # Promote to L1 after N accesses
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache hierarchy."""
        with self._lock:
            # Try L1 first
            value = self._l1_cache.get(key)
            if value is not None:
                self._track_access(key)
                return value
            
            # Try L2
            if self._l2_cache:
                value = self._l2_cache.get(key)
                if value is not None:
                    self._track_access(key)
                    
                    # Auto-promote to L1 if frequently accessed
                    if self._auto_promote and self._should_promote(key):
                        self._l1_cache.set(key, value)
                        self._logger.debug(f"Promoted {key} to L1 cache")
                    
                    return value
            
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, level: str = "auto") -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            level: Target cache level ("l1", "l2", or "auto")
        """
        with self._lock:
            if level == "l1" or level == "auto":
                self._l1_cache.set(key, value, ttl)
            
            if level == "l2" or (level == "auto" and self._l2_cache):
                self._l2_cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete value from all cache levels."""
        with self._lock:
            deleted = False
            
            if self._l1_cache.delete(key):
                deleted = True
            
            if self._l2_cache and self._l2_cache.delete(key):
                deleted = True
            
            # Clean up access tracking
            self._access_counts.pop(key, None)
            
            return deleted
    
    def invalidate(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern.
        
        Args:
            pattern: Pattern to match (simple wildcard support)
        
        Returns:
            Number of entries invalidated
        """
        # This is a simplified implementation
        # Real implementation would support proper pattern matching
        invalidated = 0
        
        if "*" in pattern:
            # Wildcard invalidation - would need to track all keys
            self._logger.warning("Wildcard invalidation not fully implemented")
        else:
            # Exact match
            if self.delete(pattern):
                invalidated = 1
        
        return invalidated
    
    def clear(self, level: Optional[str] = None) -> None:
        """Clear cache levels."""
        with self._lock:
            if level is None or level == "l1":
                self._l1_cache.clear()
            
            if level is None or level == "l2":
                if self._l2_cache:
                    self._l2_cache.clear()
            
            if level is None:
                self._access_counts.clear()
    
    def get_stats(self) -> Dict[str, CacheStats]:
        """Get statistics for all cache levels."""
        stats = {"l1": self._l1_cache.get_stats()}
        
        if self._l2_cache:
            stats["l2"] = self._l2_cache.get_stats()
        
        return stats
    
    def cleanup(self) -> Dict[str, int]:
        """Run cleanup on all cache levels."""
        cleanup_results = {}
        
        # Cleanup L1 (expired entries)
        if hasattr(self._l1_cache, 'cleanup_expired'):
            cleanup_results["l1_expired"] = self._l1_cache.cleanup_expired()
        
        # Cleanup L2
        if self._l2_cache and hasattr(self._l2_cache, 'cleanup_expired'):
            cleanup_results["l2_expired"] = self._l2_cache.cleanup_expired()
        
        return cleanup_results
    
    def _track_access(self, key: str) -> None:
        """Track access for promotion/demotion decisions."""
        self._access_counts[key] = self._access_counts.get(key, 0) + 1
    
    def _should_promote(self, key: str) -> bool:
        """Check if key should be promoted to L1."""
        return self._access_counts.get(key, 0) >= self._promote_threshold