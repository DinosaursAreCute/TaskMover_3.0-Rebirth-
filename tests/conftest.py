"""
Test configuration for TaskMover
===============================

Pytest configuration and fixtures for handling test environment setup.
"""

import pytest
import os
import sys
import tkinter as tk
from unittest.mock import Mock, patch


def pytest_configure(config):
    """Configure pytest environment."""
    # Handle headless environment for Tkinter tests
    if 'CI' in os.environ or 'HEADLESS' in os.environ:
        # Mock tkinter for headless environments
        sys.modules['tkinter'] = Mock()
        sys.modules['tkinter.ttk'] = Mock()


@pytest.fixture(scope="function")
def tk_root():
    """Provide a Tkinter root window for tests."""
    try:
        root = tk.Tk()
        root.withdraw()  # Hide window during tests
        yield root
        root.destroy()
    except tk.TclError:
        # Provide mock root for headless environments
        mock_root = Mock()
        mock_root.withdraw = Mock()
        mock_root.destroy = Mock()
        yield mock_root


@pytest.fixture(scope="function")
def mock_theme_manager():
    """Provide a mock theme manager for tests."""
    mock_manager = Mock()
    mock_manager.get_current_tokens.return_value = Mock(
        colors={
            "primary": "#2563eb",
            "background": "#ffffff",
            "text": "#000000",
            "surface": "#f8fafc"
        },
        fonts={
            "family": "Segoe UI",
            "size_body": 14,
            "weight_normal": "normal",
            "weight_bold": "bold"
        },
        spacing={
            "xs": 4,
            "sm": 8,
            "md": 16,
            "lg": 24
        }
    )
    mock_manager.get_color.return_value = "#000000"
    mock_manager.get_font.return_value = ("Segoe UI", 14)
    
    return mock_manager


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment with proper mocking."""
    # Patch theme manager for all tests
    with patch('taskmover.ui.base_component.get_theme_manager') as mock_get_theme:
        mock_manager = Mock()
        mock_manager.get_current_tokens.return_value = Mock(
            colors={
                "primary": "#2563eb", 
                "background": "#ffffff",
                "text": "#000000",
                "surface": "#f8fafc",
                "primary_dark": "#1e40af",
                "hover": "#e2e8f0",
                "error": "#dc2626"
            },
            fonts={
                "family": "Segoe UI",
                "size_body": "14",
                "size_heading_1": "24",
                "weight_normal": "normal",
                "weight_bold": "bold"
            },
            spacing={
                "xs": 4,
                "sm": 8, 
                "md": 16,
                "lg": 24
            }
        )
        mock_get_theme.return_value = mock_manager
        yield
