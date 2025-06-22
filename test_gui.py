#!/usr/bin/env python3
"""
Test script to verify TaskMover GUI can start and close
"""

import threading
import time

def test_gui():
    try:
        print("Testing TaskMover GUI startup...")
        
        from taskmover_redesign.app import TaskMoverApp
        print("✅ App import successful")
        
        app = TaskMoverApp()
        print("✅ App instantiation successful")
        
        # Start a timer to close the app after 2 seconds
        def close_app():
            time.sleep(2)
            print("⏰ Auto-closing application...")
            app.root.quit()
        
        timer_thread = threading.Thread(target=close_app, daemon=True)
        timer_thread.start()
        
        print("🚀 Starting GUI mainloop...")
        app.root.mainloop()
        print("✅ GUI started and closed successfully")
        print("🎉 All GUI tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gui()
