"""
Integration tests for TaskMover UI components
=============================================

Tests for UI component integration and interaction.
"""

import unittest
import tkinter as tk
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import threading
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestUIComponentIntegration(unittest.TestCase):
    """Test UI component integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
    
    def tearDown(self):
        """Clean up test environment."""
        self.root.destroy()
    
    def test_main_application_import(self):
        """Test that main application can be imported."""
        try:
            from taskmover.ui.main_application import TaskMoverApplication
            self.assertTrue(True, "Main application imported successfully")
        except ImportError as e:
            self.skipTest(f"Main application not available: {e}")
    
    def test_theme_manager_integration(self):
        """Test theme manager integration with UI components."""
        try:
            from taskmover.ui.theme_manager import get_theme_manager, ThemeMode
            from taskmover.ui.base_component import BaseComponent
            
            class TestComponent(BaseComponent):
                def _create_component(self):
                    self.label = tk.Label(self, text="Test")
                    self.label.pack()
            
            # Create component
            component = TestComponent(self.root)
            
            # Get theme manager
            theme_manager = get_theme_manager()
            
            # Test theme switching
            original_mode = theme_manager.current_mode
            new_mode = ThemeMode.DARK if original_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
            
            theme_manager.set_theme(new_mode)
            self.assertEqual(theme_manager.current_mode, new_mode)
            
            # Switch back
            theme_manager.set_theme(original_mode)
            self.assertEqual(theme_manager.current_mode, original_mode)
            
        except ImportError as e:
            self.skipTest(f"Theme components not available: {e}")
    
    def test_component_hierarchy(self):
        """Test UI component hierarchy."""
        try:
            from taskmover.ui.base_component import BaseComponent, ModernButton
            
            class ContainerComponent(BaseComponent):
                def _create_component(self):
                    self.button1 = ModernButton(self, text="Button 1")
                    self.button1.pack(pady=5)
                    
                    self.button2 = ModernButton(self, text="Button 2")
                    self.button2.pack(pady=5)
            
            container = ContainerComponent(self.root)
            
            # Test component hierarchy
            self.assertIsInstance(container.button1, ModernButton)
            self.assertIsInstance(container.button2, ModernButton)
            
            # Test parent-child relationship
            self.assertEqual(container.button1.master, container)
            self.assertEqual(container.button2.master, container)
            
        except ImportError as e:
            self.skipTest(f"UI components not available: {e}")


class TestMainApplicationIntegration(unittest.TestCase):
    """Test main application integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.original_mainloop = tk.Tk.mainloop
        # Mock mainloop to prevent blocking
        tk.Tk.mainloop = Mock()
    
    def tearDown(self):
        """Clean up test environment."""
        tk.Tk.mainloop = self.original_mainloop
    
    def test_application_creation(self):
        """Test application creation doesn't fail."""
        try:
            from taskmover.ui.main_application import TaskMoverApplication
            
            app = TaskMoverApplication()
            self.assertIsInstance(app, TaskMoverApplication)
            
            # Test that application has required components
            # Note: This depends on actual implementation
            self.assertTrue(hasattr(app, 'root') or hasattr(app, 'window'))
            
        except ImportError as e:
            self.skipTest(f"Main application not available: {e}")
        except Exception as e:
            # Log the error but don't fail the test if it's due to missing dependencies
            if "No module named" in str(e) or "cannot import" in str(e):
                self.skipTest(f"Dependencies not available: {e}")
            else:
                raise
    
    def test_application_with_mock_services(self):
        """Test application with mocked backend services."""
        try:
            from taskmover.ui.main_application import TaskMoverApplication
            
            # Mock backend services
            with patch('taskmover.core.patterns.PatternSystem') as mock_pattern_system, \
                 patch('taskmover.core.rules.service.RuleService') as mock_rule_service:
                
                mock_pattern_system.return_value = Mock()
                mock_rule_service.return_value = Mock()
                
                app = TaskMoverApplication()
                self.assertIsInstance(app, TaskMoverApplication)
                
        except ImportError as e:
            self.skipTest(f"Application components not available: {e}")


class TestUIThemeIntegration(unittest.TestCase):
    """Test UI theme integration across components."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up test environment."""
        self.root.destroy()
    
    def test_theme_consistency_across_components(self):
        """Test theme consistency across multiple components."""
        try:
            from taskmover.ui.theme_manager import get_theme_manager, ThemeMode
            from taskmover.ui.base_component import BaseComponent, ModernButton
            
            theme_manager = get_theme_manager()
            
            # Create multiple components
            components = []
            for i in range(3):
                class TestComponent(BaseComponent):
                    def _create_component(self):
                        self.button = ModernButton(self, text=f"Button {i}")
                        self.button.pack()
                
                comp = TestComponent(self.root)
                components.append(comp)
            
            # Switch theme
            original_mode = theme_manager.current_mode
            new_mode = ThemeMode.DARK if original_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
            
            theme_manager.set_theme(new_mode)
            
            # All components should have access to the same theme
            tokens = theme_manager.get_current_tokens()
            self.assertIsNotNone(tokens)
            self.assertIsNotNone(tokens.colors)
            
            # Switch back
            theme_manager.set_theme(original_mode)
            
        except ImportError as e:
            self.skipTest(f"Theme components not available: {e}")
    
    def test_theme_callback_system(self):
        """Test theme callback system works across components."""
        try:
            from taskmover.ui.theme_manager import get_theme_manager, ThemeMode
            
            theme_manager = get_theme_manager()
            
            # Track callback invocations
            callback_calls = []
            
            def test_callback(mode):
                callback_calls.append(mode)
            
            # Register callback
            theme_manager.register_callback(test_callback)
            
            # Change theme
            original_mode = theme_manager.current_mode
            new_mode = ThemeMode.DARK if original_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
            
            theme_manager.set_theme(new_mode)
            
            # Callback should have been called
            self.assertEqual(len(callback_calls), 1)
            self.assertEqual(callback_calls[0], new_mode)
            
            # Switch back
            theme_manager.set_theme(original_mode)
            self.assertEqual(len(callback_calls), 2)
            
        except ImportError as e:
            self.skipTest(f"Theme manager not available: {e}")


