# TaskMover Pattern System - Unified Technical Specification v3.0

## Overview

This document defines the **unified technical specification** for the TaskMover Pattern System. Based on architectural analysis, we have simplified from a dual-syntax approach to a **single, intelligent pattern language** that provides the familiarity of glob patterns with the power of SQL-like queries through intelligent parsing and automatic translation.

## Architectural Decision: Unified Pattern Language

### Why Unified Architecture?

After careful analysis, we determined that maintaining two separate syntax systems (glob/regex + SQL-like) would create unnecessary complexity without significant user benefit. Instead, we implement:

**Single Input Language** → **Intelligent Parser** → **Optimized Query Engine** → **Results**

### User Experience Examples

```bash
# Natural glob-like patterns work intuitively
*.txt                           # All text files
test_*_version_9.*_$DATE*.txt   # Complex pattern with tokens
report_$DATE_*.pdf              # Dynamic patterns with date tokens

# Enhanced syntax for power users
*.jpg AND size > 10MB           # Combined conditions
modified > today-7              # Date-relative filtering
@media                          # Pattern group references
```

### Backend Translation Examples

```bash
# User Input → Internal Query Translation

*.txt
→ name LIKE '%.txt'

test_*_version_9.*_$DATE*.txt  
→ name LIKE 'test_%_version_9.%_' + DATE() + '%.txt'

*.jpg AND size > 10MB
→ name LIKE '%.jpg' AND size > 10485760

modified > today-7
→ modified > DATE_SUB(NOW(), INTERVAL 7 DAY)
```

## Architecture Design

### Core Components (Simplified)

```
taskmover/core/patterns/
├── __init__.py                 # Public API exports
├── exceptions.py               # Pattern-specific exceptions
├── interfaces.py               # Abstract base classes and protocols
├── models/
│   ├── __init__.py
│   ├── pattern.py             # Unified Pattern entity
│   ├── pattern_group.py       # Pattern grouping and organization
│   ├── query_ast.py           # Internal query representation
│   └── metadata.py            # File metadata models
├── parsing/
│   ├── __init__.py
│   ├── intelligent_parser.py  # Main unified parser
│   ├── glob_translator.py     # Glob-to-query translation
│   ├── query_parser.py        # Advanced query parsing
│   ├── token_resolver.py      # Dynamic token handling
│   └── validator.py           # Pattern validation
├── matching/
│   ├── __init__.py
│   ├── unified_matcher.py     # Single matching engine
│   ├── query_executor.py      # Query execution engine
│   ├── content_matcher.py     # Content-based matching
│   └── metadata_matcher.py    # File metadata matching
├── storage/
│   ├── __init__.py
│   ├── repository.py          # Pattern repository
│   ├── serializer.py          # YAML/JSON serialization
│   ├── cache_manager.py       # Multi-level caching
│   └── migration.py           # Schema migration support
├── suggestions/
│   ├── __init__.py
│   ├── analyzer.py            # Workspace file analysis
│   ├── suggestion_engine.py   # Context-aware suggestions
│   ├── pattern_library.py     # Quick-access pattern dictionary
│   └── autocomplete.py        # Real-time auto-completion
├── validation/
│   ├── __init__.py
│   ├── pattern_validator.py   # Comprehensive validation
│   ├── tester.py              # Real-time pattern testing
│   └── performance_analyzer.py # Pattern performance analysis
└── ui_support/
    ├── __init__.py
    ├── builder_backend.py     # Visual pattern builder API
    ├── preview_generator.py   # Pattern preview generation
    └── date_builder.py        # Date format string builder
```

## Unified Pattern Language Specification

### Pattern Types (Simplified)

```python
class PatternComplexity(Enum):
    SIMPLE = "simple"        # Basic glob patterns: *.txt, file*.pdf
    ENHANCED = "enhanced"    # With tokens: report_$DATE*.txt
    ADVANCED = "advanced"    # With conditions: *.jpg AND size > 10MB
    COMPOSITE = "composite"  # Multiple patterns with logic
```

### Intelligent Parser Capabilities

