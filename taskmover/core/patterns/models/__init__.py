"""
Core Data Models

Unified data models for the pattern system including Pattern, PatternGroup,
and related supporting classes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
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


@dataclass
class MatchResult:
    """Result of pattern matching operation."""
    matched_files: List["Path"]
    total_files_checked: int
    execution_time_ms: float
    cache_hit: bool = False
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class PatternUsageStats:
    """Usage statistics for a pattern."""
    usage_count: int = 0
    last_used: Optional[datetime] = None
    avg_execution_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    error_rate: float = 0.0
    performance_score: float = 10.0  # 1-10 scale


@dataclass
class Pattern:
    """Unified pattern model supporting all pattern types."""
    
    # Core identification
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    
    # Pattern content
    user_expression: str = ""  # What user typed: "test_*_$DATE*.txt"
    compiled_query: str = ""   # Internal query representation
    pattern_complexity: PatternComplexity = PatternComplexity.SIMPLE
    pattern_type: PatternType = PatternType.SIMPLE_GLOB
    
    # Pattern analysis
    tokens_used: Set[str] = field(default_factory=set)
    referenced_groups: Set[str] = field(default_factory=set)
    
    # Conflict resolution
    conflict_resolution_strategy: Optional["ResolutionStrategy"] = None
    conflict_resolution_config: Dict[str, Any] = field(default_factory=dict)
    
    # Organization
    tags: List[str] = field(default_factory=list)
    group_id: Optional[UUID] = None
    category: str = "general"
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.utcnow)
    modified_date: datetime = field(default_factory=datetime.utcnow)
    author: str = ""
    version: int = 1
    status: PatternStatus = PatternStatus.ACTIVE
    
    # Performance and caching
    estimated_complexity: int = 1  # 1-10 scale
    cache_ttl: Optional[int] = None
    performance_hints: Dict[str, Any] = field(default_factory=dict)
    
    # Usage tracking
    usage_stats: PatternUsageStats = field(default_factory=PatternUsageStats)
    
    # Validation
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    last_validated: Optional[datetime] = None
    
    # Additional metadata
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
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
    path: "Path"
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
