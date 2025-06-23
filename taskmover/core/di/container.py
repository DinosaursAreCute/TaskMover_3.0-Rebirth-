"""
Dependency Injection Container Implementation

Lightweight, fast dependency injection container with constructor injection,
service lifetime management, and circular dependency detection.
"""

import threading
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, TypeVar

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

T = TypeVar("T")


class ServiceContainer(IServiceContainer):
    """
    Main dependency injection container implementation.

    Features:
    - Constructor injection with automatic dependency resolution
    - Service lifetime management (singleton, transient, scoped)
    - Circular dependency detection
    - Thread-safe service resolution
    - Named service registrations
    - Service scoping for request-scoped services
    """

    def __init__(self):
        self._registry = ServiceRegistry()
        self._singletons: dict[str, Any] = {}
        self._resolution_stack: list[type] = []
        self._lock = threading.RLock()

    def register(
        self,
        interface: type[T],
        implementation: type[T] | None = None,
        factory: Callable[[], T] | None = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        name: str | None = None,
    ) -> None:
        """Register a service with the container"""
        registration = ServiceRegistration(
            interface=interface,
            implementation=implementation,
            factory=factory,
            lifetime=lifetime,
            name=name,
        )

        with self._lock:
            self._registry.add_registration(registration)

    def resolve(self, interface: type[T], name: str | None = None) -> T:
        """Resolve a service instance"""
        with self._lock:
            return self._resolve_internal(interface, name)

    def _resolve_internal(self, interface: type[T], name: str | None = None) -> T:
        """Internal resolution with circular dependency detection"""
        # Check for circular dependencies
        if interface in self._resolution_stack:
            self._resolution_stack.append(interface)
            raise CircularDependencyException(self._resolution_stack.copy())

        try:
            self._resolution_stack.append(interface)

            # Get registration
            registration = self._registry.get_registration(interface, name)

            # Handle singleton lifetime
            if registration.lifetime == ServiceLifetime.SINGLETON:
                singleton_key = self._get_singleton_key(interface, name)
                if singleton_key not in self._singletons:
                    self._singletons[singleton_key] = registration.create_instance(self)
                return self._singletons[singleton_key]

            # Handle transient and scoped lifetimes
            elif registration.lifetime in (
                ServiceLifetime.TRANSIENT,
                ServiceLifetime.SCOPED,
            ):
                return registration.create_instance(self)

            else:
                raise ServiceLifetimeException(
                    f"Unsupported lifetime: {registration.lifetime}"
                )

        finally:
            self._resolution_stack.pop()

    def is_registered(self, interface: type[T], name: str | None = None) -> bool:
        """Check if a service is registered"""
        try:
            self._registry.get_registration(interface, name)
            return True
        except ServiceNotRegisteredException:
            return False

    def create_scope(self) -> IServiceScope:
        """Create a new service scope"""
        return ServiceScope(self)

    def _get_singleton_key(self, interface: type, name: str | None) -> str:
        """Generate unique key for singleton instances"""
        return f"{interface.__module__}.{interface.__qualname__}" + (
            f":{name}" if name else ""
        )


class ServiceScope(IServiceScope):
    """
    Service scope implementation for managing scoped service lifetimes.

    Scoped services are created once per scope and disposed when the scope ends.
    Useful for request-scoped services in web applications or operation-scoped services.
    """

    def __init__(self, container: ServiceContainer):
        self._container = container
        self._scoped_instances: dict[str, Any] = {}
        self._disposed = False
        self._lock = threading.RLock()

    def resolve(self, interface: type[T], name: str | None = None) -> T:
        """Resolve a service within this scope"""
        if self._disposed:
            raise ServiceLifetimeException(
                "Cannot resolve services from a disposed scope"
            )

        with self._lock:
            registration = self._container._registry.get_registration(interface, name)

            if registration.lifetime == ServiceLifetime.SCOPED:
                scope_key = self._get_scope_key(interface, name)
                if scope_key not in self._scoped_instances:
                    self._scoped_instances[scope_key] = registration.create_instance(
                        self._container
                    )
                return self._scoped_instances[scope_key]
            else:
                # Delegate to container for non-scoped services
                return self._container.resolve(interface, name)

    def dispose(self) -> None:
        """Dispose of all scoped services"""
        if self._disposed:
            return

        with self._lock:
            # Dispose services that implement IDisposable
            for instance in self._scoped_instances.values():
                if hasattr(instance, "dispose"):
                    try:
                        instance.dispose()
                    except Exception:
                        # Log disposal errors but continue disposing other services
                        pass

            self._scoped_instances.clear()
            self._disposed = True

    def _get_scope_key(self, interface: type, name: str | None) -> str:
        """Generate unique key for scoped instances"""
        return f"{interface.__module__}.{interface.__qualname__}" + (
            f":{name}" if name else ""
        )

    def __enter__(self) -> "ServiceScope":
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit with automatic disposal"""
        self.dispose()


class ServiceRegistry(IServiceRegistry):
    """
    Service registry implementation for managing service registrations.

    Maintains a registry of all service registrations with support for
    named registrations and multiple implementations per interface.
    """

    def __init__(self):
        self._registrations: dict[str, ServiceRegistration] = {}
        self._lock = threading.RLock()

    def add_registration(self, registration: ServiceRegistration) -> None:
        """Add a service registration"""
        with self._lock:
            key = self._get_registration_key(registration.interface, registration.name)
            self._registrations[key] = registration

    def get_registration(
        self, interface: type[T], name: str | None = None
    ) -> ServiceRegistration:
        """Get a service registration"""
        with self._lock:
            key = self._get_registration_key(interface, name)
            if key not in self._registrations:
                raise ServiceNotRegisteredException(interface, name)
            return self._registrations[key]

    def get_all_registrations(self, interface: type[T]) -> list[ServiceRegistration]:
        """Get all registrations for an interface"""
        with self._lock:
            return [
                reg
                for reg in self._registrations.values()
                if reg.interface == interface
            ]

    def _get_registration_key(self, interface: type, name: str | None) -> str:
        """Generate unique key for registrations"""
        return f"{interface.__module__}.{interface.__qualname__}" + (
            f":{name}" if name else ""
        )


# Global container instance
_global_container: ServiceContainer | None = None
_container_lock = threading.RLock()


def get_container() -> ServiceContainer:
    """Get the global service container instance"""
    global _global_container

    if _global_container is None:
        with _container_lock:
            if _global_container is None:
                _global_container = ServiceContainer()

    return _global_container


def reset_container() -> None:
    """Reset the global container (primarily for testing)"""
    global _global_container

    with _container_lock:
        _global_container = None


@contextmanager
def service_scope():
    """Context manager for creating a service scope"""
    container = get_container()
    with container.create_scope() as scope:
        yield scope