#### 1. Basic Glob Pattern Recognition
```python
# Input patterns that are automatically recognized as glob
"*.txt"           → name LIKE '%.txt'
"file_*.pdf"      → name LIKE 'file_%.pdf'  
"test_???.log"    → name LIKE 'test___log'   # ?? = any 2 chars
```

#### 2. Enhanced Glob with Tokens
```python
# Patterns with dynamic tokens
"backup_$DATE.zip"           → name LIKE 'backup_' + DATE() + '.zip'
"log_$YYYY$MM$DD_*.txt"      → name LIKE 'log_' + YEAR() + MONTH() + DAY() + '_%.txt'
"report_$USER_*.pdf"         → name LIKE 'report_' + USER() + '_%.pdf'
```

#### 3. Mixed Syntax Detection
```python
# Automatic detection of enhanced syntax
"*.jpg AND size > 10MB"      → Advanced parsing mode
"modified > today-7"         → Date expression parsing
"@media"                     → Pattern group reference
"content CONTAINS 'TODO'"    → Content-based matching
```

#### 4. Shorthand Extensions
```python
# Convenient shorthand syntax
">10MB"           → size > 10485760
"<today-30"       → modified > DATE_SUB(NOW(), INTERVAL 30 DAY)
"@documents"      → Reference to documents pattern group
".hidden"         → hidden = true
```

### Supported Field Names and Operators

#### File System Fields
- `name` / `filename`: File name (with or without extension)
- `extension` / `ext`: File extension  
- `path`: Full file path
- `directory` / `dir`: Parent directory path
- `size`: File size in bytes
- `created`: File creation date
- `modified` / `last_modified`: Last modification date
- `accessed` / `last_accessed`: Last access date
- `type`: File type (file, directory, symlink)
- `hidden`: Boolean for hidden files
- `readonly`: Boolean for read-only files

#### Enhanced Metadata Fields
- `owner`: File owner (when available)
- `permissions`: File permissions
- `mime_type`: MIME type detection
- `checksum`: File content hash (MD5, SHA256)
- `content`: Text content (searchable)
- `encoding`: File encoding (utf-8, ascii, etc.)
- `line_count`: Number of lines in text files
- `word_count`: Number of words in text files

#### Operators
- **Comparison**: `=`, `!=`, `<`, `<=`, `>`, `>=`
- **Pattern Matching**: `LIKE`, `GLOB`, `REGEX`
- **Logical**: `AND`, `OR`, `NOT`, `XOR`
- **Collection**: `IN`, `NOT IN`, `BETWEEN`
- **String**: `CONTAINS`, `STARTS_WITH`, `ENDS_WITH`
- **Null Checks**: `IS NULL`, `IS NOT NULL`

## Unified Pattern Model

```python
@dataclass
class Pattern:
    id: UUID
    name: str
    description: str
    
    # Unified pattern storage
    user_expression: str            # What user typed: "test_*_$DATE*.txt"
    compiled_query: str             # Internal query: "name LIKE 'test_%_' + DATE() + '%.txt'"
    pattern_complexity: PatternComplexity
    
    # Pattern organization
    tags: List[str]
    group_id: Optional[UUID]
    category: str
    
    # Metadata
    created_date: datetime
    modified_date: datetime
    author: str
    version: int
    
    # Performance and usage
    estimated_complexity: int = 1   # 1-10 scale
    cache_ttl: Optional[int] = None
    usage_count: int = 0
    last_used: Optional[datetime] = None
    
    # Validation results
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    last_validated: Optional[datetime] = None
```

## Intelligent Parser Architecture

### Main Parser Class

