"""
Core Data Models

Unified data models for the pattern system including Pattern, PatternGroup,
and related supporting classes.
"""

from dataclasses import dataclass, field, fields, MISSING
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from ...conflict_resolution.enums import ResolutionStrategy


class PatternComplexity(Enum):
    """Pattern complexity levels for performance optimization."""
    SIMPLE = "simple"        # Basic glob patterns: *.txt, file*.pdf
    ENHANCED = "enhanced"    # With tokens: report_$DATE*.txt
    ADVANCED = "advanced"    # With conditions: *.jpg AND size > 10MB
    COMPOSITE = "composite"  # Multiple patterns with logic


class PatternType(Enum):
    """Pattern input type detection."""
    SIMPLE_GLOB = "simple_glob"
    ENHANCED_GLOB = "enhanced_glob"
    ADVANCED_QUERY = "advanced_query"
    SHORTHAND = "shorthand"
    GROUP_REFERENCE = "group_reference"


class PatternStatus(Enum):
    """Pattern lifecycle status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    DRAFT = "draft"


@dataclass
class ValidationResult:
    """Result of pattern validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    performance_score: Optional[int] = None  # 1-10 scale


@dataclass
class ParsedPattern:
    """Result of pattern parsing with metadata."""
    original_input: str
    pattern_type: PatternType
    complexity: PatternComplexity
    compiled_query: str
    tokens_used: Set[str] = field(default_factory=set)
    referenced_groups: Set[str] = field(default_factory=set)
    estimated_complexity: int = 1
    validation_result: Optional[ValidationResult] = None


class MatchResult:
    """Result of pattern matching operation."""
    
    def __init__(self, 
                 file_path: Optional[Path] = None,  # For test compatibility
                 pattern_id: Optional[UUID] = None,  # For test compatibility  
                 confidence: Optional[float] = None,  # For test compatibility
                 execution_time_ms: Optional[float] = None,  # For test compatibility
                 matched_files: Optional[List[Path]] = None,
                 total_files_checked: int = 0,
                 cache_hit: bool = False,
                 performance_metrics: Optional[Dict[str, Any]] = None,
                 errors: Optional[List[str]] = None,
                 **kwargs):
        """Initialize MatchResult with compatibility for different constructor signatures."""
        
        # Handle test compatibility - single file result
        if file_path is not None and matched_files is None:
            # Convert string to Path if needed
            if isinstance(file_path, str):
                file_path = Path(file_path)
            self.matched_files = [file_path]
            self.pattern_id = pattern_id
            self.confidence = confidence or 1.0
        else:
            self.matched_files = matched_files or []
            self.pattern_id = pattern_id
            self.confidence = confidence or 1.0
        
        self.total_files_checked = total_files_checked
        self.execution_time_ms = execution_time_ms or 0.0
        self.cache_hit = cache_hit
        self.performance_metrics = performance_metrics or {}
        self.errors = errors or []
        
        # Handle additional kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def file_path(self) -> Optional[Path]:
        """Get the first matched file path for test compatibility."""
        return self.matched_files[0] if self.matched_files else None
    
    @file_path.setter  
    def file_path(self, value: Path):
        """Set the file path (for single file results)."""
        if isinstance(value, str):
            value = Path(value)
        self.matched_files = [value]


@dataclass
class PatternUsageStats:
    """Usage statistics for a pattern."""
    usage_count: int = 0
    last_used: Optional[datetime] = None
    avg_execution_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    error_rate: float = 0.0
    performance_score: float = 10.0  # 1-10 scale


