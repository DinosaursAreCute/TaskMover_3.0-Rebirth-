"""
TaskMover Storage & Persistence Framework
========================================

Generic storage and persistence framework providing:
- Data Repository Pattern interfaces
- File System Storage with versioning
- Database Abstraction for SQLite integration
- Transaction Support for atomic operations
- Data Migration system for schema evolution
- Multi-level Cache Management
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union
from pathlib import Path
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass


T = TypeVar("T")
K = TypeVar("K")  # Key type


class StorageBackend(Enum):
    """Supported storage backends"""
    FILE_SYSTEM = "filesystem"
    SQLITE = "sqlite"
    MEMORY = "memory"


class TransactionState(Enum):
    """Transaction states"""
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"


@dataclass
class StorageConfig:
    """Configuration for storage backends"""
    backend: StorageBackend
    connection_string: str
    pool_size: Optional[int] = None
    timeout: Optional[int] = None
    auto_create: bool = True
    backup_enabled: bool = True
    versioning_enabled: bool = True


@dataclass
class RepositoryStats:
    """Statistics for repository operations"""
    total_entities: int
    storage_size: int
    last_backup: Optional[datetime] = None
    last_migration: Optional[datetime] = None
    cache_hits: int = 0
    cache_misses: int = 0


class IEntity(ABC):
    """Base interface for storable entities"""
    
    @property
    @abstractmethod
    def id(self) -> K:
        """Entity unique identifier"""
        pass
    
    @property
    @abstractmethod
    def created_at(self) -> datetime:
        """Entity creation timestamp"""
        pass
    
    @property
    @abstractmethod
    def updated_at(self) -> datetime:
        """Entity last update timestamp"""
        pass


class IRepository(ABC, Generic[T, K]):
    """Generic repository interface for data persistence"""
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """Save entity to storage"""
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: K) -> Optional[T]:
        """Find entity by ID"""
        pass
    
    @abstractmethod
    def find_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """Find all entities with optional filters"""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """Update existing entity"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: K) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    def delete_all(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Delete multiple entities with filters"""
        pass
    
    @abstractmethod
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filters"""
        pass
    
    @abstractmethod
    def exists(self, entity_id: K) -> bool:
        """Check if entity exists"""
        pass


class IStorageBackend(ABC):
    """Interface for storage backend implementations"""
    
    @abstractmethod
    def connect(self, config: StorageConfig) -> None:
        """Connect to storage backend"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from storage backend"""
        pass
    
    @abstractmethod
    def create_table(self, table_name: str, schema: Dict[str, Any]) -> None:
        """Create table with schema"""
        pass
    
    @abstractmethod
    def insert(self, table_name: str, data: Dict[str, Any]) -> Any:
        """Insert data and return generated ID"""
        pass
    
    @abstractmethod
    def select(self, table_name: str, filters: Optional[Dict[str, Any]] = None,
               order_by: Optional[List[str]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Select data with filters"""
        pass
    
    @abstractmethod
    def update(self, table_name: str, entity_id: Any, data: Dict[str, Any]) -> bool:
        """Update entity data"""
        pass
    
    @abstractmethod
    def delete(self, table_name: str, entity_id: Any) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    def execute_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute raw SQL"""
        pass


class ITransaction(ABC):
    """Interface for database transactions"""
    
    @property
    @abstractmethod
    def state(self) -> TransactionState:
        """Transaction state"""
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """Commit transaction"""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Rollback transaction"""
        pass
    
    @abstractmethod
    def __enter__(self):
        """Context manager entry"""
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass


class IMigration(ABC):
    """Interface for data migrations"""
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Migration version"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Migration description"""
        pass
    
    @abstractmethod
    def up(self, storage: IStorageBackend) -> None:
        """Apply migration"""
        pass
    
    @abstractmethod
    def down(self, storage: IStorageBackend) -> None:
        """Revert migration"""
        pass


class IMigrationManager(ABC):
    """Interface for migration management"""
    
    @abstractmethod
    def register_migration(self, migration: IMigration) -> None:
        """Register a migration"""
        pass
    
    @abstractmethod
    def apply_migrations(self) -> List[str]:
        """Apply pending migrations"""
        pass
    
    @abstractmethod
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations"""
        pass
    
    @abstractmethod
    def rollback_migration(self, version: str) -> None:
        """Rollback to specific migration version"""
        pass


class IVersionManager(ABC):
    """Interface for entity versioning"""
    
    @abstractmethod
    def create_version(self, entity: T, change_description: str) -> str:
        """Create new version of entity"""
        pass
    
    @abstractmethod
    def get_version(self, entity_id: K, version: str) -> Optional[T]:
        """Get specific version of entity"""
        pass
    
    @abstractmethod
    def get_version_history(self, entity_id: K) -> List[Dict[str, Any]]:
        """Get version history for entity"""
        pass
    
    @abstractmethod
    def restore_version(self, entity_id: K, version: str) -> T:
        """Restore entity to specific version"""
        pass


# Import concrete implementations
from .backends import FileSystemBackend, SQLiteBackend, MemoryBackend
from .repository import BaseRepository
from .transaction import Transaction, TransactionManager
from .migration import MigrationManager, BaseMigration, CreateTableMigration, AddColumnMigration, DataMigration
from .cache import MultiLevelCacheManager, LRUCache, FileCache


__all__ = [
    # Enums and data classes
    "StorageBackend",
    "TransactionState", 
    "StorageConfig",
    "RepositoryStats",
    
    # Interfaces
    "IEntity",
    "IRepository",
    "IStorageBackend",
    "ITransaction",
    "IMigration",
    "IMigrationManager",
    "IVersionManager",
    
    # Implementations
    "FileSystemBackend",
    "SQLiteBackend", 
    "MemoryBackend",
    "BaseRepository",
    "Transaction",
    "TransactionManager",
    "MigrationManager",
    "BaseMigration",
    "CreateTableMigration",
    "AddColumnMigration", 
    "DataMigration",
    "MultiLevelCacheManager",
    "LRUCache",
    "FileCache",
]