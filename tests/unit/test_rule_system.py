"""
Test cases for Rule System
==========================

Tests for rule models, validation, and execution.
"""

import unittest
import sys
from pathlib import Path
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import real classes - rule system is now implemented
from taskmover.core.rules.models import (
    Rule, RuleStatus, ErrorHandlingBehavior, RuleExecutionResult, RuleValidationResult
)
from taskmover.core.rules.service import RuleService
from taskmover.core.rules.exceptions import RuleValidationError, RuleSystemError
RULES_AVAILABLE = True


class TestRuleModel(unittest.TestCase):
    """Test Rule model."""
    
    def test_rule_creation(self):
        """Test creating a rule."""
        pattern_id = uuid4()
        destination = Path("/test/destination")
        
        rule = Rule(
            name="Test Rule",
            description="A test rule",
            pattern_id=pattern_id,
            destination_path=destination,
            priority=5
        )
        
        self.assertIsInstance(rule.id, UUID)
        self.assertEqual(rule.name, "Test Rule")
        self.assertEqual(rule.description, "A test rule")
        self.assertEqual(rule.pattern_id, pattern_id)
        self.assertEqual(rule.destination_path, destination)
        self.assertEqual(rule.priority, 5)
        self.assertTrue(rule.is_enabled)
        # Rule model doesn't have a status field by default
    
    def test_rule_default_values(self):
        """Test rule creation with default values."""
        rule = Rule()
        
        self.assertIsInstance(rule.id, UUID)
        self.assertEqual(rule.name, "")
        self.assertEqual(rule.description, "")
        self.assertIsInstance(rule.pattern_id, UUID)
        self.assertIsInstance(rule.destination_path, Path)
        self.assertTrue(rule.is_enabled)
        self.assertEqual(rule.priority, 0)  # Default priority is 0
    
    def test_rule_timestamps(self):
        """Test rule timestamp fields."""
        rule = Rule(name="Timestamp Test")
        
        self.assertIsInstance(rule.created_date, datetime)
        self.assertIsInstance(rule.modified_date, datetime)
        # Timestamps should be close to current time
        time_diff = datetime.utcnow() - rule.created_date
        self.assertLess(time_diff.total_seconds(), 1.0)


class TestRuleStatus(unittest.TestCase):
    """Test RuleStatus enum."""
    
    def test_rule_status_values(self):
        """Test RuleStatus enum values."""
        self.assertEqual(RuleStatus.READY.value, "ready")
        self.assertEqual(RuleStatus.RUNNING.value, "running")
        self.assertEqual(RuleStatus.COMPLETED.value, "completed")
        self.assertEqual(RuleStatus.FAILED.value, "failed")
        self.assertEqual(RuleStatus.CANCELLED.value, "cancelled")
    
    def test_rule_status_comparison(self):
        """Test RuleStatus comparison."""
        self.assertEqual(RuleStatus.READY, RuleStatus.READY)
        self.assertNotEqual(RuleStatus.READY, RuleStatus.RUNNING)


class TestErrorHandlingBehavior(unittest.TestCase):
    """Test ErrorHandlingBehavior enum."""
    
    def test_error_handling_values(self):
        """Test ErrorHandlingBehavior enum values."""
        self.assertEqual(ErrorHandlingBehavior.STOP_ON_FIRST_ERROR.value, "stop_on_first_error")
        self.assertEqual(ErrorHandlingBehavior.CONTINUE_ON_RECOVERABLE.value, "continue_on_recoverable")
        self.assertEqual(ErrorHandlingBehavior.CONTINUE_ON_ALL.value, "continue_on_all")


class TestRuleValidationResult(unittest.TestCase):
    """Test RuleValidationResult model."""
    
    def test_validation_result_valid(self):
        """Test valid validation result."""
        rule_id = uuid4()
        result = RuleValidationResult(rule_id, is_valid=True)
        
        self.assertEqual(result.rule_id, rule_id)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])
    
    def test_validation_result_invalid(self):
        """Test invalid validation result."""
        rule_id = uuid4()
        errors = ["Invalid pattern", "Missing destination"]
        result = RuleValidationResult(rule_id, is_valid=False, errors=errors)
        
        self.assertEqual(result.rule_id, rule_id)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors, errors)


