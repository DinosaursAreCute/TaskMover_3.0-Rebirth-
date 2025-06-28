# TaskMover API Reference

**Version**: 1.0 (Pattern System Backend Complete)  
**Date**: June 29, 2025  
**Status**: Production Ready Backend APIs

This document provides comprehensive API documentation for the TaskMover backend system.

## 🎯 API Overview

The TaskMover backend provides a clean, interface-based API for pattern management, file organization, and conflict resolution. All APIs follow SOLID principles and use dependency injection for loose coupling.

### Core API Modules

| Module | Description | Status |
|--------|-------------|--------|
| **Pattern System** | Core pattern management and matching | ✅ Complete |
| **Conflict Resolution** | File conflict detection and resolution | ✅ Complete |
| **Logging System** | Structured logging and error tracking | ✅ Complete |
| **Storage & Caching** | Pattern storage and performance optimization | ✅ Complete |
| **Dependency Injection** | Service container and lifecycle management | ✅ Complete |

---

## 🏗️ Pattern System APIs

### Core Interfaces

#### `IPatternService`
Main service interface for pattern operations.

```python
from taskmover.core.patterns import IPatternService

class IPatternService(Protocol):
    """Core pattern service interface"""
    
    async def parse_pattern(self, pattern_input: str) -> ParsedPattern:
        """Parse user input into structured pattern"""
        
    async def match_files(self, pattern: ParsedPattern, workspace_path: str) -> List[FileMatch]:
        """Match files against pattern in workspace"""
        
    async def get_suggestions(self, partial_input: str, context: WorkspaceContext) -> List[Suggestion]:
        """Get context-aware pattern suggestions"""
        
    async def validate_pattern(self, pattern: ParsedPattern) -> ValidationResult:
        """Validate pattern syntax and semantics"""
```

#### `IPatternRepository`
Pattern storage and retrieval interface.

```python
from taskmover.core.patterns.storage import IPatternRepository

class IPatternRepository(Protocol):
    """Pattern storage interface"""
    
    async def save_pattern(self, pattern: PatternDefinition) -> str:
        """Save pattern and return ID"""
        
    async def get_pattern(self, pattern_id: str) -> Optional[PatternDefinition]:
        """Retrieve pattern by ID"""
        
    async def list_patterns(self, group: Optional[str] = None) -> List[PatternDefinition]:
        """List patterns, optionally filtered by group"""
        
    async def delete_pattern(self, pattern_id: str) -> bool:
        """Delete pattern by ID"""
```

### Data Models

#### `ParsedPattern`
Represents a parsed and validated pattern.

```python
@dataclass
class ParsedPattern:
    """Parsed pattern with optimization metadata"""
    
    id: str
    name: str
    description: str
    query: QueryAST
    metadata: PatternMetadata
    optimization_hints: List[OptimizationHint]
    created_at: datetime
    updated_at: datetime
```

#### `FileMatch`
Represents a file that matches a pattern.

```python
@dataclass
class FileMatch:
    """File that matches a pattern"""
    
    file_path: Path
    match_confidence: float
    matched_conditions: List[str]
    target_location: Optional[Path]
    conflict_info: Optional[ConflictInfo]
```

### Usage Examples

#### Basic Pattern Operations

```python
from taskmover.core.di import get_container
from taskmover.core.patterns import IPatternService

# Get pattern service
container = get_container()
pattern_service = container.resolve(IPatternService)

# Parse a pattern
pattern = await pattern_service.parse_pattern("*.py created:last_week size:>1MB")

# Match files
matches = await pattern_service.match_files(pattern, "/workspace/path")

# Get suggestions
suggestions = await pattern_service.get_suggestions("*.js", workspace_context)
```

#### Advanced Pattern Management

```python
from taskmover.core.patterns.storage import IPatternRepository

# Get repository service
pattern_repo = container.resolve(IPatternRepository)

# Save a pattern
pattern_def = PatternDefinition(
    name="Large Python Files",
    pattern="*.py size:>1MB",
    target_directory="large_files/",
    group="development"
)
pattern_id = await pattern_repo.save_pattern(pattern_def)

# List patterns by group
dev_patterns = await pattern_repo.list_patterns(group="development")
```

---

## ⚔️ Conflict Resolution APIs

### Core Interfaces

#### `IConflictResolver`
Main interface for conflict resolution.

```python
from taskmover.core.conflict_resolution import IConflictResolver

class IConflictResolver(Protocol):
    """Conflict resolution service interface"""
    
    async def detect_conflicts(self, operations: List[FileOperation]) -> List[Conflict]:
        """Detect conflicts in file operations"""
        
    async def resolve_conflict(self, conflict: Conflict, strategy: ResolutionStrategy) -> ResolutionResult:
        """Resolve a specific conflict using given strategy"""
        
    async def get_resolution_options(self, conflict: Conflict) -> List[ResolutionOption]:
        """Get available resolution options for conflict"""
```