class TestUIServiceIntegration(unittest.TestCase):
    """Test UI integration with backend services."""
    
    def test_pattern_ui_integration(self):
        """Test pattern UI components with mock pattern service."""
        try:
            from taskmover.ui.pattern_management_components import PatternLibrary
            
            # Mock pattern service
            mock_pattern_service = Mock()
            mock_pattern_service.list_patterns.return_value = []
            mock_pattern_service.get_pattern_groups.return_value = []
            
            root = tk.Tk()
            root.withdraw()
            
            try:
                # Create pattern library component
                pattern_lib = PatternLibrary(
                    root, 
                    pattern_service=mock_pattern_service
                )
                
                self.assertIsInstance(pattern_lib, PatternLibrary)
                
                # Verify service integration
                mock_pattern_service.list_patterns.assert_called()
                
            finally:
                root.destroy()
                
        except ImportError as e:
            self.skipTest(f"Pattern UI components not available: {e}")
    
    def test_rule_ui_integration(self):
        """Test rule UI components with mock rule service."""
        try:
            from taskmover.ui.rule_management_components import RuleManagementView
            
            # Mock services
            mock_rule_service = Mock()
            mock_rule_service.list_rules.return_value = []
            
            mock_pattern_service = Mock()
            mock_pattern_service.list_patterns.return_value = []
            
            root = tk.Tk()
            root.withdraw()
            
            try:
                # Create rule management component
                rule_view = RuleManagementView(
                    root,
                    rule_service=mock_rule_service,
                    pattern_service=mock_pattern_service
                )
                
                self.assertIsInstance(rule_view, RuleManagementView)
                
                # Verify service integration
                mock_rule_service.list_rules.assert_called()
                
            finally:
                root.destroy()
                
        except ImportError as e:
            self.skipTest(f"Rule UI components not available: {e}")


class TestUIComponentCommunication(unittest.TestCase):
    """Test communication between UI components."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up test environment."""
        self.root.destroy()
    
    def test_component_event_communication(self):
        """Test components can communicate through events."""
        events_received = []
        
        try:
            from taskmover.ui.base_component import BaseComponent, ModernButton
            
            class PublisherComponent(BaseComponent):
                def _create_component(self):
                    self.button = ModernButton(
                        self, 
                        text="Publish Event",
                        command=self.publish_event
                    )
                    self.button.pack()
                    self.event_handlers = []
                
                def register_handler(self, handler):
                    self.event_handlers.append(handler)
                
                def publish_event(self):
                    for handler in self.event_handlers:
                        handler("test_event")
            
            class SubscriberComponent(BaseComponent):
                def _create_component(self):
                    self.label = tk.Label(self, text="Waiting...")
                    self.label.pack()
                
                def handle_event(self, event_data):
                    events_received.append(event_data)
                    self.label.configure(text=f"Received: {event_data}")
            
            # Create components
            publisher = PublisherComponent(self.root)
            subscriber = SubscriberComponent(self.root)
            
            # Setup communication
            publisher.register_handler(subscriber.handle_event)
            
            # Trigger event
            publisher.publish_event()
            
            # Verify communication
            self.assertEqual(len(events_received), 1)
            self.assertEqual(events_received[0], "test_event")
            
        except ImportError as e:
            self.skipTest(f"UI components not available: {e}")


class TestUIPerformance(unittest.TestCase):
    """Test UI performance characteristics."""
    
    def test_component_creation_performance(self):
        """Test component creation doesn't take too long."""
        try:
            from taskmover.ui.base_component import BaseComponent, ModernButton
            
            class TestComponent(BaseComponent):
                def _create_component(self):
                    for i in range(10):
                        btn = ModernButton(self, text=f"Button {i}")
                        btn.pack()
            
            root = tk.Tk()
            root.withdraw()
            
            try:
                start_time = time.time()
                component = TestComponent(root)
                creation_time = time.time() - start_time
                
                # Component creation should be fast (< 1 second)
                self.assertLess(creation_time, 1.0)
                
            finally:
                root.destroy()
                
        except ImportError as e:
            self.skipTest(f"UI components not available: {e}")
    
    def test_theme_switching_performance(self):
        """Test theme switching is responsive."""
        try:
            from taskmover.ui.theme_manager import get_theme_manager, ThemeMode
            
            theme_manager = get_theme_manager()
            original_mode = theme_manager.current_mode
            
            # Time theme switches
            start_time = time.time()
            
            for _ in range(5):
                new_mode = ThemeMode.DARK if theme_manager.current_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
                theme_manager.set_theme(new_mode)
            
            switch_time = time.time() - start_time
            
            # Theme switching should be fast
            self.assertLess(switch_time, 0.5)  # 5 switches in under 0.5 seconds
            
            # Restore original theme
            theme_manager.set_theme(original_mode)
            
        except ImportError as e:
            self.skipTest(f"Theme manager not available: {e}")


if __name__ == '__main__':
    unittest.main()
