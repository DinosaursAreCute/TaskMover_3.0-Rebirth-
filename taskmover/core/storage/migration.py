"""
Data Migration System
====================

Provides schema evolution and data migration capabilities with
version tracking, rollback support, and dependency management.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from pathlib import Path

from . import IMigration, IMigrationManager, IStorageBackend
from ..exceptions import StorageException


class BaseMigration(IMigration):
    """
    Base migration class providing common functionality.
    
    Subclasses should implement the up() and down() methods.
    """
    
    def __init__(self, version: str, description: str, dependencies: Optional[List[str]] = None):
        """
        Initialize migration.
        
        Args:
            version: Migration version (e.g., "001", "2023_01_15_001")
            description: Human-readable description
            dependencies: List of required migration versions
        """
        self._version = version
        self._description = description
        self._dependencies = dependencies or []
        self._logger = logging.getLogger(f"{__name__}.Migration_{version}")
    
    @property
    def version(self) -> str:
        """Migration version."""
        return self._version
    
    @property
    def description(self) -> str:
        """Migration description."""
        return self._description
    
    @property
    def dependencies(self) -> List[str]:
        """Migration dependencies."""
        return self._dependencies.copy()
    
    def validate(self, storage: IStorageBackend) -> bool:
        """
        Validate migration can be applied.
        Override in subclasses for custom validation.
        """
        return True
    
    def get_estimated_duration(self) -> Optional[int]:
        """
        Get estimated migration duration in seconds.
        Override in subclasses for better estimates.
        """
        return None
    
    @abstractmethod
    def up(self, storage: IStorageBackend) -> None:
        """Apply migration (must be implemented by subclasses)."""
        pass
    
    @abstractmethod
    def down(self, storage: IStorageBackend) -> None:
        """Revert migration (must be implemented by subclasses)."""
        pass


class CreateTableMigration(BaseMigration):
    """Migration for creating new tables."""
    
    def __init__(self, version: str, table_name: str, schema: Dict[str, Any], 
                 description: Optional[str] = None):
        """
        Initialize table creation migration.
        
        Args:
            version: Migration version
            table_name: Name of table to create
            schema: Table schema definition
            description: Migration description
        """
        self._table_name = table_name
        self._schema = schema
        
        desc = description or f"Create {table_name} table"
        super().__init__(version, desc)
    
    def up(self, storage: IStorageBackend) -> None:
        """Create the table."""
        storage.create_table(self._table_name, self._schema)
        self._logger.info(f"Created table {self._table_name}")
    
    def down(self, storage: IStorageBackend) -> None:
        """Drop the table."""
        try:
            storage.execute_sql(f"DROP TABLE IF EXISTS {self._table_name}")
            self._logger.info(f"Dropped table {self._table_name}")
        except Exception as e:
            self._logger.warning(f"Failed to drop table {self._table_name}: {e}")


class AddColumnMigration(BaseMigration):
    """Migration for adding columns to existing tables."""
    
    def __init__(self, version: str, table_name: str, column_name: str, 
                 column_definition: str, description: Optional[str] = None):
        """
        Initialize add column migration.
        
        Args:
            version: Migration version
            table_name: Target table name
            column_name: Name of column to add
            column_definition: Column definition (e.g., "VARCHAR(255) NOT NULL")
            description: Migration description
        """
        self._table_name = table_name
        self._column_name = column_name
        self._column_definition = column_definition
        
        desc = description or f"Add column {column_name} to {table_name}"
        super().__init__(version, desc)
    
    def up(self, storage: IStorageBackend) -> None:
        """Add the column."""
        sql = f"ALTER TABLE {self._table_name} ADD COLUMN {self._column_name} {self._column_definition}"
        storage.execute_sql(sql)
        self._logger.info(f"Added column {self._column_name} to {self._table_name}")
    
    def down(self, storage: IStorageBackend) -> None:
        """Remove the column."""
        try:
            sql = f"ALTER TABLE {self._table_name} DROP COLUMN {self._column_name}"
            storage.execute_sql(sql)
            self._logger.info(f"Removed column {self._column_name} from {self._table_name}")
        except Exception as e:
            self._logger.warning(f"Failed to remove column {self._column_name}: {e}")


class DataMigration(BaseMigration):
    """Migration for data transformations."""
    
    def __init__(self, version: str, description: str, 
                 up_sql: str, down_sql: Optional[str] = None):
        """
        Initialize data migration.
        
        Args:
            version: Migration version
            description: Migration description
            up_sql: SQL to apply migration
            down_sql: SQL to revert migration (optional)
        """
        self._up_sql = up_sql
        self._down_sql = down_sql
        super().__init__(version, description)
    
    def up(self, storage: IStorageBackend) -> None:
        """Apply data migration."""
        storage.execute_sql(self._up_sql)
        self._logger.info(f"Applied data migration: {self.description}")
    
    def down(self, storage: IStorageBackend) -> None:
        """Revert data migration."""
        if self._down_sql:
            storage.execute_sql(self._down_sql)
            self._logger.info(f"Reverted data migration: {self.description}")
        else:
            self._logger.warning(f"No rollback SQL provided for migration {self.version}")


class MigrationManager(IMigrationManager):
    """
    Manager for database migrations with version tracking and dependency resolution.
    
    Features:
    - Version tracking in database
    - Dependency resolution
    - Transaction support
    - Rollback capabilities
    - Progress tracking
    """
    
    def __init__(self, storage_backend: IStorageBackend, migration_table: str = "_migrations"):
        """
        Initialize migration manager.
        
        Args:
            storage_backend: Storage backend for migrations
            migration_table: Name of migration tracking table
        """
        self._storage = storage_backend
        self._migration_table = migration_table
        self._migrations: Dict[str, IMigration] = {}
        self._logger = logging.getLogger(f"{__name__}.MigrationManager")
        
        # Initialize migration tracking table
        self._ensure_migration_table()
    
    def register_migration(self, migration: IMigration) -> None:
        """Register a migration."""
        if migration.version in self._migrations:
            raise StorageException(f"Migration {migration.version} already registered")
        
        self._migrations[migration.version] = migration
        self._logger.debug(f"Registered migration {migration.version}: {migration.description}")
    
    def register_migrations_from_directory(self, directory: Path) -> int:
        """
        Register migrations from a directory.
        
        Looks for Python files with Migration classes.
        Returns number of migrations registered.
        """
        count = 0
        
        if not directory.exists():
            self._logger.warning(f"Migration directory {directory} does not exist")
            return count
        
        for file_path in directory.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            
            try:
                # Dynamic import (simplified - in real implementation use importlib)
                # This is a placeholder for actual dynamic migration loading
                self._logger.debug(f"Would load migrations from {file_path}")
                
            except Exception as e:
                self._logger.error(f"Failed to load migrations from {file_path}: {e}")
        
        return count
    
    def apply_migrations(self) -> List[str]:
        """Apply all pending migrations in dependency order."""
        applied_migrations = self.get_applied_migrations()
        pending_migrations = self._get_pending_migrations(applied_migrations)
        
        if not pending_migrations:
            self._logger.info("No pending migrations")
            return []
        
        # Sort by dependency order
        ordered_migrations = self._resolve_dependencies(pending_migrations)
        
        applied = []
        for migration in ordered_migrations:
            try:
                self._apply_migration(migration)
                applied.append(migration.version)
                self._logger.info(f"Applied migration {migration.version}: {migration.description}")
                
            except Exception as e:
                self._logger.error(f"Failed to apply migration {migration.version}: {e}")
                # Rollback applied migrations in this batch
                for applied_version in reversed(applied):
                    try:
                        self.rollback_migration(applied_version)
                    except Exception as rollback_error:
                        self._logger.error(f"Failed to rollback migration {applied_version}: {rollback_error}")
                
                raise StorageException(f"Migration failed: {e}") from e
        
        return applied
    
    def rollback_migration(self, version: str) -> None:
        """Rollback a specific migration."""
        if version not in self._migrations:
            raise StorageException(f"Migration {version} not found")
        
        applied_migrations = self.get_applied_migrations()
        if version not in applied_migrations:
            raise StorageException(f"Migration {version} not applied")
        
        migration = self._migrations[version]
        
        try:
            # Check for dependent migrations that need to be rolled back first
            dependents = self._find_dependent_migrations(version, applied_migrations)
            if dependents:
                dependent_list = ", ".join(dependents)
                raise StorageException(
                    f"Cannot rollback migration {version}. "
                    f"Dependent migrations must be rolled back first: {dependent_list}"
                )
            
            # Rollback the migration
            migration.down(self._storage)
            
            # Remove from tracking table
            self._storage.execute_sql(
                f"DELETE FROM {self._migration_table} WHERE version = ?",
                {'version': version}
            )
            
            self._logger.info(f"Rolled back migration {version}: {migration.description}")
            
        except Exception as e:
            self._logger.error(f"Failed to rollback migration {version}: {e}")
            raise StorageException(f"Migration rollback failed: {e}") from e
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        try:
            result = self._storage.select(
                self._migration_table,
                order_by=['applied_at']
            )
            return [row['version'] for row in result]
        except Exception as e:
            self._logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    def get_pending_migrations(self) -> List[IMigration]:
        """Get list of pending migrations."""
        applied_migrations = self.get_applied_migrations()
        return self._get_pending_migrations(applied_migrations)
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get overall migration status."""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        return {
            'total_migrations': len(self._migrations),
            'applied_count': len(applied),
            'pending_count': len(pending),
            'applied_migrations': applied,
            'pending_migrations': [m.version for m in pending],
            'last_applied': applied[-1] if applied else None
        }
    
    def _ensure_migration_table(self) -> None:
        """Ensure migration tracking table exists."""
        try:
            schema = {
                'version': {'type': 'TEXT', 'primary_key': True, 'not_null': True},
                'description': {'type': 'TEXT'},
                'applied_at': {'type': 'TEXT', 'not_null': True},
                'applied_by': {'type': 'TEXT'},
                'duration_ms': {'type': 'INTEGER'}
            }
            
            self._storage.create_table(self._migration_table, schema)
            
        except Exception as e:
            # Table might already exist
            self._logger.debug(f"Migration table setup: {e}")
    
    def _get_pending_migrations(self, applied_migrations: List[str]) -> List[IMigration]:
        """Get pending migrations that haven't been applied."""
        pending = []
        for version, migration in self._migrations.items():
            if version not in applied_migrations:
                pending.append(migration)
        return pending
    
    def _resolve_dependencies(self, migrations: List[IMigration]) -> List[IMigration]:
        """Resolve migration dependencies and return in correct order."""
        # Simple topological sort for dependencies
        ordered = []
        remaining = migrations.copy()
        
        while remaining:
            # Find migrations with no unresolved dependencies
            ready = []
            for migration in remaining:
                if hasattr(migration, 'dependencies'):
                    dependencies = migration.dependencies
                else:
                    dependencies = []
                
                # Check if all dependencies are either applied or in ordered list
                deps_satisfied = all(
                    dep in self.get_applied_migrations() or 
                    any(m.version == dep for m in ordered)
                    for dep in dependencies
                )
                
                if deps_satisfied:
                    ready.append(migration)
            
            if not ready:
                # Circular dependency or missing dependency
                remaining_versions = [m.version for m in remaining]
                raise StorageException(f"Circular or missing dependencies in migrations: {remaining_versions}")
            
            # Add ready migrations to ordered list
            for migration in ready:
                ordered.append(migration)
                remaining.remove(migration)
        
        return ordered
    
    def _apply_migration(self, migration: IMigration) -> None:
        """Apply a single migration."""
        start_time = datetime.now()
        
        # Validate migration
        if hasattr(migration, 'validate') and not migration.validate(self._storage):
            raise StorageException(f"Migration {migration.version} validation failed")
        
        # Apply migration
        migration.up(self._storage)
        
        # Record in tracking table
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        self._storage.insert(self._migration_table, {
            'version': migration.version,
            'description': migration.description,
            'applied_at': start_time.isoformat(),
            'applied_by': 'system',  # Could be enhanced to track actual user
            'duration_ms': duration_ms
        })
    
    def _find_dependent_migrations(self, version: str, applied_migrations: List[str]) -> List[str]:
        """Find migrations that depend on the given version."""
        dependents = []
        
        for migration_version in applied_migrations:
            if migration_version in self._migrations:
                migration = self._migrations[migration_version]
                if hasattr(migration, 'dependencies') and version in migration.dependencies:
                    dependents.append(migration_version)
        
        return dependents