class TestExecutionResult(unittest.TestCase):
    """Test ExecutionResult model."""
    
    def test_execution_result_creation(self):
        """Test creating execution result."""
        rule_id = uuid4()
        result = ExecutionResult(
            rule_id=rule_id,
            status=RuleStatus.COMPLETED,
            files_processed=5
        )
        
        self.assertEqual(result.rule_id, rule_id)
        self.assertEqual(result.status, RuleStatus.COMPLETED)
        self.assertEqual(result.files_processed, 5)
        self.assertEqual(result.errors, [])
        self.assertIsInstance(result.execution_time, datetime)


class TestRuleService(unittest.TestCase):
    """Test RuleService functionality."""
    
    def setUp(self):
        """Set up test rule service."""
        self.rule_service = RuleService()
    
    def test_rule_service_creation(self):
        """Test RuleService creation."""
        service = RuleService()
        self.assertIsInstance(service, RuleService)
    
    def test_create_rule(self):
        """Test creating a rule through service."""
        rule = Rule(name="Test Rule", description="Test")
        created_rule = self.rule_service.create_rule(rule)
        
        self.assertEqual(created_rule.id, rule.id)
        self.assertEqual(created_rule.name, rule.name)
    
    def test_get_rule(self):
        """Test retrieving a rule by ID."""
        rule = Rule(name="Get Test", description="Test get")
        self.rule_service.create_rule(rule)
        
        retrieved_rule = self.rule_service.get_rule(rule.id)
        
        self.assertIsNotNone(retrieved_rule)
        self.assertEqual(retrieved_rule.id, rule.id)
        self.assertEqual(retrieved_rule.name, rule.name)
    
    def test_get_nonexistent_rule(self):
        """Test retrieving non-existent rule."""
        fake_id = uuid4()
        result = self.rule_service.get_rule(fake_id)
        self.assertIsNone(result)
    
    def test_list_rules(self):
        """Test listing all rules."""
        rule1 = Rule(name="Rule 1")
        rule2 = Rule(name="Rule 2")
        
        self.rule_service.create_rule(rule1)
        self.rule_service.create_rule(rule2)
        
        rules = self.rule_service.list_rules()
        
        self.assertEqual(len(rules), 2)
        rule_names = [r.name for r in rules]
        self.assertIn("Rule 1", rule_names)
        self.assertIn("Rule 2", rule_names)
    
    def test_validate_rule(self):
        """Test rule validation."""
        rule = Rule(name="Valid Rule", pattern_id=uuid4())
        
        validation_result = self.rule_service.validate_rule(rule)
        
        self.assertIsInstance(validation_result, RuleValidationResult)
        self.assertEqual(validation_result.rule_id, rule.id)
    
    def test_execute_rule(self):
        """Test rule execution."""
        rule = Rule(name="Execute Test")
        self.rule_service.create_rule(rule)
        
        execution_result = self.rule_service.execute_rule(rule.id)
        
        self.assertIsNotNone(execution_result)
        self.assertIsInstance(execution_result, ExecutionResult)
        self.assertEqual(execution_result.rule_id, rule.id)
    
    def test_execute_nonexistent_rule(self):
        """Test executing non-existent rule."""
        fake_id = uuid4()
        result = self.rule_service.execute_rule(fake_id)
        self.assertIsNone(result)


