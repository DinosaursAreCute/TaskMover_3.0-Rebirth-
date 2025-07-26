"""
Base Repository Implementation
=============================

Generic base repository providing common functionality for all repository types
with caching, validation, and transaction support.
"""

import logging
from abc import ABC
from typing import Any, Dict, List, Optional, TypeVar, Generic, Type, Callable
from datetime import datetime
from uuid import UUID, uuid4

from . import IRepository, IEntity, IStorageBackend, StorageConfig, RepositoryStats
from ..exceptions import StorageException


T = TypeVar("T", bound=IEntity)
K = TypeVar("K")


class BaseRepository(IRepository[T, K], ABC):
    """
    Base repository implementation providing common functionality.
    
    Features:
    - Generic CRUD operations
    - Caching support
    - Validation hooks
    - Event callbacks
    - Statistics tracking
    - Transaction support
    """
    
    def __init__(self, 
                 storage_backend: IStorageBackend,
                 entity_type: Type[T],
                 table_name: str,
                 key_field: str = "id",
                 cache_ttl: Optional[int] = 300):
        """
        Initialize base repository.
        
        Args:
            storage_backend: Storage backend implementation
            entity_type: Type of entity this repository manages
            table_name: Database table name
            key_field: Primary key field name
            cache_ttl: Cache time-to-live in seconds
        """
        self._storage = storage_backend
        self._entity_type = entity_type
        self._table_name = table_name
        self._key_field = key_field
        self._cache_ttl = cache_ttl
        self._logger = logging.getLogger(f"{__name__}.{entity_type.__name__}Repository")
        
        # Repository configuration
        self._cache_enabled = True
        self._validation_enabled = True
        self._events_enabled = True
        
        # Statistics
        self._stats = RepositoryStats(
            total_entities=0,
            storage_size=0
        )
        
        # Event callbacks
        self._before_save_callbacks: List[Callable[[T], None]] = []
        self._after_save_callbacks: List[Callable[[T], None]] = []
        self._before_delete_callbacks: List[Callable[[K], None]] = []
        self._after_delete_callbacks: List[Callable[[K], None]] = []
    
    def save(self, entity: T) -> T:
        """Save entity to storage with validation and events."""
        try:
            # Validation
            if self._validation_enabled:
                self._validate_entity(entity)
            
            # Before save events
            if self._events_enabled:
                for callback in self._before_save_callbacks:
                    callback(entity)
            
            # Check if this is an update or create
            is_update = self.exists(entity.id)
            
            if is_update:
                result = self._update_entity(entity)
            else:
                result = self._create_entity(entity)
            
            # After save events
            if self._events_enabled:
                for callback in self._after_save_callbacks:
                    callback(result)
            
            # Update statistics
            if not is_update:
                self._stats.total_entities += 1
            
            self._logger.debug(f"{'Updated' if is_update else 'Created'} entity {entity.id}")
            return result
            
        except Exception as e:
            self._logger.error(f"Failed to save entity {entity.id}: {e}")
            raise StorageException(f"Failed to save entity: {e}") from e
    
    def find_by_id(self, entity_id: K) -> Optional[T]:
        """Find entity by ID with caching support."""
        try:
            cache_key = f"{self._table_name}:{entity_id}"
            
            # Try cache first
            if self._cache_enabled:
                cached = self._get_from_cache(cache_key)
                if cached is not None:
                    self._stats.cache_hits += 1
                    return cached
                self._stats.cache_misses += 1
            
            # Query storage
            data = self._storage.select(
                self._table_name,
                filters={self._key_field: entity_id},
                limit=1
            )
            
            if not data:
                return None
            
            entity = self._deserialize_entity(data[0])
            
            # Cache the result
            if self._cache_enabled:
                self._set_cache(cache_key, entity)
            
            return entity
            
        except Exception as e:
            self._logger.error(f"Failed to find entity {entity_id}: {e}")
            raise StorageException(f"Failed to find entity: {e}") from e
    
    def find_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """Find all entities with optional filters."""
        try:
            data = self._storage.select(
                self._table_name,
                filters=filters
            )
            
            entities = [self._deserialize_entity(row) for row in data]
            
            # Cache individual entities
            if self._cache_enabled:
                for entity in entities:
                    cache_key = f"{self._table_name}:{entity.id}"
                    self._set_cache(cache_key, entity)
            
            return entities
            
        except Exception as e:
            self._logger.error(f"Failed to find entities: {e}")
            raise StorageException(f"Failed to find entities: {e}") from e
    
    def update(self, entity: T) -> T:
        """Update existing entity."""
        if not self.exists(entity.id):
            raise StorageException(f"Entity {entity.id} does not exist")
        
        return self.save(entity)
    
    def delete(self, entity_id: K) -> bool:
        """Delete entity by ID with events."""
        try:
            if not self.exists(entity_id):
                return False
            
            # Before delete events
            if self._events_enabled:
                for callback in self._before_delete_callbacks:
                    callback(entity_id)
            
            # Delete from storage
            success = self._storage.delete(self._table_name, entity_id)
            
            if success:
                # Remove from cache
                if self._cache_enabled:
                    cache_key = f"{self._table_name}:{entity_id}"
                    self._invalidate_cache(cache_key)
                
                # After delete events
                if self._events_enabled:
                    for callback in self._after_delete_callbacks:
                        callback(entity_id)
                
                # Update statistics
                self._stats.total_entities -= 1
                
                self._logger.debug(f"Deleted entity {entity_id}")
            
            return success
            
        except Exception as e:
            self._logger.error(f"Failed to delete entity {entity_id}: {e}")
            raise StorageException(f"Failed to delete entity: {e}") from e
    
    def delete_all(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Delete multiple entities with filters."""
        try:
            # Get entities to delete for event callbacks
            entities_to_delete = self.find_all(filters)
            
            # Trigger before delete events
            if self._events_enabled:
                for entity in entities_to_delete:
                    for callback in self._before_delete_callbacks:
                        callback(entity.id)
            
            # Delete from storage
            deleted_count = 0
            for entity in entities_to_delete:
                if self._storage.delete(self._table_name, entity.id):
                    deleted_count += 1
                    
                    # Remove from cache
                    if self._cache_enabled:
                        cache_key = f"{self._table_name}:{entity.id}"
                        self._invalidate_cache(cache_key)
            
            # Trigger after delete events
            if self._events_enabled:
                for entity in entities_to_delete:
                    for callback in self._after_delete_callbacks:
                        callback(entity.id)
            
            # Update statistics
            self._stats.total_entities -= deleted_count
            
            self._logger.debug(f"Deleted {deleted_count} entities")
            return deleted_count
            
        except Exception as e:
            self._logger.error(f"Failed to delete entities: {e}")
            raise StorageException(f"Failed to delete entities: {e}") from e
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filters."""
        try:
            entities = self.find_all(filters)
            return len(entities)
        except Exception as e:
            self._logger.error(f"Failed to count entities: {e}")
            raise StorageException(f"Failed to count entities: {e}") from e
    
    def exists(self, entity_id: K) -> bool:
        """Check if entity exists."""
        try:
            return self.find_by_id(entity_id) is not None
        except Exception as e:
            self._logger.error(f"Failed to check entity existence {entity_id}: {e}")
            return False
    
    def get_stats(self) -> RepositoryStats:
        """Get repository statistics."""
        # Update total count
        self._stats.total_entities = self.count()
        return self._stats
    
    # Event callback management
    def add_before_save_callback(self, callback: Callable[[T], None]) -> None:
        """Add before save event callback."""
        self._before_save_callbacks.append(callback)
    
    def add_after_save_callback(self, callback: Callable[[T], None]) -> None:
        """Add after save event callback."""
        self._after_save_callbacks.append(callback)
    
    def add_before_delete_callback(self, callback: Callable[[K], None]) -> None:
        """Add before delete event callback."""
        self._before_delete_callbacks.append(callback)
    
    def add_after_delete_callback(self, callback: Callable[[K], None]) -> None:
        """Add after delete event callback."""
        self._after_delete_callbacks.append(callback)
    
    # Abstract methods for subclasses
    def _serialize_entity(self, entity: T) -> Dict[str, Any]:
        """Serialize entity to storage format. Override in subclasses."""
        # Default implementation using entity.__dict__
        data = {}
        for key, value in entity.__dict__.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, UUID):
                data[key] = str(value)
            else:
                data[key] = value
        return data
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> T:
        """Deserialize entity from storage format. Override in subclasses."""
        # This is a basic implementation - subclasses should override
        # for proper entity construction
        try:
            return self._entity_type(**data)
        except Exception as e:
            raise StorageException(f"Failed to deserialize entity: {e}") from e
    
    def _validate_entity(self, entity: T) -> None:
        """Validate entity before save. Override in subclasses."""
        if not isinstance(entity, self._entity_type):
            raise StorageException(f"Entity must be of type {self._entity_type.__name__}")
        
        if entity.id is None:
            raise StorageException("Entity ID cannot be None")
    
    def _create_entity(self, entity: T) -> T:
        """Create new entity in storage."""
        data = self._serialize_entity(entity)
        created_id = self._storage.insert(self._table_name, data)
        
        # If ID was generated by storage, update entity
        if created_id != entity.id:
            # Update entity with generated ID (implementation specific)
            pass
        
        return entity
    
    def _update_entity(self, entity: T) -> T:
        """Update existing entity in storage."""
        data = self._serialize_entity(entity)
        success = self._storage.update(self._table_name, entity.id, data)
        
        if not success:
            raise StorageException(f"Failed to update entity {entity.id}")
        
        # Invalidate cache
        if self._cache_enabled:
            cache_key = f"{self._table_name}:{entity.id}"
            self._invalidate_cache(cache_key)
        
        return entity
    
    # Cache operations (basic implementation - can be enhanced)
    def _get_from_cache(self, key: str) -> Optional[T]:
        """Get entity from cache. Override for actual cache implementation."""
        return None
    
    def _set_cache(self, key: str, entity: T) -> None:
        """Set entity in cache. Override for actual cache implementation."""
        pass
    
    def _invalidate_cache(self, key: str) -> None:
        """Invalidate cache entry. Override for actual cache implementation."""
        pass