"""
Modern Pattern Library for TaskMover
Manages a shared library of file patterns across all rulesets.
"""

import json
import uuid
import re
import fnmatch
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime


@dataclass
class Pattern:
    """Represents a file pattern with metadata."""
    id: str
    name: str
    pattern: str
    type: str  # 'glob', 'regex', 'exact'
    description: str = ""
    examples: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    created: Optional[str] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []
        if self.tags is None:
            self.tags = []
        if self.created is None:
            self.created = datetime.now().isoformat()


class PatternLibrary:
    """Manages a library of reusable patterns shared across all rulesets."""
    
    def __init__(self, config_directory: str):
        self.config_dir = Path(config_directory)
        self.pattern_file = self.config_dir / "patterns.json"
        self.patterns: Dict[str, Pattern] = {}
        self.logger = logging.getLogger(__name__)
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.load_patterns()
        
        # Create default patterns if none exist
        if not self.patterns:
            self._create_default_patterns()
    
    def create_pattern(self, name: str, pattern: str, pattern_type: str, 
                      description: str = "", examples: Optional[List[str]] = None, 
                      tags: Optional[List[str]] = None) -> str:
        """Create new pattern and return its ID."""
        # Validate pattern
        is_valid, error_msg = self.validate_pattern(pattern, pattern_type)
        if not is_valid:
            raise ValueError(f"Invalid pattern: {error_msg}")
        
        # Check for duplicate names
        if any(p.name == name for p in self.patterns.values()):
            raise ValueError(f"Pattern name '{name}' already exists")
        
        pattern_id = str(uuid.uuid4())
        new_pattern = Pattern(
            id=pattern_id,
            name=name,
            pattern=pattern,
            type=pattern_type,
            description=description,
            examples=examples or [],
            tags=tags or []
        )
        
        self.patterns[pattern_id] = new_pattern
        self.save_patterns()
        self.logger.info(f"Created pattern: {name} ({pattern_type})")
        return pattern_id
    
    def update_pattern(self, pattern_id: str, **kwargs) -> bool:
        """Update an existing pattern."""
        if pattern_id not in self.patterns:
            return False
        
        pattern = self.patterns[pattern_id]
        
        # Validate new pattern if provided
        if 'pattern' in kwargs or 'type' in kwargs:
            new_pattern = kwargs.get('pattern', pattern.pattern)
            new_type = kwargs.get('type', pattern.type)
            is_valid, error_msg = self.validate_pattern(new_pattern, new_type)
            if not is_valid:
                raise ValueError(f"Invalid pattern: {error_msg}")
        
        # Check for duplicate names if name is being changed
        if 'name' in kwargs and kwargs['name'] != pattern.name:
            if any(p.name == kwargs['name'] for p in self.patterns.values()):
                raise ValueError(f"Pattern name '{kwargs['name']}' already exists")
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(pattern, key):
                setattr(pattern, key, value)
        
        self.save_patterns()
        self.logger.info(f"Updated pattern: {pattern.name}")
        return True
    
    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get pattern by ID."""
        return self.patterns.get(pattern_id)
    
    def get_pattern_by_name(self, name: str) -> Optional[Pattern]:
        """Get pattern by name."""
        for pattern in self.patterns.values():
            if pattern.name == name:
                return pattern
        return None
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """Delete pattern by ID."""
        if pattern_id in self.patterns:
            pattern_name = self.patterns[pattern_id].name
            del self.patterns[pattern_id]
            self.save_patterns()
            self.logger.info(f"Deleted pattern: {pattern_name}")
            return True
        return False
    
    def get_all_patterns(self) -> List[Pattern]:
        """Get all patterns sorted by name."""
        return sorted(self.patterns.values(), key=lambda p: p.name.lower())
    
    def search_patterns(self, query: str) -> List[Pattern]:
        """Search patterns by name, description, or tags."""
        query = query.lower()
        results = []
        
        for pattern in self.patterns.values():
            if (query in pattern.name.lower() or 
                query in pattern.description.lower() or
                any(query in tag.lower() for tag in (pattern.tags or [])) or
                query in pattern.pattern.lower()):
                results.append(pattern)
        
        return sorted(results, key=lambda p: p.name.lower())
    
    def test_pattern(self, pattern_id: str, test_filenames: List[str]) -> List[str]:
        """Test pattern against list of filenames and return matches."""
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return []
        
        return self._test_pattern_string(pattern.pattern, pattern.type, test_filenames)
    
    def _test_pattern_string(self, pattern_str: str, pattern_type: str, 
                           test_filenames: List[str]) -> List[str]:
        """Test a pattern string against filenames."""
        matches = []
        
        for filename in test_filenames:
            try:
                if pattern_type == "glob":
                    if fnmatch.fnmatch(filename, pattern_str):
                        matches.append(filename)
                elif pattern_type == "regex":
                    if re.search(pattern_str, filename):
                        matches.append(filename)
                elif pattern_type == "exact":
                    if filename == pattern_str:
                        matches.append(filename)
            except Exception:
                # Skip invalid matches
                continue
        
        return matches
    
    def validate_pattern(self, pattern: str, pattern_type: str) -> Tuple[bool, str]:
        """Validate a pattern string."""
        if not pattern.strip():
            return False, "Pattern cannot be empty"
        
        try:
            if pattern_type == "regex":
                re.compile(pattern)
            elif pattern_type == "glob":
                # Basic glob validation - try to compile as regex equivalent
                fnmatch.translate(pattern)
            elif pattern_type == "exact":
                # Exact patterns are always valid if not empty
                pass
            else:
                return False, f"Unknown pattern type: {pattern_type}"
            
            return True, ""
        except re.error as e:
            return False, f"Invalid regex: {str(e)}"
        except Exception as e:
            return False, f"Invalid pattern: {str(e)}"
    
    def save_patterns(self):
        """Save patterns to JSON file."""
        try:
            data = {
                "version": "2.0",
                "patterns": {pid: asdict(pattern) for pid, pattern in self.patterns.items()}
            }
            
            with open(self.pattern_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save patterns: {e}")
            raise
    
    def load_patterns(self):
        """Load patterns from JSON file."""
        if not self.pattern_file.exists():
            self.patterns = {}
            return
        
        try:
            with open(self.pattern_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.patterns = {}
            for pid, pattern_data in data.get("patterns", {}).items():
                self.patterns[pid] = Pattern(**pattern_data)
            
            self.logger.info(f"Loaded {len(self.patterns)} patterns")
        except Exception as e:
            self.logger.error(f"Failed to load patterns: {e}")
            # Backup corrupted file
            if self.pattern_file.exists():
                backup_file = self.pattern_file.with_suffix('.json.backup')
                self.pattern_file.rename(backup_file)
            self.patterns = {}
    
    def _create_default_patterns(self):
        """Create default patterns for new installations."""
        default_patterns = [
            {
                "name": "Python Files",
                "pattern": "*.py",
                "type": "glob",
                "description": "Python source files",
                "examples": ["main.py", "utils.py", "test_example.py"],
                "tags": ["code", "python"]
            },
            {
                "name": "JavaScript Files",
                "pattern": "*.js",
                "type": "glob",
                "description": "JavaScript source files",
                "examples": ["app.js", "script.js", "main.js"],
                "tags": ["code", "javascript"]
            },
            {
                "name": "Image Files",
                "pattern": "*.{jpg,jpeg,png,gif,bmp,svg}",
                "type": "glob",
                "description": "Common image file formats",
                "examples": ["photo.jpg", "icon.png", "logo.svg"],
                "tags": ["media", "images"]
            },
            {
                "name": "Document Files",
                "pattern": "*.{pdf,doc,docx,txt,rtf}",
                "type": "glob",
                "description": "Document files",
                "examples": ["report.pdf", "letter.docx", "notes.txt"],
                "tags": ["documents"]
            },
            {
                "name": "Archive Files",
                "pattern": "*.{zip,rar,7z,tar,gz}",
                "type": "glob",
                "description": "Compressed archive files",
                "examples": ["backup.zip", "data.tar.gz", "archive.rar"],
                "tags": ["archives"]
            },
            {
                "name": "Log Files",
                "pattern": r".*\.log$",
                "type": "regex",
                "description": "Application log files",
                "examples": ["app.log", "error.log", "debug.log"],
                "tags": ["logs", "debugging"]
            }
        ]
        
        for pattern_data in default_patterns:
            try:
                self.create_pattern(**pattern_data)
            except Exception as e:
                self.logger.warning(f"Failed to create default pattern {pattern_data['name']}: {e}")
        
        self.logger.info("Created default patterns")
    
    def export_patterns(self, export_path: str) -> bool:
        """Export patterns to a file."""
        try:
            data = {
                "version": "2.0",
                "exported_at": datetime.now().isoformat(),
                "patterns": {pid: asdict(pattern) for pid, pattern in self.patterns.items()}
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(self.patterns)} patterns to {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export patterns: {e}")
            return False
    
    def import_patterns(self, import_path: str, merge: bool = True) -> Tuple[bool, int]:
        """Import patterns from a file. Returns (success, count_imported)."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_patterns = data.get("patterns", {})
            count_imported = 0
            
            for pid, pattern_data in imported_patterns.items():
                try:
                    # Create new ID to avoid conflicts
                    new_id = str(uuid.uuid4())
                    pattern = Pattern(**pattern_data)
                    pattern.id = new_id
                    
                    # Handle name conflicts
                    original_name = pattern.name
                    counter = 1
                    while any(p.name == pattern.name for p in self.patterns.values()):
                        pattern.name = f"{original_name} ({counter})"
                        counter += 1
                    
                    self.patterns[new_id] = pattern
                    count_imported += 1
                except Exception as e:
                    self.logger.warning(f"Failed to import pattern {pattern_data.get('name', 'unknown')}: {e}")
            
            if count_imported > 0:
                self.save_patterns()
            
            self.logger.info(f"Imported {count_imported} patterns from {import_path}")
            return True, count_imported
        except Exception as e:
            self.logger.error(f"Failed to import patterns: {e}")
            return False, 0
