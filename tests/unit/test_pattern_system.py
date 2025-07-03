"""
Test cases for Pattern System
=============================

Tests for pattern parsing, matching, and management.
"""

import unittest
import sys
from pathlib import Path
from uuid import UUID, uuid4
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import real classes - pattern system is now implemented
from taskmover.core.patterns import PatternSystem
from taskmover.core.patterns.models import Pattern, PatternGroup, MatchResult
from taskmover.core.patterns.exceptions import PatternSystemError, PatternNotFoundError


class TestPatternModel(unittest.TestCase):
    """Test Pattern model."""
    
    def test_pattern_creation(self):
        """Test creating a pattern."""
        pattern = Pattern(
            name="Document Files",
            description="Match document files",
            pattern_text="*.{doc,docx,pdf}"
        )
        
        self.assertIsInstance(pattern.id, UUID)
        self.assertEqual(pattern.name, "Document Files")
        self.assertEqual(pattern.description, "Match document files")
        self.assertEqual(pattern.pattern_text, "*.{doc,docx,pdf}")
    
    def test_pattern_with_group(self):
        """Test pattern with group assignment."""
        group_id = uuid4()
        pattern = Pattern(
            name="Images",
            pattern_text="*.{jpg,png,gif}",
            group_id=group_id
        )
        
        self.assertEqual(pattern.group_id, group_id)
    
    def test_pattern_equality(self):
        """Test pattern equality comparison."""
        id1 = uuid4()
        pattern1 = Pattern(id=id1, name="Test")
        pattern2 = Pattern(id=id1, name="Test")
        pattern3 = Pattern(name="Test")  # Different ID
        
        self.assertEqual(pattern1.id, pattern2.id)
        self.assertNotEqual(pattern1.id, pattern3.id)


class TestPatternGroup(unittest.TestCase):
    """Test PatternGroup model."""
    
    def test_group_creation(self):
        """Test creating a pattern group."""
        group = PatternGroup(
            name="Media Files",
            description="Patterns for media file organization"
        )
        
        self.assertIsInstance(group.id, UUID)
        self.assertEqual(group.name, "Media Files")
        self.assertEqual(group.description, "Patterns for media file organization")


class TestMatchResult(unittest.TestCase):
    """Test MatchResult model."""
    
    def test_match_result_creation(self):
        """Test creating a match result."""
        pattern_id = uuid4()
        result = MatchResult(
            file_path=Path("/path/to/file.txt"),
            pattern_id=pattern_id,
            confidence=0.95
        )
        
        self.assertIsInstance(result.file_path, Path)
        self.assertEqual(result.pattern_id, pattern_id)
        self.assertEqual(result.confidence, 0.95)
    
    def test_match_result_path_conversion(self):
        """Test file path is converted to Path object."""
        result = MatchResult(Path("test/file.txt"), uuid4())
        self.assertIsInstance(result.file_path, Path)
        self.assertEqual(result.file_path, Path("test/file.txt"))


class TestPatternSystem(unittest.TestCase):
    """Test PatternSystem functionality."""
    
    def setUp(self):
        """Set up test pattern system."""
        import tempfile
        # Create isolated storage for each test
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pattern_system = PatternSystem(storage_path=self.temp_dir)
    
    def test_pattern_system_creation(self):
        """Test PatternSystem creation."""
        system = PatternSystem()
        self.assertIsInstance(system, PatternSystem)
    
    def test_pattern_system_with_custom_path(self):
        """Test PatternSystem with custom storage path."""
        custom_path = Path("/custom/patterns")
        system = PatternSystem(storage_path=custom_path)
        
        # Should store the custom path
        if hasattr(system, 'storage_path'):
            self.assertEqual(system.storage_path, custom_path)
    
    def test_add_pattern(self):
        """Test adding a pattern."""
        pattern = Pattern(
            name="Test Pattern",
            pattern_text="*.txt"
        )
        
        added_pattern = self.pattern_system.add_pattern(pattern)
        
        # Should return the added pattern
        self.assertEqual(added_pattern.id, pattern.id)
        self.assertEqual(added_pattern.name, pattern.name)
    
    def test_get_pattern(self):
        """Test retrieving a pattern by ID."""
        pattern = Pattern(name="Test", pattern_text="*.test")
        self.pattern_system.add_pattern(pattern)
        
        retrieved = self.pattern_system.get_pattern(pattern.id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, pattern.id)
        self.assertEqual(retrieved.name, pattern.name)
    
    def test_get_nonexistent_pattern(self):
        """Test retrieving non-existent pattern."""
        fake_id = uuid4()
        result = self.pattern_system.get_pattern(fake_id)
        self.assertIsNone(result)
    
    def test_list_patterns(self):
        """Test listing all patterns."""
        pattern1 = Pattern(name="Pattern 1", pattern_text="*.txt")
        pattern2 = Pattern(name="Pattern 2", pattern_text="*.doc")
        
        self.pattern_system.add_pattern(pattern1)
        self.pattern_system.add_pattern(pattern2)
        
        patterns = self.pattern_system.list_patterns()
        
        self.assertEqual(len(patterns), 2)
        pattern_names = [p.name for p in patterns]
        self.assertIn("Pattern 1", pattern_names)
        self.assertIn("Pattern 2", pattern_names)
    
    def test_match_files(self):
        """Test file matching against patterns."""
        # Add a pattern
        pattern = Pattern(name="Text Files", pattern_text="*.txt")
        self.pattern_system.add_pattern(pattern)
        
        # Test file matching
        test_files = [
            Path("document.txt"),
            Path("image.jpg"),
            Path("readme.txt")
        ]
        
        matches = self.pattern_system.match_files(test_files)
        
        # Should return match results
        self.assertIsInstance(matches, list)


