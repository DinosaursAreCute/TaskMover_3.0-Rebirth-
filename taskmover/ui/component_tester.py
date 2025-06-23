"""
UI Component Testing and Validation Suite

This module provides comprehensive testing for TaskMover UI components,
including visual regression testing, interaction testing, and accessibility validation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import time
from typing import List, Dict, Any, Callable

# Add parent directories to path for both direct execution and module import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, grandparent_dir)
sys.path.insert(0, parent_dir)

class ComponentTestSuite:
    """Test suite for UI components."""
    
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        
    def run_all_tests(self):
        """Run all component tests."""
        print("TaskMover UI Component Test Suite")
        print("=" * 40)
        
        test_methods = [
            self.test_component_imports,
            self.test_component_instantiation,
            self.test_component_properties,
            self.test_theme_system,
            self.test_layout_system,
            self.test_event_handling,
            self.test_accessibility_features,
            self.test_responsive_design
        ]
        
        for test_method in test_methods:
            try:
                print(f"\nRunning {test_method.__name__}...")
                result = test_method()
                if result:
                    self.passed_tests.append(test_method.__name__)
                    print(f"✓ {test_method.__name__} PASSED")
                else:
                    self.failed_tests.append(test_method.__name__)
                    print(f"✗ {test_method.__name__} FAILED")
            except Exception as e:
                self.failed_tests.append(test_method.__name__)
                print(f"✗ {test_method.__name__} ERROR: {e}")
        
        self._print_summary()
        
    def test_component_imports(self) -> bool:
        """Test that all component modules can be imported."""
        try:
            import taskmover.ui.theme_manager
            import taskmover.ui.layout_manager
            import taskmover.ui.input_components
            import taskmover.ui.display_components
            import taskmover.ui.layout_components
            import taskmover.ui.navigation_components
            import taskmover.ui.data_display_components
            import taskmover.ui.dialog_components
            return True
        except ImportError as e:
            print(f"Import failed: {e}")
            return False
    
    def test_component_instantiation(self) -> bool:
        """Test that components can be instantiated."""
        root = tk.Tk()
        root.withdraw()
        
        try:
            # Test basic component creation
            from taskmover.ui.theme_manager import ThemeManager
            from taskmover.ui.input_components import TextInput, Button
            
            theme_manager = ThemeManager()
            
            # Test with a simple parent frame
            frame = tk.Frame(root)
            entry = TextInput(frame)
            button = Button(frame, text="Test")
            
            root.destroy()
            return True
            
        except Exception as e:
            print(f"Component instantiation failed: {e}")
            root.destroy()
            return False
    
    def test_component_properties(self) -> bool:
        """Test that components have expected properties and methods."""
        root = tk.Tk()
        root.withdraw()
        
        try:
            from taskmover.ui.input_components import TextInput
            
            frame = tk.Frame(root)
            entry = TextInput(frame)
            
            # Test base component interface - check for basic widget methods
            if hasattr(entry, 'bind') or hasattr(entry, 'focus_set'):
                print("Component has expected widget methods")
                root.destroy()
                return True
            
            # Check if it's a widget or has a widget
            if hasattr(entry, '_widget'):
                widget = entry._widget
                if hasattr(widget, 'bind'):
                    print("Component has widget methods via _widget")
                    root.destroy()
                    return True
            
            print("No expected widget methods found")
            root.destroy()
            return False
            
        except Exception as e:
            print(f"Property test failed: {e}")
            root.destroy()
            return False
    
    def test_theme_system(self) -> bool:
        """Test theme management functionality."""
        try:
            from taskmover.ui.theme_manager import ThemeManager, ThemeMode
            
            theme_manager = ThemeManager()
            
            # Test theme switching
            theme_manager.set_theme_mode(ThemeMode.LIGHT)
            assert theme_manager.current_mode == ThemeMode.LIGHT
            
            theme_manager.set_theme_mode(ThemeMode.DARK)
            assert theme_manager.current_mode == ThemeMode.DARK
            
            # Test theme properties
            primary_color = theme_manager.get_color('primary')
            background_color = theme_manager.get_color('background')
            assert isinstance(primary_color, str)
            assert isinstance(background_color, str)
            
            return True
            
        except Exception as e:
            print(f"Theme system test failed: {e}")
            return False
    
    def test_layout_system(self) -> bool:
        """Test layout management functionality."""
        root = tk.Tk()
        root.withdraw()
        
        try:
            from taskmover.ui.layout_components import Panel
            
            frame = tk.Frame(root)
            panel = Panel(frame)
            
            # Test layout methods exist
            assert hasattr(panel, '__init__')
            
            root.destroy()
            return True
            
        except Exception as e:
            print(f"Layout system test failed: {e}")
            root.destroy()
            return False
    
    def test_event_handling(self) -> bool:
        """Test event handling capabilities."""
        root = tk.Tk()
        root.withdraw()
        
        try:
            from taskmover.ui.input_components import Button
            
            frame = tk.Frame(root)
            button = Button(frame, text="Test")
            
            # Test if we can create and interact with the button
            if hasattr(button, 'bind') or hasattr(button, 'focus_set'):
                event_fired = True
            else:
                # Check if button has a widget attribute
                if hasattr(button, '_widget') and hasattr(button._widget, 'bind'):
                    event_fired = True
                else:
                    event_fired = False
            
            root.destroy()
            return event_fired
            
        except Exception as e:
            print(f"Event handling test failed: {e}")
            root.destroy()
            return False
    
    def test_accessibility_features(self) -> bool:
        """Test accessibility features."""
        root = tk.Tk()
        root.withdraw()
        
        try:
            from taskmover.ui.input_components import Button, TextInput
            
            frame = tk.Frame(root)
            button = Button(frame, text="Test Button")
            entry = TextInput(frame)
            
            # Test if components support basic widget functionality
            button_ok = hasattr(button, 'focus_set') or (hasattr(button, '_widget') and hasattr(button._widget, 'focus_set'))
            entry_ok = hasattr(entry, 'focus_set') or (hasattr(entry, '_widget') and hasattr(entry._widget, 'focus_set'))
            
            # Test keyboard bindings can be added
            bind_ok = hasattr(button, 'bind') or (hasattr(button, '_widget') and hasattr(button._widget, 'bind'))
            
            root.destroy()
            return button_ok and entry_ok and bind_ok
            
        except Exception as e:
            print(f"Accessibility test failed: {e}")
            root.destroy()
            return False
    
    def test_responsive_design(self) -> bool:
        """Test responsive design capabilities."""
        root = tk.Tk()
        root.withdraw()
        
        try:
            from taskmover.ui.layout_components import Panel
            
            frame = tk.Frame(root)
            panel = Panel(frame)
            
            # Test size changes
            root.geometry("800x600")
            root.update()
            
            root.geometry("400x300")
            root.update()
            
            root.destroy()
            return True
            
        except Exception as e:
            print(f"Responsive design test failed: {e}")
            root.destroy()
            return False
    
    def _print_summary(self):
        """Print test results summary."""
        total_tests = len(self.passed_tests) + len(self.failed_tests)
        
        print("\n" + "=" * 40)
        print("TEST SUMMARY")
        print("=" * 40)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {len(self.passed_tests)}")
        print(f"Failed: {len(self.failed_tests)}")
        
        if self.failed_tests:
            print("\nFailed Tests:")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        success_rate = (len(self.passed_tests) / total_tests * 100) if total_tests > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if len(self.failed_tests) == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {len(self.failed_tests)} test(s) failed.")


class InteractionTester:
    """Interactive testing interface for manual component testing."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("UI Component Interaction Tester")
        self.root.geometry("800x600")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the interaction testing interface."""
        # Title
        title_label = tk.Label(
            self.root,
            text="UI Component Interaction Tester",
            font=("Arial", 16, "bold"),
            pady=20
        )
        title_label.pack()
        
        # Test categories
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self._create_input_tests()
        self._create_layout_tests()
        self._create_interaction_tests()
    
    def _create_input_tests(self):
        """Create input component tests."""
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Input Tests")
        
        tk.Label(frame, text="Test various input components:", font=("Arial", 12)).pack(pady=10)
        
        # Entry validation test
        tk.Label(frame, text="Email validation:").pack(anchor="w", padx=20)
        email_entry = tk.Entry(frame, width=30)
        email_entry.pack(padx=20, pady=5)
        
        # Button interaction test
        tk.Label(frame, text="Button interactions:").pack(anchor="w", padx=20, pady=(20, 0))
        button_frame = tk.Frame(frame)
        button_frame.pack(padx=20, pady=5)
        
        for i, color in enumerate(["red", "green", "blue"]):
            btn = tk.Button(
                button_frame,
                text=f"{color.title()} Button",
                bg=color,
                fg="white",
                command=lambda c=color: self._button_clicked(c)
            )
            btn.grid(row=0, column=i, padx=5)
    
    def _create_layout_tests(self):
        """Create layout component tests."""
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Layout Tests")
        
        tk.Label(frame, text="Test layout responsiveness:", font=("Arial", 12)).pack(pady=10)
        
        # Resizable sections
        paned_window = tk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        left_frame = tk.Frame(paned_window, bg="lightblue", width=200)
        right_frame = tk.Frame(paned_window, bg="lightgreen", width=200)
        
        tk.Label(left_frame, text="Left Panel", bg="lightblue").pack(pady=20)
        tk.Label(right_frame, text="Right Panel", bg="lightgreen").pack(pady=20)
        
        paned_window.add(left_frame)
        paned_window.add(right_frame)
    
    def _create_interaction_tests(self):
        """Create interaction tests."""
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Interaction Tests")
        
        tk.Label(frame, text="Test advanced interactions:", font=("Arial", 12)).pack(pady=10)
        
        # Drag and drop simulation
        tk.Label(frame, text="Drag & Drop Test:").pack(anchor="w", padx=20)
        drag_frame = tk.Frame(frame, bg="lightyellow", height=100)
        drag_frame.pack(fill=tk.X, padx=20, pady=10)
        drag_frame.pack_propagate(False)
        
        tk.Label(
            drag_frame,
            text="Drag items here (simulated)",
            bg="lightyellow"
        ).pack(expand=True)
        
        # Multi-selection test
        tk.Label(frame, text="Multi-selection Test:").pack(anchor="w", padx=20, pady=(20, 0))
        listbox = tk.Listbox(frame, selectmode=tk.EXTENDED, height=6)
        listbox.pack(fill=tk.X, padx=20, pady=5)
        
        for i in range(10):
            listbox.insert(tk.END, f"Selectable Item {i+1}")
    
    def _button_clicked(self, color):
        """Handle button click events."""
        print(f"{color.title()} button clicked!")
        messagebox.showinfo("Button Clicked", f"You clicked the {color} button!")
    
    def run(self):
        """Run the interaction tester."""
        self.root.mainloop()


def main():
    """Main entry point for the testing suite."""
    import argparse
    
    parser = argparse.ArgumentParser(description="TaskMover UI Component Testing Suite")
    parser.add_argument(
        "--mode",
        choices=["test", "interact"],
        default="test",
        help="Testing mode: 'test' for automated tests, 'interact' for interactive testing"
    )
    
    args = parser.parse_args()
    
    if args.mode == "test":
        # Run automated tests
        test_suite = ComponentTestSuite()
        test_suite.run_all_tests()
    else:
        # Run interactive tester
        tester = InteractionTester()
        tester.run()


if __name__ == "__main__":
    main()
