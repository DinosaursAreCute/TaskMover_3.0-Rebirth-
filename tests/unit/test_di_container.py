"""
Unit tests for the Dependency Injection container
"""

import threading
from abc import ABC, abstractmethod

import pytest

from taskmover.core.di import (
    CircularDependencyException,
    ServiceContainer,
    ServiceLifetime,
    ServiceNotRegisteredException,
    get_container,
    injectable,
    reset_container,
    service_scope,
    singleton,
    transient,
)


# Test interfaces and implementations
class ITestService(ABC):
    @abstractmethod
    def get_value(self) -> str:
        pass


class ITestRepository(ABC):
    @abstractmethod
    def get_data(self) -> str:
        pass


class TestRepository(ITestRepository):
    def get_data(self) -> str:
        return "repository_data"


class TestService(ITestService):
    def __init__(self, repository: ITestRepository):
        self.repository = repository

    def get_value(self) -> str:
        return f"service_{self.repository.get_data()}"


class TestServiceWithoutDependencies(ITestService):
    def get_value(self) -> str:
        return "simple_service"


@pytest.fixture
def container():
    """Fresh container for each test"""
    reset_container()
    return ServiceContainer()


class TestServiceContainer:
    """Test the core service container functionality"""

    def test_register_and_resolve_transient(self, container):
        """Test basic service registration and resolution"""
        # Register services
        container.register(ITestRepository, TestRepository)
        container.register(ITestService, TestService)

        # Resolve service
        service = container.resolve(ITestService)

        assert isinstance(service, TestService)
        assert service.get_value() == "service_repository_data"

    def test_singleton_lifetime(self, container):
        """Test singleton services return the same instance"""
        container.register(
            ITestService,
            TestServiceWithoutDependencies,
            lifetime=ServiceLifetime.SINGLETON,
        )

        instance1 = container.resolve(ITestService)
        instance2 = container.resolve(ITestService)

        assert instance1 is instance2

    def test_transient_lifetime(self, container):
        """Test transient services return different instances"""
        container.register(
            ITestService,
            TestServiceWithoutDependencies,
            lifetime=ServiceLifetime.TRANSIENT,
        )

        instance1 = container.resolve(ITestService)
        instance2 = container.resolve(ITestService)

        assert instance1 is not instance2

    def test_factory_registration(self, container):
        """Test factory-based service registration"""

        def create_service() -> ITestService:
            return TestServiceWithoutDependencies()

        container.register(ITestService, factory=create_service)

        service = container.resolve(ITestService)
        assert isinstance(service, TestServiceWithoutDependencies)

    def test_named_registrations(self, container):
        """Test named service registrations"""
        container.register(ITestService, TestServiceWithoutDependencies, name="simple")

        # Default registration should fail
        with pytest.raises(ServiceNotRegisteredException):
            container.resolve(ITestService)

        # Named registration should work
        service = container.resolve(ITestService, name="simple")
        assert isinstance(service, TestServiceWithoutDependencies)

    def test_service_not_registered_exception(self, container):
        """Test exception when resolving unregistered service"""
        with pytest.raises(ServiceNotRegisteredException) as exc_info:
            container.resolve(ITestService)

        assert "ITestService" in str(exc_info.value)

    def test_circular_dependency_detection(self, container):
        """Test circular dependency detection"""

        class ServiceA:
            def __init__(self, service_b: "ServiceB"):
                self.service_b = service_b

        class ServiceB:
            def __init__(self, service_a: ServiceA):
                self.service_a = service_a

        container.register(ServiceA, ServiceA)
        container.register(ServiceB, ServiceB)

        with pytest.raises(CircularDependencyException):
            container.resolve(ServiceA)

    def test_is_registered(self, container):
        """Test service registration check"""
        assert not container.is_registered(ITestService)

        container.register(ITestService, TestServiceWithoutDependencies)

        assert container.is_registered(ITestService)
        assert not container.is_registered(ITestService, name="nonexistent")

    def test_thread_safety(self, container):
        """Test thread-safe service resolution"""
        container.register(
            ITestService,
            TestServiceWithoutDependencies,
            lifetime=ServiceLifetime.SINGLETON,
        )

        instances = []

        def resolve_service():
            instances.append(container.resolve(ITestService))

        # Create multiple threads
        threads = [threading.Thread(target=resolve_service) for _ in range(10)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # All instances should be the same (singleton)
        assert len({id(instance) for instance in instances}) == 1


class TestServiceScope:
    """Test service scope functionality"""

    def test_scoped_service_lifecycle(self, container):
        """Test scoped service lifecycle"""
        container.register(
            ITestService,
            TestServiceWithoutDependencies,
            lifetime=ServiceLifetime.SCOPED,
        )

        with container.create_scope() as scope1:
            service1a = scope1.resolve(ITestService)
            service1b = scope1.resolve(ITestService)

            # Same instance within scope
            assert service1a is service1b

        with container.create_scope() as scope2:
            service2 = scope2.resolve(ITestService)

            # Different instance in different scope
            assert service2 is not service1a

    def test_service_scope_context_manager(self, container):
        """Test service scope context manager"""
        container.register(
            ITestService,
            TestServiceWithoutDependencies,
            lifetime=ServiceLifetime.SCOPED,
        )

        with service_scope() as scope:
            service = scope.resolve(ITestService)
            assert isinstance(service, TestServiceWithoutDependencies)


class TestDecorators:
    """Test dependency injection decorators"""

    def test_injectable_decorator(self):
        """Test @injectable decorator"""
        reset_container()

        @injectable(ITestService, ServiceLifetime.SINGLETON)
        class DecoratedService(ITestService):
            def get_value(self) -> str:
                return "decorated"

        container = get_container()
        service = container.resolve(ITestService)

        assert isinstance(service, DecoratedService)
        assert service.get_value() == "decorated"

    def test_singleton_decorator(self):
        """Test @singleton decorator"""
        reset_container()

        @singleton(ITestService)
        class SingletonService(ITestService):
            def get_value(self) -> str:
                return "singleton"

        container = get_container()
        instance1 = container.resolve(ITestService)
        instance2 = container.resolve(ITestService)

        assert instance1 is instance2

    def test_transient_decorator(self):
        """Test @transient decorator"""
        reset_container()

        @transient(ITestService)
        class TransientService(ITestService):
            def get_value(self) -> str:
                return "transient"

        container = get_container()
        instance1 = container.resolve(ITestService)
        instance2 = container.resolve(ITestService)

        assert instance1 is not instance2


class TestGlobalContainer:
    """Test global container functionality"""

    def test_get_container_singleton(self):
        """Test global container is singleton"""
        reset_container()

        container1 = get_container()
        container2 = get_container()

        assert container1 is container2

    def test_reset_container(self):
        """Test container reset functionality"""
        reset_container()

        container1 = get_container()
        reset_container()
        container2 = get_container()

        assert container1 is not container2
