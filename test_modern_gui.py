#!/usr/bin/env python3
"""Test the modern GUI functionality."""

try:
    from tests.modern_test_gui import ModernTestRunner
    print('✅ Modern Test Runner can be imported')
    
    # Test instantiation  
    app = ModernTestRunner()
    print('✅ Modern Test Runner instantiated successfully')
    
    # Test theme application
    app.apply_theme()
    print('✅ Theme applied successfully')
    
    # Test suite setup
    print(f'✅ {len(app.test_suites)} test suites configured')
    
    # Clean up
    app.root.destroy()
    print('✅ All tests passed - Modern GUI ready!')
    print()
    print('🚀 To launch the Modern Test Runner:')
    print('   python tests/modern_test_gui.py')
    print('   OR')  
    print('   launch_test_gui.bat')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
