"""
Ruleset Management System for TaskMover
Manages multiple collections of rules for different scenarios.
"""

import os
import json
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging


class RulesetManager:
    """Manages multiple rulesets (collections of rules) for TaskMover."""
    
    def __init__(self, base_config_directory: str):
        self.base_config_dir = base_config_directory
        self.rulesets_dir = os.path.join(base_config_directory, "rulesets")
        self.current_ruleset = "Default"
        self.logger = logging.getLogger(__name__)
        
        # Ensure directories exist
        os.makedirs(self.rulesets_dir, exist_ok=True)
        
        # Initialize default ruleset if it doesn't exist
        self._ensure_default_ruleset()
    
    def _ensure_default_ruleset(self):
        """Ensure the default ruleset exists."""
        default_path = os.path.join(self.rulesets_dir, "Default")
        if not os.path.exists(default_path):
            self.create_ruleset("Default", "Default rule collection")
    
    def get_available_rulesets(self) -> List[Dict[str, Any]]:
        """Get list of available rulesets with metadata."""
        rulesets = []
        
        if not os.path.exists(self.rulesets_dir):
            return rulesets
        
        for item in os.listdir(self.rulesets_dir):
            ruleset_path = os.path.join(self.rulesets_dir, item)
            if os.path.isdir(ruleset_path):
                metadata = self._load_ruleset_metadata(item)
                rulesets.append({
                    'name': item,
                    'description': metadata.get('description', ''),
                    'created': metadata.get('created', ''),
                    'modified': metadata.get('modified', ''),
                    'rule_count': self._count_rules_in_ruleset(item),
                    'path': ruleset_path
                })
        
        # Sort by name
        rulesets.sort(key=lambda x: x['name'])
        return rulesets
    
    def create_ruleset(self, name: str, description: str = "") -> bool:
        """Create a new ruleset."""
        if not name or not name.strip():
            return False
        
        name = name.strip()
        ruleset_path = os.path.join(self.rulesets_dir, name)
        
        if os.path.exists(ruleset_path):
            return False  # Already exists
        
        try:
            os.makedirs(ruleset_path, exist_ok=True)
            
            # Create metadata file
            metadata = {
                'name': name,
                'description': description,
                'created': datetime.now().isoformat(),
                'modified': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            metadata_path = os.path.join(ruleset_path, 'metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Create empty rules file
            rules_path = os.path.join(ruleset_path, 'rules.json')
            with open(rules_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2)
            
            self.logger.info(f"Created new ruleset: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create ruleset {name}: {e}")
            return False
    
    def delete_ruleset(self, name: str) -> bool:
        """Delete a ruleset (except Default)."""
        if name == "Default":
            return False  # Cannot delete default
        
        ruleset_path = os.path.join(self.rulesets_dir, name)
        if not os.path.exists(ruleset_path):
            return False
        
        try:
            shutil.rmtree(ruleset_path)
            self.logger.info(f"Deleted ruleset: {name}")
            
            # Switch to default if we deleted the current ruleset
            if self.current_ruleset == name:
                self.current_ruleset = "Default"
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete ruleset {name}: {e}")
            return False
    
    def duplicate_ruleset(self, source_name: str, new_name: str, description: str = "") -> bool:
        """Duplicate an existing ruleset."""
        if not new_name or not new_name.strip():
            return False
        
        new_name = new_name.strip()
        source_path = os.path.join(self.rulesets_dir, source_name)
        new_path = os.path.join(self.rulesets_dir, new_name)
        
        if not os.path.exists(source_path) or os.path.exists(new_path):
            return False
        
        try:
            shutil.copytree(source_path, new_path)
            
            # Update metadata
            metadata_path = os.path.join(new_path, 'metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                metadata.update({
                    'name': new_name,
                    'description': description or f"Copy of {source_name}",
                    'created': datetime.now().isoformat(),
                    'modified': datetime.now().isoformat()
                })
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Duplicated ruleset {source_name} to {new_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to duplicate ruleset {source_name}: {e}")
            return False
    
    def get_ruleset_path(self, name: str) -> Optional[str]:
        """Get the full path to a ruleset's rules file."""
        ruleset_path = os.path.join(self.rulesets_dir, name)
        if os.path.exists(ruleset_path):
            return os.path.join(ruleset_path, 'rules.json')
        return None
    
    def load_ruleset_rules(self, name: str) -> Dict[str, Any]:
        """Load rules from a specific ruleset."""
        rules_path = self.get_ruleset_path(name)
        if not rules_path or not os.path.exists(rules_path):
            return {}
        
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load rules from {name}: {e}")
            return {}
    
    def save_ruleset_rules(self, name: str, rules: Dict[str, Any]) -> bool:
        """Save rules to a specific ruleset."""
        rules_path = self.get_ruleset_path(name)
        if not rules_path:
            return False
        
        try:
            with open(rules_path, 'w', encoding='utf-8') as f:
                json.dump(rules, f, indent=2)
            
            # Update metadata modified time
            self._update_ruleset_modified(name)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save rules to {name}: {e}")
            return False
    
    def switch_ruleset(self, name: str) -> bool:
        """Switch to a different ruleset."""
        if name in [rs['name'] for rs in self.get_available_rulesets()]:
            self.current_ruleset = name
            self.logger.info(f"Switched to ruleset: {name}")
            return True
        return False
    
    def export_ruleset(self, name: str, export_path: str) -> bool:
        """Export a ruleset to a file."""
        ruleset_path = os.path.join(self.rulesets_dir, name)
        if not os.path.exists(ruleset_path):
            return False
        
        try:
            # Create export package
            export_data = {
                'metadata': self._load_ruleset_metadata(name),
                'rules': self.load_ruleset_rules(name),
                'exported': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to export ruleset {name}: {e}")
            return False
    
    def import_ruleset(self, import_path: str, new_name: Optional[str] = None) -> bool:
        """Import a ruleset from a file."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Extract data
            metadata = import_data.get('metadata', {})
            rules = import_data.get('rules', {})
            
            # Determine name
            ruleset_name = new_name or metadata.get('name', 'Imported')
            if ruleset_name in [rs['name'] for rs in self.get_available_rulesets()]:
                # Add suffix if name exists
                counter = 1
                base_name = ruleset_name
                while ruleset_name in [rs['name'] for rs in self.get_available_rulesets()]:
                    ruleset_name = f"{base_name} ({counter})"
                    counter += 1
            
            # Create ruleset
            description = metadata.get('description', 'Imported ruleset')
            if self.create_ruleset(ruleset_name, description):
                # Save rules
                return self.save_ruleset_rules(ruleset_name, rules)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to import ruleset: {e}")
            return False
    
    def _load_ruleset_metadata(self, name: str) -> Dict[str, Any]:
        """Load metadata for a ruleset."""
        metadata_path = os.path.join(self.rulesets_dir, name, 'metadata.json')
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Return default metadata
        return {
            'name': name,
            'description': '',
            'created': '',
            'modified': '',
            'version': '1.0'
        }
    
    def _update_ruleset_modified(self, name: str):
        """Update the modified timestamp for a ruleset."""
        metadata_path = os.path.join(self.rulesets_dir, name, 'metadata.json')
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                metadata['modified'] = datetime.now().isoformat()
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
            except Exception:
                pass
    
    def _count_rules_in_ruleset(self, name: str) -> int:
        """Count the number of rules in a ruleset."""
        rules = self.load_ruleset_rules(name)
        return len(rules)
    
    def rename_ruleset(self, old_name: str, new_name: str) -> bool:
        """Rename a ruleset."""
        if not old_name or not new_name or old_name == new_name:
            return False
        
        # Don't allow renaming Default
        if old_name == "Default":
            self.logger.error("Cannot rename the Default ruleset")
            return False
        
        old_path = os.path.join(self.rulesets_dir, old_name)
        new_path = os.path.join(self.rulesets_dir, new_name)
        
        if not os.path.exists(old_path):
            self.logger.error(f"Ruleset '{old_name}' not found")
            return False
        
        if os.path.exists(new_path):
            self.logger.error(f"Ruleset '{new_name}' already exists")
            return False
        
        try:
            # Rename the directory
            os.rename(old_path, new_path)
            
            # Update metadata
            metadata_path = os.path.join(new_path, 'metadata.json')
            if os.path.exists(metadata_path):
                metadata = self._load_ruleset_metadata(new_name)
                metadata['name'] = new_name
                metadata['modified'] = datetime.now().isoformat()
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
            
            # Update current ruleset if this was the active one
            if self.current_ruleset == old_name:
                self.current_ruleset = new_name
            
            self.logger.info(f"Renamed ruleset: {old_name} -> {new_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to rename ruleset {old_name}: {e}")
            return False
    
    def merge_rulesets(self, source_rulesets: List[str], target_name: str, 
                      description: str = "", conflict_strategy: str = 'rename') -> bool:
        """Merge multiple rulesets into a new target ruleset.
        
        Args:
            source_rulesets: List of ruleset names to merge
            target_name: Name for the new merged ruleset
            description: Description for the new ruleset
            conflict_strategy: How to handle rule conflicts:
                - 'keep_first': Keep rule from first ruleset
                - 'keep_all': Rename conflicting rules
                - 'keep_none': Skip conflicting rules
        
        Returns:
            True if successful, False otherwise
        """
        if not source_rulesets or not target_name:
            return False
        
        # Check if target already exists
        if target_name in [rs['name'] for rs in self.get_available_rulesets()]:
            self.logger.error(f"Target ruleset '{target_name}' already exists")
            return False
        
        merged_rules = {}
        rule_sources = {}  # Track which ruleset each rule came from
        
        for ruleset_name in source_rulesets:
            if ruleset_name not in [rs['name'] for rs in self.get_available_rulesets()]:
                self.logger.warning(f"Source ruleset '{ruleset_name}' not found, skipping")
                continue
            
            source_rules = self.load_ruleset_rules(ruleset_name)
            
            for rule_key, rule_data in source_rules.items():
                if rule_key not in merged_rules:
                    # No conflict, add the rule
                    merged_rules[rule_key] = rule_data.copy()
                    rule_sources[rule_key] = ruleset_name
                else:
                    # Handle conflict based on strategy
                    if conflict_strategy == 'keep_first':
                        # Keep first rule (already in merged_rules)
                        pass
                    elif conflict_strategy == 'keep_none':
                        # Skip conflicting rules - don't add this one
                        pass
                    elif conflict_strategy == 'keep_all':
                        # Create a new rule with a unique name
                        new_key = f"{rule_key} (from {ruleset_name})"
                        counter = 1
                        while new_key in merged_rules:
                            new_key = f"{rule_key} (from {ruleset_name} {counter})"
                            counter += 1
                        
                        merged_rules[new_key] = rule_data.copy()
                        rule_sources[new_key] = ruleset_name
        
        # Create the new ruleset with merged rules
        final_description = description or f"Merged from: {', '.join(source_rulesets)}"
        if self.create_ruleset(target_name, final_description):
            # Save the merged rules
            if self.save_ruleset_rules(target_name, merged_rules):
                self.logger.info(f"Successfully merged {len(source_rulesets)} rulesets into '{target_name}' with {len(merged_rules)} rules")
                return True
        
        return False
