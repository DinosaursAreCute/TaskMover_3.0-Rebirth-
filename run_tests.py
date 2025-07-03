#!/usr/bin/env python3
"""
TaskMover Comprehensive Test Runner
==================================

Runs all test suites with reporting and dark mode GUI support.
"""

import sys
import os
import subprocess
import json
from pathlib import Path
import argparse
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_test_suite(suite_name: str, test_files: list, verbose: bool = False) -> dict:
    """Run a test suite and return results."""
    print(f"\n{'='*20} {suite_name} {'='*20}")
    
    results = {
        'suite': suite_name,
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'errors': 0,
        'skipped': 0,
        'duration': 0,
        'files': []
    }
    
    start_time = time.time()
    
    for test_file in test_files:
        test_path = project_root / "tests" / test_file
        
        if not test_path.exists():
            print(f"⚠️  Test file not found: {test_file}")
            continue
        
        print(f"Running {test_file}...")
        
        try:
            # Run the test file
            cmd = [sys.executable, "-m", "unittest", f"tests.{test_file.replace('/', '.').replace('.py', '')}"]
            
            if verbose:
                cmd.append("-v")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=project_root,
                timeout=60  # 60 second timeout per test file
            )
            
            # Parse results (simplified)
            output = result.stderr + result.stdout
            
            file_result = {
                'file': test_file,
                'returncode': result.returncode,
                'output': output,
                'passed': result.returncode == 0
            }
            
            results['files'].append(file_result)
            
            if result.returncode == 0:
                print(f"  ✅ {test_file} - PASSED")
                results['passed'] += 1
            else:
                print(f"  ❌ {test_file} - FAILED")
                results['failed'] += 1
                if verbose:
                    print(f"    Output: {output[:200]}...")
            
            results['total_tests'] += 1
            
        except subprocess.TimeoutExpired:
            print(f"  ⏱️  {test_file} - TIMEOUT")
            results['errors'] += 1
            results['total_tests'] += 1
            
        except Exception as e:
            print(f"  💥 {test_file} - ERROR: {e}")
            results['errors'] += 1
            results['total_tests'] += 1
    
    results['duration'] = time.time() - start_time
    
    return results


def load_test_configuration():
    """Load test configuration from testcases.json."""
    config_path = project_root / "tests" / "testcases.json"
    
    if not config_path.exists():
        return {
            "test_suites": {
                "unit_tests": {
                    "description": "Unit tests",
                    "test_files": ["unit/test_*.py"]
                },
                "integration_tests": {
                    "description": "Integration tests", 
                    "test_files": ["integration/test_*.py"]
                }
            }
        }
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading test configuration: {e}")
        return {"test_suites": {}}


def run_gui_test_runner():
    """Launch the GUI test runner."""
    try:
        # Try simple GUI first
        from tests.simple_test_gui import SimpleTestGUI
        
        print("Launching Simple GUI Test Runner with Dark Mode...")
        app = SimpleTestGUI()
        app.run()
        return True
        
    except ImportError:
        # Fall back to complex GUI
        try:
            from tests.test_gui_runner import TestGUIRunner
            
            print("Launching Advanced GUI Test Runner...")
            app = TestGUIRunner()
            app.run()
            return True
            
        except ImportError as e:
            print(f"GUI Test Runner not available: {e}")
            print("Install required dependencies: pip install tkinter")
            return False
    except Exception as e:
        print(f"Error running GUI Test Runner: {e}")
        return False


def generate_test_report(all_results: list, output_path: str = None):
    """Generate a comprehensive test report."""
    total_suites = len(all_results)
    total_tests = sum(r['total_tests'] for r in all_results)
    total_passed = sum(r['passed'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)
    total_errors = sum(r['errors'] for r in all_results)
    total_duration = sum(r['duration'] for r in all_results)
    
    report = f"""
TaskMover Test Report
{'='*50}

SUMMARY:
--------
Test Suites: {total_suites}
Total Tests: {total_tests}
Passed:      {total_passed} ({(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%)
Failed:      {total_failed}
Errors:      {total_errors}
Duration:    {total_duration:.2f}s

DETAILED RESULTS:
-----------------
"""
    
    for result in all_results:
        report += f"\n{result['suite']}:\n"
        report += f"  Tests: {result['total_tests']}\n"
        report += f"  Passed: {result['passed']}\n"
        report += f"  Failed: {result['failed']}\n"
        report += f"  Errors: {result['errors']}\n"
        report += f"  Duration: {result['duration']:.2f}s\n"
        
        for file_result in result['files']:
            status = "✅ PASS" if file_result['passed'] else "❌ FAIL"
            report += f"    {status} {file_result['file']}\n"
    
    # Overall status
    overall_success = total_failed == 0 and total_errors == 0
    report += f"\nOVERALL: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}\n"
    
    # Print to console
    print(report)
    
    # Save to file if specified
    if output_path:
        try:
            with open(output_path, 'w') as f:
                f.write(report)
            print(f"\nReport saved to: {output_path}")
        except Exception as e:
            print(f"Error saving report: {e}")
    
    return overall_success


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description="TaskMover Test Runner")
    parser.add_argument("--gui", action="store_true", help="Launch GUI test runner")
    parser.add_argument("--suite", help="Run specific test suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--report", help="Generate report to file")
    parser.add_argument("--list", action="store_true", help="List available test suites")
    
    args = parser.parse_args()
    
    # Load test configuration
    config = load_test_configuration()
    test_suites = config.get("test_suites", {})
    
    if args.list:
        print("Available test suites:")
        for suite_name, suite_info in test_suites.items():
            print(f"  {suite_name}: {suite_info.get('description', 'No description')}")
        return
    
    if args.gui:
        success = run_gui_test_runner()
        sys.exit(0 if success else 1)
    
    print("TaskMover Test Runner")
    print("=" * 50)
    
    # Determine which suites to run
    if args.suite:
        if args.suite not in test_suites:
            print(f"Error: Unknown test suite '{args.suite}'")
            print("Available suites:", list(test_suites.keys()))
            sys.exit(1)
        suites_to_run = {args.suite: test_suites[args.suite]}
    else:
        suites_to_run = test_suites
    
    # Run test suites
    all_results = []
    
    for suite_name, suite_info in suites_to_run.items():
        test_files = suite_info.get('test_files', [])
        result = run_test_suite(suite_name, test_files, args.verbose)
        all_results.append(result)
    
    # Generate report
    overall_success = generate_test_report(all_results, args.report)
    
    # Exit with appropriate code
    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()
