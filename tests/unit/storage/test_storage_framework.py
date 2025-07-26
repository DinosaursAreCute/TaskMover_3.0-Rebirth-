"""
Tests for Storage & Persistence Framework
========================================

Test the core storage framework components including backends,
repositories, transactions, and caching.
"""

import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from uuid import uuid4

# Import storage framework components directly without going through main package
import sys
import os
import importlib.util

# Add the path and import components directly
base_path = os.path.join(os.path.dirname(__file__), '../../../taskmover/core/storage')

# Import the storage module components
spec = importlib.util.spec_from_file_location("storage_init", os.path.join(base_path, "__init__.py"))
storage_module = importlib.util.module_from_spec(spec)

# Import exceptions
spec_exc = importlib.util.spec_from_file_location("exceptions", os.path.join(os.path.dirname(__file__), '../../../taskmover/core/exceptions.py'))
exceptions_module = importlib.util.module_from_spec(spec_exc)
spec_exc.loader.exec_module(exceptions_module)
StorageException = exceptions_module.StorageException

# Load storage components
spec.loader.exec_module(storage_module)

# Extract what we need
StorageBackend = storage_module.StorageBackend
StorageConfig = storage_module.StorageConfig
IEntity = storage_module.IEntity
TransactionState = storage_module.TransactionState

# Import backends
spec_backends = importlib.util.spec_from_file_location("backends", os.path.join(base_path, "backends.py"))
backends_module = importlib.util.module_from_spec(spec_backends)
spec_backends.loader.exec_module(backends_module)

FileSystemBackend = backends_module.FileSystemBackend
SQLiteBackend = backends_module.SQLiteBackend  
MemoryBackend = backends_module.MemoryBackend

# Import repository
spec_repo = importlib.util.spec_from_file_location("repository", os.path.join(base_path, "repository.py"))
repo_module = importlib.util.module_from_spec(spec_repo)
spec_repo.loader.exec_module(repo_module)

BaseRepository = repo_module.BaseRepository

# Import transaction
spec_tx = importlib.util.spec_from_file_location("transaction", os.path.join(base_path, "transaction.py"))
tx_module = importlib.util.module_from_spec(spec_tx)
spec_tx.loader.exec_module(tx_module)

Transaction = tx_module.Transaction
TransactionManager = tx_module.TransactionManager

# Import migration
spec_migration = importlib.util.spec_from_file_location("migration", os.path.join(base_path, "migration.py"))
migration_module = importlib.util.module_from_spec(spec_migration)
spec_migration.loader.exec_module(migration_module)

MigrationManager = migration_module.MigrationManager
CreateTableMigration = migration_module.CreateTableMigration

# Import cache
spec_cache = importlib.util.spec_from_file_location("cache", os.path.join(base_path, "cache.py"))
cache_module = importlib.util.module_from_spec(spec_cache)
spec_cache.loader.exec_module(cache_module)

LRUCache = cache_module.LRUCache
MultiLevelCacheManager = cache_module.MultiLevelCacheManager


class TestEntity(IEntity):
    """Test entity for storage testing."""
    
    def __init__(self, id=None, name=None, created_at=None, updated_at=None):
        self._id = id or str(uuid4())
        self.name = name or "test"
        self._created_at = created_at or datetime.now()
        self._updated_at = updated_at or datetime.now()
    
    @property
    def id(self):
        return self._id
    
    @property
    def created_at(self):
        return self._created_at
    
    @property
    def updated_at(self):
        return self._updated_at