```python
class IntelligentPatternParser:
    """Unified parser that handles all pattern input types."""
    
    def parse(self, user_input: str) -> ParsedPattern:
        """Parse any pattern input and return structured representation."""
        
        # 1. Detect pattern type and complexity
        pattern_type = self._detect_pattern_type(user_input)
        
        # 2. Route to appropriate parser
        if pattern_type == PatternType.SIMPLE_GLOB:
            return self._parse_glob_pattern(user_input)
        elif pattern_type == PatternType.ENHANCED_GLOB:
            return self._parse_enhanced_glob(user_input)
        elif pattern_type == PatternType.ADVANCED_QUERY:
            return self._parse_advanced_query(user_input)
        elif pattern_type == PatternType.SHORTHAND:
            return self._parse_shorthand(user_input)
            
    def _detect_pattern_type(self, input_str: str) -> PatternType:
        """Intelligently detect what type of pattern the user entered."""
        
        # Check for advanced query keywords
        if any(keyword in input_str.upper() for keyword in ['AND', 'OR', 'NOT', 'WHERE', 'SIZE', 'MODIFIED']):
            return PatternType.ADVANCED_QUERY
            
        # Check for tokens
        if '$' in input_str:
            return PatternType.ENHANCED_GLOB
            
        # Check for shorthand
        if input_str.startswith(('@', '>', '<', '.')):
            return PatternType.SHORTHAND
            
        # Default to simple glob
        return PatternType.SIMPLE_GLOB
```

### Translation Examples

#### 1. Simple Glob Translation
```python
def translate_glob_to_query(glob_pattern: str) -> str:
    """Convert glob pattern to SQL LIKE query."""
    
    # *.txt → name LIKE '%.txt'
    # file_*.pdf → name LIKE 'file_%.pdf'
    # test_???.log → name LIKE 'test___.log'
    
    query_pattern = glob_pattern.replace('*', '%').replace('?', '_')
    return f"name LIKE '{query_pattern}'"
```

#### 2. Token Resolution
```python
def resolve_tokens(pattern: str) -> str:
    """Resolve dynamic tokens in patterns."""
    
    token_mappings = {
        '$DATE': 'DATE()',
        '$YYYY': 'YEAR(NOW())',
        '$MM': 'MONTH(NOW())', 
        '$DD': 'DAY(NOW())',
        '$USER': 'USER()',
        '$HOSTNAME': 'HOSTNAME()'
    }
    
    for token, replacement in token_mappings.items():
        pattern = pattern.replace(token, replacement)
    
    return pattern
```

#### 3. Advanced Query Parsing
```python
def parse_advanced_query(query: str) -> QueryAST:
    """Parse complex queries with logical operators."""
    
    # *.jpg AND size > 10MB
    # modified > today-7 AND content CONTAINS 'important'
    # (name LIKE '%.doc' OR name LIKE '%.pdf') AND size < 5MB
    
    return self.query_parser.parse(query)
```

## Pattern Groups and Organization

### System-Defined Groups with Natural References

```python
SYSTEM_GROUPS = {
    "@media": {
        "name": "Media Files",
        "patterns": ["*.jpg", "*.png", "*.gif", "*.mp4", "*.mp3"],
        "description": "Images, videos, and audio files"
    },
    "@documents": {
        "name": "Documents", 
        "patterns": ["*.pdf", "*.doc", "*.docx", "*.txt", "*.rtf"],
        "description": "Text documents and PDFs"
    },
    "@code": {
        "name": "Source Code",
        "patterns": ["*.py", "*.js", "*.html", "*.css", "*.java", "*.cpp"],
        "description": "Programming and markup files"
    },
    "@archives": {
        "name": "Archives",
        "patterns": ["*.zip", "*.tar", "*.gz", "*.rar", "*.7z"],
        "description": "Compressed and archive files"
    },
    "@temporary": {
        "name": "Temporary Files",
        "patterns": ["*.tmp", "*.temp", "*~", "*.bak"],
        "description": "Cache, temp, and backup files"
    }
}
```

### Pattern Group Usage
```python
# Users can reference groups naturally
"@media AND size > 50MB"        # Large media files
"@code AND modified > today-7"  # Recently modified code
"NOT @temporary"                # Exclude temporary files
```

## Context-Aware Suggestions

### Workspace Analysis Integration