class Pattern:
    """Unified pattern model supporting all pattern types."""
    
    def __init__(self, 
                 id: Optional[UUID] = None,
                 name: str = "",
                 description: str = "",
                 user_expression: str = "",
                 pattern_text: Optional[str] = None,  # Alias for user_expression
                 compiled_query: str = "",
                 pattern_complexity: PatternComplexity = PatternComplexity.SIMPLE,
                 pattern_type: PatternType = PatternType.SIMPLE_GLOB,
                 tokens_used: Optional[Set[str]] = None,
                 referenced_groups: Optional[Set[str]] = None,
                 conflict_resolution_strategy: Optional["ResolutionStrategy"] = None,
                 conflict_resolution_config: Optional[Dict[str, Any]] = None,
                 tags: Optional[List[str]] = None,
                 group_id: Optional[UUID] = None,
                 category: str = "general",
                 created_date: Optional[datetime] = None,
                 modified_date: Optional[datetime] = None,
                 author: str = "",
                 version: int = 1,
                 status: PatternStatus = PatternStatus.ACTIVE,
                 estimated_complexity: int = 1,
                 cache_ttl: Optional[int] = None,
                 performance_hints: Optional[Dict[str, Any]] = None,
                 usage_stats: Optional[PatternUsageStats] = None,
                 is_valid: bool = True,
                 validation_errors: Optional[List[str]] = None,
                 last_validated: Optional[datetime] = None,
                 extra_data: Optional[Dict[str, Any]] = None,
                 **kwargs):
        """Initialize Pattern with support for both user_expression and pattern_text."""
        
        # Core identification
        self.id = id or uuid4()
        self.name = name
        self.description = description
        
        # Pattern content - handle pattern_text alias for test compatibility
        if pattern_text is not None and not user_expression:
            self.user_expression = pattern_text
        else:
            self.user_expression = user_expression
        
        self.compiled_query = compiled_query
        self.pattern_complexity = pattern_complexity
        self.pattern_type = pattern_type
        
        # Pattern analysis
        self.tokens_used = tokens_used or set()
        self.referenced_groups = referenced_groups or set()
        
        # Conflict resolution
        self.conflict_resolution_strategy = conflict_resolution_strategy
        self.conflict_resolution_config = conflict_resolution_config or {}
        
        # Organization
        self.tags = tags or []
        self.group_id = group_id
        self.category = category
        
        # Metadata
        self.created_date = created_date or datetime.utcnow()
        self.modified_date = modified_date or datetime.utcnow()
        self.author = author
        self.version = version
        self.status = status
        
        # Performance and caching
        self.estimated_complexity = estimated_complexity
        self.cache_ttl = cache_ttl
        self.performance_hints = performance_hints or {}
        
        # Usage tracking
        self.usage_stats = usage_stats or PatternUsageStats()
        
        # Validation
        self.is_valid = is_valid
        self.validation_errors = validation_errors or []
        self.last_validated = last_validated
        
        # Additional metadata
        self.extra_data = extra_data or {}
        
        # Handle any additional kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        self.__post_init__()
    
    @property
    def pattern_text(self) -> str:
        """Alias for user_expression for test compatibility."""
        return self.user_expression
    
    @pattern_text.setter
    def pattern_text(self, value: str):
        """Setter for pattern_text alias."""
        self.user_expression = value
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        if not self.name and self.user_expression:
            # Auto-generate name from expression if not provided
            self.name = f"Pattern: {self.user_expression[:50]}"
        
        # Ensure modified_date is updated
        if self.created_date and not hasattr(self, '_initialized'):
            self.modified_date = self.created_date
            self._initialized = True
    
    def update_usage_stats(self, execution_time_ms: float, cache_hit: bool = False, error: bool = False):
        """Update usage statistics after pattern execution."""
        self.usage_stats.usage_count += 1
        self.usage_stats.last_used = datetime.utcnow()
        
        # Update average execution time
        if self.usage_stats.usage_count == 1:
            self.usage_stats.avg_execution_time_ms = execution_time_ms
        else:
            old_avg = self.usage_stats.avg_execution_time_ms
            count = self.usage_stats.usage_count
            self.usage_stats.avg_execution_time_ms = (old_avg * (count - 1) + execution_time_ms) / count
        
        # Update cache hit rate
        if cache_hit:
            current_hits = self.usage_stats.cache_hit_rate * (self.usage_stats.usage_count - 1)
            self.usage_stats.cache_hit_rate = (current_hits + 1) / self.usage_stats.usage_count
        else:
            current_hits = self.usage_stats.cache_hit_rate * (self.usage_stats.usage_count - 1)
            self.usage_stats.cache_hit_rate = current_hits / self.usage_stats.usage_count
        
        # Update error rate
        if error:
            current_errors = self.usage_stats.error_rate * (self.usage_stats.usage_count - 1)
            self.usage_stats.error_rate = (current_errors + 1) / self.usage_stats.usage_count
        else:
            current_errors = self.usage_stats.error_rate * (self.usage_stats.usage_count - 1)
            self.usage_stats.error_rate = current_errors / self.usage_stats.usage_count
    
    def clone(self) -> "Pattern":
        """Create a copy of this pattern with a new ID."""
        cloned = Pattern(
            name=f"{self.name} (Copy)",
            description=self.description,
            user_expression=self.user_expression,
            compiled_query=self.compiled_query,
            pattern_complexity=self.pattern_complexity,
            pattern_type=self.pattern_type,
            tags=self.tags.copy(),
            group_id=self.group_id,
            category=self.category,
            author=self.author,
            estimated_complexity=self.estimated_complexity,
            cache_ttl=self.cache_ttl,
            performance_hints=self.performance_hints.copy(),
            extra_data=self.extra_data.copy()
        )
        return cloned


