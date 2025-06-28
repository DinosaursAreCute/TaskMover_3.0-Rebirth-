"""
Conflict Resolution System

Handles conflicts at multiple scopes: global, ruleset, rule, and pattern levels.
Provides extensible conflict resolution strategies for the entire TaskMover system.
"""

from .enums import ConflictType, ConflictScope, ResolutionStrategy, ConflictSeverity
from .models import Conflict, ConflictContext, ResolutionResult, ConflictRule
from .resolver import ConflictResolver
from .strategies import (
    SkipStrategy, OverwriteStrategy, RenameStrategy, 
    PromptUserStrategy, BackupStrategy, MergeStrategy
)
from .manager import ConflictManager

__all__ = [
    'ConflictType', 'ConflictScope', 'ResolutionStrategy', 'ConflictSeverity',
    'Conflict', 'ConflictContext', 'ResolutionResult', 'ConflictRule',
    'ConflictResolver', 'ConflictManager',
    'SkipStrategy', 'OverwriteStrategy', 'RenameStrategy',
    'PromptUserStrategy', 'BackupStrategy', 'MergeStrategy'
]
