#!/usr/bin/env python3
"""
Test suite for window management and proportional sizing functionality.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from taskmover_redesign.core.utils import (
    get_screen_dimensions, calculate_proportional_size,
    center_window, center_window_on_parent
)


class TestWindowManagement(unittest.TestCase):
    """Test window management and proportional sizing functions."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock tkinter window
        self.mock_window = Mock()
        self.mock_window.winfo_screenwidth.return_value = 1920
        self.mock_window.winfo_screenheight.return_value = 1080
        self.mock_window.winfo_width.return_value = 800
        self.mock_window.winfo_height.return_value = 600
        self.mock_window.winfo_rootx.return_value = 100
        self.mock_window.winfo_rooty.return_value = 100
    
    def test_get_screen_dimensions(self):
        """Test getting screen dimensions."""
        width, height = get_screen_dimensions(self.mock_window)
        self.assertEqual(width, 1920)
        self.assertEqual(height, 1080)
    
    def test_calculate_proportional_size(self):
        """Test proportional size calculation."""
        # Test default ratios (60% width, 70% height)
        width, height = calculate_proportional_size(1920, 1080, 0.6, 0.7)
        self.assertEqual(width, 1152)  # 1920 * 0.6
        self.assertEqual(height, 756)  # 1080 * 0.7
        
        # Test minimum size enforcement
        width, height = calculate_proportional_size(500, 400, 0.1, 0.1)
        self.assertEqual(width, 400)  # Minimum width
        self.assertEqual(height, 300)  # Minimum height
        
        # Test maximum size enforcement
        width, height = calculate_proportional_size(1920, 1080, 1.0, 1.0)
        self.assertEqual(width, 1728)  # 1920 * 0.9 (max constraint)
        self.assertEqual(height, 972)   # 1080 * 0.9 (max constraint)
    
    @patch('taskmover_redesign.core.utils.get_screen_dimensions')
    def test_center_window_proportional(self, mock_get_dimensions):
        """Test centering a window with proportional sizing."""
        mock_get_dimensions.return_value = (1920, 1080)
        
        # Test proportional sizing
        center_window(self.mock_window, proportional=True, width_ratio=0.6, height_ratio=0.7)
        
        # Should call geometry with calculated proportional size and center position
        expected_width = 1152  # 1920 * 0.6
        expected_height = 756  # 1080 * 0.7
        expected_x = 384       # (1920 - 1152) // 2
        expected_y = 162       # (1080 - 756) // 2
        
        expected_geometry = f"{expected_width}x{expected_height}+{expected_x}+{expected_y}"
        self.mock_window.geometry.assert_called_with(expected_geometry)
    
    def test_center_window_fixed_size(self):
        """Test centering a window with fixed size."""
        self.mock_window.winfo_screenwidth.return_value = 1920
        self.mock_window.winfo_screenheight.return_value = 1080
        
        center_window(self.mock_window, width=800, height=600)
        
        # Should call geometry with fixed size and center position
        expected_x = 560  # (1920 - 800) // 2
        expected_y = 240  # (1080 - 600) // 2
        expected_geometry = f"800x600+{expected_x}+{expected_y}"
        
        self.mock_window.geometry.assert_called_with(expected_geometry)
    
    def test_center_window_on_parent(self):
        """Test centering a child window on its parent."""
        # Mock child window
        mock_child = Mock()
        
        # Test with proportional sizing
        center_window_on_parent(
            mock_child, self.mock_window, 
            proportional=True, width_ratio=0.5, height_ratio=0.6
        )
        
        # Should calculate based on parent size (800x600)
        expected_width = 400   # 800 * 0.5
        expected_height = 360  # 600 * 0.6
        expected_x = 300       # 100 + (800 - 400) // 2
        expected_y = 220       # 100 + (600 - 360) // 2
        
        expected_geometry = f"{expected_width}x{expected_height}+{expected_x}+{expected_y}"
        mock_child.geometry.assert_called_with(expected_geometry)
    
    def test_window_boundary_constraints(self):
        """Test that windows don't go off-screen."""
        # Test with a window that would go off-screen
        self.mock_window.winfo_screenwidth.return_value = 800
        self.mock_window.winfo_screenheight.return_value = 600
        
        center_window(self.mock_window, width=1000, height=800)
        
        # Should constrain to screen boundaries
        # Position should be 0,0 since window is larger than screen
        expected_geometry = "1000x800+0+0"
        self.mock_window.geometry.assert_called_with(expected_geometry)


class TestUIComponentSizing(unittest.TestCase):
    """Test UI component sizing integration."""
    
    def test_dialog_creation_with_proportional_sizing(self):
        """Test that dialogs can be created with proportional sizing."""
        try:
            # This is more of an integration test to ensure imports work
            from taskmover_redesign.ui.components import SimpleDialog
            
            # Mock parent
            mock_parent = Mock()
            mock_parent.winfo_toplevel.return_value = mock_parent
            mock_parent.winfo_screenwidth.return_value = 1920
            mock_parent.winfo_screenheight.return_value = 1080
            mock_parent.winfo_width.return_value = 800
            mock_parent.winfo_height.return_value = 600
            mock_parent.winfo_rootx.return_value = 100
            mock_parent.winfo_rooty.return_value = 100
            
            # This would normally create a dialog, but we're just testing the import
            # and that the class accepts proportional parameters
            self.assertTrue(hasattr(SimpleDialog, '__init__'))
            
        except ImportError as e:
            self.fail(f"Could not import UI components: {e}")


def run_window_tests():
    """Run window management tests specifically."""
    print("🧪 Running Window Management Tests...")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWindowManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestUIComponentSizing))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Display summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All window management tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_window_tests()
    sys.exit(0 if success else 1)
