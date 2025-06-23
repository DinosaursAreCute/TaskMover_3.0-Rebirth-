"""
Dependency Injection Decorators

Provides decorators for easy service registration and dependency injection.
"""

from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from .container import get_container
from .interfaces import ServiceLifetime

T = TypeVar("T")


def injectable(
    interface: type | None = None,
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
    name: str | None = None,
):
    """
    Decorator to mark a class as injectable and automatically register it.

    Args:
        interface: The interface this class implements (defaults to the class itself)
        lifetime: Service lifetime (singleton, transient, scoped)
        name: Optional name for named registrations

    Example:
        @injectable(ILogger, ServiceLifetime.SINGLETON)
        class FileLogger(ILogger):
            def __init__(self, config: IConfig):
                self.config = config
    """

    def decorator(cls: type[T]) -> type[T]:
        container = get_container()
        service_interface = interface or cls

        container.register(
            interface=service_interface,
            implementation=cls,
            lifetime=lifetime,
            name=name,
        )

        return cls

    return decorator


def singleton(interface: type | None = None, name: str | None = None):
    """
    Decorator to register a class as a singleton service.

    Args:
        interface: The interface this class implements
        name: Optional name for named registrations
    """
    return injectable(interface, ServiceLifetime.SINGLETON, name)


def transient(interface: type | None = None, name: str | None = None):
    """
    Decorator to register a class as a transient service.

    Args:
        interface: The interface this class implements
        name: Optional name for named registrations
    """
    return injectable(interface, ServiceLifetime.TRANSIENT, name)


def scoped(interface: type | None = None, name: str | None = None):
    """
    Decorator to register a class as a scoped service.

    Args:
        interface: The interface this class implements
        name: Optional name for named registrations
    """
    return injectable(interface, ServiceLifetime.SCOPED, name)


def inject(interface: type[T], name: str | None = None):
    """
    Decorator to inject a dependency into a function or method.

    Args:
        interface: The interface type to inject
        name: Optional name for named registrations

    Example:
        @inject(ILogger)
        def process_file(file_path: str, logger: ILogger):
            logger.info(f"Processing {file_path}")
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            container = get_container()
            dependency = container.resolve(interface, name)

            # Add dependency to kwargs if not already provided
            import inspect

            sig = inspect.signature(func)
            list(sig.parameters.keys())

            # Find the parameter that should receive the dependency
            for param_name, param in sig.parameters.items():
                if param.annotation == interface:
                    if param_name not in kwargs:
                        kwargs[param_name] = dependency
                    break

            return func(*args, **kwargs)

        return wrapper

    return decorator


def factory(
    interface: type[T],
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
    name: str | None = None,
):
    """
    Decorator to register a function as a service factory.

    Args:
        interface: The interface this factory creates
        lifetime: Service lifetime
        name: Optional name for named registrations

    Example:
        @factory(IDatabase, ServiceLifetime.SINGLETON)
        def create_database() -> IDatabase:
            return DatabaseConnection(connection_string)
    """

    def decorator(func: Callable[[], T]) -> Callable[[], T]:
        container = get_container()

        container.register(
            interface=interface, factory=func, lifetime=lifetime, name=name
        )

        return func

    return decorator
