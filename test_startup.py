#!/usr/bin/env python3
"""
Test script to verify TaskMover can start normally
"""

try:
    print("Testing TaskMover startup...")
    
    from taskmover_redesign.app import TaskMoverApp
    print("✅ App import successful")
    
    app = TaskMoverApp()
    print("✅ App instantiation successful")
    print("✅ Application can start normally")
    
    # Don't start the main loop, just verify it can be created
    print("🎉 All startup tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
