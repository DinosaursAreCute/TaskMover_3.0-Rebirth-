#!/usr/bin/env python3
"""
Test script for the new proportional window sizing features.
"""

import sys
import os

# Add the project root to the Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

import tkinter as tk
import ttkbootstrap as ttkb
from taskmover_redesign.core.utils import center_window, center_window_on_parent

def test_proportional_window():
    """Test the proportional window sizing functionality."""
    
    # Create main window
    root = ttkb.Window(themename="flatly")
    root.title("Test - Main Window (Proportional)")
    
    # Use proportional sizing for main window (60% of screen width, 70% of screen height)
    center_window(root, proportional=True, width_ratio=0.6, height_ratio=0.7)
    
    # Create a test button that opens a dialog
    def open_test_dialog():
        dialog = tk.Toplevel(root)
        dialog.title("Test Dialog (Proportional)")
        dialog.transient(root)
        dialog.grab_set()
        
        # Use proportional sizing for dialog (40% of parent width, 50% of parent height)
        center_window_on_parent(dialog, root, proportional=True, width_ratio=0.4, height_ratio=0.5)
        
        # Add some content
        frame = ttkb.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        
        ttkb.Label(frame, text="This dialog is proportionally sized!").pack(pady=10)
        ttkb.Label(frame, text="It should be 40% of the main window's width").pack(pady=5)
        ttkb.Label(frame, text="and 50% of the main window's height").pack(pady=5)
        
        ttkb.Button(frame, text="Close", command=dialog.destroy).pack(pady=10)
    
    # Add content to main window
    main_frame = ttkb.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)
    
    ttkb.Label(main_frame, text="Main Window (Proportional Sizing Test)", 
               font=("Arial", 16, "bold")).pack(pady=20)
    
    ttkb.Label(main_frame, text="This window should be 60% of screen width and 70% of screen height").pack(pady=10)
    
    ttkb.Button(main_frame, text="Open Test Dialog", 
                command=open_test_dialog).pack(pady=20)
    
    ttkb.Button(main_frame, text="Exit", command=root.quit).pack(pady=10)
    
    # Run the application
    root.mainloop()

if __name__ == "__main__":
    test_proportional_window()