@dataclass
class PatternGroup:
    """Pattern group for organization and management."""
    
    # Core identification
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    
    # Hierarchy
    parent_group_id: Optional[UUID] = None
    
    # Visual organization
    color: str = "#4A90E2"  # Default blue
    icon: str = "folder"
    sort_order: int = 0
    
    # Access control
    is_system: bool = False
    is_readonly: bool = False
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.utcnow)
    modified_date: datetime = field(default_factory=datetime.utcnow)
    pattern_count: int = 0
    
    # Group-specific patterns for system groups
    system_patterns: List[str] = field(default_factory=list)
    
    # Additional metadata
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization setup."""
        if self.created_date and not hasattr(self, '_initialized'):
            self.modified_date = self.created_date
            self._initialized = True


# System-defined groups
SYSTEM_GROUPS = {
    "@media": PatternGroup(
        name="Media Files",
        description="Images, videos, and audio files",
        color="#FF6B6B",
        icon="media",
        is_system=True,
        is_readonly=True,
        system_patterns=["*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff", "*.webp",
                        "*.mp4", "*.avi", "*.mov", "*.wmv", "*.flv", "*.mkv",
                        "*.mp3", "*.wav", "*.flac", "*.aac", "*.ogg", "*.wma"]
    ),
    "@documents": PatternGroup(
        name="Documents",
        description="Text documents and PDFs",
        color="#4ECDC4",
        icon="document",
        is_system=True,
        is_readonly=True,
        system_patterns=["*.pdf", "*.doc", "*.docx", "*.txt", "*.rtf", "*.odt",
                        "*.xls", "*.xlsx", "*.ppt", "*.pptx", "*.odp", "*.ods"]
    ),
    "@code": PatternGroup(
        name="Source Code",
        description="Programming and markup files",
        color="#45B7D1",
        icon="code",
        is_system=True,
        is_readonly=True,
        system_patterns=["*.py", "*.js", "*.html", "*.css", "*.java", "*.cpp", "*.c",
                        "*.cs", "*.php", "*.rb", "*.go", "*.rs", "*.ts", "*.jsx", "*.tsx",
                        "*.json", "*.xml", "*.yaml", "*.yml", "*.sql"]
    ),
    "@archives": PatternGroup(
        name="Archives",
        description="Compressed and archive files",
        color="#96CEB4",
        icon="archive",
        is_system=True,
        is_readonly=True,
        system_patterns=["*.zip", "*.tar", "*.gz", "*.bz2", "*.xz", "*.rar", "*.7z",
                        "*.tar.gz", "*.tar.bz2", "*.tar.xz"]
    ),
    "@temporary": PatternGroup(
        name="Temporary Files",
        description="Cache, temp, and build artifacts",
        color="#FFEAA7",
        icon="temporary",
        is_system=True,
        is_readonly=True,
        system_patterns=["*.tmp", "*.temp", "*~", "*.bak", "*.backup", "*.swp",
                        "*.cache", "*.log", "*.old", ".DS_Store", "Thumbs.db"]
    )
}


@dataclass
class FileMetadata:
    """File metadata for pattern matching."""
    path: Path
    name: str
    extension: str
    size: int
    created: datetime
    modified: datetime
    accessed: datetime
    is_hidden: bool
    is_readonly: bool
    mime_type: Optional[str] = None
    checksum: Optional[str] = None
    content_preview: Optional[str] = None
    line_count: Optional[int] = None
    word_count: Optional[int] = None
    encoding: Optional[str] = None
    owner: Optional[str] = None
    permissions: Optional[str] = None
