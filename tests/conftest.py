"""
Test configuration for TaskMover
===============================

Pytest configuration and fixtures for handling test environment setup.
"""

import pytest
import os
import sys
try:
    import tkinter as tk
except ImportError:
    tk = None  # type: ignore[assignment]
from unittest.mock import Mock, patch


def pytest_configure(config):
    """Configure pytest environment."""
    # Only mock tkinter if it is genuinely unavailable (no ImportError above means it's present)
    if tk is None:
        # Provide real base classes so tkinter-dependent modules can be imported.
        # Using Mock() for tk.Frame would cause a metaclass conflict with ABC.
        class _TkBase:
            """Minimal tkinter widget base for mocking."""
            def __init__(self, *args, **kwargs):
                pass
            def __getattr__(self, name):
                """Return a no-op callable for any missing tkinter method."""
                def _noop(*args, **kwargs):
                    return None
                return _noop
            def __setitem__(self, key, value):
                pass
            def __getitem__(self, key):
                return None

        from unittest.mock import MagicMock
        tkinter_mock = MagicMock()
        tkinter_mock.Frame = _TkBase
        tkinter_mock.Widget = _TkBase
        tkinter_mock.Tk = _TkBase
        tkinter_mock.Toplevel = _TkBase
        tkinter_mock.Label = _TkBase
        tkinter_mock.Button = _TkBase
        tkinter_mock.Entry = _TkBase
        tkinter_mock.Canvas = _TkBase
        tkinter_mock.Text = _TkBase
        tkinter_mock.Scrollbar = _TkBase
        tkinter_mock.TclError = Exception

        ttk_mock = MagicMock()
        ttk_mock.Frame = _TkBase
        ttk_mock.Label = _TkBase
        ttk_mock.Button = _TkBase
        ttk_mock.Entry = _TkBase
        ttk_mock.Progressbar = _TkBase
        ttk_mock.Combobox = _TkBase
        ttk_mock.Treeview = _TkBase
        ttk_mock.Scrollbar = _TkBase
        ttk_mock.Separator = _TkBase
        ttk_mock.Notebook = _TkBase
        ttk_mock.Scale = _TkBase
        tkinter_mock.ttk = ttk_mock

        tkinter_mock._IS_MOCK = True
        sys.modules['tkinter'] = tkinter_mock
        sys.modules['tkinter.ttk'] = ttk_mock


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
    try:
        patcher = patch('taskmover.ui.base_component.get_theme_manager')
        mock_get_theme = patcher.start()
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
        patcher.stop()
    except Exception:
        yield
