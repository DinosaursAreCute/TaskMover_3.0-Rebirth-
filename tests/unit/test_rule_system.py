"""
Test cases for Rule System
==========================

Tests for rule models, validation, and exclass TestRulclass TestErrorHandlingBehaviorEnum(unittest.TestCase):tatusEnum(unittest.TestCase):ution.
"""

import unittest
import sys
from pathlib import Path
from uuid import UUID, uuid4
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import real classes - rule system is now implemented  
from taskmover.core.rules import (
    Rule, RuleStatus, ErrorHandlingBehavior, RuleValidationResult, RuleService
)
from taskmover.core.rules.exceptions import RuleValidationError


class TestRuleModel(unittest.TestCase):
    """Test Rule model."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pattern_id = uuid4()
        self.destination = self.temp_dir / "destination"
        self.destination.mkdir()
    
    def tearDown(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_rule_creation(self):
        """Test creating a rule with all parameters."""
        rule = Rule(
            name="Test Rule",
            description="A test rule",
            pattern_id=self.pattern_id,
            destination_path=self.destination,
            priority=5
        )
        
        self.assertIsInstance(rule.id, UUID)
        self.assertEqual(rule.name, "Test Rule")
        self.assertEqual(rule.description, "A test rule")
        self.assertEqual(rule.pattern_id, self.pattern_id)
        self.assertEqual(rule.destination_path, self.destination)
        self.assertEqual(rule.priority, 5)
        self.assertTrue(rule.is_enabled)
    
    def test_rule_default_values(self):
        """Test rule creation with minimal parameters."""
        rule = Rule(
            pattern_id=self.pattern_id,
            destination_path=self.destination
        )
        
        self.assertIsInstance(rule.id, UUID)
        self.assertTrue(rule.name.startswith("Rule"))  # Auto-generated name
        self.assertEqual(rule.description, "")
        self.assertEqual(rule.pattern_id, self.pattern_id)
        self.assertEqual(rule.destination_path, self.destination)
        self.assertTrue(rule.is_enabled)
        self.assertEqual(rule.priority, 0)
    
    def test_rule_validation(self):
        """Test rule validation."""
        rule = Rule(
            name="Valid Rule",
            pattern_id=self.pattern_id,
            destination_path=self.destination
        )
        
        errors = rule.validate()
        self.assertEqual(len(errors), 0)
    
    def test_rule_validation_invalid_destination(self):
        """Test rule validation with invalid destination."""
        invalid_dest = self.temp_dir / "nonexistent"
        rule = Rule(
            name="Invalid Rule",
            pattern_id=self.pattern_id,
            destination_path=invalid_dest
        )
        
        errors = rule.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("does not exist" in error for error in errors))


class TestRuleStatus(unittest.TestCase):
    """Test RuleStatus enum."""
    
    def test_rule_status_values(self):
        """Test RuleStatus enum values."""
        self.assertEqual(RuleStatus.READY.value, "ready")
        self.assertEqual(RuleStatus.RUNNING.value, "running")
        self.assertEqual(RuleStatus.COMPLETED.value, "completed")
        self.assertEqual(RuleStatus.FAILED.value, "failed")
        self.assertEqual(RuleStatus.CANCELLED.value, "cancelled")


class TestErrorHandlingBehavior(unittest.TestCase):
    """Test ErrorHandlingBehavior enum."""
    
    def test_error_handling_values(self):
        """Test ErrorHandlingBehavior enum values."""
        self.assertEqual(ErrorHandlingBehavior.STOP_ON_FIRST_ERROR.value, "stop_on_first_error")
        self.assertEqual(ErrorHandlingBehavior.CONTINUE_ON_RECOVERABLE.value, "continue_on_recoverable")
        self.assertEqual(ErrorHandlingBehavior.CONTINUE_ON_ALL.value, "continue_on_all")


class TestRuleService(unittest.TestCase):
    """Test RuleService functionality."""
    
    def setUp(self):
        """Set up test rule service."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Mock the dependencies that RuleService requires
        self.mock_pattern_system = Mock()
        self.mock_conflict_manager = Mock()
        self.storage_path = self.temp_dir / "storage"
        self.storage_path.mkdir()
        
        # Create RuleService with mocked dependencies
        with patch('taskmover.core.rules.service.PatternSystem'), \
             patch('taskmover.core.rules.service.ConflictManager'):
            self.rule_service = RuleService(
                pattern_system=self.mock_pattern_system,
                conflict_manager=self.mock_conflict_manager,
                storage_path=self.storage_path
            )
    
    def tearDown(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_rule_service_creation(self):
        """Test RuleService creation."""
        self.assertIsInstance(self.rule_service, RuleService)
    
    def test_create_rule(self):
        """Test creating a rule through service."""
        destination = self.temp_dir / "dest"
        destination.mkdir()
        
        pattern_id = uuid4()
        
        created_rule = self.rule_service.create_rule(
            name="Test Rule",
            description="Test",
            pattern_id=pattern_id,
            destination_path=destination
        )
        self.assertEqual(created_rule.name, "Test Rule")
        self.assertEqual(created_rule.description, "Test")
    
    def test_get_rule(self):
        """Test retrieving a rule by ID."""
        destination = self.temp_dir / "dest"
        destination.mkdir()
        
        pattern_id = uuid4()
        created_rule = self.rule_service.create_rule(
            name="Get Test",
            description="Test get",
            pattern_id=pattern_id,
            destination_path=destination
        )
        
        retrieved_rule = self.rule_service.get_rule(created_rule.id)
        
        self.assertIsNotNone(retrieved_rule)
        self.assertEqual(retrieved_rule.id, created_rule.id)
        self.assertEqual(retrieved_rule.name, created_rule.name)
    
    def test_get_nonexistent_rule(self):
        """Test retrieving non-existent rule."""
        fake_id = uuid4()
        result = self.rule_service.get_rule(fake_id)
        self.assertIsNone(result)
    
    def test_list_rules(self):
        """Test listing all rules."""
        destination1 = self.temp_dir / "dest1"
        destination2 = self.temp_dir / "dest2"
        destination1.mkdir()
        destination2.mkdir()
        
        rule1 = self.rule_service.create_rule(
            name="Rule 1", 
            pattern_id=uuid4(), 
            destination_path=destination1
        )
        rule2 = self.rule_service.create_rule(
            name="Rule 2", 
            pattern_id=uuid4(), 
            destination_path=destination2
        )
        
        rules = self.rule_service.list_rules()
        
        self.assertEqual(len(rules), 2)
        rule_names = [r.name for r in rules]
        self.assertIn("Rule 1", rule_names)
        self.assertIn("Rule 2", rule_names)


if __name__ == '__main__':
    unittest.main()
