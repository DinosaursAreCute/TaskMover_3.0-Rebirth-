"""
Dependency Injection Interfaces

Defines the core abstractions for the TaskMover dependency injection system.
This lightweight container provides constructor injection with service lifecycle management.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any, TypeVar

T = TypeVar("T")


class ServiceLifetime(Enum):
    """Service lifetime enumeration"""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class IServiceContainer(ABC):
    """Main service container interface for dependency injection"""

    @abstractmethod
    def register(
        self,
        interface: type[T],
        implementation: type[T] | None = None,
        factory: Callable[[], T] | None = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        name: str | None = None,
    ) -> None:
        """
        Register a service with the container.

        Args:
            interface: The interface/abstract class type
            implementation: Concrete implementation class (optional if factory provided)
            factory: Factory function to create instances (optional)
            lifetime: Service lifetime (singleton, transient, scoped)
            name: Optional named registration for multiple implementations
        """
        pass

    @abstractmethod
    def resolve(self, interface: type[T], name: str | None = None) -> T:
        """
        Resolve a service instance from the container.

        Args:
            interface: The interface type to resolve
            name: Optional name for named registrations

        Returns:
            Instance of the requested service

        Raises:
            ServiceNotRegisteredException: If service is not registered
            CircularDependencyException: If circular dependency detected
        """
        pass

    @abstractmethod
    def is_registered(self, interface: type[T], name: str | None = None) -> bool:
        """Check if a service is registered"""
        pass

    @abstractmethod
    def create_scope(self) -> "IServiceScope":
        """Create a new service scope for scoped services"""
        pass


class IServiceScope(ABC):
    """Service scope interface for managing scoped service lifetimes"""

    @abstractmethod
    def resolve(self, interface: type[T], name: str | None = None) -> T:
        """Resolve a service within this scope"""
        pass

    @abstractmethod
    def dispose(self) -> None:
        """Dispose of all scoped services"""
        pass

    @abstractmethod
    def __enter__(self) -> "IServiceScope":
        """Context manager entry"""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit with automatic disposal"""
        pass


class IServiceRegistry(ABC):
    """Service registry interface for managing service registrations"""

    @abstractmethod
    def add_registration(self, registration: "ServiceRegistration") -> None:
        """Add a service registration"""
        pass

    @abstractmethod
    def get_registration(
        self, interface: type[T], name: str | None = None
    ) -> "ServiceRegistration":
        """Get a service registration"""
        pass

    @abstractmethod
    def get_all_registrations(self, interface: type[T]) -> list["ServiceRegistration"]:
        """Get all registrations for an interface"""
        pass


class ServiceRegistration:
    """Represents a service registration in the container"""

    def __init__(
        self,
        interface: type,
        implementation: type | None = None,
        factory: Callable[[], Any] | None = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        name: str | None = None,
    ):
        if implementation is None and factory is None:
            raise ValueError("Either implementation or factory must be provided")

        self.interface = interface
        self.implementation = implementation
        self.factory = factory
        self.lifetime = lifetime
        self.name = name

    def create_instance(self, container: IServiceContainer) -> Any:
        """Create an instance using this registration"""
        if self.factory:
            return self.factory()
        elif self.implementation:
            return self._create_with_injection(container)
        else:
            raise ValueError("No implementation or factory available")

    def _create_with_injection(self, container: IServiceContainer) -> Any:
        """Create instance with constructor dependency injection"""
        import inspect

        # Check if we have an implementation to work with
        if not self.implementation:
            raise ValueError("No implementation available for injection")

        # Get constructor signature
        sig = inspect.signature(self.implementation)
        kwargs = {}

        # Resolve dependencies for constructor parameters
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            if param.annotation != inspect.Parameter.empty:
                # Try to resolve dependency
                try:
                    kwargs[param_name] = container.resolve(param.annotation)
                except ServiceNotRegisteredException:
                    if param.default == inspect.Parameter.empty:
                        raise
                    # Use default value if dependency not found

        return self.implementation(**kwargs)


# Exception classes
class DIException(Exception):
    """Base exception for dependency injection errors"""

    pass


class ServiceNotRegisteredException(DIException):
    """Raised when attempting to resolve an unregistered service"""

    def __init__(self, interface: type, name: str | None = None):
        self.interface = interface
        self.name = name
        super().__init__(
            f"Service not registered: {interface.__name__}"
            + (f" (name: {name})" if name else "")
        )


class CircularDependencyException(DIException):
    """Raised when a circular dependency is detected"""

    def __init__(self, dependency_chain: list[type]):
        self.dependency_chain = dependency_chain
        chain_str = " -> ".join(t.__name__ for t in dependency_chain)
        super().__init__(f"Circular dependency detected: {chain_str}")


class ServiceLifetimeException(DIException):
    """Raised when there's an issue with service lifetime management"""

    pass