```python
class ContextAwareSuggestionEngine:
    """Provides intelligent pattern suggestions based on workspace analysis."""
    
    def suggest_patterns(self, workspace_path: Path, partial_input: str = "") -> List[PatternSuggestion]:
        """Generate context-aware pattern suggestions."""
        
        # Analyze workspace
        analysis = self.workspace_analyzer.analyze(workspace_path)
        
        # Generate suggestions based on:
        # 1. Most common file extensions in workspace
        # 2. Recent file patterns
        # 3. Directory structure patterns
        # 4. User's typing patterns
        # 5. Partial input completion
        
        suggestions = []
        
        # Extension-based suggestions
        for ext in analysis.common_extensions[:10]:
            suggestions.append(PatternSuggestion(
                pattern=f"*.{ext}",
                description=f"All {ext.upper()} files",
                confidence=0.9,
                category="extension"
            ))
        
        # Pattern completion suggestions
        if partial_input:
            completions = self._complete_pattern(partial_input, analysis)
            suggestions.extend(completions)
            
        return sorted(suggestions, key=lambda x: x.confidence, reverse=True)
```

### Auto-Completion Examples

```python
# Real-time auto-completion as user types
"test_*"     → ["test_*.txt", "test_*.log", "test_*.pdf"]
"$DATE"      → ["$DATE*.txt", "$DATE_report.pdf", "$DATE_backup.zip"]  
"size >"     → ["size > 1MB", "size > 10MB", "size > 100MB"]
"modified"   → ["modified > today-7", "modified > yesterday", "modified < today-30"]
```

## Visual Pattern Builder Backend

### Condition-Based Construction API

```python
class PatternBuilderBackend:
    """Backend API for visual pattern builder."""
    
    def get_available_fields(self) -> List[FieldDefinition]:
        """Get all fields available for pattern construction."""
        return [
            FieldDefinition(name="name", type="string", operators=["LIKE", "=", "!="]),
            FieldDefinition(name="size", type="integer", operators=[">", "<", "=", "BETWEEN"]),
            FieldDefinition(name="modified", type="datetime", operators=[">", "<", "="]),
            # ... more fields
        ]
    
    def build_pattern_from_conditions(self, conditions: List[PatternCondition]) -> str:
        """Convert visual conditions to pattern string."""
        
        # Convert visual drag-and-drop conditions to natural pattern language
        # Example: [name LIKE "*.txt", size > 10MB] → "*.txt AND size > 10MB"
        
        if len(conditions) == 1 and conditions[0].is_simple_glob():
            return conditions[0].value  # Return simple "*.txt"
        
        # Build complex query
        query_parts = []
        for condition in conditions:
            query_parts.append(self._condition_to_string(condition))
        
        return " AND ".join(query_parts)
```

## Performance and Caching

### Multi-Level Caching Strategy

```python
class UnifiedCacheManager:
    """Multi-level caching for pattern system performance."""
    
    def __init__(self):
        self.memory_cache = LRUCache(maxsize=1000)      # Parsed patterns
        self.query_cache = LRUCache(maxsize=500)        # Query results  
        self.metadata_cache = FileMetadataCache()       # File metadata
        self.compilation_cache = PatternCompilationCache() # Compiled patterns
    
    def get_pattern_result(self, pattern: str, file_paths: List[Path]) -> Optional[List[Path]]:
        """Get cached pattern matching result."""
        cache_key = self._build_cache_key(pattern, file_paths)
        return self.query_cache.get(cache_key)
    
    def cache_pattern_result(self, pattern: str, file_paths: List[Path], result: List[Path]):
        """Cache pattern matching result with TTL."""
        cache_key = self._build_cache_key(pattern, file_paths)
        self.query_cache.set(cache_key, result, ttl=300)  # 5 minute TTL
```

## Migration Strategy

### Backward Compatibility

```python
class PatternMigration:
    """Handle migration from existing patterns to unified system."""
    
    def migrate_existing_patterns(self, old_patterns: List[OldPattern]) -> List[Pattern]:
        """Convert existing glob/regex patterns to unified format."""
        
        migrated = []
        for old_pattern in old_patterns:
            new_pattern = Pattern(
                id=old_pattern.id,
                name=old_pattern.name,
                description=old_pattern.description,
                user_expression=old_pattern.pattern,  # Preserve original
                compiled_query=self._compile_pattern(old_pattern.pattern),
                pattern_complexity=self._detect_complexity(old_pattern.pattern),
                # ... copy other fields
            )
            migrated.append(new_pattern)
            
        return migrated
```

### Seamless User Transition