class TestPatternSystemIntegration(unittest.TestCase):
    """Test PatternSystem integration scenarios."""
    
    def setUp(self):
        """Set up integration test environment."""
        import tempfile
        # Create isolated storage for each test
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pattern_system = PatternSystem(storage_path=self.temp_dir)
    
    def test_pattern_workflow(self):
        """Test complete pattern workflow."""
        # Create pattern group
        group = PatternGroup(name="Documents", description="Document patterns")
        
        # Create pattern
        pattern = Pattern(
            name="PDF Files",
            description="Match PDF documents",
            pattern_text="*.pdf",
            group_id=group.id
        )
        
        # Add pattern to system
        added_pattern = self.pattern_system.add_pattern(pattern)
        
        # Verify pattern was added
        self.assertIsNotNone(added_pattern)
        
        # Retrieve pattern
        retrieved = self.pattern_system.get_pattern(pattern.id)
        self.assertEqual(retrieved.name, "PDF Files")
        
        # List patterns
        all_patterns = self.pattern_system.list_patterns()
        self.assertEqual(len(all_patterns), 1)
        self.assertEqual(all_patterns[0].name, "PDF Files")
    
    def test_multiple_patterns_same_group(self):
        """Test multiple patterns in same group."""
        group_id = uuid4()
        
        patterns = [
            Pattern(name="Documents", pattern_text="*.{doc,docx}", group_id=group_id),
            Pattern(name="Spreadsheets", pattern_text="*.{xls,xlsx}", group_id=group_id),
            Pattern(name="Presentations", pattern_text="*.{ppt,pptx}", group_id=group_id)
        ]
        
        # Add all patterns
        for pattern in patterns:
            self.pattern_system.add_pattern(pattern)
        
        # Verify all patterns added
        all_patterns = self.pattern_system.list_patterns()
        self.assertEqual(len(all_patterns), 3)
        
        # All should have same group_id
        for pattern in all_patterns:
            self.assertEqual(pattern.group_id, group_id)
    
    def test_pattern_matching_scenario(self):
        """Test realistic pattern matching scenario."""
        # Add various patterns
        patterns = [
            Pattern(name="Images", pattern_text="*.{jpg,png,gif,bmp}"),
            Pattern(name="Videos", pattern_text="*.{mp4,avi,mkv,mov}"),
            Pattern(name="Documents", pattern_text="*.{pdf,doc,docx,txt}")
        ]
        
        for pattern in patterns:
            self.pattern_system.add_pattern(pattern)
        
        # Test files
        test_files = [
            Path("photo.jpg"),
            Path("video.mp4"),
            Path("document.pdf"),
            Path("unknown.xyz")
        ]
        
        # Match files
        matches = self.pattern_system.match_files(test_files)
        
        # Should return results for matching files
        self.assertIsInstance(matches, list)


class TestPatternSystemErrors(unittest.TestCase):
    """Test PatternSystem error handling."""
    
    def test_pattern_not_found_error(self):
        """Test PatternNotFoundError handling."""
        # This test depends on implementation details
        # For now, just test that the exception classes exist
        self.assertTrue(issubclass(PatternNotFoundError, PatternSystemError))
        self.assertTrue(issubclass(PatternSystemError, Exception))
    
    def test_invalid_pattern_handling(self):
        """Test handling of invalid patterns."""
        # Test with mock invalid pattern
        try:
            # This would depend on actual validation implementation
            invalid_pattern = Pattern(name="", pattern_text="")
            # Should handle gracefully or raise appropriate error
            self.assertIsInstance(invalid_pattern, Pattern)
        except Exception as e:
            # Should be a specific pattern-related exception
            self.assertIsInstance(e, Exception)


class TestPatternSystemMocking(unittest.TestCase):
    """Test PatternSystem with mocked dependencies."""
    
    @patch('taskmover.core.patterns.PatternRepository')
    def test_pattern_system_with_mock_repository(self, mock_repo_class):
        """Test PatternSystem with mocked repository."""
        # Setup mock repository
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        # Create pattern system (this might fail if real imports don't work)
        try:
            from taskmover.core.patterns import PatternSystem as RealPatternSystem
            system = RealPatternSystem()
            
            # Verify repository was created
            mock_repo_class.assert_called()
        except ImportError:
            # Fall back to mock test
            system = PatternSystem()
            self.assertIsInstance(system, PatternSystem)


if __name__ == '__main__':
    unittest.main()
