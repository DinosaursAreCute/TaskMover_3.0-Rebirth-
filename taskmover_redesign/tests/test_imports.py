#!/usr/bin/env python3
"""
Test script to verify that all imports in the redesigned app work correctly.
"""

import sys
import os

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

def test_imports():
    """Test all the imports that the redesigned app uses."""
    try:
        print("Testing core imports...")
        from taskmover_redesign.core import (
            ConfigManager, RuleManager, FileOrganizer, 
            load_rules, save_rules, load_settings, save_settings, load_or_initialize_rules,
            get_sorted_rule_keys, move_rule_priority, start_organization,
            center_window, configure_logger, setup_logging
        )
        print("✓ Core imports successful")
        
        print("Testing UI imports...")
        from taskmover_redesign.ui import (
            Tooltip, ProgressDialog, ConfirmDialog, RuleEditor, RuleListWidget, SettingsDialog
        )
        print("✓ UI imports successful")
        
        print("Testing specific UI components...")
        from taskmover_redesign.ui.rule_components import add_rule_button, edit_rule, enable_all_rules, disable_all_rules
        from taskmover_redesign.ui.settings_components import open_settings_window
        print("✓ UI component imports successful")
        
        print("Testing tkinter and ttkbootstrap...")
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog, simpledialog
        import ttkbootstrap as ttkb
        from ttkbootstrap.constants import LEFT, RIGHT, TOP, BOTTOM, X, Y, BOTH, CENTER, VERTICAL
        print("✓ GUI library imports successful")
        
        print("\n🎉 All imports successful! The redesigned app should work.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
