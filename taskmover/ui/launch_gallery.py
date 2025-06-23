#!/usr/bin/env python3
"""
TaskMover UI Gallery Launcher

Simple launcher script for the UI component gallery.
Run this script to open the visual component showcase.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def main():
    """Launch the UI component gallery."""
    print("TaskMover UI Component Gallery")
    print("==============================")
    
    # Check if we can import tkinter
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the root window
    except ImportError:
        print("Error: Tkinter is not available. Please install it.")
        sys.exit(1)
    except Exception as e:
        print(f"Error initializing Tkinter: {e}")
        sys.exit(1)
    
    # Try to import and run the gallery
    try:
        # Add current directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Import and run the gallery
        from demo_gallery import ComponentGallery
        
        root.destroy()  # Destroy the test root window
        
        print("Starting component gallery...")
        gallery = ComponentGallery()
        gallery.run()
        
    except ImportError as e:
        messagebox.showerror(
            "Import Error",
            f"Could not import required modules:\n{e}\n\n"
            "Make sure all UI components are properly installed."
        )
        print(f"Import error: {e}")
        
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"An error occurred while starting the gallery:\n{e}"
        )
        print(f"Runtime error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
