"""
TaskMover Application Entry Point
================================

Main entry point for the TaskMover application.
"""

import sys
import os
from pathlib import Path

def main():
    """Main entry point for TaskMover application."""
    try:
        from taskmover.ui.main_application import TaskMoverApplication
        
        # Initialize and run the application
        app = TaskMoverApplication()
        app.run()
        
    except ImportError as e:
        print(f"Error importing TaskMover components: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting TaskMover: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
