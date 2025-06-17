#!/usr/bin/env python3
"""
Comprehensive test suite for TaskMover Redesigned.
Tests core functionality including config management, file operations, and UI components.
"""

import sys
import os
import tempfile
import shutil
import unittest
from pathlib import Path

# Add the project root to the Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from taskmover_redesign.core import (
    ConfigManager, RuleManager, FileOrganizer,
    load_rules, save_rules, load_settings, save_settings
)


class TestConfigManager(unittest.TestCase):
    """Test the ConfigManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_config_directory_creation(self):
        """Test that config directory is created."""
        self.assertTrue(os.path.exists(self.test_dir))
    
    def test_default_rules_creation(self):
        """Test loading default rules when no rules file exists."""
        rules = self.config_manager.load_rules()
        self.assertIsInstance(rules, dict)
    
    def test_settings_loading(self):
        """Test loading default settings."""
        settings = self.config_manager.load_settings()
        self.assertIsInstance(settings, dict)
        self.assertIn("theme", settings)
        self.assertIn("organisation_folder", settings)
    
    def test_rules_save_and_load(self):
        """Test saving and loading rules."""
        test_rules = {
            "test_rule": {
                "name": "Test Rule",
                "pattern": "*.txt",
                "destination": "Documents/Text Files",
                "enabled": True,
                "priority": 1
            }
        }
        
        # Save rules
        success = self.config_manager.save_rules(test_rules)
        self.assertTrue(success)
        
        # Load rules
        loaded_rules = self.config_manager.load_rules()
        self.assertEqual(loaded_rules["test_rule"]["name"], "Test Rule")
    
    def test_settings_save_and_load(self):
        """Test saving and loading settings."""
        test_settings = {
            "theme": "darkly",
            "organisation_folder": "/test/folder",
            "developer_mode": True
        }
        
        # Save settings
        success = self.config_manager.save_settings(test_settings)
        self.assertTrue(success)
        
        # Load settings
        loaded_settings = self.config_manager.load_settings()
        self.assertEqual(loaded_settings["theme"], "darkly")
        self.assertEqual(loaded_settings["developer_mode"], True)


class TestRuleManager(unittest.TestCase):
    """Test the RuleManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.test_dir)
        self.rule_manager = RuleManager(self.config_manager)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_rule_creation(self):
        """Test rule creation."""
        success = self.rule_manager.add_rule(
            name="Test Rule",
            patterns=["*.txt"],
            path="Documents/Text Files",
            active=True
        )
        self.assertTrue(success)
        
        # Check that rule was added
        rules = self.rule_manager.rules
        self.assertIn("Test Rule", rules)
    
    def test_rule_sorting(self):
        """Test rule sorting by priority."""
        # Add multiple rules
        self.rule_manager.add_rule("Rule 1", ["*.txt"], "Documents")
        self.rule_manager.add_rule("Rule 2", ["*.pdf"], "Documents")
        
        sorted_keys = self.rule_manager.get_sorted_rule_keys()
        self.assertIsInstance(sorted_keys, list)


class TestFileOrganizer(unittest.TestCase):
    """Test the FileOrganizer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_source = tempfile.mkdtemp()
        self.test_dest = tempfile.mkdtemp()
        self.test_rules = {
            "txt_rule": {
                "name": "Text Files",
                "patterns": ["*.txt"],
                "path": "Documents/Text Files",
                "active": True,
                "priority": 1
            }
        }
        self.organizer = FileOrganizer(self.test_source, self.test_rules)
        
        # Create test files
        self.test_txt_file = os.path.join(self.test_source, "test.txt")
        self.test_pdf_file = os.path.join(self.test_source, "test.pdf")
        
        with open(self.test_txt_file, "w") as f:
            f.write("Test content")
        with open(self.test_pdf_file, "w") as f:
            f.write("PDF content")
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_source):
            shutil.rmtree(self.test_source)
        if os.path.exists(self.test_dest):
            shutil.rmtree(self.test_dest)
    
    def test_organizer_initialization(self):
        """Test FileOrganizer initialization."""
        self.assertEqual(str(self.organizer.organization_folder), self.test_source)
        self.assertEqual(self.organizer.rules, self.test_rules)
        self.assertFalse(self.organizer.is_running)
    
    def test_organization_start_stop(self):
        """Test starting and stopping organization."""
        # Test start
        success = self.organizer.start_organization()
        self.assertTrue(success)
        self.assertTrue(self.organizer.is_running)
        
        # Test stop
        self.organizer.stop_organization()
        self.assertTrue(self.organizer.should_stop)


class TestUtilities(unittest.TestCase):
    """Test utility functions."""
    
    def test_imports(self):
        """Test that all required modules can be imported."""
        try:
            from taskmover_redesign.core.utils import center_window, get_safe_filename
            from taskmover_redesign.ui.components import Tooltip, ProgressDialog, ConfirmDialog
            from taskmover_redesign.app import TaskMoverApp
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_safe_filename_generation(self):
        """Test safe filename generation."""
        from taskmover_redesign.core.utils import get_safe_filename
        
        # Test normal filename
        self.assertEqual(get_safe_filename("normal.txt"), "normal.txt")
        
        # Test filename with invalid characters
        unsafe_name = "file<>:name|?.txt"
        safe_name = get_safe_filename(unsafe_name)
        self.assertNotIn("<", safe_name)
        self.assertNotIn(">", safe_name)
        self.assertNotIn(":", safe_name)
        self.assertNotIn("|", safe_name)
        self.assertNotIn("?", safe_name)


def run_tests():
    """Run all tests and display results."""
    print("🧪 Running TaskMover Redesigned Test Suite...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManager))
    suite.addTests(loader.loadTestsFromTestCase(TestRuleManager))
    suite.addTests(loader.loadTestsFromTestCase(TestFileOrganizer))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilities))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Display summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
