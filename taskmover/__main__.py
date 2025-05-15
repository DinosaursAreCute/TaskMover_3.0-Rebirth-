"""
Main entry point for the TaskMover application.

This script imports the `run` function from the `app` module and executes it
when the script is run as the main program.
"""

try:
    from taskmover.app import run
except ImportError:
    from app import run

if __name__ == "__main__":
    # Execute the main application logic.
    run()
