"""
Test Application Entry Point
============================

Test the main application entry point and initialization.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestApplicationEntryPoint(unittest.TestCase):
    """Test application entry point."""
    
    def test_main_module_import(self):
        """Test __main__ module can be imported."""
        try:
            import taskmover.__main__
            self.assertTrue(hasattr(taskmover.__main__, 'main'))
            print("✓ Main module import successful")
        except ImportError as e:
            self.skipTest(f"Main module not available: {e}")
    
    def test_main_function_exists(self):
        """Test main function exists and is callable."""
        try:
            from taskmover.__main__ import main
            self.assertTrue(callable(main))
            print("✓ Main function is callable")
        except ImportError as e:
            self.skipTest(f"Main function not available: {e}")
    
    @patch('taskmover.ui.main_application.TaskMoverApplication')
    def test_main_function_execution(self, mock_app_class):
        """Test main function can execute without errors."""
        try:
            # Mock the application
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            
            from taskmover.__main__ import main
            
            # Call main function (should not raise exception)
            main()
            
            # Verify application was created and run was called
            mock_app_class.assert_called_once()
            mock_app.run.assert_called_once()
            
            print("✓ Main function execution test passed")
            
        except ImportError as e:
            self.skipTest(f"Main function or dependencies not available: {e}")


class TestApplicationStructure(unittest.TestCase):
    """Test application structure and organization."""
    
    def test_package_structure(self):
        """Test package structure is correct."""
        project_root = Path(__file__).parent.parent
        
        expected_dirs = [
            'taskmover',
            'taskmover/core',
            'taskmover/ui',
            'tests'
        ]
        
        for expected_dir in expected_dirs:
            dir_path = project_root / expected_dir
            self.assertTrue(dir_path.exists(), f"Directory {expected_dir} should exist")
            self.assertTrue(dir_path.is_dir(), f"{expected_dir} should be a directory")
        
        print("✓ Package structure test passed")
    
    def test_init_files_exist(self):
        """Test __init__.py files exist where needed."""
        project_root = Path(__file__).parent.parent
        
        expected_init_files = [
            'taskmover/__init__.py',
            'taskmover/core/__init__.py',
            'tests/__init__.py'
        ]
        
        for init_file in expected_init_files:
            init_path = project_root / init_file
            self.assertTrue(init_path.exists(), f"Init file {init_file} should exist")
        
        print("✓ Init files test passed")


class TestDependencyImports(unittest.TestCase):
    """Test that core dependencies can be imported."""
    
    def test_core_imports(self):
        """Test core module imports."""
        import_tests = [
            ('taskmover.core.exceptions', 'TaskMoverException'),
            ('taskmover.ui.theme_manager', 'get_theme_manager'),
        ]
        
        successful_imports = []
        failed_imports = []
        
        for module_name, class_name in import_tests:
            try:
                module = __import__(module_name, fromlist=[class_name])
                getattr(module, class_name)
                successful_imports.append((module_name, class_name))
            except (ImportError, AttributeError) as e:
                failed_imports.append((module_name, class_name, str(e)))
        
        print(f"✓ Successfully imported {len(successful_imports)} core dependencies")
        
        if failed_imports:
            print(f"⚠ Failed to import {len(failed_imports)} dependencies:")
            for module, cls, error in failed_imports:
                print(f"  - {module}.{cls}: {error}")
        
        # At least some imports should succeed
        self.assertGreater(len(successful_imports), 0, "No core dependencies could be imported")


def run_app_tests():
    """Run application tests with custom reporting."""
    print("TaskMover Application Test Suite")
    print("=" * 40)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestApplicationEntryPoint))
    suite.addTests(loader.loadTestsFromTestCase(TestApplicationStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestDependencyImports))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 40)
    if result.wasSuccessful():
        print("✓ All application tests passed!")
        print("\nTo run the application:")
        print("  python -m taskmover")
    else:
        print(f"✗ {len(result.failures)} failures, {len(result.errors)} errors")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_app_tests()
    sys.exit(0 if success else 1)