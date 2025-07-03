"""
Test cases for UI Theme Manager
===============================

Tests for theme management, dark mode, and design tokens.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from taskmover.ui.theme_manager import (
    ThemeManager,
    get_theme_manager,
    ThemeMode,
    DesignTokens,
    DarkTokens
)


class TestDesignTokens(unittest.TestCase):
    """Test design tokens system."""
    
    def test_design_tokens_creation(self):
        """Test DesignTokens creation with defaults."""
        tokens = DesignTokens()
        
        # Check colors are populated
        self.assertIn("primary", tokens.colors)
        self.assertIn("background", tokens.colors)
        self.assertIn("text", tokens.colors)
        
        # Check fonts are populated
        self.assertIn("family", tokens.fonts)
        self.assertIn("size_body", tokens.fonts)
        
        # Check spacing is populated
        self.assertIn("sm", tokens.spacing)
        self.assertIn("md", tokens.spacing)
        
        # Check shadows and radius
        self.assertIn("sm", tokens.shadows)
        self.assertIn("md", tokens.radius)
    
    def test_dark_tokens_inheritance(self):
        """Test DarkTokens inherits and overrides correctly."""
        dark_tokens = DarkTokens()
        
        # Should have all base properties
        self.assertIn("primary", dark_tokens.colors)
        self.assertIn("family", dark_tokens.fonts)
        
        # Dark theme specific colors
        self.assertEqual(dark_tokens.colors["background"], "#0f172a")
        self.assertEqual(dark_tokens.colors["text"], "#f8fafc")
        
        # Should still have inherited properties
        self.assertIn("sm", dark_tokens.spacing)
        self.assertIn("md", dark_tokens.radius)
    
    def test_tokens_consistency(self):
        """Test token structure consistency."""
        light_tokens = DesignTokens()
        dark_tokens = DarkTokens()
        
        # Both should have same keys in main categories
        self.assertEqual(set(light_tokens.colors.keys()), set(dark_tokens.colors.keys()))
        self.assertEqual(set(light_tokens.fonts.keys()), set(dark_tokens.fonts.keys()))
        self.assertEqual(set(light_tokens.spacing.keys()), set(dark_tokens.spacing.keys()))


class TestThemeManager(unittest.TestCase):
    """Test ThemeManager functionality."""
    
    def setUp(self):
        """Set up test theme manager."""
        self.theme_manager = ThemeManager()
    
    def test_theme_manager_initialization(self):
        """Test ThemeManager initializes correctly."""
        self.assertIsInstance(self.theme_manager.current_mode, ThemeMode)
        self.assertEqual(self.theme_manager.current_mode, ThemeMode.LIGHT)
        
        tokens = self.theme_manager.get_current_tokens()
        self.assertIsInstance(tokens, DesignTokens)
    
    def test_theme_switching(self):
        """Test switching between themes."""
        # Start in light mode
        self.assertEqual(self.theme_manager.current_mode, ThemeMode.LIGHT)
        light_tokens = self.theme_manager.get_current_tokens()
        
        # Switch to dark mode
        self.theme_manager.set_theme_mode(ThemeMode.DARK)
        self.assertEqual(self.theme_manager.current_mode, ThemeMode.DARK)
        dark_tokens = self.theme_manager.get_current_tokens()
        
        # Verify different tokens
        self.assertNotEqual(
            light_tokens.colors["background"],
            dark_tokens.colors["background"]
        )
        
        # Switch back to light
        self.theme_manager.set_theme_mode(ThemeMode.LIGHT)
        self.assertEqual(self.theme_manager.current_mode, ThemeMode.LIGHT)
    
    def test_theme_change_callbacks(self):
        """Test theme change callbacks."""
        callback_called = []
        
        def test_callback(theme_mode):
            callback_called.append(theme_mode)
        
        # Register callback
        self.theme_manager.register_callback(test_callback)
        
        # Change theme
        self.theme_manager.set_theme_mode(ThemeMode.DARK)
        
        # Verify callback was called
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0], ThemeMode.DARK)
    
    def test_multiple_callbacks(self):
        """Test multiple theme change callbacks."""
        callbacks_called = []
        
        def callback1(mode):
            callbacks_called.append(("cb1", mode))
        
        def callback2(mode):
            callbacks_called.append(("cb2", mode))
        
        # Register callbacks
        self.theme_manager.register_callback(callback1)
        self.theme_manager.register_callback(callback2)
        
        # Change theme
        self.theme_manager.set_theme_mode(ThemeMode.DARK)
        
        # Both callbacks should be called
        self.assertEqual(len(callbacks_called), 2)
        self.assertIn(("cb1", ThemeMode.DARK), callbacks_called)
        self.assertIn(("cb2", ThemeMode.DARK), callbacks_called)
    
    def test_auto_theme_mode(self):
        """Test AUTO theme mode behavior."""
        # Set to auto mode
        self.theme_manager.set_theme_mode(ThemeMode.AUTO)
        self.assertEqual(self.theme_manager.current_mode, ThemeMode.AUTO)
        
        # Should still return valid tokens (defaults to light for testing)
        tokens = self.theme_manager.get_current_tokens()
        self.assertIsInstance(tokens, DesignTokens)


class TestSingletonThemeManager(unittest.TestCase):
    """Test theme manager singleton behavior."""
    
    def test_get_theme_manager_singleton(self):
        """Test that get_theme_manager returns singleton."""
        manager1 = get_theme_manager()
        manager2 = get_theme_manager()
        
        self.assertIs(manager1, manager2)
        self.assertIsInstance(manager1, ThemeManager)
    
    def test_singleton_state_persistence(self):
        """Test that singleton maintains state."""
        manager1 = get_theme_manager()
        manager1.set_theme_mode(ThemeMode.DARK)
        
        manager2 = get_theme_manager()
        self.assertEqual(manager2.current_mode, ThemeMode.DARK)


class TestThemeTokenValues(unittest.TestCase):
    """Test specific theme token values."""
    
    def test_light_theme_colors(self):
        """Test light theme color values."""
        tokens = DesignTokens()
        
        # Primary color should be blue
        self.assertEqual(tokens.colors["primary"], "#2563eb")
        
        # Background should be white
        self.assertEqual(tokens.colors["background"], "#ffffff")
        
        # Text should be dark
        self.assertEqual(tokens.colors["text"], "#1e293b")
    
    def test_dark_theme_colors(self):
        """Test dark theme color values."""
        tokens = DarkTokens()
        
        # Background should be dark
        self.assertEqual(tokens.colors["background"], "#0f172a")
        
        # Text should be light
        self.assertEqual(tokens.colors["text"], "#f8fafc")
        
        # Primary should be adjusted for dark theme
        self.assertEqual(tokens.colors["primary"], "#3b82f6")
    
    def test_typography_tokens(self):
        """Test typography token values."""
        tokens = DesignTokens()
        
        # Font family
        self.assertEqual(tokens.fonts["family"], "Segoe UI")
        self.assertEqual(tokens.fonts["family_mono"], "Consolas")
        
        # Font sizes should be strings (for Tkinter)
        self.assertIsInstance(tokens.fonts["size_body"], str)
        self.assertIsInstance(tokens.fonts["size_heading_1"], str)
        
        # Font weights
        self.assertIn(tokens.fonts["weight_normal"], ["normal", "bold"])
        self.assertIn(tokens.fonts["weight_bold"], ["normal", "bold"])
    
    def test_spacing_tokens(self):
        """Test spacing token values."""
        tokens = DesignTokens()
        
        # Spacing should be integers
        self.assertIsInstance(tokens.spacing["xs"], int)
        self.assertIsInstance(tokens.spacing["sm"], int)
        
        # Spacing should increase
        self.assertLess(tokens.spacing["xs"], tokens.spacing["sm"])
        self.assertLess(tokens.spacing["sm"], tokens.spacing["md"])
        self.assertLess(tokens.spacing["md"], tokens.spacing["lg"])


class TestThemeIntegration(unittest.TestCase):
    """Test theme integration scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.last_callback_mode = None
    
    def test_theme_switching_scenario(self):
        """Test complete theme switching scenario."""
        manager = get_theme_manager()
        
        # Start with light theme
        manager.set_theme_mode(ThemeMode.LIGHT)
        light_bg = manager.get_current_tokens().colors["background"]
        
        # Switch to dark
        manager.set_theme_mode(ThemeMode.DARK)
        dark_bg = manager.get_current_tokens().colors["background"]
        
        # Colors should be different
        self.assertNotEqual(light_bg, dark_bg)
        
        # Switch back to light
        manager.set_theme_mode(ThemeMode.LIGHT)
        back_to_light_bg = manager.get_current_tokens().colors["background"]
        
        # Should match original light theme
        self.assertEqual(light_bg, back_to_light_bg)
    
    def test_callback_error_handling(self):
        """Test theme manager handles callback errors gracefully."""
        manager = get_theme_manager()
        
        def failing_callback(mode):
            raise Exception("Callback error")
        
        def working_callback(mode):
            self.last_callback_mode = mode
        
        # Register both callbacks
        manager.register_callback(failing_callback)
        manager.register_callback(working_callback)
        
        # Change theme - should not raise exception
        try:
            manager.set_theme_mode(ThemeMode.DARK)
            # Working callback should still be called
            self.assertEqual(self.last_callback_mode, ThemeMode.DARK)
        except Exception:
            self.fail("Theme change raised exception due to callback error")


if __name__ == '__main__':
    unittest.main()
