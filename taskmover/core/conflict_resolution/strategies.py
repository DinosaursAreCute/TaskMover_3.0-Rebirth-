"""
Conflict Resolution Strategies

Concrete implementations of different conflict resolution strategies.
"""

import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..logging import get_logger
from .models import Conflict, ResolutionResult, ConflictItem
from .enums import ResolutionStrategy, ConflictType


class BaseResolutionStrategy(ABC):
    """Base class for all conflict resolution strategies."""
    
    def __init__(self, name: str):
        self.name = name
        self._logger = get_logger(f"conflict_resolution.{name}")
    
    @abstractmethod
    def can_resolve(self, conflict: Conflict) -> bool:
        """Check if this strategy can resolve the given conflict."""
        pass
    
    @abstractmethod
    def resolve(self, conflict: Conflict, config: Optional[Dict[str, Any]] = None) -> ResolutionResult:
        """Resolve the conflict using this strategy."""
        pass
    
    @abstractmethod
    def estimate_impact(self, conflict: Conflict) -> Dict[str, Any]:
        """Estimate the impact of resolving with this strategy."""
        pass
    
    def _create_success_result(self, conflict: Conflict, action: str, 
                             files_affected: Optional[List[Path]] = None,
                             data_changes: Optional[Dict[str, Any]] = None) -> ResolutionResult:
        """Create a successful resolution result."""
        return ResolutionResult(
            conflict_id=conflict.id,
            success=True,
            strategy_used=ResolutionStrategy(self.name.lower()),
            action_taken=action,
            files_affected=files_affected or [],
            data_changes=data_changes or {}
        )
    
    def _create_failure_result(self, conflict: Conflict, error: str) -> ResolutionResult:
        """Create a failed resolution result."""
        return ResolutionResult(
            conflict_id=conflict.id,
            success=False,
            strategy_used=ResolutionStrategy(self.name.lower()),
            error_message=error
        )


class SkipStrategy(BaseResolutionStrategy):
    """Strategy that skips the conflicting operation."""
    
    def __init__(self):
        super().__init__("skip")
    
    def can_resolve(self, conflict: Conflict) -> bool:
        """Skip can resolve any conflict by not performing the operation."""
        return True
    
    def resolve(self, conflict: Conflict, config: Optional[Dict[str, Any]] = None) -> ResolutionResult:
        """Resolve by skipping the conflicting operation."""
        try:
            self._logger.info(f"Skipping conflict: {conflict.title}")
            
            action = f"Skipped operation due to {conflict.conflict_type.value}"
            if conflict.new_item:
                action += f" - did not process {conflict.new_item.name}"
            
            return self._create_success_result(conflict, action)
            
        except Exception as e:
            return self._create_failure_result(conflict, f"Failed to skip: {e}")
    
    def estimate_impact(self, conflict: Conflict) -> Dict[str, Any]:
        """Estimate impact of skipping."""
        return {
            "risk_level": "none",
            "data_loss": False,
            "files_modified": 0,
            "operation_skipped": True
        }


class OverwriteStrategy(BaseResolutionStrategy):
    """Strategy that overwrites the existing item."""
    
    def __init__(self):
        super().__init__("overwrite")
    
    def can_resolve(self, conflict: Conflict) -> bool:
        """Can resolve conflicts where overwriting makes sense."""
        return conflict.conflict_type in [
            ConflictType.FILE_EXISTS,
            ConflictType.DUPLICATE_NAME,
            ConflictType.VERSION_MISMATCH
        ]
    
    def resolve(self, conflict: Conflict, config: Optional[Dict[str, Any]] = None) -> ResolutionResult:
        """Resolve by overwriting the existing item."""
        try:
            files_affected = []
            
            if conflict.conflict_type == ConflictType.FILE_EXISTS:
                if conflict.existing_item and conflict.new_item and conflict.existing_item.path:
                    # Overwrite existing file
                    existing_path = Path(conflict.existing_item.path)
                    
                    if existing_path.exists():
                        self._logger.info(f"Overwriting {existing_path}")
                        files_affected.append(existing_path)
                        
                        # The actual file operation would be handled by the calling code
                        # This strategy just indicates that overwriting is the chosen action
                    
            action = f"Overwrote existing item: {conflict.existing_item.name if conflict.existing_item else 'unknown'}"
            
            return self._create_success_result(conflict, action, files_affected)
            
        except Exception as e:
            return self._create_failure_result(conflict, f"Failed to overwrite: {e}")
    
    def estimate_impact(self, conflict: Conflict) -> Dict[str, Any]:
        """Estimate impact of overwriting."""
        return {
            "risk_level": "medium",
            "data_loss": True,
            "files_modified": 1,
            "existing_data_lost": True
        }


