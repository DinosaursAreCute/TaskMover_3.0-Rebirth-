"""
Pattern Repository

Handles storage, retrieval, and management of patterns with
YAML/JSON serialization and data persistence.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime

from ..interfaces import BasePatternComponent, IPatternRepository, ISerializationProvider
from ..models import Pattern, PatternGroup, PatternStatus, SYSTEM_GROUPS
from ..exceptions import PatternStorageError, PatternNotFoundError


class PatternRepository(BasePatternComponent, IPatternRepository):
    """
    Repository for pattern storage and retrieval.
    
    Supports YAML and JSON formats with automatic backup and migration.
    """
    
    def __init__(self, 
        storage_path: Path,
        serialization_provider: Optional[ISerializationProvider] = None,
        format: str = "yaml"):
        super().__init__("pattern_repository")
        
        self._storage_path = Path(storage_path)
        self._serialization_provider = serialization_provider or YamlSerializationProvider()
        self._format = format.lower()
        
        # Storage file paths
        self._patterns_file = self._storage_path / f"patterns.{self._format}"
        self._groups_file = self._storage_path / f"groups.{self._format}"
        self._backup_dir = self._storage_path / "backups"
        
        # In-memory caches for performance
        self._patterns_cache: Dict[UUID, Pattern] = {}
        self._groups_cache: Dict[UUID, PatternGroup] = {}
        self._cache_dirty = False
        
        # Ensure storage directory exists
        self._initialize_storage()
        
        # Load existing data
        self._load_data()
        
        self._logger.info(f"PatternRepository initialized with {len(self._patterns_cache)} patterns")
    
    def save(self, pattern: Pattern) -> None:
        """
        Save a pattern to storage.
        
        Args:
            pattern: Pattern to save
            
        Raises:
            PatternStorageError: If save operation fails
        """
        try:
            self._log_operation("save_pattern", pattern_id=str(pattern.id), pattern_name=pattern.name)
            
            # Update modified timestamp
            pattern.modified_date = datetime.utcnow()
            
            # Add to cache
            self._patterns_cache[pattern.id] = pattern
            self._cache_dirty = True
            
            # Persist to storage
            self._persist_patterns()
            
            self._logger.info(f"Pattern saved: {pattern.name} ({pattern.id})")
            
        except Exception as e:
            self._log_error(e, "save_pattern", pattern_id=str(pattern.id))
            raise PatternStorageError(f"Failed to save pattern {pattern.id}: {e}", "save")
    
    def get(self, pattern_id: UUID) -> Optional[Pattern]:
        """
        Retrieve a pattern by ID.
        
        Args:
            pattern_id: UUID of the pattern to retrieve
            
        Returns:
            Pattern if found, None otherwise
        """
        try:
            pattern = self._patterns_cache.get(pattern_id)
            if pattern:
                self._log_operation("get_pattern", pattern_id=str(pattern_id), found=True)
                return pattern
            else:
                self._log_operation("get_pattern", pattern_id=str(pattern_id), found=False)
                return None
                
        except Exception as e:
            self._log_error(e, "get_pattern", pattern_id=str(pattern_id))
            return None
    
    def get_by_name(self, name: str) -> Optional[Pattern]:
        """
        Retrieve a pattern by name.
        
        Args:
            name: Name of the pattern to retrieve
            
        Returns:
            Pattern if found, None otherwise
        """
        try:
            for pattern in self._patterns_cache.values():
                if pattern.name == name:
                    return pattern
            return None
            
        except Exception as e:
            self._log_error(e, "get_by_name", pattern_name=name)
            return None
    
    def list_patterns(self, filters: Optional[Dict[str, Any]] = None) -> List[Pattern]:
        """
        List patterns with optional filtering.
        
        Args:
            filters: Optional dictionary of filters to apply
            
        Returns:
            List of patterns matching the filters
        """
        try:
            self._log_operation("list_patterns", filter_count=len(filters) if filters else 0)
            
            patterns = list(self._patterns_cache.values())
            
            if not filters:
                return patterns
            
            # Apply filters
            filtered_patterns = []
            for pattern in patterns:
                if self._matches_filters(pattern, filters):
                    filtered_patterns.append(pattern)
            
            self._logger.debug(f"Listed {len(filtered_patterns)} patterns after filtering")
            return filtered_patterns
            
        except Exception as e:
            self._log_error(e, "list_patterns")
            return []
    
    def search_patterns(self, query: str) -> List[Pattern]:
        """
        Search patterns by name, description, or expression.
        
        Args:
            query: Search query string
            
        Returns:
            List of patterns matching the search query
        """
        try:
            self._log_operation("search_patterns", query=query)
            
            query_lower = query.lower()
            matching_patterns = []
            
            for pattern in self._patterns_cache.values():
                # Search in name, description, and expression
                if (query_lower in pattern.name.lower() or
                    query_lower in pattern.description.lower() or
                    query_lower in pattern.user_expression.lower() or
                    any(query_lower in tag.lower() for tag in pattern.tags)):
                    matching_patterns.append(pattern)
            
            self._logger.debug(f"Found {len(matching_patterns)} patterns matching '{query}'")
            return matching_patterns
            
        except Exception as e:
            self._log_error(e, "search_patterns", query=query)
            return []
    
    def delete(self, pattern_id: UUID) -> bool:
        """
        Delete a pattern by ID.
        
        Args:
            pattern_id: UUID of the pattern to delete
            
        Returns:
            True if pattern was deleted, False if not found
            
        Raises:
            PatternStorageError: If delete operation fails
        """
        try:
            self._log_operation("delete_pattern", pattern_id=str(pattern_id))
            
            if pattern_id not in self._patterns_cache:
                return False
            
            # Remove from cache
            pattern = self._patterns_cache.pop(pattern_id)
            self._cache_dirty = True
            
            # Persist changes
            self._persist_patterns()
            
            self._logger.info(f"Pattern deleted: {pattern.name} ({pattern_id})")
            return True
            
        except Exception as e:
            self._log_error(e, "delete_pattern", pattern_id=str(pattern_id))
            raise PatternStorageError(f"Failed to delete pattern {pattern_id}: {e}", "delete")
    
    def save_group(self, group: PatternGroup) -> None:
        """Save a pattern group."""
        try:
            self._log_operation("save_group", group_id=str(group.id), group_name=group.name)
            
            # Update modified timestamp
            group.modified_date = datetime.utcnow()
            
            # Add to cache
            self._groups_cache[group.id] = group
            self._cache_dirty = True
            
            # Persist to storage
            self._persist_groups()
            
            self._logger.info(f"Group saved: {group.name} ({group.id})")
            
        except Exception as e:
            self._log_error(e, "save_group", group_id=str(group.id))
            raise PatternStorageError(f"Failed to save group {group.id}: {e}", "save_group")
    
    def get_group(self, group_id: UUID) -> Optional[PatternGroup]:
        """Retrieve a pattern group by ID."""
        return self._groups_cache.get(group_id)
    
    def list_groups(self) -> List[PatternGroup]:
        """List all pattern groups."""
        # Include system groups and user-defined groups
        all_groups = list(SYSTEM_GROUPS.values()) + list(self._groups_cache.values())
        return all_groups
    
    def delete_group(self, group_id: UUID) -> bool:
        """Delete a pattern group."""
        try:
            if group_id not in self._groups_cache:
                return False
            
            # Check if group has patterns
            patterns_in_group = [p for p in self._patterns_cache.values() if p.group_id == group_id]
            if patterns_in_group:
                # Move patterns to default group (None)
                for pattern in patterns_in_group:
                    pattern.group_id = None
                    pattern.modified_date = datetime.utcnow()
                self._persist_patterns()
            
            # Remove group
            group = self._groups_cache.pop(group_id)
            self._persist_groups()
            
            self._logger.info(f"Group deleted: {group.name} ({group_id})")
            return True
            
        except Exception as e:
            self._log_error(e, "delete_group", group_id=str(group_id))
            raise PatternStorageError(f"Failed to delete group {group_id}: {e}", "delete_group")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics."""
        try:
            active_patterns = len([p for p in self._patterns_cache.values() if p.status == PatternStatus.ACTIVE])
            
            stats = {
                'total_patterns': len(self._patterns_cache),
                'active_patterns': active_patterns,
                'inactive_patterns': len(self._patterns_cache) - active_patterns,
                'total_groups': len(self._groups_cache),
                'system_groups': len(SYSTEM_GROUPS),
                'storage_path': str(self._storage_path),
                'storage_format': self._format,
                'last_modified': max(
                    (p.modified_date for p in self._patterns_cache.values()),
                    default=datetime.utcnow()
                ).isoformat()
            }
            
            return stats
            
        except Exception as e:
            self._log_error(e, "get_statistics")
            return {}
    
    def backup(self) -> Path:
        """Create a backup of all pattern data."""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_file = self._backup_dir / f"patterns_backup_{timestamp}.{self._format}"
            
            # Ensure backup directory exists
            self._backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create backup data
            backup_data = {
                'patterns': [self._pattern_to_dict(p) for p in self._patterns_cache.values()],
                'groups': [self._group_to_dict(g) for g in self._groups_cache.values()],
                'metadata': {
                    'backup_timestamp': timestamp,
                    'format_version': '1.0',
                    'pattern_count': len(self._patterns_cache),
                    'group_count': len(self._groups_cache)
                }
            }
            
            # Write backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                if self._format == 'yaml':
                    yaml.dump(backup_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
            
            self._logger.info(f"Backup created: {backup_file}")
            return backup_file
            
        except Exception as e:
            self._log_error(e, "backup")
            raise PatternStorageError(f"Failed to create backup: {e}", "backup")
    
    def restore(self, backup_file: Path) -> None:
        """Restore pattern data from backup."""
        try:
            self._log_operation("restore", backup_file=str(backup_file))
            
            if not backup_file.exists():
                raise PatternStorageError(f"Backup file not found: {backup_file}", "restore")
            
            # Load backup data
            with open(backup_file, 'r', encoding='utf-8') as f:
                if backup_file.suffix.lower() == '.yaml':
                    backup_data = yaml.safe_load(f)
                else:
                    backup_data = json.load(f)
            
            # Clear current data
            self._patterns_cache.clear()
            self._groups_cache.clear()
            
            # Restore patterns
            for pattern_data in backup_data.get('patterns', []):
                pattern = self._dict_to_pattern(pattern_data)
                self._patterns_cache[pattern.id] = pattern
            
            # Restore groups
            for group_data in backup_data.get('groups', []):
                group = self._dict_to_group(group_data)
                self._groups_cache[group.id] = group
            
            # Persist restored data
            self._persist_patterns()
            self._persist_groups()
            
            self._logger.info(f"Restored {len(self._patterns_cache)} patterns and {len(self._groups_cache)} groups")
            
        except Exception as e:
            self._log_error(e, "restore", backup_file=str(backup_file))
            raise PatternStorageError(f"Failed to restore backup: {e}", "restore")
    
    def _initialize_storage(self) -> None:
        """Initialize storage directory and files."""
        try:
            # Create storage directory
            self._storage_path.mkdir(parents=True, exist_ok=True)
            
            # Create empty files if they don't exist
            if not self._patterns_file.exists():
                self._write_empty_file(self._patterns_file)
            
            if not self._groups_file.exists():
                self._write_empty_file(self._groups_file)
            
            self._logger.debug(f"Storage initialized at {self._storage_path}")
            
        except Exception as e:
            raise PatternStorageError(f"Failed to initialize storage: {e}", "initialize")
    
    def _write_empty_file(self, file_path: Path) -> None:
        """Write an empty data structure to a file."""
        empty_data = {'patterns': [], 'groups': []} if 'patterns' in file_path.name else []
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if self._format == 'yaml':
                yaml.dump(empty_data, f)
            else:
                json.dump(empty_data, f, indent=2)
    
    def _load_data(self) -> None:
        """Load patterns and groups from storage."""
        try:
            # Load patterns
            if self._patterns_file.exists():
                with open(self._patterns_file, 'r', encoding='utf-8') as f:
                    if self._format == 'yaml':
                        data = yaml.safe_load(f) or []
                    else:
                        data = json.load(f) or []
                    
                    # Handle both list and dict formats
                    if isinstance(data, dict):
                        patterns_data = data.get('patterns', [])
                    else:
                        patterns_data = data
                    
                    for pattern_data in patterns_data:
                        pattern = self._dict_to_pattern(pattern_data)
                        self._patterns_cache[pattern.id] = pattern
            
            # Load groups
            if self._groups_file.exists():
                with open(self._groups_file, 'r', encoding='utf-8') as f:
                    if self._format == 'yaml':
                        data = yaml.safe_load(f) or []
                    else:
                        data = json.load(f) or []
                    
                    # Handle both list and dict formats
                    if isinstance(data, dict):
                        groups_data = data.get('groups', [])
                    else:
                        groups_data = data
                    
                    for group_data in groups_data:
                        group = self._dict_to_group(group_data)
                        self._groups_cache[group.id] = group
            
            self._logger.debug(f"Loaded {len(self._patterns_cache)} patterns and {len(self._groups_cache)} groups")
            
        except Exception as e:
            self._log_error(e, "load_data")
            # Continue with empty cache on load error
            self._patterns_cache.clear()
            self._groups_cache.clear()
    
    def _persist_patterns(self) -> None:
        """Persist patterns to storage."""
        try:
            patterns_data = [self._pattern_to_dict(p) for p in self._patterns_cache.values()]
            
            with open(self._patterns_file, 'w', encoding='utf-8') as f:
                if self._format == 'yaml':
                    yaml.dump(patterns_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(patterns_data, f, indent=2, ensure_ascii=False, default=str)
            
            self._cache_dirty = False
            
        except Exception as e:
            raise PatternStorageError(f"Failed to persist patterns: {e}", "persist_patterns")
    
    def _persist_groups(self) -> None:
        """Persist groups to storage."""
        try:
            groups_data = [self._group_to_dict(g) for g in self._groups_cache.values()]
            
            with open(self._groups_file, 'w', encoding='utf-8') as f:
                if self._format == 'yaml':
                    yaml.dump(groups_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(groups_data, f, indent=2, ensure_ascii=False, default=str)
            
        except Exception as e:
            raise PatternStorageError(f"Failed to persist groups: {e}", "persist_groups")
    
    def _pattern_to_dict(self, pattern: Pattern) -> Dict[str, Any]:
        """Convert pattern to dictionary for serialization."""
        return {
            'id': str(pattern.id),
            'name': pattern.name,
            'description': pattern.description,
            'user_expression': pattern.user_expression,
            'compiled_query': pattern.compiled_query,
            'pattern_complexity': pattern.pattern_complexity.value,
            'pattern_type': pattern.pattern_type.value,
            'tags': pattern.tags,
            'group_id': str(pattern.group_id) if pattern.group_id else None,
            'category': pattern.category,
            'created_date': pattern.created_date.isoformat(),
            'modified_date': pattern.modified_date.isoformat(),
            'author': pattern.author,
            'version': pattern.version,
            'status': pattern.status.value,
            'estimated_complexity': pattern.estimated_complexity,
            'cache_ttl': pattern.cache_ttl,
            'performance_hints': pattern.performance_hints,
            'usage_stats': {
                'usage_count': pattern.usage_stats.usage_count,
                'last_used': pattern.usage_stats.last_used.isoformat() if pattern.usage_stats.last_used else None,
                'avg_execution_time_ms': pattern.usage_stats.avg_execution_time_ms,
                'cache_hit_rate': pattern.usage_stats.cache_hit_rate,
                'error_rate': pattern.usage_stats.error_rate,
                'performance_score': pattern.usage_stats.performance_score
            },
            'is_valid': pattern.is_valid,
            'validation_errors': pattern.validation_errors,
            'last_validated': pattern.last_validated.isoformat() if pattern.last_validated else None,
            'extra_data': pattern.extra_data
        }
    
    def _dict_to_pattern(self, data: Dict[str, Any]) -> Pattern:
        """Convert dictionary to pattern object."""
        from ..models import PatternType, PatternComplexity, PatternStatus, PatternUsageStats
        from uuid import UUID
        
        # Handle usage stats
        usage_stats_data = data.get('usage_stats', {})
        usage_stats = PatternUsageStats(
            usage_count=usage_stats_data.get('usage_count', 0),
            last_used=datetime.fromisoformat(usage_stats_data['last_used']) if usage_stats_data.get('last_used') else None,
            avg_execution_time_ms=usage_stats_data.get('avg_execution_time_ms', 0.0),
            cache_hit_rate=usage_stats_data.get('cache_hit_rate', 0.0),
            error_rate=usage_stats_data.get('error_rate', 0.0),
            performance_score=usage_stats_data.get('performance_score', 10.0)
        )
        
        return Pattern(
            id=UUID(data['id']),
            name=data.get('name', ''),
            description=data.get('description', ''),
            user_expression=data.get('user_expression', ''),
            compiled_query=data.get('compiled_query', ''),
            pattern_complexity=PatternComplexity(data.get('pattern_complexity', 'simple')),
            pattern_type=PatternType(data.get('pattern_type', 'simple_glob')),
            tags=data.get('tags', []),
            group_id=UUID(data['group_id']) if data.get('group_id') else None,
            category=data.get('category', 'general'),
            created_date=datetime.fromisoformat(data.get('created_date', datetime.utcnow().isoformat())),
            modified_date=datetime.fromisoformat(data.get('modified_date', datetime.utcnow().isoformat())),
            author=data.get('author', ''),
            version=data.get('version', 1),
            status=PatternStatus(data.get('status', 'active')),
            estimated_complexity=data.get('estimated_complexity', 1),
            cache_ttl=data.get('cache_ttl'),
            performance_hints=data.get('performance_hints', {}),
            usage_stats=usage_stats,
            is_valid=data.get('is_valid', True),
            validation_errors=data.get('validation_errors', []),
            last_validated=datetime.fromisoformat(data['last_validated']) if data.get('last_validated') else None,
            extra_data=data.get('extra_data', {})
        )
    
    def _group_to_dict(self, group: PatternGroup) -> Dict[str, Any]:
        """Convert group to dictionary for serialization."""
        return {
            'id': str(group.id),
            'name': group.name,
            'description': group.description,
            'parent_group_id': str(group.parent_group_id) if group.parent_group_id else None,
            'color': group.color,
            'icon': group.icon,
            'sort_order': group.sort_order,
            'is_system': group.is_system,
            'is_readonly': group.is_readonly,
            'created_date': group.created_date.isoformat(),
            'modified_date': group.modified_date.isoformat(),
            'pattern_count': group.pattern_count,
            'system_patterns': group.system_patterns,
            'extra_data': group.extra_data
        }
    
    def _dict_to_group(self, data: Dict[str, Any]) -> PatternGroup:
        """Convert dictionary to group object."""
        from uuid import UUID
        
        return PatternGroup(
            id=UUID(data['id']),
            name=data.get('name', ''),
            description=data.get('description', ''),
            parent_group_id=UUID(data['parent_group_id']) if data.get('parent_group_id') else None,
            color=data.get('color', '#4A90E2'),
            icon=data.get('icon', 'folder'),
            sort_order=data.get('sort_order', 0),
            is_system=data.get('is_system', False),
            is_readonly=data.get('is_readonly', False),
            created_date=datetime.fromisoformat(data.get('created_date', datetime.utcnow().isoformat())),
            modified_date=datetime.fromisoformat(data.get('modified_date', datetime.utcnow().isoformat())),
            pattern_count=data.get('pattern_count', 0),
            system_patterns=data.get('system_patterns', []),
            extra_data=data.get('extra_data', {})
        )
    
    def _matches_filters(self, pattern: Pattern, filters: Dict[str, Any]) -> bool:
        """Check if pattern matches the given filters."""
        for key, value in filters.items():
            if key == 'status' and pattern.status.value != value:
                return False
            elif key == 'category' and pattern.category != value:
                return False
            elif key == 'group_id' and pattern.group_id != value:
                return False
            elif key == 'tags' and not any(tag in pattern.tags for tag in value):
                return False
            elif key == 'pattern_type' and pattern.pattern_type.value != value:
                return False
            elif key == 'complexity' and pattern.pattern_complexity.value != value:
                return False
        
        return True


class YamlSerializationProvider(ISerializationProvider):
    """YAML serialization provider."""
    
    def serialize(self, obj: Any) -> str:
        return yaml.dump(obj, default_flow_style=False, allow_unicode=True)
    
    def deserialize(self, data: str, target_type: type) -> Any:
        return yaml.safe_load(data)


class JsonSerializationProvider(ISerializationProvider):
    """JSON serialization provider."""
    
    def serialize(self, obj: Any) -> str:
        return json.dumps(obj, indent=2, ensure_ascii=False, default=str)
    
    def deserialize(self, data: str, target_type: type) -> Any:
        return json.loads(data)
