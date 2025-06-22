#!/usr/bin/env python3
"""
Test all UI imports
"""

try:
    from taskmover_redesign.ui.rule_components import add_rule_button, edit_rule, enable_all_rules, disable_all_rules
    print("✅ rule_components imports successful")
    
    from taskmover_redesign.ui.settings_components import open_settings_window
    print("✅ settings_components imports successful")
    
    from taskmover_redesign.ui.pattern_tab import PatternManagementTab
    print("✅ pattern_tab imports successful")
    
    from taskmover_redesign.ui.components import Tooltip, ProgressDialog, ConfirmDialog
    print("✅ components imports successful")
    
    print("🎉 All UI imports successful!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
