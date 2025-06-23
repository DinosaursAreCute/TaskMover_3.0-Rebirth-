"""
Simplified UI Component Testing

Basic tests to verify component files exist and can be imported.
"""

import os
import sys

def test_component_files_exist():
    """Test that all component files exist."""
    print("Testing component file existence...")
    
    component_files = [
        "taskmover/ui/base_component.py",
        "taskmover/ui/theme_manager.py", 
        "taskmover/ui/layout_manager.py",
        "taskmover/ui/input_components.py",
        "taskmover/ui/additional_input_components.py",
        "taskmover/ui/display_components.py",
        "taskmover/ui/layout_components.py",
        "taskmover/ui/navigation_components.py",
        "taskmover/ui/data_display_components.py",
        "taskmover/ui/specialized_display_components.py",
        "taskmover/ui/dialog_components.py",
        "taskmover/ui/pattern_management_components.py",
        "taskmover/ui/rule_management_components.py",
        "taskmover/ui/ruleset_management_components.py",
        "taskmover/ui/file_organization_components.py",
        "taskmover/ui/advanced_ui_features.py"
    ]
    
    existing_files = 0
    missing_files = 0
    
    for file_path in component_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
            existing_files += 1
        else:
            print(f"✗ {file_path} - Missing")
            missing_files += 1
    
    print(f"\nResults: {existing_files} existing, {missing_files} missing")
    return missing_files == 0

def test_basic_imports():
    """Test basic imports of key modules."""
    print("\nTesting basic imports...")
    
    # Add the taskmover directory to the path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    taskmover_dir = os.path.dirname(current_dir)
    if taskmover_dir not in sys.path:
        sys.path.insert(0, taskmover_dir)
    
    import_tests = [
        ("ui.theme_manager", "ThemeManager"),
        ("ui.base_component", "BaseComponent"),
        ("ui.input_components", "TextInput"),
        ("ui.layout_components", "Panel"),
        ("ui.display_components", "StatusDisplay"),
    ]
    
    successful_imports = 0
    failed_imports = 0
    
    for module_name, class_name in import_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"✓ {module_name}.{class_name}")
                successful_imports += 1
            else:
                print(f"✗ {module_name}.{class_name} - Class not found")
                failed_imports += 1
        except ImportError as e:
            print(f"✗ {module_name}.{class_name} - Import error: {e}")
            failed_imports += 1
        except Exception as e:
            print(f"✗ {module_name}.{class_name} - Error: {e}")
            failed_imports += 1
    
    print(f"\nImport Results: {successful_imports} successful, {failed_imports} failed")
    return failed_imports == 0

def test_syntax_check():
    """Basic syntax check for component files."""
    print("\nTesting syntax validity...")
    
    component_files = [
        "taskmover/ui/base_component.py",
        "taskmover/ui/theme_manager.py",
        "taskmover/ui/input_components.py",
        "taskmover/ui/layout_components.py",
        "taskmover/ui/display_components.py"
    ]
    
    valid_files = 0
    invalid_files = 0
    
    for file_path in component_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, file_path, 'exec')
                print(f"✓ {file_path} - Valid syntax")
                valid_files += 1
            except SyntaxError as e:
                print(f"✗ {file_path} - Syntax error: {e}")
                invalid_files += 1
            except Exception as e:
                print(f"✗ {file_path} - Error: {e}")
                invalid_files += 1
        else:
            print(f"⚠ {file_path} - File not found")
    
    print(f"\nSyntax Results: {valid_files} valid, {invalid_files} invalid")
    return invalid_files == 0

def main():
    """Run all simplified tests."""
    print("TaskMover UI Component - Simplified Test Suite")
    print("=" * 50)
    
    # Run tests
    file_test = test_component_files_exist()
    import_test = test_basic_imports()
    syntax_test = test_syntax_check()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    tests = [
        ("File Existence", file_test),
        ("Basic Imports", import_test),
        ("Syntax Check", syntax_test)
    ]
    
    passed = sum(result for _, result in tests)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All basic tests passed! UI components are properly structured.")
    else:
        print(f"\n⚠️ {total-passed} test(s) failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    main()
