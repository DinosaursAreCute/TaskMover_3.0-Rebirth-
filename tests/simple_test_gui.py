#!/usr/bin/env python3
"""
Simple GUI Test Runner with Dark Mode
=====================================

A simplified but functional GUI test runner for TaskMover with dark mode support.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os
import subprocess
import threading
import io
import importlib.util
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SimpleTestGUI:
    """Simple GUI test runner with dark mode."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TaskMover Test Runner")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)
        
        # Configure window icon and styling
        try:
            self.root.iconbitmap(default='')  # Remove default icon
        except:
            pass
        
        # Theme state - dark mode by default
        self.dark_mode = True
        self.running_tests = False
        
        # Enhanced color scheme
        self.colors = {
            'light': {
                'bg': '#f8f9fa',
                'fg': '#212529',
                'surface': '#ffffff',
                'primary': '#0d6efd',
                'success': '#198754',
                'warning': '#ffc107',
                'danger': '#dc3545',
                'secondary': '#6c757d',
                'button_bg': '#e9ecef',
                'text_bg': '#ffffff',
                'border': '#dee2e6',
                'hover': '#e9ecef'
            },
            'dark': {
                'bg': '#0d1117',
                'fg': '#f0f6fc',
                'surface': '#161b22',
                'primary': '#58a6ff',
                'success': '#3fb950',
                'warning': '#d29922',
                'danger': '#f85149',
                'secondary': '#8b949e',
                'button_bg': '#21262d',
                'text_bg': '#0d1117',
                'border': '#30363d',
                'hover': '#262c36'
            }
        }
        
        self.setup_ui()
        self.apply_theme()
        
        # Force initial theme application after a short delay
        self.root.after(100, self.apply_theme)
    
    def setup_ui(self):
        """Setup the user interface with improved usability."""
        # Main container with padding
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Header section
        self.setup_header(main_frame)
        
        # Test selection section
        self.setup_test_controls(main_frame)
        
        # Status and progress section
        self.setup_status_section(main_frame)
        
        # Results section
        self.setup_results_section(main_frame)
        
        # Store widget references for theming
        self.collect_widgets_for_theming(main_frame)
    
    def setup_header(self, parent):
        """Setup the header section."""
        header_frame = tk.Frame(parent)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title and description
        title_frame = tk.Frame(header_frame)
        title_frame.pack(side="left", fill="x", expand=True)
        
        self.title_label = tk.Label(
            title_frame,
            text="TaskMover Test Runner",
            font=("Segoe UI", 18, "bold")
        )
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = tk.Label(
            title_frame,
            text="Run and monitor TaskMover test suites",
            font=("Segoe UI", 10)
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Theme toggle (optional)
        self.theme_button = tk.Button(
            header_frame,
            text="☀️ Light",
            command=self.toggle_theme,
            font=("Segoe UI", 9),
            padx=15,
            pady=5,
            relief="flat",
            cursor="hand2"
        )
        self.theme_button.pack(side="right", pady=5)
    
    def setup_test_controls(self, parent):
        """Setup test selection and control section."""
        controls_frame = tk.LabelFrame(
            parent, 
            text=" Test Selection ", 
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=10
        )
        controls_frame.pack(fill="x", pady=(0, 15))
        
        # Test suite selection
        selection_frame = tk.Frame(controls_frame)
        selection_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            selection_frame, 
            text="Test Suite:", 
            font=("Segoe UI", 10)
        ).pack(side="left", padx=(0, 10))
        
        self.test_var = tk.StringVar(value="Quick Test")
        self.test_combo = ttk.Combobox(
            selection_frame,
            textvariable=self.test_var,
            values=[
                "Quick Test",
                "Safe Mode Tests", 
                "Unit Tests",
                "Integration Tests", 
                "UI Tests",
                "All Tests"
            ],
            state="readonly",
            font=("Segoe UI", 10),
            width=20
        )
        self.test_combo.pack(side="left", padx=(0, 20))
        
        # Action buttons
        button_frame = tk.Frame(selection_frame)
        button_frame.pack(side="right")
        
        self.run_button = tk.Button(
            button_frame,
            text="▶ Run Tests",
            command=self.run_tests,
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2"
        )
        self.run_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = tk.Button(
            button_frame,
            text="⏹ Stop",
            command=self.stop_tests,
            font=("Segoe UI", 10),
            padx=15,
            pady=8,
            state="disabled",
            relief="flat",
            cursor="hand2"
        )
        self.stop_button.pack(side="left")
    
    def setup_status_section(self, parent):
        """Setup status and progress section."""
        status_frame = tk.Frame(parent)
        status_frame.pack(fill="x", pady=(0, 15))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            status_frame, 
            mode="indeterminate",
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        # Status label
        self.status_label = tk.Label(
            status_frame, 
            text="Ready to run tests",
            font=("Segoe UI", 10),
            anchor="e"
        )
        self.status_label.pack(side="right")
    
    def setup_results_section(self, parent):
        """Setup results display section."""
        results_frame = tk.LabelFrame(
            parent, 
            text=" Test Results ", 
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=10
        )
        results_frame.pack(fill="both", expand=True)
        
        # Summary cards
        self.setup_summary_cards(results_frame)
        
        # Output area
        self.setup_output_area(results_frame)
    
    def setup_summary_cards(self, parent):
        """Setup test summary cards."""
        summary_frame = tk.Frame(parent)
        summary_frame.pack(fill="x", pady=(0, 15))
        
        self.summary_cards = {}
        card_configs = [
            ("total", "Total", "#6c757d"),
            ("passed", "Passed", "#3fb950"),
            ("failed", "Failed", "#f85149"),
            ("errors", "Errors", "#d29922")
        ]
        
        for i, (key, label, color) in enumerate(card_configs):
            card_frame = tk.Frame(summary_frame, relief="solid", bd=1, padx=10, pady=8)
            card_frame.pack(side="left", fill="x", expand=True, padx=(0, 10) if i < 3 else (0, 0))
            
            tk.Label(
                card_frame, 
                text=label, 
                font=("Segoe UI", 9),
                fg=color
            ).pack()
            
            count_label = tk.Label(
                card_frame, 
                text="0", 
                font=("Segoe UI", 16, "bold")
            )
            count_label.pack()
            
            self.summary_cards[key] = count_label
    
    def setup_output_area(self, parent):
        """Setup the test output area."""
        output_frame = tk.Frame(parent)
        output_frame.pack(fill="both", expand=True)
        
        # Output text with scrollbar
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=18,
            font=("Consolas", 10),
            wrap=tk.WORD,
            relief="solid",
            bd=1,
            padx=10,
            pady=10
        )
        self.output_text.pack(fill="both", expand=True)
        
        # Configure text tags for colored output
        self.setup_text_tags()
    
    def setup_text_tags(self):
        """Setup text tags for colored output."""
        theme = self.colors['dark'] if self.dark_mode else self.colors['light']
        
        self.output_text.tag_configure("success", foreground=theme['success'])
        self.output_text.tag_configure("error", foreground=theme['danger'])
        self.output_text.tag_configure("warning", foreground=theme['warning'])
        self.output_text.tag_configure("info", foreground=theme['primary'])
        self.output_text.tag_configure("header", font=("Consolas", 10, "bold"))
    
    def collect_widgets_for_theming(self, main_frame):
        """Collect all widgets for theme application."""
        self.widgets = {
            'frames': [],
            'labels': [self.title_label, self.subtitle_label, self.status_label] + list(self.summary_cards.values()),
            'buttons': [self.theme_button, self.run_button, self.stop_button],
            'text': [self.output_text]
        }
        
        # Recursively collect frames
        def collect_frames(widget):
            if isinstance(widget, (tk.Frame, tk.LabelFrame)):
                self.widgets['frames'].append(widget)
            for child in widget.winfo_children():
                collect_frames(child)
        
        collect_frames(main_frame)
    
    def apply_theme(self):
        """Apply current theme to all widgets with modern styling."""
        theme = self.colors['dark'] if self.dark_mode else self.colors['light']
        
        # Configure root window
        self.root.configure(bg=theme['bg'])
        
        # Apply theme recursively to all widgets
        def configure_widget_theme(widget):
            try:
                widget_class = widget.winfo_class()
                
                if widget_class in ['Frame', 'Toplevel']:
                    widget.configure(bg=theme['bg'])
                elif widget_class == 'Label':
                    widget.configure(bg=theme['bg'], fg=theme['fg'])
                elif widget_class == 'LabelFrame':
                    widget.configure(
                        bg=theme['bg'], 
                        fg=theme['fg'],
                        highlightbackground=theme['border'],
                        highlightthickness=1
                    )
                elif widget_class == 'Button':
                    if hasattr(widget, 'cget') and 'hand2' in str(widget.cget('cursor')):
                        # Style buttons with hand cursor (action buttons)
                        if widget == self.run_button:
                            widget.configure(
                                bg=theme['primary'],
                                fg='white',
                                activebackground=theme['hover'],
                                activeforeground='white',
                                highlightthickness=0,
                                bd=0
                            )
                        elif widget == self.stop_button:
                            widget.configure(
                                bg=theme['danger'],
                                fg='white',
                                activebackground=theme['hover'],
                                activeforeground='white',
                                highlightthickness=0,
                                bd=0
                            )
                        else:
                            widget.configure(
                                bg=theme['button_bg'],
                                fg=theme['fg'],
                                activebackground=theme['hover'],
                                activeforeground=theme['fg'],
                                highlightthickness=0,
                                bd=0
                            )
                elif widget_class == 'Text':
                    widget.configure(
                        bg=theme['text_bg'],
                        fg=theme['fg'],
                        insertbackground=theme['fg'],
                        selectbackground=theme['primary'],
                        selectforeground='white',
                        highlightcolor=theme['primary'],
                        highlightthickness=1,
                        bd=0
                    )
                
                # Recursively apply to children
                for child in widget.winfo_children():
                    configure_widget_theme(child)
                    
            except (tk.TclError, AttributeError):
                pass
        
        # Apply theme to entire widget tree
        configure_widget_theme(self.root)
        
        # Configure ttk widgets with modern styling
        style = ttk.Style()
        try:
            if self.dark_mode:
                style.theme_use('clam')
                style.configure('TCombobox', 
                    fieldbackground=theme['surface'],
                    background=theme['button_bg'],
                    foreground=theme['fg'],
                    arrowcolor=theme['fg'],
                    bordercolor=theme['border'],
                    lightcolor=theme['surface'],
                    darkcolor=theme['surface'])
                style.configure('Custom.Horizontal.TProgressbar',
                    background=theme['primary'],
                    troughcolor=theme['surface'],
                    bordercolor=theme['border'],
                    lightcolor=theme['primary'],
                    darkcolor=theme['primary'])
            else:
                style.theme_use('winnative')
        except tk.TclError:
            pass
        
        # Update text tags for colored output
        self.setup_text_tags()
        
        # Update theme button text
        self.theme_button.configure(
            text="☀️ Light" if self.dark_mode else "🌙 Dark"
        )
        
        # Update summary card styling
        for key, card in self.summary_cards.items():
            parent = card.master
            parent.configure(
                bg=theme['surface'],
                highlightbackground=theme['border'],
                highlightthickness=1
            )
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
    
    def run_tests(self):
        """Run the selected test suite."""
        if self.running_tests:
            return
        
        self.running_tests = True
        self.run_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.progress.start()
        
        # Clear previous results
        self.clear_results()
        
        # Start tests in thread
        test_thread = threading.Thread(target=self.run_tests_thread)
        test_thread.daemon = True
        test_thread.start()
    
    def run_tests_thread(self):
        """Run tests in background thread."""
        try:
            test_suite = self.test_var.get()
            self.update_status("Preparing tests...")
            
            # Determine test command
            if test_suite == "Quick Test":
                self.run_quick_test()
            elif test_suite == "Safe Mode Tests":
                self.run_safe_mode_tests()
            elif test_suite == "Unit Tests":
                self.run_test_directory(project_root / "tests" / "unit")
            elif test_suite == "Integration Tests":
                self.run_test_directory(project_root / "tests" / "integration")
            elif test_suite == "UI Tests":
                self.run_specific_tests(["test_ui.py", "test_app.py"])
            else:  # All Tests
                self.run_all_test_files()
                
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.append_output(f"Error running tests: {str(e)}\\n")
        finally:
            self.root.after(0, self.test_complete)
    
    def run_quick_test(self):
        """Run a quick import and basic functionality test."""
        self.update_status("Running quick test...")
        
        test_script = f'''
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(r"{project_root}")
sys.path.insert(0, str(project_root))

print("=== TaskMover Quick Test ===")
print(f"Python version: {{sys.version}}")
print(f"Project root: {{project_root}}")
print(f"Python path: {{sys.path[:3]}}...")  # Show first few entries
print()

test_results = {{
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": 0
}}

def run_test(name, test_func):
    test_results["total"] += 1
    try:
        test_func()
        print(f"✅ {{name}}")
        test_results["passed"] += 1
        return True
    except ImportError as e:
        print(f"❌ {{name}} - Import Error: {{e}}")
        test_results["failed"] += 1
        return False
    except Exception as e:
        print(f"❌ {{name}} - Error: {{e}}")
        test_results["errors"] += 1
        return False

# Test 1: Basic package import
def test_basic_import():
    import taskmover
    assert hasattr(taskmover, '__version__') or hasattr(taskmover, '__name__')

run_test("Basic TaskMover package import", test_basic_import)

# Test 2: Core exceptions
def test_exceptions():
    from taskmover.core.exceptions import TaskMoverException
    assert issubclass(TaskMoverException, Exception)

run_test("Core exceptions import", test_exceptions)

# Test 3: Theme manager
def test_theme_manager():
    from taskmover.ui.theme_manager import get_theme_manager, ThemeMode
    theme_manager = get_theme_manager()
    assert hasattr(theme_manager, 'current_mode')

run_test("Theme manager import and creation", test_theme_manager)

# Test 4: Main application
def test_main_app():
    from taskmover.ui.main_application import TaskMoverApplication
    assert callable(TaskMoverApplication)

run_test("Main application import", test_main_app)

# Test 5: Pattern system
def test_pattern_system():
    from taskmover.core.patterns import PatternManager
    assert callable(PatternManager)

run_test("Pattern system import", test_pattern_system)

# Test 6: Rule system  
def test_rule_system():
    from taskmover.core.rules import RuleEngine
    assert callable(RuleEngine)

run_test("Rule system import", test_rule_system)

# Test 7: Settings
def test_settings():
    from taskmover.core.settings import SettingsManager
    assert callable(SettingsManager)

run_test("Settings manager import", test_settings)

print()
print("=== Test Summary ===")
print(f"Total tests: {{test_results['total']}}")
print(f"Passed: {{test_results['passed']}}")
print(f"Failed: {{test_results['failed']}}")
print(f"Errors: {{test_results['errors']}}")

if test_results["passed"] == test_results["total"]:
    print("\\n🎉 All quick tests PASSED! TaskMover components are working correctly.")
else:
    print("\\n⚠️  Some tests failed. Check the output above for details.")
'''
        
        self.run_python_script(test_script)
    
    def run_unittest_discovery(self, start_dir):
        """Run unittest discovery in specified directory."""
        self.update_status(f"Running tests in {start_dir}...")
        
        # Use a more reliable approach to avoid import conflicts
        if start_dir == ".":
            # Run all tests by executing individual test files
            self.run_all_test_files()
        else:
            # Run specific test directory
            test_path = project_root / "tests" / start_dir
            if test_path.exists():
                self.run_test_directory(test_path)
            else:
                self.append_output(f"Test directory not found: {start_dir}\n")
    
    def run_all_test_files(self):
        """Run all test files individually to avoid import conflicts."""
        test_files = [
            "test_app.py",
            "test_ui.py", 
            "test_utils.py"
        ]
        
        # Try direct test execution first
        try:
            self.run_tests_directly()
        except Exception as e:
            self.append_output(f"Direct test execution failed: {e}\n")
            self.append_output("Falling back to subprocess execution...\n")
            
            # Fallback to subprocess execution
            for test_file in test_files:
                test_path = project_root / "tests" / test_file
                if test_path.exists():
                    self.append_output(f"\n{'='*60}\n")
                    self.append_output(f"Running {test_file}...\n")
                    self.append_output(f"{'='*60}\n")
                    cmd = [sys.executable, str(test_path)]
                    self.run_command(cmd)
        
        # Also run unit and integration test directories
        for subdir in ["unit", "integration"]:
            subdir_path = project_root / "tests" / subdir
            if subdir_path.exists():
                self.run_test_directory(subdir_path)
    
    def run_tests_directly(self):
        """Run tests by importing and executing them directly."""
        self.append_output("Running tests via direct import...\n")
        
        # Import and run test modules directly
        import importlib.util
        import unittest
        
        test_files = [
            ("test_app", project_root / "tests" / "test_app.py"),
            ("test_ui", project_root / "tests" / "test_ui.py"),
            ("test_utils", project_root / "tests" / "test_utils.py")
        ]
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        
        for module_name, test_path in test_files:
            if not test_path.exists():
                continue
                
            self.append_output(f"\n--- Running {test_path.name} directly ---\n")
            
            try:
                # Load the module
                spec = importlib.util.spec_from_file_location(module_name, test_path)
                if spec is None or spec.loader is None:
                    self.append_output(f"Could not load spec for {test_path.name}\n")
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find test classes
                loader = unittest.TestLoader()
                suite = unittest.TestSuite()
                
                for item_name in dir(module):
                    item = getattr(module, item_name)
                    if isinstance(item, type) and issubclass(item, unittest.TestCase):
                        suite.addTests(loader.loadTestsFromTestCase(item))
                
                # Run tests
                stream = io.StringIO()
                runner = unittest.TextTestRunner(stream=stream, verbosity=2)
                result = runner.run(suite)
                
                # Capture output
                test_output = stream.getvalue()
                self.append_output(test_output)
                
                # Update totals
                total_tests += result.testsRun
                total_failed += len(result.failures)
                total_errors += len(result.errors)
                total_passed += result.testsRun - len(result.failures) - len(result.errors)
                
            except Exception as e:
                self.append_output(f"Error running {test_path.name}: {e}\n")
                total_errors += 1
        
        self.update_summary(total_tests, total_passed, total_failed, total_errors)
    
    def run_test_directory(self, test_dir):
        """Run tests in a specific directory using direct file execution."""
        self.append_output(f"\n{'='*60}\n")
        self.append_output(f"Running tests in {test_dir.name}/\n")
        self.append_output(f"{'='*60}\n")
        
        # Find all test files in the directory
        test_files = list(test_dir.glob("test_*.py"))
        
        if not test_files:
            self.append_output(f"No test files found in {test_dir}\n")
            return
        
        for test_file in test_files:
            self.append_output(f"\n--- Running {test_file.name} ---\n")
            cmd = [sys.executable, str(test_file)]
            self.run_command(cmd)
    
    def run_specific_tests(self, test_files):
        """Run specific test files."""
        self.update_status("Running specific tests...")
        
        for test_file in test_files:
            test_path = project_root / "tests" / test_file
            if test_path.exists():
                cmd = [sys.executable, str(test_path)]
                self.run_command(cmd)
            else:
                self.append_output(f"Test file not found: {test_file}\\n")
    
    def run_python_script(self, script_content):
        """Run Python script content."""
        try:
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                temp_file = f.name
            
            cmd = [sys.executable, temp_file]
            self.run_command(cmd)
            
            # Clean up
            os.unlink(temp_file)
            
        except Exception as e:
            self.append_output(f"Error running script: {str(e)}\\n")
    
    def run_command(self, cmd):
        """Run a command and capture output."""
        try:
            # Set up comprehensive environment
            env = os.environ.copy()
            
            # Ensure proper Python path includes project root
            current_pythonpath = env.get('PYTHONPATH', '')
            project_paths = [str(project_root)]
            
            # Add tests directory to path for test imports
            project_paths.append(str(project_root / "tests"))
            
            if current_pythonpath:
                project_paths.append(current_pythonpath)
            
            env['PYTHONPATH'] = os.pathsep.join(project_paths)
            
            # Additional environment variables to handle Windows issues
            env['PYTHONDONTWRITEBYTECODE'] = '1'  # Prevent .pyc file issues
            env['PYTHONUNBUFFERED'] = '1'  # Ensure immediate output
            
            # Set working directory to project root
            working_dir = str(project_root)
            
            self.append_output(f"Running command: {' '.join(cmd)}\n")
            self.append_output(f"Working directory: {working_dir}\n")
            self.append_output(f"PYTHONPATH: {env['PYTHONPATH']}\n")
            self.append_output("-" * 60 + "\n")
            
            # Use a more robust subprocess call with shell=True on Windows
            import platform
            use_shell = platform.system() == 'Windows'
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # Increased timeout
                env=env,
                cwd=working_dir,
                shell=use_shell,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
            )
            
            output = result.stdout + result.stderr
            self.append_output(output)
            self.append_output("\n" + "=" * 60 + "\n")
            
            # Parse results
            self.parse_test_results(output, result.returncode)
            
        except subprocess.TimeoutExpired:
            self.append_output("⚠️ Test execution timed out after 120 seconds\n")
            self.update_summary(0, 0, 1, 0)
        except Exception as e:
            self.append_output(f"❌ Error executing command: {str(e)}\n")
            import traceback
            self.append_output(traceback.format_exc())
            self.update_summary(0, 0, 0, 1)
    
    def parse_test_results(self, output, returncode):
        """Parse test output and update summary."""
        lines = output.split('\n')
        
        total = 0
        passed = 0
        failed = 0
        errors = 0
        
        # Look for unittest patterns
        for line in lines:
            line = line.strip()
            
            # Standard unittest output: "Ran X tests"
            if 'Ran ' in line and ' test' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'Ran' and i + 1 < len(parts):
                        try:
                            total = int(parts[i + 1])
                        except ValueError:
                            pass
            
            # Look for failure/error patterns
            elif 'FAILED' in line and '(' in line:
                # Parse "FAILED (failures=X, errors=Y)" or "FAILED (failures=X)"
                if 'failures=' in line:
                    try:
                        start = line.find('failures=') + 9
                        end = line.find(',', start)
                        if end == -1:
                            end = line.find(')', start)
                        failed = int(line[start:end])
                    except (ValueError, IndexError):
                        pass
                
                if 'errors=' in line:
                    try:
                        start = line.find('errors=') + 7
                        end = line.find(',', start)
                        if end == -1:
                            end = line.find(')', start)
                        errors = int(line[start:end])
                    except (ValueError, IndexError):
                        pass
            
            # Quick test specific patterns
            elif 'Total tests:' in line:
                try:
                    total = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
            elif 'Passed:' in line:
                try:
                    passed = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
            elif 'Failed:' in line:
                try:
                    failed = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
            elif 'Errors:' in line:
                try:
                    errors = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
        
        # Calculate passed if not already set
        if total > 0 and passed == 0:
            passed = total - failed - errors
        
        # Handle cases where we have explicit counts from quick test
        if total == 0 and (passed > 0 or failed > 0 or errors > 0):
            total = passed + failed + errors
        
        # Fallback logic for simple success/failure
        if total == 0:
            if returncode == 0 and any(indicator in output for indicator in ['✅', 'PASSED', 'All quick tests PASSED']):
                total = passed = 1
            elif returncode != 0 or any(indicator in output for indicator in ['❌', 'FAILED', 'ERROR']):
                total = 1
                if 'Import Error' in output or 'ModuleNotFoundError' in output:
                    errors = 1
                else:
                    failed = 1
        
        self.update_summary(total, passed, failed, errors)
    
    def update_status(self, message):
        """Update status label."""
        self.root.after(0, lambda: self.status_label.configure(text=message))
    
    def append_output(self, text):
        """Append text to output area."""
        def update():
            self.output_text.insert(tk.END, text)
            self.output_text.see(tk.END)
        
        self.root.after(0, update)
    
    def update_summary(self, total, passed, failed, errors):
        """Update summary labels."""
        def update():
            self.summary_cards['total'].configure(text=str(total))
            self.summary_cards['passed'].configure(text=str(passed))
            self.summary_cards['failed'].configure(text=str(failed))
            self.summary_cards['errors'].configure(text=str(errors))
        
        self.root.after(0, update)
    
    def clear_results(self):
        """Clear all results."""
        self.output_text.delete(1.0, tk.END)
        for label in self.summary_cards.values():
            label.configure(text="0")
        self.status_label.configure(text="Running tests...")
    
    def stop_tests(self):
        """Stop running tests."""
        self.running_tests = False
        self.update_status("Tests stopped")
        self.test_complete()
    
    def test_complete(self):
        """Handle test completion."""
        self.running_tests = False
        self.run_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.progress.stop()
        
        if self.status_label.cget("text") == "Running tests...":
            self.status_label.configure(text="Tests completed")
    
    def run(self):
        """Start the GUI."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass


def main():
    """Main entry point."""
    app = SimpleTestGUI()
    app.run()


if __name__ == "__main__":
    main()
