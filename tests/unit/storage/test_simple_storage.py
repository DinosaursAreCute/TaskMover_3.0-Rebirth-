"""
Simple Storage Framework Test
============================

Test the storage framework components with direct imports.
"""

import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from uuid import uuid4

# Add the path to import components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

# Import individual components to avoid circular dependencies
import importlib.util

def import_module_from_path(name, file_path):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_memory_backend():
    """Test the memory backend directly."""
    print("Testing Memory Backend...")
    
    # Import the backend directly
    base_path = os.path.join(os.path.dirname(__file__), '../../../taskmover/core/storage')
    backends = import_module_from_path("backends", os.path.join(base_path, "backends.py"))
    storage_init = import_module_from_path("storage_init", os.path.join(base_path, "__init__.py"))
    
    # Create backend
    backend = backends.MemoryBackend()
    
    # Create config
    config = storage_init.StorageConfig(
        backend=storage_init.StorageBackend.MEMORY,
        connection_string=""
    )
    
    # Test connection
    backend.connect(config)
    print("✅ Memory backend connected")
    
    # Test table creation
    backend.create_table("test_table", {})
    print("✅ Table created")
    
    # Test insert
    data = {'id': 'test1', 'name': 'Test Item'}
    result_id = backend.insert("test_table", data)
    assert result_id == 'test1'
    print("✅ Insert successful")
    
    # Test select
    results = backend.select("test_table")
    assert len(results) == 1
    assert results[0]['name'] == 'Test Item'
    print("✅ Select successful")
    
    # Test update
    success = backend.update("test_table", 'test1', {'name': 'Updated'})
    assert success is True
    print("✅ Update successful")
    
    # Test delete
    success = backend.delete("test_table", 'test1')
    assert success is True
    print("✅ Delete successful")
    
    # Test final state
    results = backend.select("test_table")
    assert len(results) == 0
    print("✅ Final verification successful")
    
    backend.disconnect()
    print("✅ Memory backend test completed")


def test_file_system_backend():
    """Test the file system backend."""
    print("\nTesting File System Backend...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Import components
        base_path = os.path.join(os.path.dirname(__file__), '../../../taskmover/core/storage')
        backends = import_module_from_path("backends", os.path.join(base_path, "backends.py"))
        storage_init = import_module_from_path("storage_init", os.path.join(base_path, "__init__.py"))
        
        # Create backend
        backend = backends.FileSystemBackend()
        
        # Create config
        config = storage_init.StorageConfig(
            backend=storage_init.StorageBackend.FILE_SYSTEM,
            connection_string=temp_dir
        )
        
        # Connect
        backend.connect(config)
        print("✅ File system backend connected")
        
        # Create table with schema
        schema = {
            'id': {'type': 'TEXT', 'primary_key': True},
            'name': {'type': 'TEXT'},
            'created_at': {'type': 'TEXT'}
        }
        backend.create_table("test_table", schema)
        print("✅ Table with schema created")
        
        # Test operations
        data = {
            'id': 'test1',
            'name': 'Test Item',
            'created_at': datetime.now().isoformat()
        }
        
        result_id = backend.insert("test_table", data)
        assert result_id == 'test1'
        print("✅ Insert successful")
        
        results = backend.select("test_table")
        assert len(results) == 1
        print("✅ Select successful")
        
        # Verify file was created
        table_dir = Path(temp_dir) / "test_table"
        assert table_dir.exists()
        assert (table_dir / "test1.json").exists()
        print("✅ File creation verified")
        
        backend.disconnect()
        print("✅ File system backend test completed")


def test_lru_cache():
    """Test the LRU cache implementation."""
    print("\nTesting LRU Cache...")
    
    # Import cache module
    base_path = os.path.join(os.path.dirname(__file__), '../../../taskmover/core/storage')
    cache_module = import_module_from_path("cache", os.path.join(base_path, "cache.py"))
    
    # Create cache
    cache = cache_module.LRUCache(max_size=3)
    
    # Test basic operations
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    
    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"
    print("✅ Basic cache operations successful")
    
    # Test eviction
    cache.set("key4", "value4")  # Should evict key1 (least recently used)
    assert cache.get("key1") is None  # Should be evicted
    assert cache.get("key4") == "value4"
    print("✅ LRU eviction successful")
    
    # Test stats
    stats = cache.get_stats()
    assert stats.entries > 0
    assert stats.hits > 0
    print("✅ Cache statistics working")
    
    print("✅ LRU cache test completed")


if __name__ == "__main__":
    print("🧪 Running Storage Framework Tests...\n")
    
    try:
        test_memory_backend()
        test_file_system_backend()
        test_lru_cache()
        
        print("\n🎉 All storage framework tests passed!")
        print("\n✅ Storage & Persistence Framework is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise