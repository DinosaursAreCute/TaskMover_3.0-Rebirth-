"""
Professional Test Runner GUI
============================

A modern, professional-grade test runner implementing the concepts from TEST_GUI_CONCEPT.md.
Features hierarchical test discovery, real-time progress monitoring, and advanced reporting.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import subprocess
import threading
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import sys


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Individual test result."""
    name: str
    status: TestStatus
    duration: float = 0.0
    output: str = ""
    error: str = ""


@dataclass
class TestSuite:
    """Test suite information."""
    name: str
    path: Path
    test_count: int
    description: str = ""
    enabled: bool = True


class ProfessionalTestRunner:
    """
    Modern test runner GUI implementing professional features:
    - Hierarchical test discovery
    - Real-time progress monitoring
    - Multi-level progress dashboard
    - Structured log interface
    - Performance metrics
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TaskMover Professional Test Runner")
        self.root.geometry("1200x800")
        
        # Application state
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_results: Dict[str, TestResult] = {}
        self.running = False
        self.start_time = 0.0
        
        # Style configuration
        self.setup_styles()
        self.create_ui()
        self.discover_tests()
    
    def setup_styles(self):
        """Configure modern styling."""
        self.colors = {
            'bg': '#2d3748',
            'surface': '#4a5568',
            'primary': '#4299e1',
            'success': '#48bb78',
            'error': '#f56565',
            'warning': '#ed8936',
            'text': '#f7fafc',
            'text_secondary': '#a0aec0'
        }
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom styles
        style.configure('Header.TLabel', 
                       background=self.colors['bg'], 
                       foreground=self.colors['text'],
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Status.TLabel',
                       background=self.colors['surface'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 9))
    
    def setup_output_tags(self):
        """Configure text tags for colored output."""
        # Define color tags for different types of output
        self.output_text.tag_configure("PASSED", foreground=self.colors['success'], font=('Consolas', 10, 'bold'))
        self.output_text.tag_configure("FAILED", foreground=self.colors['error'], font=('Consolas', 10, 'bold'))
        self.output_text.tag_configure("ERROR", foreground=self.colors['error'], font=('Consolas', 10, 'bold'))
        self.output_text.tag_configure("SKIPPED", foreground=self.colors['warning'], font=('Consolas', 10, 'bold'))
        self.output_text.tag_configure("WARNING", foreground=self.colors['warning'])
        self.output_text.tag_configure("INFO", foreground=self.colors['primary'])
        self.output_text.tag_configure("TIMESTAMP", foreground=self.colors['text_secondary'], font=('Consolas', 9))
        self.output_text.tag_configure("SUMMARY", foreground=self.colors['text'], font=('Consolas', 10, 'bold'))
        self.output_text.tag_configure("FILE_PATH", foreground=self.colors['primary'], underline=True)
    
    def log_colored(self, message: str, tag: str = ""):
        """Add colored message to output log with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        timestamp_text = f"[{timestamp}] "
        
        # Insert timestamp with special formatting
        self.output_text.insert(tk.END, timestamp_text, "TIMESTAMP")
        
        # Insert message with appropriate coloring
        if tag:
            self.output_text.insert(tk.END, f"{message}\n", tag)
        else:
            # Auto-detect content type for coloring
            if "PASSED" in message or "✅" in message:
                self.output_text.insert(tk.END, f"{message}\n", "PASSED")
            elif "FAILED" in message or "❌" in message:
                self.output_text.insert(tk.END, f"{message}\n", "FAILED")
                # Also add to failed tests tab
                self.add_to_failed_tests(message)
            elif "ERROR" in message or "💥" in message:
                self.output_text.insert(tk.END, f"{message}\n", "ERROR")
                self.add_to_failed_tests(message)
            elif "SKIPPED" in message or "⏭️" in message:
                self.output_text.insert(tk.END, f"{message}\n", "SKIPPED")
            elif "WARNING" in message or "⚠️" in message:
                self.output_text.insert(tk.END, f"{message}\n", "WARNING")
            elif message.startswith("="):
                self.output_text.insert(tk.END, f"{message}\n", "SUMMARY")
            elif "::" in message and (".py" in message):
                self.output_text.insert(tk.END, f"{message}\n", "FILE_PATH")
            else:
                self.output_text.insert(tk.END, f"{message}\n")
        
        self.output_text.see(tk.END)
    
    def add_to_failed_tests(self, message: str):
        """Add failed test information to the failed tests tab."""
        timestamp = time.strftime("%H:%M:%S")
        timestamp_text = f"[{timestamp}] "
        
        # Insert timestamp with formatting
        self.failed_text.insert(tk.END, timestamp_text, "TIMESTAMP")
        
        # Insert message with appropriate coloring
        if "FAILED" in message:
            self.failed_text.insert(tk.END, f"{message}\n", "FAILED")
        elif "ERROR" in message:
            self.failed_text.insert(tk.END, f"{message}\n", "ERROR")
        else:
            self.failed_text.insert(tk.END, f"{message}\n")
        
        self.failed_text.see(tk.END)
        
        # Update failed tests tab title with count
        current_content = self.failed_text.get(1.0, tk.END).strip()
        failed_count = len([line for line in current_content.split('\n') if line.strip()])
        if failed_count > 0:
            self.notebook.tab(1, text=f"❌ Failed Tests ({failed_count})")
    
    def update_summary_tab(self, passed: int, failed: int, errors: int, skipped: int, elapsed: float, test_suites: List[str]):
        """Update the summary tab with comprehensive test results."""
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        
        total = passed + failed + errors + skipped
        
        # Header
        self.summary_text.insert(tk.END, "TEST EXECUTION SUMMARY\n", "HEADER")
        self.summary_text.insert(tk.END, "="*50 + "\n\n", "HEADER")
        
        # Overall results
        self.summary_text.insert(tk.END, "📊 OVERALL RESULTS\n", "HEADER")
        self.summary_text.insert(tk.END, f"• Total Tests:     {total}\n")
        
        if passed > 0:
            self.summary_text.insert(tk.END, f"• Passed:          {passed} ({passed/total*100:.1f}% of total)\n", "SUCCESS")
        if failed > 0:
            self.summary_text.insert(tk.END, f"• Failed:          {failed} ({failed/total*100:.1f}% of total)\n", "ERROR")
        if errors > 0:
            self.summary_text.insert(tk.END, f"• Errors:          {errors} ({errors/total*100:.1f}% of total)\n", "ERROR")
        if skipped > 0:
            self.summary_text.insert(tk.END, f"• Skipped:         {skipped} ({skipped/total*100:.1f}% of total)\n", "WARNING")
        
        # Performance metrics
        self.summary_text.insert(tk.END, "\n⏱️ PERFORMANCE METRICS\n", "HEADER")
        self.summary_text.insert(tk.END, f"• Execution Time:  {elapsed:.2f} seconds\n", "METRICS")
        self.summary_text.insert(tk.END, f"• Test Rate:       {total/elapsed:.1f} tests/second\n", "METRICS")
        self.summary_text.insert(tk.END, f"• Average per Test: {elapsed/total*1000:.1f}ms\n", "METRICS")
        
        # Test suites executed
        self.summary_text.insert(tk.END, "\n📁 TEST SUITES EXECUTED\n", "HEADER")
        for suite in test_suites:
            self.summary_text.insert(tk.END, f"• {suite}\n")
        
        # Quality assessment
        self.summary_text.insert(tk.END, "\n🎯 QUALITY ASSESSMENT\n", "HEADER")
        success_rate = passed/total*100 if total > 0 else 0
        if failed + errors == 0:
            self.summary_text.insert(tk.END, f"• Success Rate:    {success_rate:.1f}%\n", "SUCCESS")
            self.summary_text.insert(tk.END, "• Reliability:     🟢 Excellent\n", "SUCCESS")
        elif failed + errors < 5:
            self.summary_text.insert(tk.END, f"• Success Rate:    {success_rate:.1f}%\n", "WARNING")
            self.summary_text.insert(tk.END, "• Reliability:     🟡 Needs Attention\n", "WARNING")
        else:
            self.summary_text.insert(tk.END, f"• Success Rate:    {success_rate:.1f}%\n", "ERROR")
            self.summary_text.insert(tk.END, "• Reliability:     🔴 Critical Issues\n", "ERROR")
        
        coverage_assessment = '🟢 Comprehensive' if total > 50 else '🟡 Moderate' if total > 20 else '🔴 Limited'
        self.summary_text.insert(tk.END, f"• Test Coverage:   {coverage_assessment}\n")
        
        # Recommendations
        self.summary_text.insert(tk.END, "\n💡 RECOMMENDATIONS\n", "HEADER")
        if failed > 0:
            self.summary_text.insert(tk.END, f"• Review and fix {failed} failing test(s)\n", "ERROR")
        if errors > 0:
            self.summary_text.insert(tk.END, f"• Investigate {errors} test error(s)\n", "ERROR")
        if skipped > 0:
            self.summary_text.insert(tk.END, f"• Consider re-enabling {skipped} skipped test(s)\n", "WARNING")
        if failed + errors == 0:
            self.summary_text.insert(tk.END, "• All tests passed! Consider adding more test coverage\n", "SUCCESS")
        
        # Next steps
        self.summary_text.insert(tk.END, "\n📈 NEXT STEPS\n", "HEADER")
        self.summary_text.insert(tk.END, "• Review failed tests in the 'Failed Tests' tab\n")
        self.summary_text.insert(tk.END, "• Check test output for detailed error messages\n")
        self.summary_text.insert(tk.END, "• Update code to fix failing tests\n")
        self.summary_text.insert(tk.END, "• Re-run tests to verify fixes\n")
        
        self.summary_text.insert(tk.END, f"\nGenerated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n", "METRICS")
        
        self.summary_text.config(state=tk.DISABLED)
    
    def create_ui(self):
        """Create the professional UI layout."""
        self.root.configure(bg=self.colors['bg'])
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel - Test Selection
        self.create_test_selection_panel(content_frame)
        
        # Right panel - Execution and Results
        self.create_execution_panel(content_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Create application header with controls."""
        header = tk.Frame(parent, bg=self.colors['bg'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Title
        title = tk.Label(header, 
                        text="🧪 TaskMover Professional Test Runner",
                        bg=self.colors['bg'],
                        fg=self.colors['text'],
                        font=('Segoe UI', 16, 'bold'))
        title.pack(side=tk.LEFT, padx=(0, 20))
        
        # Control buttons
        controls = tk.Frame(header, bg=self.colors['bg'])
        controls.pack(side=tk.RIGHT)
        
        self.run_btn = tk.Button(controls,
                                text="▶️ Run Selected",
                                bg=self.colors['primary'],
                                fg='white',
                                font=('Segoe UI', 10, 'bold'),
                                padx=20, pady=8,
                                relief=tk.FLAT,
                                command=self.run_tests)
        self.run_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(controls,
                                 text="⏹️ Stop",
                                 bg=self.colors['error'],
                                 fg='white',
                                 font=('Segoe UI', 10, 'bold'),
                                 padx=20, pady=8,
                                 relief=tk.FLAT,
                                 state=tk.DISABLED,
                                 command=self.stop_tests)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = tk.Button(controls,
                               text="🔄 Refresh",
                               bg=self.colors['surface'],
                               fg=self.colors['text'],
                               font=('Segoe UI', 10),
                               padx=15, pady=8,
                               relief=tk.FLAT,
                               command=self.discover_tests)
        refresh_btn.pack(side=tk.LEFT)
    
    def create_test_selection_panel(self, parent):
        """Create test selection and filtering panel."""
        # Left panel container
        left_panel = tk.Frame(parent, bg=self.colors['surface'], width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Panel header
        header = tk.Label(left_panel,
                         text="📁 Test Selection",
                         bg=self.colors['surface'],
                         fg=self.colors['text'],
                         font=('Segoe UI', 12, 'bold'),
                         pady=10)
        header.pack(fill=tk.X)
        
        # Search box
        search_frame = tk.Frame(left_panel, bg=self.colors['surface'])
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(search_frame, text="🔍", bg=self.colors['surface'], fg=self.colors['text']).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 10))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Quick presets
        presets_frame = tk.LabelFrame(left_panel, 
                                     text="⚡ Quick Presets",
                                     bg=self.colors['surface'],
                                     fg=self.colors['text'],
                                     font=('Segoe UI', 10, 'bold'))
        presets_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        presets = [
            ("All Tests", self.select_all_tests),
            ("Unit Tests", lambda: self.filter_tests("unit")),
            ("Integration Tests", lambda: self.filter_tests("integration")),
            ("Failed in Last Run", self.select_failed_tests)
        ]
        
        for text, command in presets:
            btn = tk.Button(presets_frame, text=text, command=command,
                           bg=self.colors['bg'], fg=self.colors['text'],
                           relief=tk.FLAT, pady=2)
            btn.pack(fill=tk.X, padx=5, pady=2)
        
        # Test tree
        tree_frame = tk.Frame(left_panel, bg=self.colors['surface'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.test_tree = ttk.Treeview(tree_frame, show='tree headings', columns=('count', 'status'))
        self.test_tree.heading('#0', text='Test Suite')
        self.test_tree.heading('count', text='Tests')
        self.test_tree.heading('status', text='Status')
        self.test_tree.column('count', width=60)
        self.test_tree.column('status', width=80)
        
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.test_tree.yview)
        self.test_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.test_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_execution_panel(self, parent):
        """Create execution control and results panel."""
        right_panel = tk.Frame(parent, bg=self.colors['bg'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Progress dashboard
        self.create_progress_dashboard(right_panel)
        
        # Results area
        self.create_results_area(right_panel)
    
    def create_progress_dashboard(self, parent):
        """Create multi-level progress dashboard."""
        progress_frame = tk.LabelFrame(parent,
                                      text="📊 Execution Dashboard",
                                      bg=self.colors['bg'],
                                      fg=self.colors['text'],
                                      font=('Segoe UI', 12, 'bold'))
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Current test info
        current_frame = tk.Frame(progress_frame, bg=self.colors['bg'])
        current_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.current_test_label = tk.Label(current_frame,
                                          text="Ready to run tests",
                                          bg=self.colors['bg'],
                                          fg=self.colors['text'],
                                          font=('Segoe UI', 11))
        self.current_test_label.pack(anchor=tk.W)
        
        # Main progress bar
        progress_bar_frame = tk.Frame(progress_frame, bg=self.colors['bg'])
        progress_bar_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.main_progress = ttk.Progressbar(progress_bar_frame, mode='determinate')
        self.main_progress.pack(fill=tk.X)
        
        # Metrics frame
        metrics_frame = tk.Frame(progress_frame, bg=self.colors['bg'])
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create metric displays
        metric_names = ['Passed', 'Failed', 'Errors', 'Skipped', 'Rate']
        self.metric_labels = {}
        
        for i, name in enumerate(metric_names):
            frame = tk.Frame(metrics_frame, bg=self.colors['surface'], relief=tk.RAISED, bd=1)
            frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            
            title = tk.Label(frame, text=name, bg=self.colors['surface'], 
                           fg=self.colors['text_secondary'], font=('Segoe UI', 8))
            title.pack()
            
            value = tk.Label(frame, text="0", bg=self.colors['surface'],
                           fg=self.colors['text'], font=('Segoe UI', 14, 'bold'))
            value.pack()
            
            self.metric_labels[name.lower()] = value
    
    def create_results_area(self, parent):
        """Create structured results and log interface."""
        results_frame = tk.LabelFrame(parent,
                                     text="📄 Test Output & Logs",
                                     bg=self.colors['bg'],
                                     fg=self.colors['text'],
                                     font=('Segoe UI', 12, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tab control for different views
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # All output tab
        all_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(all_frame, text="📄 All Output")
        
        self.output_text = tk.Text(all_frame, 
                                  bg=self.colors['bg'],
                                  fg=self.colors['text'],
                                  font=('Consolas', 10),
                                  wrap=tk.WORD)
        
        # Configure text tags for colored output
        self.setup_output_tags()
        
        output_scroll = ttk.Scrollbar(all_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_scroll.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Failed tests tab
        failed_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(failed_frame, text="❌ Failed Tests")
        
        self.failed_text = tk.Text(failed_frame,
                                  bg=self.colors['bg'],
                                  fg=self.colors['text'],
                                  font=('Consolas', 10),
                                  wrap=tk.WORD)
        
        # Configure color tags for failed tests
        self.failed_text.tag_configure("TIMESTAMP", foreground=self.colors['text_secondary'])
        self.failed_text.tag_configure("FAILED", foreground=self.colors['error'], font=('Consolas', 10, 'bold'))
        self.failed_text.tag_configure("ERROR", foreground=self.colors['error'], font=('Consolas', 10, 'bold'))
        
        failed_scroll = ttk.Scrollbar(failed_frame, orient=tk.VERTICAL, command=self.failed_text.yview)
        self.failed_text.configure(yscrollcommand=failed_scroll.set)
        
        self.failed_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        failed_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Summary tab
        summary_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(summary_frame, text="📊 Summary")
        
        # Summary content with scrollable text
        self.summary_text = tk.Text(summary_frame,
                                   bg=self.colors['bg'],
                                   fg=self.colors['text'],
                                   font=('Segoe UI', 11),
                                   wrap=tk.WORD,
                                   state=tk.DISABLED)
        
        # Configure color tags for summary
        self.summary_text.tag_configure("HEADER", foreground=self.colors['primary'], font=('Segoe UI', 12, 'bold'))
        self.summary_text.tag_configure("SUCCESS", foreground=self.colors['success'], font=('Segoe UI', 11, 'bold'))
        self.summary_text.tag_configure("ERROR", foreground=self.colors['error'], font=('Segoe UI', 11, 'bold'))
        self.summary_text.tag_configure("WARNING", foreground=self.colors['warning'], font=('Segoe UI', 11, 'bold'))
        self.summary_text.tag_configure("METRICS", foreground=self.colors['text_secondary'])
        
        summary_scroll = ttk.Scrollbar(summary_frame, orient=tk.VERTICAL, command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=summary_scroll.set)
        
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        summary_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_status_bar(self, parent):
        """Create status bar with system information."""
        status_frame = tk.Frame(parent, bg=self.colors['surface'], height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame,
                                    text="Ready │ 0 tests selected │ Python 3.11.9",
                                    bg=self.colors['surface'],
                                    fg=self.colors['text_secondary'],
                                    font=('Segoe UI', 9))
        self.status_label.pack(side=tk.LEFT, padx=10, anchor=tk.W)
        
        # Right side status
        time_label = tk.Label(status_frame,
                             text=time.strftime("%H:%M:%S"),
                             bg=self.colors['surface'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 9))
        time_label.pack(side=tk.RIGHT, padx=10)
    
    def discover_tests(self):
        """Discover available test suites with hierarchical organization."""
        self.log("🔍 Discovering tests...")
        
        # Clear existing tests
        for item in self.test_tree.get_children():
            self.test_tree.delete(item)
        
        test_dirs = {
            "Unit Tests": Path("tests/unit"),
            "Integration Tests": Path("tests/integration"),
            "Application Tests": Path("tests"),
            "Performance Tests": Path("tests/performance") if Path("tests/performance").exists() else None
        }
        
        total_tests = 0
        
        for category, path in test_dirs.items():
            if path is None or not path.exists():
                continue
                
            category_id = self.test_tree.insert('', 'end', text=category, values=('', ''))
            
            # Find Python test files
            test_files = list(path.glob("test_*.py"))
            category_count = 0
            
            for test_file in test_files:
                try:
                    # Estimate test count by counting test methods
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        test_count = content.count('def test_')
                    
                    if test_count > 0:
                        self.test_tree.insert(category_id, 'end', 
                                            text=test_file.stem,
                                            values=(test_count, '⏳'))
                        category_count += test_count
                        
                        # Store test suite info
                        self.test_suites[test_file.stem] = TestSuite(
                            name=test_file.stem,
                            path=test_file,
                            test_count=test_count,
                            description=f"{category} - {test_file.name}"
                        )
                
                except Exception as e:
                    self.log(f"Error reading {test_file}: {e}")
            
            # Update category count
            self.test_tree.item(category_id, values=(category_count, ''))
            total_tests += category_count
            
            # Expand category
            self.test_tree.item(category_id, open=True)
        
        self.update_status(f"Ready │ {total_tests} tests discovered │ Python {sys.version.split()[0]}")
        self.log(f"✅ Test discovery complete. Found {total_tests} tests in {len(self.test_suites)} suites.")
    
    def select_all_tests(self):
        """Select all available tests."""
        for item in self.test_tree.get_children():
            self.test_tree.selection_add(item)
            for child in self.test_tree.get_children(item):
                self.test_tree.selection_add(child)
    
    def filter_tests(self, filter_type: str):
        """Filter tests by type."""
        self.test_tree.selection_remove(self.test_tree.selection())
        
        for item in self.test_tree.get_children():
            text = self.test_tree.item(item, 'text').lower()
            if filter_type.lower() in text:
                self.test_tree.selection_add(item)
                for child in self.test_tree.get_children(item):
                    self.test_tree.selection_add(child)
    
    def select_failed_tests(self):
        """Select tests that failed in the last run."""
        # Implementation would select based on stored results
        self.log("🔍 Selecting previously failed tests...")
    
    def run_tests(self):
        """Execute selected tests with real-time monitoring."""
        selected_items = self.test_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select tests to run.")
            return
        
        self.running = True
        self.start_time = time.time()
        self.run_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        
        # Clear previous results
        self.output_text.delete(1.0, tk.END)
        self.failed_text.delete(1.0, tk.END)  # Clear failed tests tab
        self.notebook.tab(1, text="❌ Failed Tests")  # Reset failed tests tab title
        self.reset_metrics()
        
        self.log("🚀 Starting test execution...")
        self.current_test_label.configure(text="Initializing test runner...")
        
        # Run tests in separate thread
        thread = threading.Thread(target=self._execute_tests, args=(selected_items,))
        thread.daemon = True
        thread.start()
    
    def _execute_tests(self, selected_items):
        """Execute tests in background thread."""
        try:
            # Get unique test files from selection
            test_files = set()
            executed_suites = []
            
            for item in selected_items:
                text = self.test_tree.item(item, 'text')
                if text in self.test_suites:
                    test_files.add(self.test_suites[text].path)
                    executed_suites.append(text)
            
            total_tests = sum(self.test_suites[f.stem].test_count 
                             for f in test_files if f.stem in self.test_suites)
            
            self.root.after(0, lambda: self.main_progress.configure(maximum=total_tests))
            
            current_test = 0
            passed = failed = errors = skipped = 0
            
            for test_file in test_files:
                if not self.running:
                    break
                
                suite_name = test_file.stem
                self.root.after(0, lambda s=suite_name: 
                              self.current_test_label.configure(text=f"Running: {s}"))
                
                # Execute pytest for this file
                cmd = [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short", "--no-header"]
                
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        cwd=Path.cwd(),
                        universal_newlines=True
                    )
                    
                    # Read output line by line
                    if process.stdout:
                        for line in process.stdout:
                            if not self.running:
                                process.terminate()
                                break
                            
                            line = line.strip()
                            if line:  # Only process non-empty lines
                                self.root.after(0, lambda l=line: self.log_colored(l))
                                
                                # Parse test results
                                if " PASSED " in line or "::test_" in line and line.endswith(" PASSED"):
                                    passed += 1
                                    current_test += 1
                                elif " FAILED " in line or "::test_" in line and line.endswith(" FAILED"):
                                    failed += 1
                                    current_test += 1
                                elif " ERROR " in line or "::test_" in line and line.endswith(" ERROR"):
                                    errors += 1
                                    current_test += 1
                                elif " SKIPPED " in line or "::test_" in line and line.endswith(" SKIPPED"):
                                    skipped += 1
                                    current_test += 1
                                
                                # Update progress
                                if current_test > 0:
                                    self.root.after(0, lambda: self.main_progress.configure(value=current_test))
                                    
                                    # Update metrics
                                    elapsed = time.time() - self.start_time
                                    rate = current_test / elapsed if elapsed > 0 else 0
                                    
                                    self.root.after(0, lambda: self.update_metrics(passed, failed, errors, skipped, rate))
                    
                    process.wait()
                    
                except subprocess.SubprocessError as e:
                    error_msg = f"Error running {suite_name}: {e}"
                    self.root.after(0, lambda msg=error_msg: self.log_colored(msg, "ERROR"))
                except Exception as e:
                    error_msg = f"Unexpected error with {suite_name}: {e}"
                    self.root.after(0, lambda msg=error_msg: self.log_colored(msg, "ERROR"))
            
            # Test execution complete
            elapsed = time.time() - self.start_time
            
            def finish_callback():
                self._finish_tests(passed, failed, errors, skipped, elapsed, executed_suites)
            
            self.root.after(0, finish_callback)
            
        except Exception as e:
            error_msg = f"❌ Error during test execution: {e}"
            self.root.after(0, lambda msg=error_msg: self.log_colored(msg, "ERROR"))
            self.root.after(0, self._finish_tests_error)
    
    def _finish_tests(self, passed, failed, errors, skipped, elapsed, executed_suites):
        """Finish test execution and update UI."""
        self.running = False
        self.run_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        
        total = passed + failed + errors + skipped
        self.current_test_label.configure(
            text=f"✅ Completed: {total} tests in {elapsed:.2f}s"
        )
        
        # Final summary
        summary = f"\n\n{'='*60}\n"
        summary += f"TEST EXECUTION SUMMARY\n"
        summary += f"{'='*60}\n"
        summary += f"Total Tests: {total}\n"
        summary += f"Passed: {passed} ({passed/total*100:.1f}%)\n"
        summary += f"Failed: {failed} ({failed/total*100:.1f}%)\n"
        summary += f"Errors: {errors} ({errors/total*100:.1f}%)\n"
        summary += f"Skipped: {skipped} ({skipped/total*100:.1f}%)\n"
        summary += f"Execution Time: {elapsed:.2f}s\n"
        summary += f"Test Rate: {total/elapsed:.1f} tests/second\n"
        
        self.log_colored(summary, "SUMMARY")
        
        # Update the summary tab with comprehensive results
        self.update_summary_tab(passed, failed, errors, skipped, elapsed, executed_suites)
        
        # Update status
        status_color = "🟢" if failed == 0 and errors == 0 else "🔴"
        self.update_status(f"{status_color} Complete │ {passed}✅ {failed}❌ {errors}💥 │ {elapsed:.1f}s")
    
    def _finish_tests_error(self):
        """Handle test execution error."""
        self.running = False
        self.run_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.current_test_label.configure(text="❌ Test execution failed")
    
    def stop_tests(self):
        """Stop test execution."""
        self.running = False
        self.log("\n⏹️ Test execution stopped by user")
        self.current_test_label.configure(text="Stopped")
        self.run_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
    
    def update_metrics(self, passed, failed, errors, skipped, rate):
        """Update real-time metrics display."""
        self.metric_labels['passed'].configure(text=str(passed))
        self.metric_labels['failed'].configure(text=str(failed))
        self.metric_labels['errors'].configure(text=str(errors))
        self.metric_labels['skipped'].configure(text=str(skipped))
        self.metric_labels['rate'].configure(text=f"{rate:.1f}/s")
    
    def reset_metrics(self):
        """Reset all metrics to zero."""
        for label in self.metric_labels.values():
            label.configure(text="0")
        self.main_progress.configure(value=0)
    
    def log(self, message: str):
        """Add message to output log with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.output_text.insert(tk.END, formatted_message)
        self.output_text.see(tk.END)
    
    def update_status(self, status: str):
        """Update status bar."""
        self.status_label.configure(text=status)
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Run the professional test runner."""
    try:
        app = ProfessionalTestRunner()
        app.run()
    except Exception as e:
        print(f"Error starting test runner: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
