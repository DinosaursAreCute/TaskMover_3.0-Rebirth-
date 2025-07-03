#!/usr/bin/env python3
"""
Test Runner Demo
================

Simple demo to verify the professional test runner works with colored output,
failed tests display, and summary generation.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the test runner
try:
    from tests.professional_test_runner import ProfessionalTestRunner
    
    print("Starting Professional Test Runner...")
    print("Features to test:")
    print("- ✅ Colored output in 'All Output' tab")
    print("- ❌ Failed tests in 'Failed Tests' tab")
    print("- 📊 Summary in 'Summary' tab")
    print("\nLaunching GUI...")
    
    app = ProfessionalTestRunner()
    app.run()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
