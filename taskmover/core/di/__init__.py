"""
TaskMover Dependency Injection Package

Lightweight dependency injection container with:
- Constructor injection with automatic dependency resolution
- Service lifetime management (singleton, transient, scoped)
- Circular dependency detection
- Thread-safe service resolution
- Decorator-based service registration
- Service scoping for request/operation-scoped services

Usage:
    from taskmover.core.di import get_container, injectable, singleton

    # Register services
    @singleton(ILogger)
    class FileLogger(ILogger):
        def __init__(self, config: IConfig):
            self.config = config

    # Resolve services
    container = get_container()
    logger = container.resolve(ILogger)
"""

from .container import (
    ServiceContainer,
    ServiceScope,
    get_container,
    reset_container,
    service_scope,
)
from .decorators import factory, inject, injectable, scoped, singleton, transient
from .interfaces import (
    CircularDependencyException,
    IServiceContainer,
    IServiceRegistry,
    IServiceScope,
    ServiceLifetime,
    ServiceLifetimeException,
    ServiceNotRegisteredException,
    ServiceRegistration,
)

__all__ = [
    # Container classes
    "ServiceContainer",
    "ServiceScope",
    "get_container",
    "reset_container",
    "service_scope",
    # Interfaces
    "IServiceContainer",
    "IServiceScope",
    "IServiceRegistry",
    "ServiceRegistration",
    "ServiceLifetime",
    # Exceptions
    "ServiceNotRegisteredException",
    "CircularDependencyException",
    "ServiceLifetimeException",
    # Decorators
    "injectable",
    "singleton",
    "transient",
    "scoped",
    "inject",
    "factory",
]

__version__ = "1.0.0"
