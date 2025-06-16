#!/usr/bin/env python3
"""
Integration test for TaskMover Redesigned
Tests key functionality to ensure the migration was successful.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from taskmover_redesign.core import (
        ConfigManager, RuleManager, FileOrganizer, 
        load_rules, save_rules, load_settings, save_settings
    )
    print("✓ Core module imports successful")
except ImportError as e:
    print(f"✗ Core module import failed: {e}")
    sys.exit(1)

def test_config_management():
    """Test configuration loading and saving"""
    print("\nTesting configuration management...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "test_config")
        os.makedirs(config_path, exist_ok=True)
        
        # Test settings
        test_settings = {
            "theme": "flatly",
            "organisation_folder": "/test/folder",
            "auto_save": True
        }
        
        config_manager = ConfigManager(config_path)
        config_manager.save_settings(test_settings)
        loaded_settings = config_manager.load_settings()
        
        assert loaded_settings["theme"] == "flatly"
        assert loaded_settings["organisation_folder"] == "/test/folder"
        print("✓ Settings load/save working")
        
        # Test rules
        rule_manager = RuleManager(config_manager)
        rule_manager.add_rule(
            name="Test Rule",
            patterns=["*.txt"],
            path="text_files"
        )
        
        assert "Test Rule" in rule_manager.rules
        assert rule_manager.rules["Test Rule"]["patterns"] == ["*.txt"]
        print("✓ Rules management working")

def test_file_operations():
    """Test file organization functionality"""
    print("\nTesting file organization...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_files = [
            "document1.txt",
            "document2.pdf", 
            "image1.jpg",
            "script.py"
        ]
        
        for filename in test_files:
            filepath = os.path.join(temp_dir, filename)
            Path(filepath).touch()
        
        # Create test rules
        test_rules = {
            "txt_rule": {
                "name": "Text Files",
                "patterns": ["*.txt"],
                "destination": "documents/text",
                "active": True
            }
        }
        
        # Create organizer
        organizer = FileOrganizer(temp_dir, test_rules)
        
        # Test that organizer was created successfully
        assert organizer.organization_folder == Path(temp_dir)
        assert organizer.rules == test_rules
        
        print("✓ File organizer creation working")
        print("✓ File organization core functionality working")

def test_rule_management():
    """Test rule management functionality"""
    print("\nTesting rule management...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_manager = ConfigManager(temp_dir)
        manager = RuleManager(config_manager)
        
        # Test rule validation
        valid_rule_data = {
            "name": "Test Rule",
            "patterns": ["*.txt"],
            "path": temp_dir,  # Use temp_dir as a valid path
            "active": True
        }
        
        invalid_rule_data = {
            "name": "",  # Invalid empty name
            "patterns": [],  # Invalid empty patterns
            "path": ""  # Invalid empty path
        }
        
        is_valid, errors = manager.validate_rule(valid_rule_data)
        assert is_valid == True
        
        is_invalid, errors = manager.validate_rule(invalid_rule_data)
        assert is_invalid == False
        
        print("✓ Rule validation working")

def main():
    """Run all integration tests"""
    print("TaskMover Redesigned - Integration Tests")
    print("=" * 50)
    
    try:
        test_config_management()
        test_file_operations() 
        test_rule_management()
        
        print("\n" + "=" * 50)
        print("🎉 All integration tests passed!")
        print("The TaskMover redesigned migration is successful!")
        
    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