class RenameStrategy(BaseResolutionStrategy):
    """Strategy that renames the new item to avoid conflict."""
    
    def __init__(self):
        super().__init__("rename")
    
    def can_resolve(self, conflict: Conflict) -> bool:
        """Can resolve naming conflicts."""
        return conflict.conflict_type in [
            ConflictType.FILE_EXISTS,
            ConflictType.DUPLICATE_NAME
        ]
    
    def resolve(self, conflict: Conflict, config: Optional[Dict[str, Any]] = None) -> ResolutionResult:
        """Resolve by renaming the new item."""
        try:
            if not conflict.new_item:
                return self._create_failure_result(conflict, "No new item to rename")
            
            # Generate new name
            original_name = conflict.new_item.name
            new_name = self._generate_unique_name(original_name, conflict)
            
            # Update the conflict item with new name
            conflict.new_item.name = new_name
            if conflict.new_item.path:
                old_path = Path(conflict.new_item.path)
                new_path = old_path.parent / new_name
                conflict.new_item.path = new_path
            
            action = f"Renamed {original_name} to {new_name}"
            files_affected = [conflict.new_item.path] if conflict.new_item.path else []
            
            return self._create_success_result(
                conflict, action, files_affected,
                data_changes={"new_name": new_name, "original_name": original_name}
            )
            
        except Exception as e:
            return self._create_failure_result(conflict, f"Failed to rename: {e}")
    
    def _generate_unique_name(self, original_name: str, conflict: Conflict) -> str:
        """Generate a unique name for the item."""
        base_name = original_name
        extension = ""
        
        # Split name and extension
        if "." in original_name:
            base_name, extension = original_name.rsplit(".", 1)
            extension = f".{extension}"
        
        # Try different suffixes
        for i in range(1, 1000):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if i == 1:
                new_name = f"{base_name}_copy{extension}"
            elif i == 2:
                new_name = f"{base_name}_{timestamp}{extension}"
            else:
                new_name = f"{base_name}_copy_{i}{extension}"
            
            # Check if this name would conflict
            # In a real implementation, this would check against the file system
            # or database to ensure uniqueness
            if not self._name_conflicts(new_name, conflict):
                return new_name
        
        # Fallback with UUID
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return f"{base_name}_{unique_id}{extension}"
    
    def _name_conflicts(self, name: str, conflict: Conflict) -> bool:
        """Check if the proposed name would cause a conflict."""
        # Basic implementation - in reality this would check against
        # the actual target location
        if conflict.existing_item and conflict.existing_item.name == name:
            return True
        return False
    
    def estimate_impact(self, conflict: Conflict) -> Dict[str, Any]:
        """Estimate impact of renaming."""
        return {
            "risk_level": "low",
            "data_loss": False,
            "files_modified": 0,
            "files_renamed": 1,
            "name_changed": True
        }


