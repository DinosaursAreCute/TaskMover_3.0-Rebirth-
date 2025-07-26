"""
Storage Backend Implementations
==============================

Concrete implementations of storage backends including file system,
SQLite database, and in-memory storage.
"""

import json
import sqlite3
import threading
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from . import IStorageBackend, StorageConfig, StorageBackend
from ..exceptions import StorageException


class FileSystemBackend(IStorageBackend):
    """
    File system-based storage backend.
    
    Features:
    - JSON file storage
    - Atomic write operations
    - Backup support
    - Thread-safe operations
    """
    
    def __init__(self):
        self._config: Optional[StorageConfig] = None
        self._base_path: Optional[Path] = None
        self._lock = threading.RLock()
        self._logger = logging.getLogger(f"{__name__}.FileSystemBackend")
        self._connected = False
    
    def connect(self, config: StorageConfig) -> None:
        """Connect to file system storage."""
        if config.backend != StorageBackend.FILE_SYSTEM:
            raise StorageException(f"Invalid backend type: {config.backend}")
        
        self._config = config
        self._base_path = Path(config.connection_string)
        
        # Create base directory if needed
        if config.auto_create:
            self._base_path.mkdir(parents=True, exist_ok=True)
        
        self._connected = True
        self._logger.info(f"Connected to file system storage at {self._base_path}")
    
    def disconnect(self) -> None:
        """Disconnect from file system storage."""
        self._connected = False
        self._config = None
        self._base_path = None
        self._logger.info("Disconnected from file system storage")
    
    def create_table(self, table_name: str, schema: Dict[str, Any]) -> None:
        """Create table (directory) with schema file."""
        self._ensure_connected()
        
        with self._lock:
            table_dir = self._base_path / table_name
            table_dir.mkdir(exist_ok=True)
            
            # Store schema information
            schema_file = table_dir / "_schema.json"
            with open(schema_file, 'w') as f:
                json.dump(schema, f, indent=2)
            
            self._logger.debug(f"Created table {table_name}")
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> Any:
        """Insert data into table (create JSON file)."""
        self._ensure_connected()
        
        with self._lock:
            table_dir = self._base_path / table_name
            if not table_dir.exists():
                self.create_table(table_name, {})
            
            # Generate ID if not provided
            entity_id = data.get('id')
            if not entity_id:
                # Use timestamp-based ID for file system
                entity_id = f"{datetime.now().timestamp():.6f}"
                data['id'] = entity_id
            
            # Write data to file
            file_path = table_dir / f"{entity_id}.json"
            temp_path = table_dir / f"{entity_id}.json.tmp"
            
            # Atomic write operation
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            temp_path.rename(file_path)
            
            self._logger.debug(f"Inserted entity {entity_id} into {table_name}")
            return entity_id
    
    def select(self, table_name: str, filters: Optional[Dict[str, Any]] = None,
               order_by: Optional[List[str]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Select data from table (read JSON files)."""
        self._ensure_connected()
        
        with self._lock:
            table_dir = self._base_path / table_name
            if not table_dir.exists():
                return []
            
            results = []
            
            # Read all JSON files in directory
            for file_path in table_dir.glob("*.json"):
                if file_path.name.startswith("_"):  # Skip metadata files
                    continue
                
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Apply filters
                    if filters and not self._matches_filters(data, filters):
                        continue
                    
                    results.append(data)
                    
                except (json.JSONDecodeError, IOError) as e:
                    self._logger.warning(f"Failed to read {file_path}: {e}")
                    continue
            
            # Apply ordering
            if order_by:
                for field in reversed(order_by):
                    reverse = field.startswith('-')
                    field_name = field[1:] if reverse else field
                    results.sort(key=lambda x: x.get(field_name, ''), reverse=reverse)
            
            # Apply limit
            if limit and limit > 0:
                results = results[:limit]
            
            return results
    
    def update(self, table_name: str, entity_id: Any, data: Dict[str, Any]) -> bool:
        """Update entity data."""
        self._ensure_connected()
        
        with self._lock:
            table_dir = self._base_path / table_name
            file_path = table_dir / f"{entity_id}.json"
            
            if not file_path.exists():
                return False
            
            # Read existing data
            try:
                with open(file_path, 'r') as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                return False
            
            # Merge data
            existing_data.update(data)
            existing_data['updated_at'] = datetime.now().isoformat()
            
            # Atomic write
            temp_path = table_dir / f"{entity_id}.json.tmp"
            with open(temp_path, 'w') as f:
                json.dump(existing_data, f, indent=2, default=str)
            
            temp_path.rename(file_path)
            
            self._logger.debug(f"Updated entity {entity_id} in {table_name}")
            return True
    
    def delete(self, table_name: str, entity_id: Any) -> bool:
        """Delete entity by ID."""
        self._ensure_connected()
        
        with self._lock:
            table_dir = self._base_path / table_name
            file_path = table_dir / f"{entity_id}.json"
            
            if not file_path.exists():
                return False
            
            # Create backup if enabled
            if self._config.backup_enabled:
                backup_dir = table_dir / "_deleted"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"{entity_id}_{datetime.now().timestamp()}.json"
                file_path.rename(backup_path)
            else:
                file_path.unlink()
            
            self._logger.debug(f"Deleted entity {entity_id} from {table_name}")
            return True
    
    def execute_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute raw SQL (not supported by file system backend)."""
        raise StorageException("Raw SQL execution not supported by file system backend")
    
    def _ensure_connected(self) -> None:
        """Ensure backend is connected."""
        if not self._connected:
            raise StorageException("Backend not connected")
    
    def _matches_filters(self, data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if data matches filters."""
        for key, value in filters.items():
            if key not in data:
                return False
            
            data_value = data[key]
            
            # Handle different filter types
            if isinstance(value, dict):
                # Range filters like {'$gte': 10, '$lt': 20}
                for op, filter_value in value.items():
                    if op == '$gte' and not (data_value >= filter_value):
                        return False
                    elif op == '$gt' and not (data_value > filter_value):
                        return False
                    elif op == '$lte' and not (data_value <= filter_value):
                        return False
                    elif op == '$lt' and not (data_value < filter_value):
                        return False
                    elif op == '$ne' and data_value == filter_value:
                        return False
                    elif op == '$in' and data_value not in filter_value:
                        return False
                    elif op == '$nin' and data_value in filter_value:
                        return False
            else:
                # Direct equality
                if data_value != value:
                    return False
        
        return True


class SQLiteBackend(IStorageBackend):
    """
    SQLite database storage backend.
    
    Features:
    - Relational database storage
    - SQL query support
    - Transaction support
    - Connection pooling
    """
    
    def __init__(self):
        self._config: Optional[StorageConfig] = None
        self._db_path: Optional[Path] = None
        self._connection: Optional[sqlite3.Connection] = None
        self._lock = threading.RLock()
        self._logger = logging.getLogger(f"{__name__}.SQLiteBackend")
        self._connected = False
    
    def connect(self, config: StorageConfig) -> None:
        """Connect to SQLite database."""
        if config.backend != StorageBackend.SQLITE:
            raise StorageException(f"Invalid backend type: {config.backend}")
        
        self._config = config
        self._db_path = Path(config.connection_string)
        
        # Create directory if needed
        if config.auto_create:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        self._connection = sqlite3.connect(
            str(self._db_path),
            timeout=config.timeout or 30,
            check_same_thread=False
        )
        self._connection.row_factory = sqlite3.Row  # Enable dict-like access
        
        self._connected = True
        self._logger.info(f"Connected to SQLite database at {self._db_path}")
    
    def disconnect(self) -> None:
        """Disconnect from SQLite database."""
        if self._connection:
            self._connection.close()
            self._connection = None
        
        self._connected = False
        self._config = None
        self._db_path = None
        self._logger.info("Disconnected from SQLite database")
    
    def create_table(self, table_name: str, schema: Dict[str, Any]) -> None:
        """Create table with schema."""
        self._ensure_connected()
        
        with self._lock:
            # Convert schema to SQL
            columns = []
            for field_name, field_def in schema.items():
                column_def = f"{field_name} {field_def.get('type', 'TEXT')}"
                
                if field_def.get('primary_key'):
                    column_def += " PRIMARY KEY"
                if field_def.get('not_null'):
                    column_def += " NOT NULL"
                if 'default' in field_def:
                    column_def += f" DEFAULT {field_def['default']}"
                
                columns.append(column_def)
            
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            
            cursor = self._connection.cursor()
            cursor.execute(sql)
            self._connection.commit()
            
            self._logger.debug(f"Created table {table_name}")
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> Any:
        """Insert data into table."""
        self._ensure_connected()
        
        with self._lock:
            columns = list(data.keys())
            placeholders = ', '.join(['?' for _ in columns])
            values = list(data.values())
            
            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            cursor = self._connection.cursor()
            cursor.execute(sql, values)
            self._connection.commit()
            
            entity_id = cursor.lastrowid or data.get('id')
            
            self._logger.debug(f"Inserted entity {entity_id} into {table_name}")
            return entity_id
    
    def select(self, table_name: str, filters: Optional[Dict[str, Any]] = None,
               order_by: Optional[List[str]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Select data from table."""
        self._ensure_connected()
        
        with self._lock:
            sql = f"SELECT * FROM {table_name}"
            params = []
            
            # Add WHERE clause
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(f"{key} = ?")
                    params.append(value)
                sql += f" WHERE {' AND '.join(conditions)}"
            
            # Add ORDER BY clause
            if order_by:
                sql += f" ORDER BY {', '.join(order_by)}"
            
            # Add LIMIT clause
            if limit:
                sql += f" LIMIT {limit}"
            
            cursor = self._connection.cursor()
            cursor.execute(sql, params)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def update(self, table_name: str, entity_id: Any, data: Dict[str, Any]) -> bool:
        """Update entity data."""
        self._ensure_connected()
        
        with self._lock:
            set_clauses = []
            values = []
            
            for key, value in data.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            values.append(entity_id)  # For WHERE clause
            
            sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = ?"
            
            cursor = self._connection.cursor()
            cursor.execute(sql, values)
            self._connection.commit()
            
            affected_rows = cursor.rowcount
            
            self._logger.debug(f"Updated entity {entity_id} in {table_name}")
            return affected_rows > 0
    
    def delete(self, table_name: str, entity_id: Any) -> bool:
        """Delete entity by ID."""
        self._ensure_connected()
        
        with self._lock:
            sql = f"DELETE FROM {table_name} WHERE id = ?"
            
            cursor = self._connection.cursor()
            cursor.execute(sql, [entity_id])
            self._connection.commit()
            
            affected_rows = cursor.rowcount
            
            self._logger.debug(f"Deleted entity {entity_id} from {table_name}")
            return affected_rows > 0
    
    def execute_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute raw SQL."""
        self._ensure_connected()
        
        with self._lock:
            cursor = self._connection.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            if sql.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                self._connection.commit()
                return cursor.rowcount
    
    def _ensure_connected(self) -> None:
        """Ensure backend is connected."""
        if not self._connected:
            raise StorageException("Backend not connected")


class MemoryBackend(IStorageBackend):
    """
    In-memory storage backend for testing and temporary data.
    
    Features:
    - Fast in-memory operations
    - Thread-safe operations
    - No persistence (data lost on restart)
    """
    
    def __init__(self):
        self._config: Optional[StorageConfig] = None
        self._tables: Dict[str, Dict[Any, Dict[str, Any]]] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._logger = logging.getLogger(f"{__name__}.MemoryBackend")
        self._connected = False
        self._id_counter = 0
    
    def connect(self, config: StorageConfig) -> None:
        """Connect to memory storage."""
        if config.backend != StorageBackend.MEMORY:
            raise StorageException(f"Invalid backend type: {config.backend}")
        
        self._config = config
        self._connected = True
        self._logger.info("Connected to memory storage")
    
    def disconnect(self) -> None:
        """Disconnect from memory storage."""
        self._tables.clear()
        self._schemas.clear()
        self._connected = False
        self._config = None
        self._logger.info("Disconnected from memory storage")
    
    def create_table(self, table_name: str, schema: Dict[str, Any]) -> None:
        """Create table in memory."""
        self._ensure_connected()
        
        with self._lock:
            self._tables[table_name] = {}
            self._schemas[table_name] = schema
            
            self._logger.debug(f"Created table {table_name}")
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> Any:
        """Insert data into memory table."""
        self._ensure_connected()
        
        with self._lock:
            if table_name not in self._tables:
                self.create_table(table_name, {})
            
            # Generate ID if not provided
            entity_id = data.get('id')
            if not entity_id:
                self._id_counter += 1
                entity_id = self._id_counter
                data['id'] = entity_id
            
            # Store data (deep copy to avoid reference issues)
            self._tables[table_name][entity_id] = data.copy()
            
            self._logger.debug(f"Inserted entity {entity_id} into {table_name}")
            return entity_id
    
    def select(self, table_name: str, filters: Optional[Dict[str, Any]] = None,
               order_by: Optional[List[str]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Select data from memory table."""
        self._ensure_connected()
        
        with self._lock:
            if table_name not in self._tables:
                return []
            
            results = []
            
            for entity_id, data in self._tables[table_name].items():
                # Apply filters
                if filters and not self._matches_filters(data, filters):
                    continue
                
                results.append(data.copy())
            
            # Apply ordering
            if order_by:
                for field in reversed(order_by):
                    reverse = field.startswith('-')
                    field_name = field[1:] if reverse else field
                    results.sort(key=lambda x: x.get(field_name, ''), reverse=reverse)
            
            # Apply limit
            if limit and limit > 0:
                results = results[:limit]
            
            return results
    
    def update(self, table_name: str, entity_id: Any, data: Dict[str, Any]) -> bool:
        """Update entity data in memory."""
        self._ensure_connected()
        
        with self._lock:
            if table_name not in self._tables or entity_id not in self._tables[table_name]:
                return False
            
            # Update data
            self._tables[table_name][entity_id].update(data)
            self._tables[table_name][entity_id]['updated_at'] = datetime.now().isoformat()
            
            self._logger.debug(f"Updated entity {entity_id} in {table_name}")
            return True
    
    def delete(self, table_name: str, entity_id: Any) -> bool:
        """Delete entity from memory."""
        self._ensure_connected()
        
        with self._lock:
            if table_name not in self._tables or entity_id not in self._tables[table_name]:
                return False
            
            del self._tables[table_name][entity_id]
            
            self._logger.debug(f"Deleted entity {entity_id} from {table_name}")
            return True
    
    def execute_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute raw SQL (limited support for memory backend)."""
        # Basic SQL simulation for testing
        # In a real implementation, this could use an SQL parser
        raise StorageException("Raw SQL execution not fully supported by memory backend")
    
    def _ensure_connected(self) -> None:
        """Ensure backend is connected."""
        if not self._connected:
            raise StorageException("Backend not connected")
    
    def _matches_filters(self, data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if data matches filters."""
        for key, value in filters.items():
            if key not in data or data[key] != value:
                return False
        return True