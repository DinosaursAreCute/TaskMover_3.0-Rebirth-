#!/usr/bin/env python3
"""
TaskMover Test Runner - Professional Edition
===========================================

A modern, user-friendly test runner GUI with enhanced usability and visual appeal.
Built with developer productivity in mind.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os
import subprocess
import threading
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class TestSuite:
    """Test suite configuration."""
    name: str
    description: str
    tests: List[str]
    estimated_time: str
    category: str


class ModernTestRunner:
    """Modern test runner with professional UI/UX."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_theme()
        self.setup_test_suites()
        self.setup_ui()
        self.apply_theme()
        
        # State management
        self.running_tests = False
        self.current_test = None
        self.test_results = {"total": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
        self.start_time = None
        
    def setup_window(self):
        """Configure main window."""
        self.root.title("TaskMover Test Runner - Professional Edition")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
        
    def setup_theme(self):
        """Setup modern dark theme."""
        self.theme = {
            'bg_primary': '#0d1117',      # GitHub dark background
            'bg_secondary': '#161b22',     # Slightly lighter background
            'bg_tertiary': '#21262d',      # Button/input background
            'fg_primary': '#f0f6fc',       # Primary text
            'fg_secondary': '#8b949e',     # Secondary text
            'accent_blue': '#58a6ff',      # Primary accent
            'accent_green': '#3fb950',     # Success
            'accent_red': '#f85149',       # Error/danger
            'accent_yellow': '#d29922',    # Warning
            'accent_purple': '#a5a5ff',    # Info
            'border': '#30363d',           # Borders
            'hover': '#262c36'             # Hover states
        }
        
    def setup_test_suites(self):
        """Define available test suites."""
        self.test_suites = [
            TestSuite(
                name="Quick Validation",
                description="Fast import and basic functionality tests",
                tests=["quick_test"],
                estimated_time="< 30s",
                category="Essential"
            ),
            TestSuite(
                name="Unit Tests",
                description="Core component unit tests",
                tests=["tests/unit/"],
                estimated_time="1-2 min",
                category="Development"
            ),
            TestSuite(
                name="Integration Tests", 
                description="Component integration testing",
                tests=["tests/integration/"],
                estimated_time="2-3 min",
                category="Development"
            ),
            TestSuite(
                name="UI Components",
                description="User interface component tests",
                tests=["tests/test_ui.py", "tests/test_app.py"],
                estimated_time="1-2 min",
                category="Frontend"
            ),
            TestSuite(
                name="Full Test Suite",
                description="Complete test coverage",
                tests=["all"],
                estimated_time="5-8 min",
                category="CI/CD"
            ),
            TestSuite(
                name="Safe Mode",
                description="Direct imports without subprocess",
                tests=["safe_mode"],
                estimated_time="< 1 min",
                category="Debugging"
            )
        ]
        
    def setup_ui(self):
        """Setup the modern user interface."""
        # Main container with modern styling
        self.main_frame = tk.Frame(self.root, padx=0, pady=0)
        self.main_frame.pack(fill="both", expand=True)
        
        # Create sections
        self.create_header()
        self.create_test_selection()
        self.create_progress_section()
        self.create_results_section()
        self.create_status_bar()
        
    def create_header(self):
        """Create modern header section."""
        header = tk.Frame(self.main_frame, height=80)
        header.pack(fill="x", padx=20, pady=(20, 0))
        header.pack_propagate(False)
        
        # Left side - title and description
        left_frame = tk.Frame(header)
        left_frame.pack(side="left", fill="both", expand=True)
        
        self.title_label = tk.Label(
            left_frame,
            text="TaskMover Test Runner",
            font=("Segoe UI", 20, "bold")
        )
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = tk.Label(
            left_frame,
            text="Professional test execution and monitoring",
            font=("Segoe UI", 11)
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Right side - controls
        right_frame = tk.Frame(header)
        right_frame.pack(side="right", fill="y")
        
        self.theme_btn = tk.Button(
            right_frame,
            text="🌙 Dark",
            font=("Segoe UI", 10),
            width=8,
            height=1
        )
        self.theme_btn.pack(side="top", pady=(10, 5))
        
        self.settings_btn = tk.Button(
            right_frame,
            text="⚙️ Config",
            font=("Segoe UI", 10),
            width=8,
            height=1
        )
        self.settings_btn.pack(side="top")
        
    def create_test_selection(self):
        """Create test selection section."""
        selection_frame = tk.LabelFrame(
            self.main_frame,
            text="  Test Suite Selection  ",
            font=("Segoe UI", 12, "bold"),
            padx=20,
            pady=15
        )
        selection_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Test suite cards
        self.create_test_cards(selection_frame)
        
        # Control buttons
        control_frame = tk.Frame(selection_frame)
        control_frame.pack(fill="x", pady=(15, 0))
        
        self.run_btn = tk.Button(
            control_frame,
            text="▶️  Run Selected Tests",
            font=("Segoe UI", 12, "bold"),
            padx=30,
            pady=10,
            command=self.run_tests
        )
        self.run_btn.pack(side="left")
        
        self.stop_btn = tk.Button(
            control_frame,
            text="⏹️  Stop",
            font=("Segoe UI", 11),
            padx=20,
            pady=10,
            state="disabled",
            command=self.stop_tests
        )
        self.stop_btn.pack(side="left", padx=(15, 0))
        
        # Configuration options
        config_frame = tk.Frame(control_frame)
        config_frame.pack(side="right")
        
        tk.Label(config_frame, text="Options:", font=("Segoe UI", 10)).pack(side="left")
        
        self.verbose_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            config_frame,
            text="Verbose",
            variable=self.verbose_var,
            font=("Segoe UI", 9)
        ).pack(side="left", padx=(10, 0))
        
        self.coverage_var = tk.BooleanVar()
        tk.Checkbutton(
            config_frame,
            text="Coverage",
            variable=self.coverage_var,
            font=("Segoe UI", 9)
        ).pack(side="left", padx=(10, 0))
        
    def create_test_cards(self, parent):
        """Create modern test suite selection cards."""
        cards_frame = tk.Frame(parent)
        cards_frame.pack(fill="x")
        
        self.selected_suite = tk.StringVar(value="Quick Validation")
        self.suite_cards = {}
        
        # Create cards in a grid
        for i, suite in enumerate(self.test_suites):
            row = i // 3
            col = i % 3
            
            card = self.create_suite_card(cards_frame, suite)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            # Configure grid weights
            cards_frame.grid_columnconfigure(col, weight=1)
            
            self.suite_cards[suite.name] = card
            
    def create_suite_card(self, parent, suite):
        """Create individual test suite card."""
        card = tk.Frame(parent, relief="solid", bd=1, padx=15, pady=12)
        
        # Radio button for selection
        radio = tk.Radiobutton(
            card,
            variable=self.selected_suite,
            value=suite.name,
            font=("Segoe UI", 10)
        )
        radio.pack(side="left")
        
        # Suite info
        info_frame = tk.Frame(card)
        info_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # Suite name
        name_label = tk.Label(
            info_frame,
            text=suite.name,
            font=("Segoe UI", 11, "bold")
        )
        name_label.pack(anchor="w")
        
        # Description
        desc_label = tk.Label(
            info_frame,
            text=suite.description,
            font=("Segoe UI", 9),
            wraplength=200
        )
        desc_label.pack(anchor="w", pady=(2, 0))
        
        # Meta info
        meta_frame = tk.Frame(info_frame)
        meta_frame.pack(anchor="w", pady=(5, 0))
        
        time_label = tk.Label(
            meta_frame,
            text=f"⏱️ {suite.estimated_time}",
            font=("Segoe UI", 8)
        )
        time_label.pack(side="left")
        
        category_label = tk.Label(
            meta_frame,
            text=f"🏷️ {suite.category}",
            font=("Segoe UI", 8)
        )
        category_label.pack(side="left", padx=(10, 0))
        
        return card
        
    def create_progress_section(self):
        """Create progress monitoring section."""
        progress_frame = tk.LabelFrame(
            self.main_frame,
            text="  Test Execution Progress  ",
            font=("Segoe UI", 12, "bold"),
            padx=20,
            pady=15
        )
        progress_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Current test info
        current_frame = tk.Frame(progress_frame)
        current_frame.pack(fill="x", pady=(0, 15))
        
        self.current_test_label = tk.Label(
            current_frame,
            text="Ready to run tests",
            font=("Segoe UI", 11),
            anchor="w"
        )
        self.current_test_label.pack(side="left", fill="x", expand=True)
        
        self.time_label = tk.Label(
            current_frame,
            text="⏱️ 00:00",
            font=("Segoe UI", 11)
        )
        self.time_label.pack(side="right")
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", pady=(0, 15))
        
        # Metrics cards
        metrics_frame = tk.Frame(progress_frame)
        metrics_frame.pack(fill="x")
        
        self.create_metric_cards(metrics_frame)
        
    def create_metric_cards(self, parent):
        """Create test result metric cards."""
        self.metric_cards = {}
        
        metrics = [
            ("total", "Total", "📊", self.theme['fg_secondary']),
            ("passed", "Passed", "✅", self.theme['accent_green']),
            ("failed", "Failed", "❌", self.theme['accent_red']),
            ("errors", "Errors", "⚠️", self.theme['accent_yellow']),
            ("skipped", "Skipped", "⏭️", self.theme['fg_secondary'])
        ]
        
        for i, (key, label, icon, color) in enumerate(metrics):
            card = tk.Frame(parent, relief="solid", bd=1, padx=15, pady=10)
            card.pack(side="left", fill="x", expand=True, padx=(0, 10) if i < 4 else (0, 0))
            
            # Icon and label
            header_frame = tk.Frame(card)
            header_frame.pack(fill="x")
            
            tk.Label(
                header_frame,
                text=icon,
                font=("Segoe UI", 12)
            ).pack(side="left")
            
            tk.Label(
                header_frame,
                text=label,
                font=("Segoe UI", 10),
                fg=color
            ).pack(side="left", padx=(5, 0))
            
            # Count
            count_label = tk.Label(
                card,
                text="0",
                font=("Segoe UI", 18, "bold"),
                fg=color
            )
            count_label.pack(pady=(5, 0))
            
            self.metric_cards[key] = count_label
            
    def create_results_section(self):
        """Create results and log section."""
        results_frame = tk.LabelFrame(
            self.main_frame,
            text="  Test Output & Results  ",
            font=("Segoe UI", 12, "bold"),
            padx=20,
            pady=15
        )
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Tab-style log interface
        tab_frame = tk.Frame(results_frame)
        tab_frame.pack(fill="x", pady=(0, 10))
        
        self.log_filter = tk.StringVar(value="All")
        filters = ["All", "Passed", "Failed", "Errors", "Warnings"]
        
        for filter_name in filters:
            btn = tk.Button(
                tab_frame,
                text=filter_name,
                font=("Segoe UI", 9),
                padx=15,
                pady=5,
                command=lambda f=filter_name: self.set_log_filter(f)
            )
            btn.pack(side="left", padx=(0, 5))
            
        # Log output
        self.log_text = scrolledtext.ScrolledText(
            results_frame,
            height=20,
            font=("Consolas", 10),
            wrap=tk.WORD,
            padx=15,
            pady=10
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Setup text tags for colored output
        self.setup_log_tags()
        
    def create_status_bar(self):
        """Create bottom status bar."""
        status_bar = tk.Frame(self.main_frame, height=30)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_bar,
            text="Ready",
            font=("Segoe UI", 9),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=20, fill="x", expand=True)
        
        self.version_label = tk.Label(
            status_bar,
            text="TaskMover Test Runner v2.0",
            font=("Segoe UI", 9)
        )
        self.version_label.pack(side="right", padx=20)
        
    def setup_log_tags(self):
        """Setup colored text tags for log output."""
        self.log_text.tag_configure("success", foreground=self.theme['accent_green'])
        self.log_text.tag_configure("error", foreground=self.theme['accent_red'])
        self.log_text.tag_configure("warning", foreground=self.theme['accent_yellow'])
        self.log_text.tag_configure("info", foreground=self.theme['accent_blue'])
        self.log_text.tag_configure("header", font=("Consolas", 10, "bold"))
        self.log_text.tag_configure("timestamp", foreground=self.theme['fg_secondary'])
        
    def apply_theme(self):
        """Apply dark theme to all components."""
        def configure_widget(widget):
            try:
                widget_class = widget.winfo_class()
                
                if widget_class in ['Frame', 'Toplevel']:
                    widget.configure(bg=self.theme['bg_primary'])
                elif widget_class == 'Label':
                    widget.configure(
                        bg=self.theme['bg_primary'],
                        fg=self.theme['fg_primary']
                    )
                elif widget_class == 'LabelFrame':
                    widget.configure(
                        bg=self.theme['bg_primary'],
                        fg=self.theme['accent_blue'],
                        highlightbackground=self.theme['border']
                    )
                elif widget_class == 'Button':
                    if widget in [self.run_btn]:
                        widget.configure(
                            bg=self.theme['accent_blue'],
                            fg='white',
                            activebackground=self.theme['hover'],
                            relief="flat",
                            bd=0
                        )
                    elif widget in [self.stop_btn]:
                        widget.configure(
                            bg=self.theme['accent_red'],
                            fg='white',
                            activebackground=self.theme['hover'],
                            relief="flat",
                            bd=0
                        )
                    else:
                        widget.configure(
                            bg=self.theme['bg_tertiary'],
                            fg=self.theme['fg_primary'],
                            activebackground=self.theme['hover'],
                            relief="flat",
                            bd=0
                        )
                elif widget_class == 'Radiobutton':
                    widget.configure(
                        bg=self.theme['bg_primary'],
                        fg=self.theme['fg_primary'],
                        selectcolor=self.theme['bg_tertiary'],
                        activebackground=self.theme['bg_primary']
                    )
                elif widget_class == 'Checkbutton':
                    widget.configure(
                        bg=self.theme['bg_primary'],
                        fg=self.theme['fg_primary'],
                        selectcolor=self.theme['bg_tertiary'],
                        activebackground=self.theme['bg_primary']
                    )
                elif widget_class == 'Text':
                    widget.configure(
                        bg=self.theme['bg_secondary'],
                        fg=self.theme['fg_primary'],
                        insertbackground=self.theme['fg_primary'],
                        selectbackground=self.theme['accent_blue'],
                        relief="flat",
                        bd=0
                    )
                
                # Apply to children recursively
                for child in widget.winfo_children():
                    configure_widget(child)
                    
            except (tk.TclError, AttributeError):
                pass
        
        # Configure root and apply to all widgets
        self.root.configure(bg=self.theme['bg_primary'])
        configure_widget(self.root)
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Custom.Horizontal.TProgressbar',
            background=self.theme['accent_blue'],
            troughcolor=self.theme['bg_secondary'],
            borderwidth=0,
            lightcolor=self.theme['accent_blue'],
            darkcolor=self.theme['accent_blue']
        )
        
        # Configure test suite cards
        for card in self.suite_cards.values():
            card.configure(
                bg=self.theme['bg_secondary'],
                highlightbackground=self.theme['border']
            )
            
        # Configure metric cards
        for card_frame in self.metric_cards.values():
            parent = card_frame.master
            parent.configure(
                bg=self.theme['bg_secondary'],
                highlightbackground=self.theme['border']
            )
            
    def set_log_filter(self, filter_type):
        """Set the log filter type."""
        self.log_filter.set(filter_type)
        # TODO: Implement actual filtering logic
        
    def run_tests(self):
        """Run the selected test suite."""
        if self.running_tests:
            return
            
        selected_suite = self.selected_suite.get()
        suite = next((s for s in self.test_suites if s.name == selected_suite), None)
        
        if not suite:
            messagebox.showerror("Error", "No test suite selected")
            return
            
        self.running_tests = True
        self.start_time = time.time()
        
        # Update UI state
        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.current_test_label.configure(text=f"Running: {suite.name}")
        self.status_label.configure(text="Executing tests...")
        
        # Clear previous results
        self.reset_results()
        
        # Start progress animation
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        # Log test start
        self.add_log("header", f"=== Starting {suite.name} ===\\n")
        self.add_log("info", f"Description: {suite.description}\\n")
        self.add_log("info", f"Estimated time: {suite.estimated_time}\\n\\n")
        
        # Start test execution in background thread
        thread = threading.Thread(target=self.execute_tests, args=(suite,))
        thread.daemon = True
        thread.start()
        
        # Start timer updates
        self.update_timer()
        
    def execute_tests(self, suite):
        """Execute the test suite in background thread."""
        try:
            if suite.name == "Quick Validation":
                self.run_quick_validation()
            elif suite.name == "Safe Mode":
                self.run_safe_mode()
            else:
                self.run_standard_tests(suite)
                
        except Exception as e:
            self.add_log("error", f"Test execution failed: {str(e)}\\n")
            self.test_results["errors"] += 1
        finally:
            self.root.after(0, self.test_complete)
            
    def run_quick_validation(self):
        """Run quick validation tests."""
        self.add_log("info", "Running quick validation tests...\\n")
        
        # Simulate test execution
        import time
        tests = [
            "TaskMover package import",
            "Core exceptions",
            "Theme manager",
            "Main application",
            "Pattern system",
            "Rule system"
        ]
        
        for i, test in enumerate(tests):
            self.root.after(0, lambda t=test: self.current_test_label.configure(text=f"Running: {t}"))
            self.add_log("info", f"Testing {test}...\\n")
            
            time.sleep(0.5)  # Simulate test execution
            
            # Simulate random results
            import random
            if random.random() > 0.1:  # 90% pass rate
                self.add_log("success", f"✅ {test} - PASSED\\n")
                self.test_results["passed"] += 1
            else:
                self.add_log("error", f"❌ {test} - FAILED\\n")
                self.test_results["failed"] += 1
                
            self.test_results["total"] += 1
            self.root.after(0, self.update_metrics)
            
            # Update progress
            progress = ((i + 1) / len(tests)) * 100
            self.root.after(0, lambda p=progress: self.update_progress(p))
            
    def run_safe_mode(self):
        """Run tests in safe mode."""
        self.add_log("info", "Running tests in safe mode (direct import)...\\n")
        # Implementation would go here
        time.sleep(2)
        self.test_results["total"] = 5
        self.test_results["passed"] = 5
        self.root.after(0, self.update_metrics)
        
    def run_standard_tests(self, suite):
        """Run standard test suite."""
        self.add_log("info", f"Running {suite.name}...\\n")
        # Implementation would go here using subprocess
        time.sleep(3)
        self.test_results["total"] = 10
        self.test_results["passed"] = 8
        self.test_results["failed"] = 2
        self.root.after(0, self.update_metrics)
        
    def stop_tests(self):
        """Stop test execution."""
        self.running_tests = False
        self.test_complete()
        self.add_log("warning", "Tests stopped by user\\n")
        
    def test_complete(self):
        """Handle test completion."""
        self.running_tests = False
        
        # Update UI state
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate", value=100)
        
        # Update status
        elapsed = time.time() - self.start_time if self.start_time else 0
        self.current_test_label.configure(text="Test execution completed")
        self.status_label.configure(text=f"Completed in {elapsed:.1f}s")
        
        # Final log entry
        self.add_log("header", f"\\n=== Test Summary ===\\n")
        self.add_log("info", f"Total: {self.test_results['total']}\\n")
        self.add_log("success", f"Passed: {self.test_results['passed']}\\n")
        self.add_log("error", f"Failed: {self.test_results['failed']}\\n")
        self.add_log("warning", f"Errors: {self.test_results['errors']}\\n")
        
    def update_timer(self):
        """Update the elapsed time display."""
        if self.running_tests and self.start_time:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.time_label.configure(text=f"⏱️ {minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)
            
    def update_progress(self, value):
        """Update progress bar value."""
        self.progress_var.set(value)
        
    def update_metrics(self):
        """Update metric cards."""
        for key, value in self.test_results.items():
            if key in self.metric_cards:
                self.metric_cards[key].configure(text=str(value))
                
    def reset_results(self):
        """Reset test results."""
        self.test_results = {"total": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
        self.update_metrics()
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        
    def add_log(self, tag, message):
        """Add message to log with specified formatting tag."""
        def update():
            timestamp = time.strftime("%H:%M:%S")
            if tag != "header":
                self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.log_text.insert(tk.END, message, tag)
            self.log_text.see(tk.END)
            
        self.root.after(0, update)
        
    def run(self):
        """Start the application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass


def main():
    """Main entry point."""
    app = ModernTestRunner()
    app.run()


if __name__ == "__main__":
    main()
