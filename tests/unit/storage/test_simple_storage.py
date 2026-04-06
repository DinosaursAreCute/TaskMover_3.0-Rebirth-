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

# Setup proper path for imports
import sys
import os
import types

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Pre-register taskmover as a namespace package to avoid executing taskmover/__init__.py
# which imports tkinter UI components that may not be available in CI
if 'taskmover' not in sys.modules:
    _taskmover_mod = types.ModuleType('taskmover')
    _taskmover_mod.__path__ = [os.path.join(_project_root, 'taskmover')]
    _taskmover_mod.__package__ = 'taskmover'
    sys.modules['taskmover'] = _taskmover_mod

from taskmover.core.storage import StorageConfig, StorageBackend
from taskmover.core.storage.backends import MemoryBackend, FileSystemBackend
from taskmover.core.storage.cache import LRUCache


def test_memory_backend():
    """Test the memory backend directly."""
    print("Testing Memory Backend...")

    # Create backend
    backend = MemoryBackend()

    # Create config
    config = StorageConfig(
        backend=StorageBackend.MEMORY,
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
        # Create backend
        backend = FileSystemBackend()
        
        # Create config
        config = StorageConfig(
            backend=StorageBackend.FILE_SYSTEM,
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
    
    # Create cache
    cache = LRUCache(max_size=3)
    
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