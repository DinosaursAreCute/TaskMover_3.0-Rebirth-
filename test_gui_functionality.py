#!/usr/bin/env python3
"""Test the GUI test runner functionality."""

try:
    from tests.simple_test_gui import SimpleTestGUI
    print('✅ SimpleTestGUI can be imported')
    
    # Test theme colors
    gui = SimpleTestGUI()
    print('✅ SimpleTestGUI can be instantiated')
    
    # Test theme application
    gui.dark_mode = True
    gui.apply_theme()
    print('✅ Dark mode theme can be applied')
    
    gui.root.destroy()
    print('✅ GUI cleanup successful')
    
    print('\n🎉 All GUI tests passed! Ready to launch.')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