class TestRepository(BaseRepository):
    """Test repository implementation."""
    
    def __init__(self, storage_backend):
        super().__init__(storage_backend, TestEntity, "test_entities", "id")
    
    def _serialize_entity(self, entity):
        return {
            'id': entity.id,
            'name': entity.name,
            'created_at': entity.created_at.isoformat(),
            'updated_at': entity.updated_at.isoformat()
        }
    
    def _deserialize_entity(self, data):
        return TestEntity(
            id=data['id'],
            name=data['name'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )


def test_file_system_backend():
    """Test file system storage backend."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Configure and connect
        config = StorageConfig(
            backend=StorageBackend.FILE_SYSTEM,
            connection_string=temp_dir
        )
        
        backend = FileSystemBackend()
        backend.connect(config)
        
        # Create table
        schema = {
            'id': {'type': 'TEXT', 'primary_key': True},
            'name': {'type': 'TEXT'},
            'created_at': {'type': 'TEXT'}
        }
        backend.create_table("test_table", schema)
        
        # Test insert
        data = {
            'id': 'test1',
            'name': 'Test Item',
            'created_at': datetime.now().isoformat()
        }
        result_id = backend.insert("test_table", data)
        assert result_id == 'test1'
        
        # Test select
        results = backend.select("test_table")
        assert len(results) == 1
        assert results[0]['name'] == 'Test Item'
        
        # Test update
        success = backend.update("test_table", 'test1', {'name': 'Updated Item'})
        assert success is True
        
        # Verify update
        results = backend.select("test_table", filters={'id': 'test1'})
        assert results[0]['name'] == 'Updated Item'
        
        # Test delete
        success = backend.delete("test_table", 'test1')
        assert success is True
        
        # Verify delete
        results = backend.select("test_table")
        assert len(results) == 0
        
        backend.disconnect()


def test_memory_backend():
    """Test in-memory storage backend."""
    config = StorageConfig(
        backend=StorageBackend.MEMORY,
        connection_string=""
    )
    
    backend = MemoryBackend()
    backend.connect(config)
    
    # Test basic operations
    backend.create_table("test_table", {})
    
    data = {'id': 'test1', 'name': 'Test Item'}
    result_id = backend.insert("test_table", data)
    assert result_id == 'test1'
    
    results = backend.select("test_table")
    assert len(results) == 1
    
    success = backend.update("test_table", 'test1', {'name': 'Updated'})
    assert success is True
    
    success = backend.delete("test_table", 'test1')
    assert success is True
    
    backend.disconnect()


def test_repository_operations():
    """Test repository CRUD operations."""
    # Use memory backend for testing
    config = StorageConfig(
        backend=StorageBackend.MEMORY,
        connection_string=""
    )
    
    backend = MemoryBackend()
    backend.connect(config)
    
    # Create repository
    repo = TestRepository(backend)
    
    # Create table
    schema = {
        'id': {'type': 'TEXT', 'primary_key': True},
        'name': {'type': 'TEXT'},
        'created_at': {'type': 'TEXT'},
        'updated_at': {'type': 'TEXT'}
    }
    backend.create_table("test_entities", schema)
    
    # Test save (create)
    entity = TestEntity(name="Test Entity")
    saved_entity = repo.save(entity)
    assert saved_entity.id == entity.id
    assert saved_entity.name == "Test Entity"
    
    # Test find by ID
    found_entity = repo.find_by_id(entity.id)
    assert found_entity is not None
    assert found_entity.name == "Test Entity"
    
    # Test update
    entity.name = "Updated Entity"
    updated_entity = repo.update(entity)
    assert updated_entity.name == "Updated Entity"
    
    # Test find all
    entities = repo.find_all()
    assert len(entities) == 1
    
    # Test exists
    assert repo.exists(entity.id) is True
    assert repo.exists("nonexistent") is False
    
    # Test count
    assert repo.count() == 1
    
    # Test delete
    success = repo.delete(entity.id)
    assert success is True
    assert repo.count() == 0


def test_lru_cache():
    """Test LRU cache implementation."""
    cache = LRUCache(max_size=3)
    
    # Test basic operations
    cache.set("key1", "value1")
    cache.set("key2", "value2") 
    cache.set("key3", "value3")
    
    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"
    
    # Test eviction (should evict key1 as least recently used)
    cache.set("key4", "value4")
    assert cache.get("key1") is None  # Should be evicted
    assert cache.get("key4") == "value4"
    
    # Test TTL
    cache.set("ttl_key", "ttl_value", ttl=1)  # 1 second TTL
    assert cache.get("ttl_key") == "ttl_value"
    
    # Test stats
    stats = cache.get_stats()
    assert stats.entries > 0
    assert stats.hits > 0


def test_multi_level_cache():
    """Test multi-level cache manager."""
    l1_cache = LRUCache(max_size=2)
    
    cache_manager = MultiLevelCacheManager(l1_cache=l1_cache)
    
    # Test basic operations
    cache_manager.set("key1", "value1")
    assert cache_manager.get("key1") == "value1"
    
    # Test deletion
    assert cache_manager.delete("key1") is True
    assert cache_manager.get("key1") is None
    
    # Test stats
    stats = cache_manager.get_stats()
    assert "l1" in stats


def test_transaction_basic():
    """Test basic transaction functionality."""
    config = StorageConfig(
        backend=StorageBackend.MEMORY,
        connection_string=""
    )
    
    backend = MemoryBackend()
    backend.connect(config)
    
    # Create transaction
    transaction = Transaction(uuid4(), backend)
    
    # Add operations
    transaction.add_operation("INSERT", "test_table", {"id": "1", "name": "test"})
    
    # Test state
    from taskmover.core.storage import TransactionState
    assert transaction.state == TransactionState.ACTIVE
    
    # Create table for transaction
    backend.create_table("test_table", {})
    
    # Commit transaction
    transaction.commit()
    assert transaction.state == TransactionState.COMMITTED


def test_migration_manager():
    """Test migration management."""
    config = StorageConfig(
        backend=StorageBackend.MEMORY,
        connection_string=""
    )
    
    backend = MemoryBackend()
    backend.connect(config)
    
    # Create migration manager
    migration_manager = MigrationManager(backend)
    
    # Create a test migration
    schema = {
        'id': {'type': 'TEXT', 'primary_key': True},
        'name': {'type': 'TEXT'}
    }
    migration = CreateTableMigration("001", "test_table", schema)
    
    # Register and apply migration
    migration_manager.register_migration(migration)
    applied = migration_manager.apply_migrations()
    
    assert "001" in applied
    assert "001" in migration_manager.get_applied_migrations()


if __name__ == "__main__":
    # Run tests manually if not using pytest
    print("Running storage framework tests...")
    
    try:
        test_memory_backend()
        print("✅ Memory backend test passed")
        
        test_file_system_backend()
        print("✅ File system backend test passed")
        
        test_repository_operations()
        print("✅ Repository operations test passed")
        
        test_lru_cache()
        print("✅ LRU cache test passed")
        
        test_multi_level_cache()
        print("✅ Multi-level cache test passed")
        
        test_transaction_basic()
        print("✅ Transaction test passed")
        
        test_migration_manager()
        print("✅ Migration manager test passed")
        
        print("\n🎉 All storage framework tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise