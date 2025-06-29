# TaskMover Architecture

## Overview

TaskMover is built with a clean, modular architecture following SOLID principles and dependency injection patterns. The system consists of three main layers: Core Business Logic, User Interface, and Infrastructure.

## Core Architecture

### System Layers

```
┌─────────────────────────────────────┐
│           User Interface            │
│  ┌─────────────┬─────────────────┐  │
│  │ Modern UI   │  CLI Interface  │  │
│  │ Components  │  (Future)       │  │
│  └─────────────┴─────────────────┘  │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│          Core Business Logic        │
│  ┌──────────┬──────────┬─────────┐  │
│  │ Pattern  │  Rule    │ Conflict│  │
│  │ System   │  System  │ Resolver│  │
│  └──────────┴──────────┴─────────┘  │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│          Infrastructure             │
│  ┌──────────┬──────────┬─────────┐  │
│  │ Logging  │ Storage  │ DI      │  │
│  │ System   │ Layer    │ Container│ │
│  └──────────┴──────────┴─────────┘  │
└─────────────────────────────────────┘
```

## Core Systems

### Pattern System (`taskmover/core/patterns/`)

The Pattern System provides intelligent file matching capabilities:

- **Models**: Data structures for patterns, groups, and metadata
- **Parsing**: Intelligent pattern parser that translates user input to optimized queries
- **Matching**: Unified matching engine supporting multiple pattern types
- **Storage**: Pattern persistence with YAML-based repository
- **Suggestions**: Context-aware pattern suggestions based on workspace analysis
- **Validation**: Pattern syntax validation and optimization

### Rule System (`taskmover/core/rules/`)

The Rule System provides file organization automation:

- **Models**: Data structures for rules, execution results, and conflicts
- **Service**: High-level rule management and execution
- **Storage**: Rule persistence with YAML-based repository and caching
- **Validation**: Rule validation and conflict detection
- **Exceptions**: Comprehensive exception hierarchy for error handling

#### Rule System Integration

```
┌─────────────┐    references    ┌─────────────┐
│    Rule     │ ───────────────► │   Pattern   │
│   System    │                  │   System    │
└─────────────┘                  └─────────────┘
       │                                │
       │ uses for                       │ provides
       │ file matching                  │ matching
       ▼                                ▼
┌─────────────┐    resolves      ┌─────────────┐
│  Conflict   │ ◄─────────────── │ File System │
│  Manager    │                  │ Operations  │
└─────────────┘                  └─────────────┘
```

### Conflict Resolution (`taskmover/core/conflict_resolution/`)

Handles file operation conflicts:

- **Conflict Detection**: Identifies potential file conflicts
- **Resolution Strategies**: Multiple conflict resolution approaches
- **User Interaction**: Interactive conflict resolution when needed

### Infrastructure Systems

#### Dependency Injection (`taskmover/core/di/`)

- **Service Container**: Manages service lifetime and dependencies
- **Registration**: Service registration with lifetime management
- **Resolution**: Automatic dependency resolution

#### Logging System (`taskmover/core/logging/`)

- **Structured Logging**: Comprehensive logging with context tracking
- **Performance Monitoring**: Operation timing and performance metrics
- **Multiple Outputs**: Console, file, and structured JSON logging

#### Storage Layer

- **YAML Persistence**: Human-readable storage format
- **Backup System**: Automatic backup and versioning
- **Caching**: In-memory caching for performance

## Data Flow

### Rule Execution Flow

```
1. User creates/selects rule
2. Rule Service validates rule
3. Pattern System matches files
4. Conflict Manager checks for conflicts
5. File operations executed
6. Results logged and stored
```

### Pattern Matching Flow

```
1. Pattern input received
2. Intelligent Parser processes input
3. Unified Matcher executes pattern
4. Results cached and returned
5. Suggestions generated for future use
```

## Design Principles

### SOLID Principles

- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for base types
- **Interface Segregation**: Clients don't depend on unused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

### Clean Architecture

- **Dependency Direction**: Dependencies point inward toward business logic
- **Layer Separation**: Clear boundaries between layers
- **Testability**: Each layer can be tested in isolation

### Performance Considerations

- **Caching**: Multi-level caching for frequently accessed data
- **Lazy Loading**: Load data only when needed
- **Async Operations**: Non-blocking operations where possible

## Testing Strategy

### Test Structure

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests between systems
├── performance/       # Performance and load testing
└── fixtures/          # Test data and mock objects
```

### Test Coverage

- **Unit Tests**: 100% coverage of business logic
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Load and stress testing

## Extension Points

### Adding New Pattern Types

1. Implement pattern parser in `parsing/`
2. Add matcher in `matching/`
3. Update validation in `validation/`
4. Add tests and documentation

### Adding New Conflict Resolution Strategies

1. Implement strategy in `conflict_resolution/`
2. Register with Conflict Manager
3. Add UI components if needed
4. Update documentation

### Adding New Storage Backends

1. Implement repository interface
2. Add configuration options
3. Update dependency injection setup
4. Add migration tools if needed

## Future Enhancements

### Planned Features

- **Real-time File Watching**: Automatic rule execution on file changes
- **Plugin System**: Third-party extensions and patterns
- **Cloud Storage**: Remote pattern and rule storage
- **Advanced Analytics**: Detailed usage and performance analytics

### Scalability Improvements

- **Database Backend**: Optional database storage for large datasets
- **Distributed Processing**: Multi-threaded file operations
- **Memory Optimization**: Improved memory usage for large file sets

## Configuration

### System Configuration

Configuration is managed through:

- **YAML Files**: User-friendly configuration format
- **Environment Variables**: Runtime configuration overrides
- **Command Line Arguments**: Development and debugging options

### Logging Configuration

- **Log Levels**: Configurable verbosity levels
- **Output Formats**: Console, file, and structured formats
- **Performance Tracking**: Optional performance metrics collection

## Security Considerations

### File System Access

- **Permission Checking**: Verify file system permissions before operations
- **Path Validation**: Sanitize and validate all file paths
- **Atomic Operations**: Ensure file operations are atomic where possible

### Data Validation

- **Input Sanitization**: Validate all user input
- **Pattern Security**: Prevent malicious pattern expressions
- **Configuration Validation**: Validate all configuration data

## Maintenance

### Code Quality

- **Linting**: Automated code quality checks
- **Type Hints**: Full type annotation coverage
- **Documentation**: Comprehensive API documentation

### Monitoring

- **Performance Metrics**: Track system performance
- **Error Tracking**: Comprehensive error logging
- **Usage Analytics**: Optional usage statistics collection