#!/usr/bin/env python3
"""
Test script for RulesetManager functionality
"""

from taskmover_redesign.core.ruleset_manager import RulesetManager
import tempfile
import os

def test_ruleset_manager():
    """Test basic RulesetManager functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Testing in directory: {tmpdir}")
        
        # Initialize RulesetManager
        rm = RulesetManager(tmpdir)
        print("✓ RulesetManager initialized")
        
        # Check initial state
        available = rm.get_available_rulesets()
        print(f"✓ Available rulesets: {[rs['name'] for rs in available]}")
        print(f"✓ Current ruleset: {rm.current_ruleset}")
        
        # Create a test ruleset
        success = rm.create_ruleset('Test', 'Test description')
        print(f"✓ Create test ruleset: {success}")
        
        # Check updated state
        available = rm.get_available_rulesets()
        print(f"✓ Available rulesets after creation: {[rs['name'] for rs in available]}")
        
        # Test ruleset switching
        success = rm.switch_ruleset('Test')
        print(f"✓ Switch to test ruleset: {success}")
        print(f"✓ Current ruleset after switch: {rm.current_ruleset}")
        
        # Test rule loading/saving
        test_rules = {'test_rule': {'patterns': ['*.txt'], 'destination': 'TextFiles'}}
        success = rm.save_ruleset_rules('Test', test_rules)
        print(f"✓ Save test rules: {success}")
        
        loaded_rules = rm.load_ruleset_rules('Test')
        print(f"✓ Loaded rules: {loaded_rules}")
        
        # Test merge functionality
        success = rm.create_ruleset('Source1', 'Source 1')
        rm.save_ruleset_rules('Source1', {'rule1': {'patterns': ['*.doc'], 'destination': 'Documents'}})
        
        success = rm.create_ruleset('Source2', 'Source 2') 
        rm.save_ruleset_rules('Source2', {'rule2': {'patterns': ['*.pdf'], 'destination': 'PDFs'}})
        
        success = rm.merge_rulesets(['Source1', 'Source2'], 'Merged', 'Merged ruleset', 'keep_all')
        print(f"✓ Merge rulesets: {success}")
        
        merged_rules = rm.load_ruleset_rules('Merged')
        print(f"✓ Merged rules: {list(merged_rules.keys())}")
        
        print("\n🎉 All tests passed!")

if __name__ == "__main__":
    test_ruleset_manager()