1. **Existing patterns continue to work**: No user action required
2. **Gradual feature introduction**: New features become available naturally
3. **Optional migration tools**: Help users optimize patterns if desired
4. **Clear documentation**: Guide users to new capabilities

## Implementation Phases (Updated)

### Phase 1: Unified Core Infrastructure (Weeks 1-2)
- [ ] Implement unified Pattern model
- [ ] Create IntelligentPatternParser
- [ ] Build basic glob-to-query translation
- [ ] Implement UnifiedPatternMatcher
- [ ] Set up pattern repository with caching

### Phase 2: Enhanced Parsing & Translation (Weeks 3-4)
- [ ] Add token resolution system ($DATE, $USER, etc.)
- [ ] Implement advanced query parsing
- [ ] Add shorthand syntax support (@groups, >size, etc.)
- [ ] Create pattern validation framework
- [ ] Implement query optimization

### Phase 3: Context-Aware Features (Weeks 5-6)
- [ ] Build workspace analysis engine
- [ ] Implement suggestion system
- [ ] Create pattern library with system groups
- [ ] Add auto-completion support
- [ ] Build pattern usage analytics

### Phase 4: Visual Builder & UI Support (Weeks 7-8)
- [ ] Create pattern builder backend API
- [ ] Implement condition-based construction
- [ ] Add drag-and-drop support structures
- [ ] Build date format builder
- [ ] Create pattern preview system

### Phase 5: Performance & Caching (Weeks 9-10)
- [ ] Implement multi-level caching
- [ ] Add query optimization engine
- [ ] Create incremental processing
- [ ] Build performance monitoring
- [ ] Optimize for large file sets

### Phase 6: Testing & Polish (Weeks 11-12)
- [ ] Comprehensive testing framework
- [ ] Pattern debugging tools
- [ ] Performance benchmarking
- [ ] Documentation and examples
- [ ] Migration tools and guides

## Success Metrics

### Performance Targets
- **Pattern parsing**: <5ms for simple patterns, <20ms for complex queries
- **Pattern matching**: <100ms for 1000 files, <1s for 10,000 files  
- **Memory usage**: <25MB for pattern system components
- **Cache hit rate**: >85% for repeated operations

### User Experience Targets
- **Pattern creation time**: 60% reduction with auto-suggestions
- **Error rate**: <2% pattern syntax errors with intelligent parsing
- **Feature adoption**: >50% users using enhanced features within 3 months
- **User satisfaction**: >90% positive feedback on unified interface

## Advantages of Unified Architecture

### 1. **Simplified Implementation**
- Single parser instead of dual-syntax system
- One matching engine for all pattern types
- Reduced code complexity and maintenance

### 2. **Enhanced User Experience**
- Natural, intuitive pattern entry
- No confusion about which syntax to use
- Gradual feature discovery

### 3. **Better Performance**
- Single optimization pipeline
- More effective caching strategy
- Reduced translation overhead

### 4. **Easier Extension**
- New features integrate naturally
- Consistent auto-completion and suggestions
- Unified testing and validation

### 5. **Cleaner Architecture**
- Clear separation of concerns
- Single source of truth for pattern logic
- Simplified dependency management

---

## Conclusion

The unified pattern system provides the best of both worlds: the familiarity and simplicity that users expect, combined with powerful features and intelligent behavior. By implementing a single, smart parser that can handle everything from basic glob patterns to complex queries, we create a system that's both easier to implement and more pleasant to use.

**Key Benefits:**
- ✅ **Simplified Architecture**: Single parser, single matcher, cleaner codebase
- ✅ **Natural User Experience**: Familiar patterns work, enhanced features discoverable
- ✅ **Backward Compatibility**: Existing patterns continue to work seamlessly
- ✅ **Performance Optimized**: Single optimization pipeline, effective caching
- ✅ **Future-Proof**: Easy to extend with new features and capabilities

**Status**: ✅ **Unified Specification Complete** - Ready for development team implementation

**Next Steps**: 
1. Development team review of unified approach
2. Begin Phase 1 implementation with simplified architecture
3. Create pattern examples and user documentation
4. Set up performance benchmarking baseline
