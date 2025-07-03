"""
Test cases for TaskMover core exceptions
========================================

Tests for the exception hierarchy and error handling.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from taskmover.core.exceptions import (
    TaskMoverException,
    ConfigurationException,
    ServiceException,
    CircularDependencyException,
    StorageException,
    ValidationException
)


class TestTaskMoverExceptions(unittest.TestCase):
    """Test TaskMover exception hierarchy."""
    
    def test_base_exception_creation(self):
        """Test TaskMoverException creation."""
        msg = "Test error message"
        exc = TaskMoverException(msg)
        
        self.assertEqual(str(exc), msg)
        self.assertEqual(exc.message, msg)
        self.assertIsNone(exc.inner_exception)
    
    def test_exception_with_inner_exception(self):
        """Test exception with inner exception."""
        inner = ValueError("Inner error")
        msg = "Outer error"
        exc = TaskMoverException(msg, inner)
        
        self.assertEqual(exc.message, msg)
        self.assertEqual(exc.inner_exception, inner)
        self.assertIn("Inner: Inner error", str(exc))
    
    def test_configuration_exception(self):
        """Test ConfigurationException."""
        exc = ConfigurationException("Config error")
        self.assertIsInstance(exc, TaskMoverException)
        self.assertEqual(exc.message, "Config error")
    
    def test_service_exception(self):
        """Test ServiceException."""
        exc = ServiceException("Service error")
        self.assertIsInstance(exc, TaskMoverException)
        self.assertEqual(exc.message, "Service error")
    
    def test_circular_dependency_exception(self):
        """Test CircularDependencyException."""
        exc = CircularDependencyException("Circular dependency detected")
        self.assertIsInstance(exc, ServiceException)
        self.assertIsInstance(exc, TaskMoverException)
    
    def test_storage_exception(self):
        """Test StorageException."""
        exc = StorageException("Storage error")
        self.assertIsInstance(exc, TaskMoverException)
        self.assertEqual(exc.message, "Storage error")
    
    def test_validation_exception(self):
        """Test ValidationException."""
        exc = ValidationException("Validation failed")
        self.assertIsInstance(exc, TaskMoverException)
        self.assertEqual(exc.message, "Validation failed")
    
    def test_exception_inheritance_chain(self):
        """Test that all custom exceptions inherit from TaskMoverException."""
        exceptions = [
            ConfigurationException,
            ServiceException,
            CircularDependencyException,
            StorageException,
            ValidationException
        ]
        
        for exc_class in exceptions:
            with self.subTest(exception=exc_class.__name__):
                exc = exc_class("test")
                self.assertIsInstance(exc, TaskMoverException)
                self.assertIsInstance(exc, Exception)


class TestExceptionHandling(unittest.TestCase):
    """Test exception handling scenarios."""
    
    def test_exception_chaining(self):
        """Test exception chaining for debugging."""
        try:
            # Simulate nested error
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ConfigurationException("Config load failed", e)
        except ConfigurationException as exc:
            self.assertIsNotNone(exc.inner_exception)
            self.assertIsInstance(exc.inner_exception, ValueError)
            self.assertIn("Original error", str(exc))
    
    def test_exception_message_formatting(self):
        """Test exception message formatting."""
        # Simple message
        exc1 = TaskMoverException("Simple message")
        self.assertEqual(str(exc1), "Simple message")
        
        # Message with inner exception
        inner = RuntimeError("Runtime issue")
        exc2 = TaskMoverException("Outer message", inner)
        expected = "Outer message (Inner: Runtime issue)"
        self.assertEqual(str(exc2), expected)
    
    def test_exception_in_mock_scenario(self):
        """Test exceptions in realistic scenarios."""
        # Mock configuration loading failure
        def load_config():
            raise ConfigurationException("Configuration file not found")
        
        with self.assertRaises(ConfigurationException) as cm:
            load_config()
        
        self.assertIn("Configuration file not found", str(cm.exception))
        
        # Mock service resolution failure
        def resolve_service():
            raise ServiceException("Service not registered")
        
        with self.assertRaises(ServiceException) as cm:
            resolve_service()
        
        self.assertIn("Service not registered", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