#### `IConflictStrategy`
Interface for conflict resolution strategies.

```python
from taskmover.core.conflict_resolution.strategies import IConflictStrategy

class IConflictStrategy(Protocol):
    """Conflict resolution strategy interface"""
    
    def can_handle(self, conflict: Conflict) -> bool:
        """Check if strategy can handle this conflict type"""
        
    async def resolve(self, conflict: Conflict, context: ResolutionContext) -> ResolutionResult:
        """Execute resolution strategy"""
        
    def get_options(self, conflict: Conflict) -> List[ResolutionOption]:
        """Get resolution options for this conflict"""
```

### Data Models

#### `Conflict`
Represents a detected file operation conflict.

```python
@dataclass
class Conflict:
    """File operation conflict"""
    
    id: str
    type: ConflictType
    source_path: Path
    target_path: Path
    description: str
    severity: ConflictSeverity
    auto_resolvable: bool
    suggested_resolution: Optional[ResolutionStrategy]
```

#### `ResolutionResult`
Result of conflict resolution attempt.

```python
@dataclass
class ResolutionResult:
    """Result of conflict resolution"""
    
    success: bool
    strategy_used: ResolutionStrategy
    actions_taken: List[str]
    final_path: Optional[Path]
    error_message: Optional[str]
```

### Usage Examples

#### Conflict Detection and Resolution

```python
from taskmover.core.conflict_resolution import IConflictResolver
from taskmover.core.conflict_resolution.enums import ResolutionStrategy

# Get conflict resolver
conflict_resolver = container.resolve(IConflictResolver)

# Detect conflicts
operations = [FileOperation(source="/file1.txt", target="/existing.txt")]
conflicts = await conflict_resolver.detect_conflicts(operations)

# Resolve conflicts
for conflict in conflicts:
    options = await conflict_resolver.get_resolution_options(conflict)
    result = await conflict_resolver.resolve_conflict(
        conflict, 
        ResolutionStrategy.RENAME_TARGET
    )
```

---

## 📝 Logging System APIs

### Core Interfaces

#### `ILogManager`
Main logging management interface.

```python
from taskmover.core.logging import ILogManager

class ILogManager(Protocol):
    """Logging management interface"""
    
    def get_logger(self, name: str) -> IStructuredLogger:
        """Get logger instance for component"""
        
    def configure_from_config(self, config_path: str) -> None:
        """Configure logging from YAML config"""
        
    def set_global_level(self, level: LogLevel) -> None:
        """Set global logging level"""
```

#### `IStructuredLogger`
Structured logging interface with context support.

```python
from taskmover.core.logging.interfaces import IStructuredLogger

class IStructuredLogger(Protocol):
    """Structured logger with context support"""
    
    def info(self, message: str, **context) -> None:
        """Log info message with context"""
        
    def error(self, message: str, error: Optional[Exception] = None, **context) -> None:
        """Log error with exception details"""
        
    def debug(self, message: str, **context) -> None:
        """Log debug information"""
        
    def with_context(self, **context) -> 'IStructuredLogger':
        """Create logger with additional context"""
```

### Usage Examples

#### Basic Logging

```python
from taskmover.core.logging import get_logger

# Get logger for component
logger = get_logger("pattern_service")

# Log with context
logger.info(
    "Pattern parsed successfully",
    pattern_id="abc123",
    file_count=42,
    parse_time_ms=150
)

# Log errors with exception
try:
    # Some operation
    pass
except Exception as e:
    logger.error(
        "Pattern parsing failed",
        error=e,
        pattern_input="invalid_pattern",
        user_id="user123"
    )
```

#### Contextual Logging

```python
# Create logger with persistent context
service_logger = logger.with_context(
    service="pattern_service",
    version="1.0",
    user_id="user123"
)

# All subsequent logs include this context
service_logger.info("Service started")
service_logger.debug("Processing request", request_id="req456")
```

---

## 🏪 Dependency Injection APIs

### Core Interfaces

#### `ServiceContainer`
Main dependency injection container.

```python
from taskmover.core.di import ServiceContainer, ServiceLifetime

# Create container
container = ServiceContainer()

# Register services
container.register(IPatternService, PatternService, ServiceLifetime.SINGLETON)
container.register(IConflictResolver, ConflictResolver, ServiceLifetime.TRANSIENT)

# Resolve services
pattern_service = container.resolve(IPatternService)
```

#### Service Registration Decorators

```python
from taskmover.core.di import injectable, singleton, transient

# Register as singleton
@singleton(IPatternService)
class PatternService:
    def __init__(self, repository: IPatternRepository):
        self.repository = repository

# Register as transient
@transient(IConflictResolver)
class ConflictResolver:
    pass

# Manual registration
@injectable(ILogManager, ServiceLifetime.SINGLETON)
class LogManager:
    pass
```

