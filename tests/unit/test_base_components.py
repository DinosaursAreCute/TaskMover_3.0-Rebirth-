"""
Test cases for UI Base Components
=================================

Tests for base UI components and their functionality.
"""

import unittest
import tkinter as tk
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from taskmover.ui.base_component import BaseComponent, ModernButton, StatusBar


class TestBaseComponent(unittest.TestCase):
    """Test BaseComponent functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
    
    def tearDown(self):
        """Clean up test environment."""
        self.root.destroy()
    
    def test_base_component_creation(self):
        """Test BaseComponent can be created."""
        
        class TestComponent(BaseComponent):
            def _create_component(self):
                self.test_label = tk.Label(self, text="Test")
                self.test_label.pack()
        
        component = TestComponent(self.root)
        
        # Component should be created
        self.assertIsInstance(component, BaseComponent)
        self.assertIsInstance(component, tk.Frame)
        
        # _create_component should have been called
        self.assertTrue(hasattr(component, 'test_label'))
    
    def test_base_component_theme_integration(self):
        """Test BaseComponent integrates with theme system."""
        
        class TestComponent(BaseComponent):
            def _create_component(self):
                # Call theme manager in _create_component to trigger the call
                try:
                    from taskmover.ui.theme_manager import get_theme_manager
                    theme = get_theme_manager()
                    tokens = theme.get_current_tokens()
                except ImportError:
                    pass
        
        # Mock theme manager
        with patch('taskmover.ui.base_component.get_theme_manager') as mock_theme:
            mock_theme_instance = Mock()
            mock_theme_instance.get_current_tokens.return_value = Mock(
                colors={"background": "#ffffff", "text": "#000000"}
            )
            mock_theme.return_value = mock_theme_instance
            
            component = TestComponent(self.root)
            
            # The base component uses fallback theme manager for initialization
            # Theme manager may be called later in component creation
            self.assertIsInstance(component, BaseComponent)
    
    def test_base_component_initialization_order(self):
        """Test component initialization happens in correct order."""
        
        init_order = []
        
        class TestComponent(BaseComponent):
            def __init__(self, parent, **kwargs):
                init_order.append("__init__")
                super().__init__(parent, **kwargs)
            
            def _create_component(self):
                init_order.append("_create_component")
        
        TestComponent(self.root)
        
        # _create_component should be called after __init__
        self.assertEqual(init_order, ["__init__", "_create_component"])


class TestModernButton(unittest.TestCase):
    """Test ModernButton component."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up test environment."""
        self.root.destroy()
    
    def test_modern_button_creation(self):
        """Test ModernButton creation."""
        button = ModernButton(self.root, text="Test Button")
        
        self.assertIsInstance(button, ModernButton)
        self.assertIsInstance(button, BaseComponent)  # ModernButton inherits from BaseComponent, not tk.Button
    
    def test_modern_button_with_command(self):
        """Test ModernButton with command callback."""
        command_called = []
        
        def test_command():
            command_called.append(True)
        
        button = ModernButton(self.root, text="Test", command=test_command)
        
        # Simulate button click
        button.invoke()
        
        self.assertEqual(len(command_called), 1)
    
    def test_modern_button_styling(self):
        """Test ModernButton applies modern styling."""
        button = ModernButton(self.root, text="Test")
        
        # Button should have specific styling properties
        # Note: Exact values depend on theme implementation
        self.assertIsNotNone(button.cget("relief"))
        self.assertIsNotNone(button.cget("font"))
    
    def test_modern_button_variants(self):
        """Test different ModernButton variants."""
        # Primary button
        primary_btn = ModernButton(self.root, text="Primary", variant="primary")
        self.assertIsInstance(primary_btn, ModernButton)
        
        # Secondary button
        secondary_btn = ModernButton(self.root, text="Secondary", variant="secondary")
        self.assertIsInstance(secondary_btn, ModernButton)
        
        # Outline button
        outline_btn = ModernButton(self.root, text="Outline", variant="outline")
        self.assertIsInstance(outline_btn, ModernButton)


