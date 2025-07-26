# Storage & Persistence Framework Documentation

## Overview

The Storage & Persistence Framework provides a comprehensive, generic storage system for TaskMover with the following key features:

- **Data Repository Pattern**: Generic repository interfaces for all data types
- **Multiple Storage Backends**: File System, SQLite, and In-Memory storage
- **Transaction Support**: Atomic operations with rollback capabilities
- **Data Migration System**: Schema evolution and version management
- **Multi-Level Cache Management**: Performance optimization with LRU caching
- **Thread-Safe Operations**: Safe concurrent access to storage resources

## Architecture

```
storage/
├── __init__.py              # Main interfaces and exports
├── backends.py              # Storage backend implementations
├── repository.py            # Generic repository base class
├── transaction.py           # Transaction management
├── migration.py             # Data migration system
└── cache.py                 # Multi-level caching system
```

## Core Interfaces

### IRepository
Generic repository interface for data persistence:
```python
class IRepository(ABC, Generic[T, K]):
    def save(self, entity: T) -> T
    def find_by_id(self, entity_id: K) -> Optional[T]
    def find_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]
    def update(self, entity: T) -> T
    def delete(self, entity_id: K) -> bool
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int
    def exists(self, entity_id: K) -> bool
```

### IStorageBackend
Storage backend interface for different storage types:
```python
class IStorageBackend(ABC):
    def connect(self, config: StorageConfig) -> None
    def create_table(self, table_name: str, schema: Dict[str, Any]) -> None
    def insert(self, table_name: str, data: Dict[str, Any]) -> Any
    def select(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]
    def update(self, table_name: str, entity_id: Any, data: Dict[str, Any]) -> bool
    def delete(self, table_name: str, entity_id: Any) -> bool
```

## Storage Backends

### FileSystemBackend
- **Purpose**: JSON file-based storage with directory structure
- **Features**: Atomic writes, backup support, thread-safe operations
- **Use Case**: Small to medium datasets, human-readable storage

### SQLiteBackend  
- **Purpose**: Relational database storage
- **Features**: SQL queries, transaction support, connection pooling
- **Use Case**: Complex queries, larger datasets, ACID compliance

### MemoryBackend
- **Purpose**: In-memory storage for testing and temporary data
- **Features**: Fast operations, no persistence
- **Use Case**: Testing, caching, temporary data

## Usage Examples

### Basic Repository Usage

```python
from taskmover.core.storage import (
    MemoryBackend, StorageConfig, StorageBackend, BaseRepository
)

# Configure storage
config = StorageConfig(
    backend=StorageBackend.MEMORY,
    connection_string=""
)

# Create backend and connect
backend = MemoryBackend()
backend.connect(config)

# Create repository
class MyEntity:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class MyRepository(BaseRepository):
    def __init__(self, backend):
        super().__init__(backend, MyEntity, "my_entities", "id")

repo = MyRepository(backend)

# Use repository
entity = MyEntity("1", "Test")
saved = repo.save(entity)
found = repo.find_by_id("1")
```

### Transaction Usage

```python
from taskmover.core.storage import TransactionManager

# Create transaction manager
tx_manager = TransactionManager()

# Use transaction
with tx_manager.transaction(backend) as tx:
    tx.add_operation("INSERT", "table1", {"id": "1", "data": "test"})
    tx.add_operation("UPDATE", "table2", {"field": "value"}, entity_id="2")
    # Automatically commits on success, rolls back on exception
```

### Migration Usage

```python
from taskmover.core.storage import MigrationManager, CreateTableMigration

# Create migration manager
migration_manager = MigrationManager(backend)

# Define migration
schema = {
    'id': {'type': 'TEXT', 'primary_key': True},
    'name': {'type': 'TEXT', 'not_null': True}
}
migration = CreateTableMigration("001", "users", schema)

# Apply migration
migration_manager.register_migration(migration)
applied = migration_manager.apply_migrations()
```

### Cache Usage

```python
from taskmover.core.storage import LRUCache, MultiLevelCacheManager

# Create caches
l1_cache = LRUCache(max_size=100, default_ttl=300)
cache_manager = MultiLevelCacheManager(l1_cache=l1_cache)

# Use cache
cache_manager.set("key", "value", ttl=600)
value = cache_manager.get("key")
```

## Configuration

### StorageConfig
```python
@dataclass
class StorageConfig:
    backend: StorageBackend           # Storage backend type
    connection_string: str            # Connection details
    pool_size: Optional[int] = None   # Connection pool size
    timeout: Optional[int] = None     # Operation timeout
    auto_create: bool = True          # Auto-create directories/tables
    backup_enabled: bool = True       # Enable automatic backups
    versioning_enabled: bool = True   # Enable entity versioning
```

## Error Handling

The framework uses structured exceptions:

```python
from taskmover.core.exceptions import StorageException

try:
    repository.save(entity)
except StorageException as e:
    logger.error(f"Storage operation failed: {e}")
```

## Performance Features

### Multi-Level Caching
- **L1 Cache**: In-memory LRU cache for frequently accessed data
- **L2 Cache**: Persistent file cache for larger datasets
- **Auto-promotion**: Frequently accessed items promoted to faster cache levels

### Optimization Features
- Connection pooling for database backends
- Batch operations for bulk data processing  
- Lazy loading for large datasets
- Query result caching with TTL
- Automatic cache invalidation

## Thread Safety

All components are designed to be thread-safe:
- Storage backends use locks for concurrent access
- Repositories support concurrent operations
- Cache implementations use thread-safe data structures
- Transaction isolation prevents data corruption

## Testing

The framework includes comprehensive tests:

```bash
# Run storage framework tests
python tests/unit/storage/test_direct_storage.py
```

Test coverage includes:
- All storage backends (Memory, File, SQLite)
- Repository CRUD operations
- Transaction commit/rollback scenarios
- Cache eviction policies
- Migration application and rollback
- Concurrent access patterns

## Integration with TaskMover

The Storage & Persistence Framework integrates with existing TaskMover components:

- **Settings System**: Uses file-based storage for configuration
- **Pattern System**: Repositories for pattern storage and caching
- **Rule System**: Persistent rule storage with versioning
- **Conflict Resolution**: Transaction support for atomic conflict resolution
- **Logging System**: Integration for audit trails and monitoring

## Future Enhancements

Planned improvements for the framework:

1. **Database Backends**: PostgreSQL, MySQL support
2. **Cloud Storage**: S3, Azure Blob integration
3. **Replication**: Master-slave replication for high availability
4. **Sharding**: Horizontal scaling for large datasets
5. **Query Language**: Advanced query capabilities
6. **Schema Validation**: Automatic schema validation and evolution
7. **Compression**: Data compression for storage optimization
8. **Encryption**: At-rest and in-transit encryption

## Conclusion

The Storage & Persistence Framework provides a robust, scalable foundation for data management in TaskMover. It supports multiple storage backends, ensures data consistency through transactions, and provides high performance through multi-level caching.

The generic repository pattern allows easy integration with existing TaskMover components while maintaining clean separation of concerns and enabling future enhancements.