### Usage Examples

#### Service Resolution with Dependencies

```python
from taskmover.core.di import get_container

# Services are automatically injected based on constructor parameters
class PatternService:
    def __init__(
        self,
        repository: IPatternRepository,
        logger: IStructuredLogger,
        cache: ICacheManager
    ):
        self.repository = repository
        self.logger = logger
        self.cache = cache

# Automatic dependency resolution
container = get_container()
service = container.resolve(IPatternService)  # All dependencies injected
```

---

## 🚀 Quick Start Examples

### Complete Pattern Processing Workflow

```python
from taskmover.core.di import get_container
from taskmover.core.patterns import IPatternService
from taskmover.core.conflict_resolution import IConflictResolver

async def process_files_with_pattern():
    # Get services
    container = get_container()
    pattern_service = container.resolve(IPatternService)
    conflict_resolver = container.resolve(IConflictResolver)
    
    # Parse pattern
    pattern = await pattern_service.parse_pattern(
        "*.py created:today size:>500KB -> organized/python/"
    )
    
    # Find matching files
    matches = await pattern_service.match_files(pattern, "/workspace")
    
    # Create file operations
    operations = [
        FileOperation(match.file_path, match.target_location)
        for match in matches
    ]
    
    # Detect and resolve conflicts
    conflicts = await conflict_resolver.detect_conflicts(operations)
    for conflict in conflicts:
        result = await conflict_resolver.resolve_conflict(
            conflict, 
            ResolutionStrategy.RENAME_TARGET
        )
        
    return operations, conflicts
```

### Service Registration and Configuration

```python
from taskmover.core.di import get_container
from taskmover.core.logging import configure_logging

def setup_application():
    # Configure logging
    configure_logging("config/logging_config.yml")
    
    # Get configured container
    container = get_container()
    
    # All services are already registered via decorators
    # Ready to resolve and use
    pattern_service = container.resolve(IPatternService)
    
    return container
```

---

## 🔧 Configuration

### Logging Configuration
Logging is configured via YAML file at `config/logging_config.yml`:

```yaml
version: 1
formatters:
  structured:
    class: taskmover.core.logging.formatters.StructuredFormatter
    format: "{timestamp} | {level} | {name} | {message} | {context}"

handlers:
  console:
    class: logging.StreamHandler
    formatter: structured
    level: INFO
    
  file:
    class: logging.FileHandler
    filename: logs/taskmover.log
    formatter: structured
    level: DEBUG

loggers:
  taskmover:
    level: DEBUG
    handlers: [console, file]
    propagate: false
```

### Service Configuration
Services can be configured through the DI container:

```python
# Custom service configuration
container.register(
    ICacheManager,
    RedisCacheManager,
    ServiceLifetime.SINGLETON,
    configuration={
        "redis_url": "redis://localhost:6379",
        "default_ttl": 3600
    }
)
```

---

## 📊 Performance Considerations

### Caching
- **Pattern Cache**: Parsed patterns are cached for reuse
- **File Metadata Cache**: File system metadata is cached for performance
- **Query Optimization**: Query plans are optimized and cached

### Async/Await
- All file I/O operations are asynchronous
- Pattern matching supports parallel processing
- Conflict resolution can process multiple conflicts concurrently

### Memory Management
- Lazy loading of file metadata
- Streaming for large file sets
- Configurable cache limits

---

## 🔍 Error Handling

### Exception Types

```python
from taskmover.core.patterns.exceptions import (
    PatternParseException,
    PatternValidationException,
    FileMatchException
)

from taskmover.core.conflict_resolution.exceptions import (
    ConflictResolutionException,
    UnsupportedConflictTypeException
)
```

### Error Context
All exceptions include structured context:

```python
try:
    pattern = await pattern_service.parse_pattern(invalid_input)
except PatternParseException as e:
    # Exception includes:
    # - Original input
    # - Parse position
    # - Suggested corrections
    # - Context information
    logger.error("Pattern parse failed", error=e)
```

---

## 📈 Testing APIs

### Test Utilities
```python
from taskmover.tests.fixtures import (
    create_test_pattern,
    create_test_workspace,
    create_test_conflicts
)

# Create test data
pattern = create_test_pattern("test_pattern")
workspace = create_test_workspace()
conflicts = create_test_conflicts(count=5)
```

### Mock Services
```python
from taskmover.tests.mocks import (
    MockPatternService,
    MockConflictResolver,
    MockRepository
)

# Use mocks in tests
container.register(IPatternService, MockPatternService)
```

---

*Last Updated: June 29, 2025*  
*API Version: 1.0 (Backend Complete)*
