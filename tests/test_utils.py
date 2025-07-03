"""
Test Utilities and Helpers
==========================

Utilities for testing TaskMover components.
"""

import unittest
import sys
from pathlib import Path
from uuid import uuid4
import tempfile
import shutil
from unittest.mock import Mock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestTestingUtilities(unittest.TestCase):
    """Test utility functions for testing."""
    
    def test_create_test_directory(self):
        """Test creating temporary test directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test_taskdir"
            test_dir.mkdir()
            
            self.assertTrue(test_dir.exists())
            self.assertTrue(test_dir.is_dir())
            
            # Create test files
            test_file = test_dir / "test.txt"
            test_file.write_text("test content")
            
            self.assertTrue(test_file.exists())
            self.assertEqual(test_file.read_text(), "test content")
    
    def test_create_mock_pattern(self):
        """Test creating mock pattern objects."""
        mock_pattern = Mock()
        mock_pattern.id = uuid4()
        mock_pattern.name = "Test Pattern"
        mock_pattern.pattern_text = "*.txt"
        
        self.assertIsNotNone(mock_pattern.id)
        self.assertEqual(mock_pattern.name, "Test Pattern")
        self.assertEqual(mock_pattern.pattern_text, "*.txt")
    
    def test_create_mock_rule(self):
        """Test creating mock rule objects."""
        mock_rule = Mock()
        mock_rule.id = uuid4()
        mock_rule.name = "Test Rule"
        mock_rule.pattern_id = uuid4()
        mock_rule.destination_path = Path("/test/dest")
        mock_rule.is_enabled = True
        mock_rule.priority = 10
        
        self.assertIsNotNone(mock_rule.id)
        self.assertEqual(mock_rule.name, "Test Rule")
        self.assertIsNotNone(mock_rule.pattern_id)
        self.assertTrue(mock_rule.is_enabled)


class TestFileSystemHelpers(unittest.TestCase):
    """Test file system helper utilities."""
    
    def test_create_test_file_structure(self):
        """Test creating test file structures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            
            # Create test structure
            test_files = [
                "document.pdf",
                "image.jpg",
                "video.mp4",
                "archive.zip",
                "subfolder/nested.txt"
            ]
            
            for file_path in test_files:
                full_path = base_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(f"Content of {file_path}")
            
            # Verify structure
            for file_path in test_files:
                full_path = base_path / file_path
                self.assertTrue(full_path.exists())
                self.assertEqual(full_path.read_text(), f"Content of {file_path}")
    
    def test_file_extension_matching(self):
        """Test file extension matching utilities."""
        test_cases = [
            ("document.pdf", ".pdf", True),
            ("image.JPG", ".jpg", True),  # Case insensitive
            ("archive.tar.gz", ".gz", True),
            ("noextension", ".txt", False),
            ("file.txt", ".pdf", False)
        ]
        
        for filename, extension, expected in test_cases:
            with self.subTest(filename=filename, extension=extension):
                result = Path(filename).suffix.lower() == extension.lower()
                self.assertEqual(result, expected)


class TestMockServices(unittest.TestCase):
    """Test mock service implementations."""
    
    def test_mock_pattern_service(self):
        """Test mock pattern service."""
        class MockPatternService:
            def __init__(self):
                self._patterns = {}
            
            def add_pattern(self, pattern):
                self._patterns[pattern.id] = pattern
                return pattern
            
            def get_pattern(self, pattern_id):
                return self._patterns.get(pattern_id)
            
            def list_patterns(self):
                return list(self._patterns.values())
        
        service = MockPatternService()
        
        # Test pattern
        pattern = Mock()
        pattern.id = uuid4()
        pattern.name = "Test"
        
        # Add pattern
        added = service.add_pattern(pattern)
        self.assertEqual(added.id, pattern.id)
        
        # Get pattern
        retrieved = service.get_pattern(pattern.id)
        self.assertEqual(retrieved.id, pattern.id)
        
        # List patterns
        patterns = service.list_patterns()
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0].id, pattern.id)
    
    def test_mock_rule_service(self):
        """Test mock rule service."""
        class MockRuleService:
            def __init__(self):
                self._rules = {}
            
            def create_rule(self, rule):
                self._rules[rule.id] = rule
                return rule
            
            def get_rule(self, rule_id):
                return self._rules.get(rule_id)
            
            def list_rules(self):
                return list(self._rules.values())
        
        service = MockRuleService()
        
        # Test rule
        rule = Mock()
        rule.id = uuid4()
        rule.name = "Test Rule"
        
        # Create rule
        created = service.create_rule(rule)
        self.assertEqual(created.id, rule.id)
        
        # Get rule
        retrieved = service.get_rule(rule.id)
        self.assertEqual(retrieved.id, rule.id)
        
        # List rules
        rules = service.list_rules()
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].id, rule.id)


class TestDataGeneration(unittest.TestCase):
    """Test data generation utilities."""
    
    def test_generate_test_patterns(self):
        """Test generating test pattern data."""
        test_patterns = [
            {"name": "Images", "pattern": "*.{jpg,png,gif,bmp}"},
            {"name": "Documents", "pattern": "*.{pdf,doc,docx,txt}"},
            {"name": "Videos", "pattern": "*.{mp4,avi,mkv,mov}"},
            {"name": "Archives", "pattern": "*.{zip,rar,7z,tar.gz}"}
        ]
        
        for pattern_data in test_patterns:
            self.assertIn("name", pattern_data)
            self.assertIn("pattern", pattern_data)
            self.assertTrue(len(pattern_data["name"]) > 0)
            self.assertTrue(len(pattern_data["pattern"]) > 0)
    
    def test_generate_test_rules(self):
        """Test generating test rule data."""
        test_rules = [
            {"name": "Organize Images", "pattern": "Images", "dest": "Pictures"},
            {"name": "Organize Documents", "pattern": "Documents", "dest": "Documents"},
            {"name": "Organize Videos", "pattern": "Videos", "dest": "Videos"},
            {"name": "Archive Downloads", "pattern": "Archives", "dest": "Archives"}
        ]
        
        for rule_data in test_rules:
            self.assertIn("name", rule_data)
            self.assertIn("pattern", rule_data)
            self.assertIn("dest", rule_data)


def create_test_environment():
    """Create a complete test environment."""
    # This would set up a test directory structure, mock services, etc.
    test_env = {
        'temp_dir': tempfile.mkdtemp(),
        'mock_pattern_service': Mock(),
        'mock_rule_service': Mock(),
        'test_files': []
    }
    
    return test_env


def cleanup_test_environment(test_env):
    """Clean up test environment."""
    if 'temp_dir' in test_env and Path(test_env['temp_dir']).exists():
        shutil.rmtree(test_env['temp_dir'])


if __name__ == '__main__':
    unittest.main()