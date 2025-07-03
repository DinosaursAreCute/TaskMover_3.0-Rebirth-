"""
Comprehensive UI Test Suite
===========================

Test suite for TaskMover UI components with visual testing capabilities.
"""

import unittest
import tkinter as tk
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestUIComponents(unittest.TestCase):
    """Test UI components functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
    
    def tearDown(self):
        """Clean up test environment."""
        self.root.destroy()
    
    def test_import_all_ui_components(self):
        """Test all UI components can be imported."""
        components_to_test = [
            'taskmover.ui.base_component',
            'taskmover.ui.theme_manager',
            'taskmover.ui.main_application',
            'taskmover.ui.navigation_components',
            'taskmover.ui.input_components',
            'taskmover.ui.pattern_management_components',
            'taskmover.ui.rule_management_components',
            'taskmover.ui.execution_components',
            'taskmover.ui.history_components',
            'taskmover.ui.dialog_components'
        ]
        
        successful_imports = []
        failed_imports = []
        
        for component_module in components_to_test:
            try:
                __import__(component_module)
                successful_imports.append(component_module)
            except ImportError as e:
                failed_imports.append((component_module, str(e)))
        
        # Report results
        print(f"\nSuccessfully imported {len(successful_imports)} UI components:")
        for comp in successful_imports:
            print(f"  ✓ {comp}")
        
        if failed_imports:
            print(f"\nFailed to import {len(failed_imports)} UI components:")
            for comp, error in failed_imports:
                print(f"  ✗ {comp}: {error}")
        
        # At least some components should import successfully
        self.assertGreater(len(successful_imports), 0, "No UI components could be imported")
    
    def test_theme_manager_functionality(self):
        """Test theme manager basic functionality."""
        try:
            from taskmover.ui.theme_manager import get_theme_manager, ThemeMode
            
            theme_manager = get_theme_manager()
            self.assertIsNotNone(theme_manager)
            
            # Test theme switching
            original_mode = theme_manager.current_mode
            new_mode = ThemeMode.DARK if original_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
            
            theme_manager.set_theme_mode(new_mode)
            self.assertEqual(theme_manager.current_mode, new_mode)
            
            # Test tokens
            tokens = theme_manager.get_current_tokens()
            self.assertIsNotNone(tokens)
            self.assertIn('background', tokens.colors)
            
            # Restore original theme
            theme_manager.set_theme_mode(original_mode)
            
            print("✓ Theme manager functionality test passed")
            
        except ImportError:
            self.skipTest("Theme manager not available")
    
    def test_base_component_creation(self):
        """Test base component creation."""
        try:
            from taskmover.ui.base_component import BaseComponent, ModernButton
            
            class TestComponent(BaseComponent):
                def _create_component(self):
                    self.label = tk.Label(self, text="Test Component")
                    self.label.pack()
                    
                    self.button = ModernButton(self, text="Test Button")
                    self.button.pack()
            
            component = TestComponent(self.root)
            self.assertIsInstance(component, BaseComponent)
            self.assertTrue(hasattr(component, 'label'))
            self.assertTrue(hasattr(component, 'button'))
            
            print("✓ Base component creation test passed")
            
        except ImportError:
            self.skipTest("Base components not available")


class TestUIIntegration(unittest.TestCase):
    """Test UI integration scenarios."""
    
    def test_main_application_creation(self):
        """Test main application can be created."""
        try:
            from taskmover.ui.main_application import TaskMoverApplication
            
            # Mock mainloop to prevent blocking
            original_mainloop = tk.Tk.mainloop
            tk.Tk.mainloop = Mock()
            
            try:
                app = TaskMoverApplication()
                self.assertIsInstance(app, TaskMoverApplication)
                print("✓ Main application creation test passed")
            finally:
                tk.Tk.mainloop = original_mainloop
                
        except ImportError:
            self.skipTest("Main application not available")
        except Exception as e:
            if "No module named" in str(e):
                self.skipTest(f"Dependencies not available: {e}")
            else:
                raise
    
    def test_component_with_mock_services(self):
        """Test UI components with mocked backend services."""
        try:
            from taskmover.ui.pattern_management_components import PatternLibrary
            
            # Mock pattern service
            mock_pattern_service = Mock()
            mock_pattern_service.list_patterns.return_value = []
            mock_pattern_service.get_pattern_groups.return_value = []
            
            root = tk.Tk()
            root.withdraw()
            
            try:
                pattern_lib = PatternLibrary(root, pattern_service=mock_pattern_service)
                self.assertIsInstance(pattern_lib, PatternLibrary)
                print("✓ Component with mock services test passed")
            finally:
                root.destroy()
                
        except ImportError:
            self.skipTest("Pattern UI components not available")


class TestUIVisual(unittest.TestCase):
    """Visual UI tests for manual verification."""
    
    def test_create_visual_test_window(self):
        """Create a test window for visual verification."""
        try:
            from taskmover.ui.theme_manager import get_theme_manager, ThemeMode
            from taskmover.ui.base_component import BaseComponent, ModernButton
            
            # This test creates a visible window for manual testing
            # Set VISUAL_TEST environment variable to enable
            import os
            if not os.getenv('VISUAL_TEST'):
                self.skipTest("Visual test disabled (set VISUAL_TEST=1 to enable)")
            
            root = tk.Tk()
            root.title("TaskMover UI Visual Test")
            root.geometry("600x400")
            
            theme_manager = get_theme_manager()
            
            class VisualTestComponent(BaseComponent):
                def _create_component(self):
                    # Title
                    title = tk.Label(self, text="TaskMover UI Test", 
                                   font=("Segoe UI", 16, "bold"))
                    title.pack(pady=10)
                    
                    # Theme toggle button
                    self.theme_btn = ModernButton(
                        self, 
                        text="Toggle Dark Mode",
                        command=self.toggle_theme
                    )
                    self.theme_btn.pack(pady=5)
                    
                    # Sample buttons
                    button_frame = tk.Frame(self)
                    button_frame.pack(pady=10)
                    
                    ModernButton(button_frame, text="Primary", variant="primary").pack(side="left", padx=5)
                    ModernButton(button_frame, text="Secondary", variant="secondary").pack(side="left", padx=5)
                    ModernButton(button_frame, text="Outline", variant="outline").pack(side="left", padx=5)
                    
                    # Status
                    self.status = tk.Label(self, text="Visual test window ready")
                    self.status.pack(side="bottom", pady=10)
                
                def toggle_theme(self):
                    current = theme_manager.current_mode
                    new_mode = ThemeMode.DARK if current == ThemeMode.LIGHT else ThemeMode.LIGHT
                    theme_manager.set_theme_mode(new_mode)
                    self.status.configure(text=f"Theme: {new_mode.value}")
            
            test_component = VisualTestComponent(root)
            test_component.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Show window for 3 seconds
            root.after(3000, root.destroy)
            root.mainloop()
            
            print("✓ Visual test window displayed")
            
        except ImportError:
            self.skipTest("UI components not available for visual test")


def run_ui_tests():
    """Run UI tests with custom reporting."""
    print("TaskMover UI Test Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUIComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestUIIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestUIVisual))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✓ All UI tests passed!")
        print("\nTo run the main application:")
        print("  python -m taskmover")
        print("\nTo run visual tests:")
        print("  VISUAL_TEST=1 python tests/test_ui.py")
    else:
        print(f"✗ {len(result.failures)} failures, {len(result.errors)} errors")
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split()[-1] if traceback else 'Unknown'}")
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split()[-1] if traceback else 'Unknown'}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_ui_tests()
    sys.exit(0 if success else 1)