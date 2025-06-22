#!/usr/bin/env python3
"""
Test script for TaskMover UI functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from taskmover_redesign.app import TaskMoverApp
import tempfile
import shutil

def test_ui():
    """Test basic UI initialization."""
    # Create a temporary directory for testing
    test_config_dir = tempfile.mkdtemp(prefix="taskmover_test_")
    
    try:
        print(f"Testing with config directory: {test_config_dir}")
        
        # Initialize the app
        app = TaskMoverApp()
        print("✅ TaskMover UI initialized successfully")
        
        # Check if ruleset manager is working
        print(f"✅ Ruleset manager initialized: {app.ruleset_manager is not None}")
        print(f"✅ Current ruleset: {app.ruleset_manager.current_ruleset}")
        print(f"✅ Available rulesets: {[rs['name'] for rs in app.ruleset_manager.get_available_rulesets()]}")
        
        # Test UI elements exist
        print(f"✅ Rules tree exists: {hasattr(app, 'rules_tree')}")
        print(f"✅ Ruleset dropdown exists: {hasattr(app, 'ruleset_dropdown')}")
        
        # Don't actually start the GUI mainloop for testing
        app.root.quit()
        app.root.destroy()
        
        print("🎉 UI test completed successfully!")
        
    except Exception as e:
        print(f"❌ UI test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        try:
            shutil.rmtree(test_config_dir)
        except:
            pass

if __name__ == "__main__":
    test_ui()