class BackupStrategy(BaseResolutionStrategy):
    """Strategy that backs up existing item before replacing."""
    
    def __init__(self):
        super().__init__("backup_replace")
    
    def can_resolve(self, conflict: Conflict) -> bool:
        """Can resolve file conflicts by backing up."""
        return conflict.conflict_type in [
            ConflictType.FILE_EXISTS,
            ConflictType.VERSION_MISMATCH
        ]
    
    def resolve(self, conflict: Conflict, config: Optional[Dict[str, Any]] = None) -> ResolutionResult:
        """Resolve by backing up existing item and replacing."""
        try:
            if not conflict.existing_item or not conflict.existing_item.path:
                return self._create_failure_result(conflict, "No existing item to backup")
            
            existing_path = Path(conflict.existing_item.path)
            if not existing_path.exists():
                return self._create_failure_result(conflict, f"Existing file not found: {existing_path}")
            
            # Generate backup path
            backup_path = self._generate_backup_path(existing_path, config)
            
            # Create backup
            self._logger.info(f"Creating backup: {existing_path} -> {backup_path}")
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(existing_path, backup_path)
            
            action = f"Backed up {existing_path.name} to {backup_path.name}, ready for replacement"
            files_affected = [existing_path, backup_path]
            
            return self._create_success_result(
                conflict, action, files_affected,
                data_changes={"backup_path": str(backup_path)},
            )
            
        except Exception as e:
            return self._create_failure_result(conflict, f"Failed to backup: {e}")
    
    def _generate_backup_path(self, original_path: Path, config: Optional[Dict[str, Any]] = None) -> Path:
        """Generate backup file path."""
        if config and "backup_dir" in config:
            backup_dir = Path(config["backup_dir"])
        else:
            backup_dir = original_path.parent / "backups"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{original_path.stem}_backup_{timestamp}{original_path.suffix}"
        
        return backup_dir / backup_name
    
    def estimate_impact(self, conflict: Conflict) -> Dict[str, Any]:
        """Estimate impact of backup and replace."""
        backup_size = 0
        if conflict.existing_item and conflict.existing_item.size:
            backup_size = conflict.existing_item.size
        
        return {
            "risk_level": "low",
            "data_loss": False,
            "files_modified": 1,
            "backup_created": True,
            "backup_size_bytes": backup_size
        }


class PromptUserStrategy(BaseResolutionStrategy):
    """Strategy that prompts the user for a decision."""
    
    def __init__(self):
        super().__init__("prompt_user")
    
    def can_resolve(self, conflict: Conflict) -> bool:
        """Can always prompt user for any conflict."""
        return True
    
    def resolve(self, conflict: Conflict, config: Optional[Dict[str, Any]] = None) -> ResolutionResult:
        """Resolve by prompting user (placeholder implementation)."""
        # In a real implementation, this would trigger UI prompt
        # For now, we return a pending result
        return ResolutionResult(
            conflict_id=conflict.id,
            success=False,
            strategy_used=ResolutionStrategy.PROMPT_USER,
            action_taken="User prompt required",
            error_message="User interaction required - conflict pending resolution"
        )
    
    def estimate_impact(self, conflict: Conflict) -> Dict[str, Any]:
        """Estimate impact of user prompt."""
        return {
            "risk_level": "user_dependent",
            "data_loss": "user_dependent",
            "files_modified": "user_dependent",
            "user_interaction_required": True
        }


class MergeStrategy(BaseResolutionStrategy):
    """Strategy that attempts to merge conflicting items."""
    
    def __init__(self):
        super().__init__("merge")
    
    def can_resolve(self, conflict: Conflict) -> bool:
        """Can attempt merge for certain types of conflicts."""
        return conflict.conflict_type in [
            ConflictType.VERSION_MISMATCH,
            ConflictType.DATA_INCONSISTENCY
        ]
    
    def resolve(self, conflict: Conflict, config: Optional[Dict[str, Any]] = None) -> ResolutionResult:
        """Resolve by merging items (placeholder implementation)."""
        # Complex merge logic would go here
        # For now, return failure as merge is complex
        return self._create_failure_result(
            conflict, 
            "Merge strategy not fully implemented - requires domain-specific logic"
        )
    
    def estimate_impact(self, conflict: Conflict) -> Dict[str, Any]:
        """Estimate impact of merging."""
        return {
            "risk_level": "medium",
            "data_loss": False,
            "files_modified": 1,
            "data_combined": True,
            "merge_complexity": "high"
        }
