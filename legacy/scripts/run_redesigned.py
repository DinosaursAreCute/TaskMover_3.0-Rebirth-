#!/usr/bin/env python3
"""
Runner script for the redesigned TaskMover interface.
This allows you to test the new UI without modifying the existing app.
"""

import sys
import os

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run the redesigned app
from taskmover_redesign.app import main

if __name__ == "__main__":
    main()
