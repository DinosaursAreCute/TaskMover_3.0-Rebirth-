"""
TaskMover UI Component Gallery and Demo

This module provides a comprehensive visual showcase of all TaskMover UI components,
serving as both a testing framework and documentation tool.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the parent directory to the path to import our components
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the parent directories to the path to import our components
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, grandparent_dir)
sys.path.insert(0, parent_dir)

# Import only classes that actually exist
try:
    from taskmover.ui.theme_manager import ThemeManager, ThemeMode
    from taskmover.ui.input_components import TextInput, TextArea, Button, IconButton, Checkbox, RadioButton
    from taskmover.ui.display_components import Label, Badge, Tooltip, ProgressBar, StatusIndicator
    from taskmover.ui.layout_components import Panel
    from taskmover.ui.navigation_components import Breadcrumb
    from taskmover.ui.data_display_components import DataTable, ListView, TreeView
    from taskmover.ui.dialog_components import MessageDialog, ConfirmationDialog, InputDialog, SettingsDialog, ProgressDialog
    
    # Set placeholders for missing components
    ContextMenu = PatternEditor = PatternList = PatternTester = PatternBuilder = None
    RuleEditor = RuleList = ConditionBuilder = ActionSelector = None
    RulesetEditor = RulesetList = RulesetImportExport = RulesetValidation = None
    FileOrganizer = SourceSelector = DestinationBuilder = OperationPreview = ExecutionMonitor = None
    PropertyGrid = None
    
except ImportError as e:
    print(f"Warning: Some imports failed: {e}")
    # Define placeholders for missing classes
    TextInput = TextArea = Button = IconButton = Checkbox = RadioButton = None
    Label = Badge = Tooltip = ProgressBar = StatusIndicator = None
    Panel = Breadcrumb = None
    DataTable = ListView = TreeView = PropertyGrid = None
    MessageDialog = ConfirmationDialog = InputDialog = SettingsDialog = ProgressDialog = None
    PatternEditor = PatternList = PatternTester = PatternBuilder = None
    RuleEditor = RuleList = ConditionBuilder = ActionSelector = None
    RulesetEditor = RulesetList = RulesetImportExport = RulesetValidation = None
    FileOrganizer = SourceSelector = DestinationBuilder = OperationPreview = ExecutionMonitor = None
    ContextMenu = None


class ComponentGallery:
    """Main gallery application for showcasing all UI components."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TaskMover UI Component Gallery")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize theme manager
        try:
            if 'ThemeManager' in globals():
                self.theme_manager = ThemeManager()
            else:
                self.theme_manager = None
        except:
            self.theme_manager = None
        
        # Component categories for organization
        self.categories = {
            "Input Components": self._create_input_demo,
            "Display Components": self._create_display_demo,
            "Layout Components": self._create_layout_demo,
            "Navigation Components": self._create_navigation_demo,
            "Data Display": self._create_data_display_demo,
            "Specialized Display": self._create_specialized_demo,
            "Dialog Components": self._create_dialog_demo,
            "Pattern Management": self._create_pattern_demo,
            "Rule Management": self._create_rule_demo,
            "Ruleset Management": self._create_ruleset_demo,
            "File Organization": self._create_file_org_demo,
            "Advanced Features": self._create_advanced_demo
        }
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the main gallery interface."""
        # Create main layout
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="TaskMover UI Component Gallery",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="Visual showcase and testing framework for all UI components",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#666666"
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Theme toggle button
        theme_frame = tk.Frame(main_frame, bg="#f0f0f0")
        theme_frame.pack(pady=(0, 20))
        
        theme_button = tk.Button(
            theme_frame,
            text="Toggle Dark Mode",
            command=self._toggle_theme,
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        theme_button.pack()
        
        # Create notebook for categories
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Add tabs for each category
        for category_name, create_func in self.categories.items():
            tab_frame = tk.Frame(self.notebook, bg="white")
            self.notebook.add(tab_frame, text=category_name)
            
            # Create scrollable content for each tab
            canvas = tk.Canvas(tab_frame, bg="white")
            scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="white")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Populate the tab with components
            create_func(scrollable_frame)
            
            # Bind mousewheel to canvas
            canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
    
    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        if self.theme_manager:
            try:
                # Use the correct method name from ThemeManager
                current_mode = self.theme_manager.current_mode
                if 'ThemeMode' in globals():
                    new_mode = ThemeMode.DARK if current_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
                    self.theme_manager.set_theme_mode(new_mode)
                    print(f"Theme switched to: {new_mode.value}")
                else:
                    print("ThemeMode not available")
            except Exception as e:
                print(f"Theme switching error: {e}")
        else:
            print("Theme manager not available")
    
    def _create_section_header(self, parent, title, description=""):
        """Create a section header with title and optional description."""
        header_frame = tk.Frame(parent, bg="white")
        header_frame.pack(fill=tk.X, pady=(20, 10))
        
        title_label = tk.Label(
            header_frame,
            text=title,
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#333333"
        )
        title_label.pack(anchor="w")
        
        if description:
            desc_label = tk.Label(
                header_frame,
                text=description,
                font=("Arial", 10),
                bg="white",
                fg="#666666"
            )
            desc_label.pack(anchor="w", pady=(2, 0))
        
        # Separator line
        separator = tk.Frame(header_frame, height=1, bg="#dddddd")
        separator.pack(fill=tk.X, pady=(10, 0))
    
    def _create_component_demo(self, parent, component_class, title, description="", **kwargs):
        """Create a demo section for a specific component."""
        demo_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1)
        demo_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Component title
        title_label = tk.Label(
            demo_frame,
            text=title,
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        )
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Component description
        if description:
            desc_label = tk.Label(
                demo_frame,
                text=description,
                font=("Arial", 9),
                bg="white",
                fg="#666666",
                wraplength=500,
                justify=tk.LEFT
            )
            desc_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Component instance
        try:
            if component_class:
                component = component_class(demo_frame, **kwargs)
                if hasattr(component, 'pack'):
                    component.pack(padx=10, pady=10)
                elif hasattr(component, 'grid'):
                    component.grid(padx=10, pady=10)
            else:
                placeholder_label = tk.Label(
                    demo_frame,
                    text=f"{title} - Component placeholder",
                    font=("Arial", 10, "italic"),
                    bg="white",
                    fg="#888888"
                )
                placeholder_label.pack(padx=10, pady=10)
        except Exception as e:
            error_label = tk.Label(
                demo_frame,
                text=f"Error creating component: {str(e)}",
                font=("Arial", 9),
                bg="white",
                fg="red"
            )
            error_label.pack(padx=10, pady=10)
    
    def _create_input_demo(self, parent):
        """Create demo for input components."""
        self._create_section_header(
            parent,
            "Input Components",
            "Basic and advanced input controls for user interaction"
        )
        
        # Basic input components
        self._create_component_demo(
            parent, TextInput, "Text Input",
            "Enhanced text input with validation and styling"
        )
        
        self._create_component_demo(
            parent, Button, "Button",
            "Styled button with hover effects and themes"
        )
        
        self._create_component_demo(
            parent, Checkbox, "Checkbox",
            "Enhanced checkbox with custom styling"
        )
        
        self._create_component_demo(
            parent, RadioButton, "Radio Button",
            "Styled radio button for option selection"
        )
        
        self._create_component_demo(
            parent, TextArea, "Text Area",
            "Multi-line text input component"
        )
        
        # Additional input components
        self._create_component_demo(
            parent, None, "File Selector",
            "File and directory selection component"
        )
        
        self._create_component_demo(
            parent, None, "Date Time Picker",
            "Date and time selection widget"
        )
        
        self._create_component_demo(
            parent, None, "Color Picker",
            "Color selection interface"
        )
        
        self._create_component_demo(
            parent, None, "Slider Input",
            "Numeric input with slider control"
        )
        
        self._create_component_demo(
            parent, None, "Search Box",
            "Search input with autocomplete"
        )
    
    def _create_display_demo(self, parent):
        """Create demo for display components."""
        self._create_section_header(
            parent,
            "Display Components",
            "Components for displaying information and content"
        )
        
        self._create_component_demo(
            parent, Label, "Label",
            "Enhanced label with styling options"
        )
        
        self._create_component_demo(
            parent, StatusIndicator, "Status Indicator",
            "Visual status display with colors and icons"
        )
        
        self._create_component_demo(
            parent, ProgressBar, "Progress Bar",
            "Progress indication for long operations"
        )
        
        self._create_component_demo(
            parent, Badge, "Badge",
            "Small status or count indicator"
        )
        
        self._create_component_demo(
            parent, Tooltip, "Tooltip",
            "Hover information display"
        )
    
    def _create_layout_demo(self, parent):
        """Create demo for layout components."""
        self._create_section_header(
            parent,
            "Layout Components",
            "Containers and layout management components"
        )
        
        self._create_component_demo(
            parent, Panel, "Panel",
            "Basic container with styling"
        )
        
        self._create_component_demo(
            parent, None, "Splitter",
            "Resizable split container"
        )
        
        self._create_component_demo(
            parent, None, "Tab Container",
            "Tabbed interface container"
        )
        
        self._create_component_demo(
            parent, None, "Accordion",
            "Collapsible content sections"
        )
        
        self._create_component_demo(
            parent, None, "Card",
            "Content card with styling"
        )
        
        self._create_component_demo(
            parent, None, "Group Box",
            "Grouped content container"
        )
    
    def _create_navigation_demo(self, parent):
        """Create demo for navigation components."""
        self._create_section_header(
            parent,
            "Navigation Components",
            "Navigation and menu components"
        )
        
        self._create_component_demo(
            parent, None, "Menu Bar",
            "Application menu bar"
        )
        
        self._create_component_demo(
            parent, ContextMenu, "Context Menu",
            "Right-click context menu"
        )
        
        self._create_component_demo(
            parent, None, "Toolbar",
            "Tool and action bar"
        )
        
        self._create_component_demo(
            parent, Breadcrumb, "Breadcrumb",
            "Navigation breadcrumb trail"
        )
        
        self._create_component_demo(
            parent, None, "Sidebar",
            "Application sidebar navigation"
        )
        
        self._create_component_demo(
            parent, None, "Status Bar",
            "Application status bar"
        )
    
    def _create_data_display_demo(self, parent):
        """Create demo for data display components."""
        self._create_section_header(
            parent,
            "Data Display Components",
            "Components for displaying structured data"
        )
        
        # Sample data for demonstration
        sample_data = [
            {"name": "File1.txt", "size": "1.2 KB", "modified": "2024-01-15"},
            {"name": "Document.pdf", "size": "2.5 MB", "modified": "2024-01-14"},
            {"name": "Image.jpg", "size": "800 KB", "modified": "2024-01-13"}
        ]
        
        self._create_component_demo(
            parent, DataTable, "Data Table",
            "Sortable data table with selection",
            data=sample_data
        )
        
        self._create_component_demo(
            parent, ListView, "List View",
            "Flexible list display component",
            items=["Item 1", "Item 2", "Item 3"]
        )
        
        self._create_component_demo(
            parent, TreeView, "Tree View",
            "Hierarchical data display"
        )
        
        self._create_component_demo(
            parent, PropertyGrid, "Property Grid",
            "Key-value property editor"
        )
        
        self._create_component_demo(
            parent, None, "Chart",
            "Data visualization component"
        )
    
    def _create_specialized_demo(self, parent):
        """Create demo for specialized display components."""
        self._create_section_header(
            parent,
            "Specialized Display Components",
            "Specialized components for specific use cases"
        )
        
        self._create_component_demo(
            parent, None, "File List",
            "File listing with icons and details"
        )
        
        self._create_component_demo(
            parent, None, "Preview Pane",
            "File content preview component"
        )
        
        self._create_component_demo(
            parent, None, "Log Viewer",
            "Scrollable log display with filtering"
        )
        
        self._create_component_demo(
            parent, None, "Console Output",
            "Terminal-style output display"
        )
        
        self._create_component_demo(
            parent, None, "Image Viewer",
            "Image display with zoom and pan"
        )
    
    def _create_dialog_demo(self, parent):
        """Create demo for dialog components."""
        self._create_section_header(
            parent,
            "Dialog Components",
            "Modal dialogs and popup windows"
        )
        
        # Create buttons to show dialogs
        button_frame = tk.Frame(parent, bg="white")
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        dialogs = [
            ("Message Dialog", MessageDialog, "Show information dialog"),
            ("Confirmation Dialog", ConfirmationDialog, "Show yes/no confirmation"),
            ("Input Dialog", InputDialog, "Show text input dialog"),
            ("File Dialog", None, "Show file selection dialog"),
            ("Settings Dialog", SettingsDialog, "Show settings configuration"),
            ("About Dialog", None, "Show about information"),
            ("Progress Dialog", ProgressDialog, "Show progress indicator"),
            ("Error Dialog", None, "Show error message")
        ]
        
        for i, (name, dialog_class, description) in enumerate(dialogs):
            btn = tk.Button(
                button_frame,
                text=f"Show {name}",
                command=lambda d=dialog_class: self._show_dialog(d) if d else print(f"{name} - placeholder"),
                bg="#2196F3",
                fg="white",
                relief=tk.FLAT,
                padx=15,
                pady=5
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="ew")
            
        # Configure grid weights
        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1)
    
    def _create_pattern_demo(self, parent):
        """Create demo for pattern management components."""
        self._create_section_header(
            parent,
            "Pattern Management Components",
            "Components for managing file patterns and rules"
        )
        
        self._create_component_demo(
            parent, PatternEditor, "Pattern Editor",
            "Editor for file matching patterns"
        )
        
        self._create_component_demo(
            parent, PatternList, "Pattern List",
            "List of configured patterns"
        )
        
        self._create_component_demo(
            parent, PatternTester, "Pattern Tester",
            "Test patterns against sample files"
        )
        
        self._create_component_demo(
            parent, PatternBuilder, "Pattern Builder",
            "Visual pattern construction tool"
        )
    
    def _create_rule_demo(self, parent):
        """Create demo for rule management components."""
        self._create_section_header(
            parent,
            "Rule Management Components",
            "Components for creating and managing organization rules"
        )
        
        self._create_component_demo(
            parent, RuleEditor, "Rule Editor",
            "Editor for organization rules"
        )
        
        self._create_component_demo(
            parent, RuleList, "Rule List",
            "List of configured rules"
        )
        
        self._create_component_demo(
            parent, ConditionBuilder, "Condition Builder",
            "Visual rule condition builder"
        )
        
        self._create_component_demo(
            parent, ActionSelector, "Action Selector",
            "Selection of available actions"
        )
    
    def _create_ruleset_demo(self, parent):
        """Create demo for ruleset management components."""
        self._create_section_header(
            parent,
            "Ruleset Management Components",
            "Components for managing collections of rules"
        )
        
        self._create_component_demo(
            parent, RulesetEditor, "Ruleset Editor",
            "Editor for rule collections"
        )
        
        self._create_component_demo(
            parent, RulesetList, "Ruleset List",
            "List of available rulesets"
        )
        
        self._create_component_demo(
            parent, RulesetImportExport, "Ruleset Import/Export",
            "Import and export ruleset configurations"
        )
        
        self._create_component_demo(
            parent, RulesetValidation, "Ruleset Validation",
            "Validation and conflict detection"
        )
    
    def _create_file_org_demo(self, parent):
        """Create demo for file organization components."""
        self._create_section_header(
            parent,
            "File Organization Components",
            "Components for file organization operations"
        )
        
        self._create_component_demo(
            parent, FileOrganizer, "File Organizer",
            "Main file organization interface"
        )
        
        self._create_component_demo(
            parent, SourceSelector, "Source Selector",
            "Source directory selection"
        )
        
        self._create_component_demo(
            parent, DestinationBuilder, "Destination Builder",
            "Destination path construction"
        )
        
        self._create_component_demo(
            parent, OperationPreview, "Operation Preview",
            "Preview of organization operations"
        )
        
        self._create_component_demo(
            parent, ExecutionMonitor, "Execution Monitor",
            "Monitor organization execution"
        )
    
    def _create_advanced_demo(self, parent):
        """Create demo for advanced UI features."""
        self._create_section_header(
            parent,
            "Advanced UI Features",
            "Advanced interactions and behaviors"
        )
        
        # Create demo area for advanced features
        demo_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1)
        demo_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Drag and drop demo
        drag_label = tk.Label(
            demo_frame,
            text="Drag & Drop Demo Area",
            font=("Arial", 12, "bold"),
            bg="#e3f2fd",
            fg="#1976d2",
            relief=tk.RAISED,
            bd=2,
            height=3
        )
        drag_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Multi-selection demo
        selection_frame = tk.Frame(demo_frame, bg="white")
        selection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            selection_frame,
            text="Multi-Selection Demo:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).pack(anchor="w")
        
        # Sample list for multi-selection
        listbox = tk.Listbox(selection_frame, selectmode=tk.EXTENDED, height=4)
        listbox.pack(fill=tk.X, pady=5)
        for i in range(5):
            listbox.insert(tk.END, f"Item {i+1}")
        
        # Context menu demo
        context_label = tk.Label(
            demo_frame,
            text="Right-click for context menu",
            font=("Arial", 10),
            bg="#fff3e0",
            fg="#f57c00",
            relief=tk.RAISED,
            bd=1,
            height=2
        )
        context_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Keyboard navigation info
        kbd_label = tk.Label(
            demo_frame,
            text="Keyboard Navigation: Tab, Shift+Tab, Enter, Space, Arrow keys",
            font=("Arial", 9),
            bg="#f3e5f5",
            fg="#7b1fa2",
            relief=tk.RAISED,
            bd=1
        )
        kbd_label.pack(fill=tk.X, padx=10, pady=10)
    
    def _show_dialog(self, dialog_class):
        """Show a sample dialog."""
        try:
            if dialog_class == MessageDialog:
                dialog = dialog_class(self.root, "Sample Message", "This is a sample message dialog.")
            elif dialog_class == ConfirmationDialog:
                dialog = dialog_class(self.root, "Confirm Action", "Are you sure you want to proceed?")
            elif dialog_class == InputDialog:
                dialog = dialog_class(self.root, "Enter Value", "Please enter a value:")
            else:
                dialog = dialog_class(self.root)
            
            # Show dialog (implementation would depend on the dialog class)
            print(f"Showing {dialog_class.__name__}")
            
        except Exception as e:
            print(f"Error showing dialog: {e}")
    
    def run(self):
        """Run the gallery application."""
        self.root.mainloop()


def main():
    """Main entry point for the gallery application."""
    print("Starting TaskMover UI Component Gallery...")
    
    try:
        gallery = ComponentGallery()
        gallery.run()
    except Exception as e:
        print(f"Error running gallery: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