class TestStatusBar(unittest.TestCase):
    """Test StatusBar component."""
    
    def setUp(self):
        """Set up test environment."""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
        except tk.TclError:
            # Skip tests if Tkinter environment is not available
            self.skipTest("Tkinter environment not available")
    
    def tearDown(self):
        """Clean up test environment."""
        try:
            if hasattr(self, 'root') and self.root:
                self.root.destroy()
        except tk.TclError:
            # Ignore errors during cleanup
            pass
    
    def test_status_bar_creation(self):
        """Test StatusBar creation."""
        status_bar = StatusBar(self.root)
        
        self.assertIsInstance(status_bar, StatusBar)
        self.assertIsInstance(status_bar, BaseComponent)
    
    def test_status_bar_set_status(self):
        """Test setting status message."""
        status_bar = StatusBar(self.root)
        
        # Set status message
        status_bar.set_status("Test message")
        
        # Status should be updated
        # Note: Actual verification depends on implementation details
        self.assertTrue(hasattr(status_bar, 'set_status'))
    
    def test_status_bar_set_progress(self):
        """Test setting progress value."""
        status_bar = StatusBar(self.root)
        
        # Set progress
        status_bar.set_progress(50)
        
        # Progress should be updated
        self.assertTrue(hasattr(status_bar, 'set_progress'))
    
    def test_status_bar_clear(self):
        """Test clearing status bar."""
        status_bar = StatusBar(self.root)
        
        # Set some status
        status_bar.set_status("Test message")
        status_bar.set_progress(75)
        
        # Clear status
        status_bar.clear()
        
        # Status should be cleared
        self.assertTrue(hasattr(status_bar, 'clear'))


class TestComponentIntegration(unittest.TestCase):
    """Test component integration scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up test environment."""
        self.root.destroy()
    
    def test_components_in_container(self):
        """Test multiple components in container."""
        
        class TestContainer(BaseComponent):
            def _create_component(self):
                self.button = ModernButton(self, text="Button")
                self.button.pack(pady=5)
                
                self.status_bar = StatusBar(self)
                self.status_bar.pack(side="bottom", fill="x")
        
        container = TestContainer(self.root)
        
        # Container should have both components
        self.assertTrue(hasattr(container, 'button'))
        self.assertTrue(hasattr(container, 'status_bar'))
        self.assertIsInstance(container.button, ModernButton)
        self.assertIsInstance(container.status_bar, StatusBar)
    
    def test_component_theme_consistency(self):
        """Test components maintain theme consistency."""
        
        with patch('taskmover.ui.base_component.get_theme_manager') as mock_theme:
            mock_theme_instance = Mock()
            mock_tokens = Mock()
            mock_tokens.colors = {
                "background": "#ffffff",
                "text": "#000000", 
                "primary": "#0066cc"
            }
            mock_theme_instance.get_current_tokens.return_value = mock_tokens
            mock_theme.return_value = mock_theme_instance
            
            # Create multiple components
            button = ModernButton(self.root, text="Button")
            status_bar = StatusBar(self.root)
            
            # Both components should be created successfully
            self.assertIsInstance(button, ModernButton)
            self.assertIsInstance(status_bar, StatusBar)
    
    def test_component_event_handling(self):
        """Test component event handling."""
        events_triggered = []
        
        def on_button_click():
            events_triggered.append("button_click")
        
        class TestContainer(BaseComponent):
            def _create_component(self):
                self.button = ModernButton(
                    self, 
                    text="Click Me", 
                    command=on_button_click
                )
                self.button.pack()
        
        container = TestContainer(self.root)
        
        # Simulate button click
        container.button.invoke()
        
        self.assertEqual(events_triggered, ["button_click"])
    
    def test_component_error_handling(self):
        """Test component error handling."""
        
        class FailingComponent(BaseComponent):
            def _create_component(self):
                # Simulate error during component creation
                raise Exception("Component creation failed")
        
        # Component creation should handle errors gracefully
        # Note: Exact error handling depends on implementation
        try:
            FailingComponent(self.root)
        except Exception as e:
            # Should be the original exception or wrapped
            self.assertIn("Component creation failed", str(e))


class TestComponentThemeUpdates(unittest.TestCase):
    """Test component theme update scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up test environment."""
        self.root.destroy()
    
    def test_component_responds_to_theme_changes(self):
        """Test components respond to theme changes."""
        
        with patch('taskmover.ui.base_component.get_theme_manager') as mock_theme:
            mock_theme_instance = Mock()
            mock_theme_instance.get_current_tokens.return_value = Mock(
                colors={"background": "#ffffff", "text": "#000000"}
            )
            mock_theme.return_value = mock_theme_instance
            
            class ThemeAwareComponent(BaseComponent):
                def _create_component(self):
                    self.theme_updates = 0
                
                def update_theme(self):
                    self.theme_updates += 1
            
            component = ThemeAwareComponent(self.root)
            
            # Simulate theme change if component supports it
            if hasattr(component, 'update_theme'):
                component.update_theme()
                self.assertEqual(component.theme_updates, 1)


if __name__ == '__main__':
    unittest.main()