class TestRuleServiceIntegration(unittest.TestCase):
    """Test RuleService integration scenarios."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.rule_service = RuleService()
    
    def test_rule_lifecycle(self):
        """Test complete rule lifecycle."""
        # Create rule
        rule = Rule(
            name="Lifecycle Test",
            description="Test complete lifecycle",
            pattern_id=uuid4(),
            destination_path=Path("/test/dest"),
            priority=5
        )
        
        # Add rule to service
        created_rule = self.rule_service.create_rule(rule)
        self.assertIsNotNone(created_rule)
        
        # Validate rule
        validation_result = self.rule_service.validate_rule(rule)
        self.assertTrue(validation_result.is_valid)
        
        # Execute rule
        execution_result = self.rule_service.execute_rule(rule.id)
        self.assertIsNotNone(execution_result)
        
        # Verify rule still exists
        retrieved_rule = self.rule_service.get_rule(rule.id)
        self.assertEqual(retrieved_rule.name, "Lifecycle Test")
    
    def test_multiple_rules_same_pattern(self):
        """Test multiple rules using same pattern."""
        pattern_id = uuid4()
        
        rules = [
            Rule(name="Rule 1", pattern_id=pattern_id, destination_path=Path("/dest1")),
            Rule(name="Rule 2", pattern_id=pattern_id, destination_path=Path("/dest2")),
            Rule(name="Rule 3", pattern_id=pattern_id, destination_path=Path("/dest3"))
        ]
        
        # Add all rules
        for rule in rules:
            self.rule_service.create_rule(rule)
        
        # Verify all rules added
        all_rules = self.rule_service.list_rules()
        self.assertEqual(len(all_rules), 3)
        
        # All should have same pattern_id
        for rule in all_rules:
            self.assertEqual(rule.pattern_id, pattern_id)
    
    def test_rule_priority_ordering(self):
        """Test rules can be ordered by priority."""
        rules = [
            Rule(name="Low Priority", priority=1),
            Rule(name="High Priority", priority=10),
            Rule(name="Medium Priority", priority=5)
        ]
        
        # Add rules
        for rule in rules:
            self.rule_service.create_rule(rule)
        
        # Get all rules
        all_rules = self.rule_service.list_rules()
        
        # Sort by priority (higher first)
        sorted_rules = sorted(all_rules, key=lambda r: r.priority, reverse=True)
        
        self.assertEqual(sorted_rules[0].name, "High Priority")
        self.assertEqual(sorted_rules[1].name, "Medium Priority")
        self.assertEqual(sorted_rules[2].name, "Low Priority")


class TestRuleErrors(unittest.TestCase):
    """Test rule error handling."""
    
    def test_rule_error_hierarchy(self):
        """Test rule error class hierarchy."""
        # Test that error classes exist and inherit correctly
        self.assertTrue(issubclass(RuleValidationError, RuleError))
        self.assertTrue(issubclass(RuleError, Exception))
    
    def test_rule_validation_error(self):
        """Test RuleValidationError."""
        try:
            raise RuleValidationError("Validation failed")
        except RuleValidationError as e:
            self.assertIn("Validation failed", str(e))
        except Exception:
            self.fail("RuleValidationError should be catchable as RuleValidationError")
    
    def test_rule_error_with_context(self):
        """Test rule errors with additional context."""
        rule_id = uuid4()
        error_msg = f"Rule {rule_id} validation failed: invalid pattern"
        
        try:
            raise RuleError(error_msg)
        except RuleError as e:
            self.assertIn(str(rule_id), str(e))
            self.assertIn("validation failed", str(e))


class TestRuleServiceMocking(unittest.TestCase):
    """Test RuleService with mocked dependencies."""
    
    @patch('taskmover.core.rules.storage.RuleRepository')
    def test_rule_service_with_mock_repository(self, mock_repo_class):
        """Test RuleService with mocked repository."""
        # Setup mock repository
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        # This test depends on actual implementation
        # For now, just test that our mock service works
        service = RuleService()
        self.assertIsInstance(service, RuleService)
    
    def test_rule_service_with_mock_pattern_service(self):
        """Test RuleService with mocked pattern service."""
        # Mock pattern service
        mock_pattern_service = Mock()
        mock_pattern_service.get_pattern.return_value = Mock(id=uuid4(), name="Mock Pattern")
        
        # Create rule service (this might be enhanced in real implementation)
        service = RuleService()
        
        # Test with mock pattern
        rule = Rule(name="Test", pattern_id=uuid4())
        created_rule = service.create_rule(rule)
        
        self.assertEqual(created_rule.name, "Test")


if __name__ == '__main__':
    unittest.main()
