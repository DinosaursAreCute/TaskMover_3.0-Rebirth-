#!/usr/bin/env python3
"""
TaskMover Redesigned - Main entry point
"""

import sys
import os

# Add the parent directory to the path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from taskmover_redesign.app import TaskMoverApp

def main():
    """Main entry point for TaskMover Redesigned"""
    try:
        app = TaskMoverApp()
        app.root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting TaskMover: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
