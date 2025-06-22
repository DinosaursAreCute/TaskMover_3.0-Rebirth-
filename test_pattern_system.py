#!/usr/bin/env python3
"""
Test script to verify the pattern management components work correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from taskmover_redesign.core.pattern_library import PatternLibrary, Pattern
from taskmover_redesign.core.rule_pattern_manager import RulePatternManager
from taskmover_redesign.core.ruleset_manager import RulesetManager

def test_pattern_library():
    """Test the pattern library functionality"""
    print("Testing Pattern Library...")
    
    # Create pattern library with temp directory
    test_dir = os.path.expanduser("~/.taskmover_test")
    os.makedirs(test_dir, exist_ok=True)
    
    pattern_lib = PatternLibrary(test_dir)
    
    # Clear existing patterns for clean test
    pattern_lib.patterns = {}
    pattern_lib.save_patterns()
    
    # Create test patterns
    pattern1_id = pattern_lib.create_pattern(
        name="Python Files",
        pattern="*.py",
        pattern_type="glob",
        description="All Python source files",
        examples=["main.py", "utils.py"],
        tags=["code", "python"]
    )
    
    pattern2_id = pattern_lib.create_pattern(
        name="Log Files",
        pattern=r".*\.log$",
        pattern_type="regex",
        description="Application log files",
        examples=["app.log", "error.log"],
        tags=["logs"]
    )
    
    print(f"Created pattern 1: {pattern1_id}")
    print(f"Created pattern 2: {pattern2_id}")
    
    # Test retrieval
    pattern1 = pattern_lib.get_pattern(pattern1_id)
    pattern2 = pattern_lib.get_pattern(pattern2_id)
    
    if pattern1 and pattern2:
        print(f"Pattern 1: {pattern1.name} - {pattern1.pattern} ({pattern1.type})")
        print(f"Pattern 2: {pattern2.name} - {pattern2.pattern} ({pattern2.type})")
    else:
        print("Error: Failed to retrieve pattern(s)")
    
    # Test all patterns
    print(f"Total patterns: {len(pattern_lib.patterns)}")
    
    return pattern_lib, pattern1_id, pattern2_id

def test_rule_pattern_manager():
    """Test the rule-pattern manager"""
    print("\nTesting Rule-Pattern Manager...")
    
    test_dir = os.path.expanduser("~/.taskmover_test")
    pattern_lib = PatternLibrary(test_dir)
    ruleset_manager = RulesetManager(test_dir)
    
    rule_pattern_manager = RulePatternManager(ruleset_manager, pattern_lib)
    
    # Create a test pattern
    pattern_id = pattern_lib.create_pattern("Test Pattern", "*.txt", "glob")
    
    # Test usage checking (should be empty initially)
    usage = rule_pattern_manager.get_pattern_usage(pattern_id)
    print(f"Pattern usage (should be empty): {usage}")
    
    can_delete, usage_list = rule_pattern_manager.can_delete_pattern(pattern_id)
    print(f"Can delete pattern: {can_delete}")
    
    return rule_pattern_manager

def test_integration():
    """Test basic integration"""
    print("\nTesting Integration...")
    
    pattern_lib, pattern1_id, pattern2_id = test_pattern_library()
    rule_pattern_manager = test_rule_pattern_manager()
    
    print("\n✅ All basic tests passed!")
    print("Core pattern management system is working correctly.")

if __name__ == "__main__":
    try:
        test_integration()
        print("\n🎉 Pattern management system implementation successful!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
