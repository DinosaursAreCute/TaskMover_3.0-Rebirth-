"""
Rule Repository

Handles storage, retrieval, and management of rules with
YAML serialization and data persistence.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime

from ...patterns.interfaces import BasePatternComponent
from ..models import Rule, RuleValidationResult
from ..exceptions import RuleSystemError, RuleNotFoundError


class RuleRepository(BasePatternComponent):
    """
    Repository for rule storage and retrieval.
    
    Uses YAML format for human-readable persistence with automatic backup.
    """
    
    def __init__(self, storage_path: Path):
        super().__init__("rule_repository")
        
        self._storage_path = Path(storage_path)
        self._rules_file = self._storage_path / "rules.yaml"
        self._backup_dir = self._storage_path / "backups"
        
        # In-memory cache for performance
        self._rules_cache: Dict[UUID, Rule] = {}
        self._cache_dirty = False
        
        # Ensure storage directory exists
        self._initialize_storage()
        
        # Load existing data
        self._load_rules()
        
        self._logger.info(f"RuleRepository initialized with {len(self._rules_cache)} rules")
    
    def _initialize_storage(self) -> None:
        """Initialize storage directories and files."""
        try:
            self._storage_path.mkdir(parents=True, exist_ok=True)
            self._backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create empty rules file if it doesn't exist
            if not self._rules_file.exists():
                self._rules_file.write_text("rules: []\n", encoding='utf-8')
                
        except Exception as e:
            self._log_error(e, "initialize_storage")
            raise RuleSystemError(f"Failed to initialize rule storage: {e}")
    
    def _load_rules(self) -> None:
        """Load rules from storage file."""
        try:
            if not self._rules_file.exists():
                return
            
            with open(self._rules_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data or 'rules' not in data:
                return
            
            # Deserialize rules
            for rule_data in data['rules']:
                try:
                    rule = self._deserialize_rule(rule_data)
                    self._rules_cache[rule.id] = rule
                except Exception as e:
                    self._logger.warning(f"Failed to load rule: {e}")
                    
            self._cache_dirty = False
            self._logger.info(f"Loaded {len(self._rules_cache)} rules from storage")
            
        except Exception as e:
            self._log_error(e, "load_rules")
            # Don't raise - allow empty repository on load failure
            self._logger.warning(f"Failed to load rules, starting with empty repository: {e}")
    
    def _persist_rules(self) -> None:
        """Persist all rules to storage file."""
        try:
            # Create backup before saving
            self._create_backup()
            
            # Serialize all rules
            rules_data = []
            for rule in self._rules_cache.values():
                rules_data.append(self._serialize_rule(rule))
            
            data = {
                'rules': rules_data,
                'metadata': {
                    'version': '1.0',
                    'created': datetime.utcnow().isoformat(),
                    'rule_count': len(rules_data)
                }
            }
            
            # Write to file
            with open(self._rules_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)
            
            self._cache_dirty = False
            self._logger.debug(f"Persisted {len(rules_data)} rules to storage")
            
        except Exception as e:
            self._log_error(e, "persist_rules")
            raise RuleSystemError(f"Failed to persist rules: {e}")
    
    def _create_backup(self) -> None:
        """Create a backup of the current rules file."""
        try:
            if not self._rules_file.exists():
                return
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_file = self._backup_dir / f"rules_backup_{timestamp}.yaml"
            
            # Copy current file to backup
            import shutil
            shutil.copy2(self._rules_file, backup_file)
            
            # Clean old backups (keep last 10)
            backups = sorted(self._backup_dir.glob("rules_backup_*.yaml"))
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()
                    
        except Exception as e:
            self._logger.warning(f"Failed to create backup: {e}")
    
    def _serialize_rule(self, rule: Rule) -> Dict[str, Any]:
        """Serialize a rule to dictionary format."""
        return {
            'id': str(rule.id),
            'name': rule.name,
            'description': rule.description,
            'pattern_id': str(rule.pattern_id),
            'destination_path': str(rule.destination_path),
            'is_enabled': rule.is_enabled,
            'priority': rule.priority,
            'error_handling': rule.error_handling.value,
            'created_date': rule.created_date.isoformat(),
            'modified_date': rule.modified_date.isoformat(),
            'author': rule.author,
            'last_executed': rule.last_executed.isoformat() if rule.last_executed else None,
            'execution_count': rule.execution_count,
            'files_processed': rule.files_processed
        }
    
    def _deserialize_rule(self, data: Dict[str, Any]) -> Rule:
        """Deserialize a rule from dictionary format."""
        from ..models import ErrorHandlingBehavior
        
        return Rule(
            id=UUID(data['id']),
            name=data['name'],
            description=data.get('description', ''),
            pattern_id=UUID(data['pattern_id']),
            destination_path=Path(data['destination_path']),
            is_enabled=data.get('is_enabled', True),
            priority=data.get('priority', 0),
            error_handling=ErrorHandlingBehavior(data.get('error_handling', 'continue_on_recoverable')),
            created_date=datetime.fromisoformat(data['created_date']),
            modified_date=datetime.fromisoformat(data['modified_date']),
            author=data.get('author', 'user'),
            last_executed=datetime.fromisoformat(data['last_executed']) if data.get('last_executed') else None,
            execution_count=data.get('execution_count', 0),
            files_processed=data.get('files_processed', 0)
        )
    
    def save(self, rule: Rule) -> None:
        """
        Save a rule to storage.
        
        Args:
            rule: Rule to save
            
        Raises:
            RuleSystemError: If save operation fails
        """
        try:
            self._log_operation("save_rule", rule_id=str(rule.id), rule_name=rule.name)
            
            # Update modified timestamp
            rule.modified_date = datetime.utcnow()
            
            # Add to cache
            self._rules_cache[rule.id] = rule
            self._cache_dirty = True
            
            # Persist to storage
            self._persist_rules()
            
            self._logger.info(f"Rule saved: {rule.name} ({rule.id})")
            
        except Exception as e:
            self._log_error(e, "save_rule", rule_id=str(rule.id))
            raise RuleSystemError(f"Failed to save rule {rule.id}: {e}")
    
    def get(self, rule_id: UUID) -> Optional[Rule]:
        """
        Retrieve a rule by ID.
        
        Args:
            rule_id: UUID of the rule to retrieve
            
        Returns:
            Rule if found, None otherwise
        """
        try:
            rule = self._rules_cache.get(rule_id)
            if rule:
                self._log_operation("get_rule", rule_id=str(rule_id), found=True)
                return rule
            else:
                self._log_operation("get_rule", rule_id=str(rule_id), found=False)
                return None
                
        except Exception as e:
            self._log_error(e, "get_rule", rule_id=str(rule_id))
            return None
    
    def delete(self, rule_id: UUID) -> bool:
        """
        Delete a rule from storage.
        
        Args:
            rule_id: UUID of the rule to delete
            
        Returns:
            True if rule was deleted, False if not found
        """
        try:
            self._log_operation("delete_rule", rule_id=str(rule_id))
            
            if rule_id in self._rules_cache:
                del self._rules_cache[rule_id]
                self._cache_dirty = True
                self._persist_rules()
                
                self._logger.info(f"Rule deleted: {rule_id}")
                return True
            else:
                self._logger.info(f"Rule not found for deletion: {rule_id}")
                return False
                
        except Exception as e:
            self._log_error(e, "delete_rule", rule_id=str(rule_id))
            raise RuleSystemError(f"Failed to delete rule {rule_id}: {e}")
    
    def list_rules(self, active_only: bool = False) -> List[Rule]:
        """
        List all rules with optional filtering.
        
        Args:
            active_only: If True, only return enabled rules
            
        Returns:
            List of rules matching criteria
        """
        try:
            rules = list(self._rules_cache.values())
            
            if active_only:
                rules = [rule for rule in rules if rule.is_enabled]
            
            # Sort by priority (highest first), then by name
            rules.sort(key=lambda r: (-r.priority, r.name))
            
            self._log_operation("list_rules", 
                              total_count=len(self._rules_cache),
                              filtered_count=len(rules),
                              active_only=active_only)
            
            return rules
            
        except Exception as e:
            self._log_error(e, "list_rules")
            return []
    
    def search_rules(self, query: str) -> List[Rule]:
        """
        Search rules by name or description.
        
        Args:
            query: Search query string
            
        Returns:
            List of rules matching the query
        """
        try:
            query_lower = query.lower()
            matched_rules = []
            
            for rule in self._rules_cache.values():
                if (query_lower in rule.name.lower() or 
                    query_lower in rule.description.lower()):
                    matched_rules.append(rule)
            
            # Sort by priority (highest first), then by name
            matched_rules.sort(key=lambda r: (-r.priority, r.name))
            
            self._log_operation("search_rules", 
                              query=query,
                              results_count=len(matched_rules))
            
            return matched_rules
            
        except Exception as e:
            self._log_error(e, "search_rules", query=query)
            return []
    
    def get_rules_by_pattern(self, pattern_id: UUID) -> List[Rule]:
        """
        Get all rules that use a specific pattern.
        
        Args:
            pattern_id: UUID of the pattern
            
        Returns:
            List of rules using the pattern
        """
        try:
            matching_rules = [
                rule for rule in self._rules_cache.values()
                if rule.pattern_id == pattern_id
            ]
            
            # Sort by priority (highest first)
            matching_rules.sort(key=lambda r: -r.priority)
            
            self._log_operation("get_rules_by_pattern",
                              pattern_id=str(pattern_id),
                              rules_count=len(matching_rules))
            
            return matching_rules
            
        except Exception as e:
            self._log_error(e, "get_rules_by_pattern", pattern_id=str(pattern_id))
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics."""
        try:
            total_rules = len(self._rules_cache)
            active_rules = len([r for r in self._rules_cache.values() if r.is_enabled])
            
            return {
                'total_rules': total_rules,
                'active_rules': active_rules,
                'inactive_rules': total_rules - active_rules,
                'cache_dirty': self._cache_dirty,
                'storage_file': str(self._rules_file),
                'storage_exists': self._rules_file.exists()
            }
            
        except Exception as e:
            self._log_error(e, "get_statistics")
            return {}
