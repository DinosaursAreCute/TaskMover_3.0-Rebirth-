"""
UI Component Documentation Generator

This module generates comprehensive documentation for all TaskMover UI components,
including usage examples, API reference, and visual documentation.
"""

import os
import sys
import inspect
from typing import Dict, List, Any
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ComponentDocumentationGenerator:
    """Generates documentation for UI components."""
    
    def __init__(self, output_dir: str = "docs/ui_components"):
        self.output_dir = output_dir
        self.components_info = {}
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_all_documentation(self):
        """Generate complete documentation for all components."""
        print("Generating UI Component Documentation...")
        
        # Discover and document all components
        self._discover_components()
        self._generate_overview()
        self._generate_component_docs()
        self._generate_style_guide()
        self._generate_usage_examples()
        
        print(f"Documentation generated in: {self.output_dir}")
    
    def _discover_components(self):
        """Discover all UI components and their properties."""
        component_modules = [
            'ui.input_components',
            'ui.additional_input_components',
            'ui.display_components',
            'ui.layout_components',
            'ui.navigation_components',
            'ui.data_display_components',
            'ui.specialized_display_components',
            'ui.dialog_components',
            'ui.pattern_management_components',
            'ui.rule_management_components',
            'ui.ruleset_management_components',
            'ui.file_organization_components'
        ]
        
        for module_name in component_modules:
            try:
                module = __import__(module_name, fromlist=[''])
                self._extract_module_components(module, module_name)
            except ImportError as e:
                print(f"Could not import {module_name}: {e}")
    
    def _extract_module_components(self, module, module_name: str):
        """Extract component information from a module."""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if hasattr(obj, '__module__') and obj.__module__ == module_name:
                component_info = {
                    'name': name,
                    'module': module_name,
                    'docstring': inspect.getdoc(obj) or "No documentation available",
                    'methods': self._get_public_methods(obj),
                    'properties': self._get_properties(obj),
                    'constructor_params': self._get_constructor_params(obj)
                }
                self.components_info[name] = component_info
    
    def _get_public_methods(self, cls) -> List[Dict[str, str]]:
        """Get public methods of a class."""
        methods = []
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            if not name.startswith('_'):
                methods.append({
                    'name': name,
                    'docstring': inspect.getdoc(method) or "No documentation",
                    'signature': str(inspect.signature(method))
                })
        return methods
    
    def _get_properties(self, cls) -> List[str]:
        """Get properties of a class."""
        return [name for name, obj in inspect.getmembers(cls, inspect.isdatadescriptor)
                if not name.startswith('_')]
    
    def _get_constructor_params(self, cls) -> Dict[str, str]:
        """Get constructor parameters."""
        try:
            sig = inspect.signature(cls.__init__)
            params = {}
            for name, param in sig.parameters.items():
                if name != 'self':
                    params[name] = {
                        'type': str(param.annotation) if param.annotation != param.empty else 'Any',
                        'default': str(param.default) if param.default != param.empty else 'Required'
                    }
            return params
        except Exception:
            return {}
    
    def _generate_overview(self):
        """Generate overview documentation."""
        overview_content = self._create_overview_content()
        
        with open(os.path.join(self.output_dir, "README.md"), 'w') as f:
            f.write(overview_content)
    
    def _create_overview_content(self) -> str:
        """Create overview documentation content."""
        content = """# TaskMover UI Components Documentation

## Overview

This documentation provides comprehensive information about all TaskMover UI components,
including usage examples, API reference, and best practices.

## Component Categories

### Input Components
Components for user input and interaction:
"""
        
        # Group components by category
        categories = {
            'Input': ['CustomEntry', 'CustomButton', 'CustomCheckbox', 'CustomRadioButton', 'CustomCombobox',
                     'FileSelector', 'DateTimePicker', 'ColorPicker', 'SliderInput', 'SearchBox'],
            'Display': ['CustomLabel', 'IconLabel', 'StatusIndicator', 'ProgressBar', 'Badge', 'Tooltip'],
            'Layout': ['Panel', 'Splitter', 'TabContainer', 'Accordion', 'Card', 'GroupBox'],
            'Navigation': ['MenuBar', 'ContextMenu', 'Toolbar', 'Breadcrumb', 'Sidebar', 'StatusBar'],
            'Data Display': ['DataTable', 'ListView', 'TreeView', 'PropertyGrid', 'Chart'],
            'Specialized': ['FileList', 'PreviewPane', 'LogViewer', 'ConsoleOutput', 'ImageViewer'],
            'Dialogs': ['MessageDialog', 'ConfirmationDialog', 'InputDialog', 'FileDialog', 
                       'SettingsDialog', 'AboutDialog', 'ProgressDialog', 'ErrorDialog'],
            'Pattern Management': ['PatternEditor', 'PatternList', 'PatternTester', 'PatternBuilder'],
            'Rule Management': ['RuleEditor', 'RuleList', 'ConditionBuilder', 'ActionSelector'],
            'Ruleset Management': ['RulesetEditor', 'RulesetList', 'RulesetImportExport', 'RulesetValidation'],
            'File Organization': ['FileOrganizer', 'SourceSelector', 'DestinationBuilder', 
                                'OperationPreview', 'ExecutionMonitor']
        }
        
        for category, components in categories.items():
            content += f"\n### {category} Components\n"
            for component in components:
                if component in self.components_info:
                    info = self.components_info[component]
                    short_desc = info['docstring'].split('.')[0] if info['docstring'] else "No description"
                    content += f"- **{component}**: {short_desc}\n"
                else:
                    content += f"- **{component}**: Component definition\n"
        
        content += """
## Quick Start

```python
from ui.input_components import CustomEntry, CustomButton
from ui.layout_components import Panel
from ui.theme_manager import ThemeManager

# Create a simple form
panel = Panel(parent)
entry = CustomEntry(panel, placeholder="Enter text...")
button = CustomButton(panel, text="Submit")

# Apply theme
theme_manager = ThemeManager()
theme_manager.apply_theme(panel, "modern")
```

## Architecture

The UI system is built on the following principles:

1. **Component-Based**: Each UI element is a reusable component
2. **Theme-Driven**: Consistent styling through theme system
3. **Event-Driven**: Components communicate through events
4. **Accessible**: Built-in accessibility features
5. **Responsive**: Adapts to different screen sizes

## Documentation Structure

- `components/` - Individual component documentation
- `examples/` - Usage examples and code samples
- `style-guide/` - Visual style guide and design patterns
- `api/` - Complete API reference

For detailed information about specific components, see the individual component documentation files.
"""
        
        return content
    
    def _generate_component_docs(self):
        """Generate individual component documentation."""
        components_dir = os.path.join(self.output_dir, "components")
        os.makedirs(components_dir, exist_ok=True)
        
        for component_name, info in self.components_info.items():
            doc_content = self._create_component_doc(component_name, info)
            
            filename = f"{component_name.lower()}.md"
            with open(os.path.join(components_dir, filename), 'w') as f:
                f.write(doc_content)
    
    def _create_component_doc(self, name: str, info: Dict[str, Any]) -> str:
        """Create documentation for a single component."""
        content = f"""# {name}

## Description
{info['docstring']}

## Module
`{info['module']}`

## Constructor Parameters
"""
        
        if info['constructor_params']:
            content += "| Parameter | Type | Default | Description |\n"
            content += "|-----------|------|---------|-------------|\n"
            for param, details in info['constructor_params'].items():
                content += f"| `{param}` | {details['type']} | {details['default']} | Parameter description |\n"
        else:
            content += "No documented parameters.\n"
        
        content += "\n## Methods\n"
        if info['methods']:
            for method in info['methods']:
                content += f"### {method['name']}{method['signature']}\n"
                content += f"{method['docstring']}\n\n"
        else:
            content += "No public methods documented.\n"
        
        content += "\n## Properties\n"
        if info['properties']:
            for prop in info['properties']:
                content += f"- `{prop}`\n"
        else:
            content += "No properties documented.\n"
        
        content += f"""
## Usage Example

```python
from {info['module']} import {name}

# Basic usage
component = {name}(parent)
component.pack()

# With configuration
component.configure(
    # Add relevant configuration options
)
```

## See Also
- [Component Gallery](../gallery.md)
- [Style Guide](../style-guide/README.md)
- [Examples](../examples/{name.lower()}.py)
"""
        
        return content
    
    def _generate_style_guide(self):
        """Generate visual style guide."""
        style_dir = os.path.join(self.output_dir, "style-guide")
        os.makedirs(style_dir, exist_ok=True)
        
        style_content = """# TaskMover UI Style Guide

## Design Principles

### 1. Consistency
All components follow consistent design patterns for:
- Color usage
- Typography
- Spacing
- Interactive states

### 2. Accessibility
- High contrast ratios
- Keyboard navigation
- Screen reader support
- Focus indicators

### 3. Responsiveness
- Adaptive layouts
- Scalable components
- Flexible sizing

## Color Palette

### Light Theme
- **Primary**: #2196F3 (Blue)
- **Secondary**: #4CAF50 (Green)
- **Accent**: #FF9800 (Orange)
- **Background**: #FFFFFF (White)
- **Surface**: #F5F5F5 (Light Gray)
- **Text**: #333333 (Dark Gray)

### Dark Theme
- **Primary**: #1976D2 (Dark Blue)
- **Secondary**: #388E3C (Dark Green)
- **Accent**: #F57C00 (Dark Orange)
- **Background**: #121212 (Dark Gray)
- **Surface**: #1E1E1E (Darker Gray)
- **Text**: #FFFFFF (White)

## Typography

### Font Hierarchy
- **Heading 1**: Arial, 24px, Bold
- **Heading 2**: Arial, 18px, Bold
- **Heading 3**: Arial, 16px, Bold
- **Body Text**: Arial, 12px, Regular
- **Caption**: Arial, 10px, Regular

## Spacing System

### Padding and Margins
- **XS**: 4px
- **SM**: 8px
- **MD**: 16px
- **LG**: 24px
- **XL**: 32px

### Component Spacing
- Form elements: 8px vertical spacing
- Sections: 16px vertical spacing
- Panels: 24px padding

## Component States

### Interactive States
1. **Default**: Normal appearance
2. **Hover**: Slight color change, subtle elevation
3. **Active**: Pressed appearance
4. **Focus**: Clear focus indicator
5. **Disabled**: Reduced opacity, no interaction

### Validation States
1. **Success**: Green border/background
2. **Warning**: Orange border/background
3. **Error**: Red border/background
4. **Info**: Blue border/background

## Layout Guidelines

### Grid System
- 12-column responsive grid
- Flexible gutters (16px default)
- Breakpoints: 768px, 1024px, 1200px

### Component Sizing
- Minimum touch target: 44px
- Button height: 32px
- Input height: 28px
- Icon size: 16px, 24px, 32px

## Animation Guidelines

### Timing
- Quick interactions: 150ms
- Standard transitions: 250ms
- Complex animations: 350ms

### Easing
- Ease-out for entering elements
- Ease-in for exiting elements
- Ease-in-out for state changes
"""
        
        with open(os.path.join(style_dir, "README.md"), 'w') as f:
            f.write(style_content)
    
    def _generate_usage_examples(self):
        """Generate usage examples."""
        examples_dir = os.path.join(self.output_dir, "examples")
        os.makedirs(examples_dir, exist_ok=True)
        
        # Create example files for major component categories
        examples = {
            "basic_form.py": self._create_basic_form_example(),
            "data_display.py": self._create_data_display_example(),
            "layout_demo.py": self._create_layout_demo_example(),
            "dialog_examples.py": self._create_dialog_examples(),
            "advanced_features.py": self._create_advanced_features_example()
        }
        
        for filename, content in examples.items():
            with open(os.path.join(examples_dir, filename), 'w') as f:
                f.write(content)
    
    def _create_basic_form_example(self) -> str:
        """Create basic form example."""
        return '''"""
Basic Form Example

Demonstrates how to create a simple form using TaskMover UI components.
"""

import tkinter as tk
from ui.input_components import CustomEntry, CustomButton, CustomCheckbox
from ui.layout_components import Panel
from ui.display_components import CustomLabel

class BasicFormExample:
    def __init__(self, parent):
        self.parent = parent
        self.create_form()
    
    def create_form(self):
        # Main panel
        form_panel = Panel(self.parent, title="User Registration")
        form_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Name field
        name_label = CustomLabel(form_panel, text="Full Name:")
        name_label.pack(anchor="w", pady=(10, 2))
        
        self.name_entry = CustomEntry(form_panel, placeholder="Enter your full name")
        self.name_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Email field
        email_label = CustomLabel(form_panel, text="Email:")
        email_label.pack(anchor="w", pady=(0, 2))
        
        self.email_entry = CustomEntry(form_panel, placeholder="Enter your email")
        self.email_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Newsletter checkbox
        self.newsletter_check = CustomCheckbox(
            form_panel,
            text="Subscribe to newsletter"
        )
        self.newsletter_check.pack(anchor="w", pady=10)
        
        # Submit button
        submit_btn = CustomButton(
            form_panel,
            text="Register",
            command=self.submit_form
        )
        submit_btn.pack(pady=20)
    
    def submit_form(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        newsletter = self.newsletter_check.get()
        
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Newsletter: {newsletter}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Basic Form Example")
    root.geometry("400x300")
    
    example = BasicFormExample(root)
    root.mainloop()
'''
    
    def _create_data_display_example(self) -> str:
        """Create data display example."""
        return '''"""
Data Display Example

Demonstrates how to display data using TaskMover UI components.
"""

import tkinter as tk
from ui.data_display_components import DataTable, ListView
from ui.layout_components import Panel, Splitter

class DataDisplayExample:
    def __init__(self, parent):
        self.parent = parent
        self.create_display()
    
    def create_display(self):
        # Create splitter for side-by-side display
        splitter = Splitter(self.parent, orient="horizontal")
        splitter.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel with list view
        left_panel = Panel(splitter, title="File List")
        self.create_list_view(left_panel)
        
        # Right panel with data table
        right_panel = Panel(splitter, title="File Details")
        self.create_data_table(right_panel)
        
        splitter.add(left_panel)
        splitter.add(right_panel)
    
    def create_list_view(self, parent):
        files = [
            "document1.pdf",
            "image1.jpg",
            "spreadsheet1.xlsx",
            "presentation1.pptx",
            "archive1.zip"
        ]
        
        list_view = ListView(parent, items=files)
        list_view.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_data_table(self, parent):
        data = [
            {"Name": "document1.pdf", "Size": "2.3 MB", "Modified": "2024-01-15"},
            {"Name": "image1.jpg", "Size": "1.8 MB", "Modified": "2024-01-14"},
            {"Name": "spreadsheet1.xlsx", "Size": "456 KB", "Modified": "2024-01-13"},
            {"Name": "presentation1.pptx", "Size": "5.2 MB", "Modified": "2024-01-12"},
            {"Name": "archive1.zip", "Size": "12.1 MB", "Modified": "2024-01-11"}
        ]
        
        table = DataTable(parent, data=data)
        table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Data Display Example")
    root.geometry("800x600")
    
    example = DataDisplayExample(root)
    root.mainloop()
'''
    
    def _create_layout_demo_example(self) -> str:
        """Create layout demo example."""
        return '''"""
Layout Demo Example

Demonstrates various layout options using TaskMover UI components.
"""

import tkinter as tk
from ui.layout_components import Panel, TabContainer, Accordion, Card
from ui.display_components import CustomLabel

class LayoutDemoExample:
    def __init__(self, parent):
        self.parent = parent
        self.create_layout_demo()
    
    def create_layout_demo(self):
        # Main tab container
        tab_container = TabContainer(self.parent)
        tab_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel demo tab
        self.create_panel_demo(tab_container)
        
        # Accordion demo tab
        self.create_accordion_demo(tab_container)
        
        # Card layout demo tab
        self.create_card_demo(tab_container)
    
    def create_panel_demo(self, parent):
        frame = tk.Frame(parent)
        parent.add(frame, text="Panels")
        
        # Nested panels
        outer_panel = Panel(frame, title="Outer Panel")
        outer_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        inner_panel1 = Panel(outer_panel, title="Inner Panel 1")
        inner_panel1.pack(fill=tk.X, padx=10, pady=5)
        
        CustomLabel(inner_panel1, text="Content in first inner panel").pack(pady=10)
        
        inner_panel2 = Panel(outer_panel, title="Inner Panel 2")
        inner_panel2.pack(fill=tk.X, padx=10, pady=5)
        
        CustomLabel(inner_panel2, text="Content in second inner panel").pack(pady=10)
    
    def create_accordion_demo(self, parent):
        frame = tk.Frame(parent)
        parent.add(frame, text="Accordion")
        
        accordion = Accordion(frame)
        accordion.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add accordion sections
        sections = [
            ("Section 1", "This is the content of the first section."),
            ("Section 2", "This is the content of the second section."),
            ("Section 3", "This is the content of the third section.")
        ]
        
        for title, content in sections:
            section_frame = tk.Frame(accordion)
            CustomLabel(section_frame, text=content).pack(pady=20)
            accordion.add_section(title, section_frame)
    
    def create_card_demo(self, parent):
        frame = tk.Frame(parent)
        parent.add(frame, text="Cards")
        
        # Create a grid of cards
        for i in range(6):
            row = i // 3
            col = i % 3
            
            card = Card(frame, title=f"Card {i+1}")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            CustomLabel(card, text=f"Content for card {i+1}").pack(pady=20)
        
        # Configure grid weights
        for i in range(3):
            frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            frame.grid_rowconfigure(i, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Layout Demo Example")
    root.geometry("900x700")
    
    example = LayoutDemoExample(root)
    root.mainloop()
'''
    
    def _create_dialog_examples(self) -> str:
        """Create dialog examples."""
        return '''"""
Dialog Examples

Demonstrates various dialog types using TaskMover UI components.
"""

import tkinter as tk
from ui.input_components import CustomButton
from ui.dialog_components import MessageDialog, ConfirmationDialog, InputDialog
from ui.layout_components import Panel

class DialogExamples:
    def __init__(self, parent):
        self.parent = parent
        self.create_dialog_buttons()
    
    def create_dialog_buttons(self):
        panel = Panel(self.parent, title="Dialog Examples")
        panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Message dialog button
        msg_btn = CustomButton(
            panel,
            text="Show Message Dialog",
            command=self.show_message_dialog
        )
        msg_btn.pack(pady=10)
        
        # Confirmation dialog button
        confirm_btn = CustomButton(
            panel,
            text="Show Confirmation Dialog",
            command=self.show_confirmation_dialog
        )
        confirm_btn.pack(pady=10)
        
        # Input dialog button
        input_btn = CustomButton(
            panel,
            text="Show Input Dialog",
            command=self.show_input_dialog
        )
        input_btn.pack(pady=10)
    
    def show_message_dialog(self):
        dialog = MessageDialog(
            self.parent,
            title="Information",
            message="This is a sample message dialog."
        )
        dialog.show()
    
    def show_confirmation_dialog(self):
        dialog = ConfirmationDialog(
            self.parent,
            title="Confirm Action",
            message="Are you sure you want to proceed?"
        )
        result = dialog.show()
        print(f"Confirmation result: {result}")
    
    def show_input_dialog(self):
        dialog = InputDialog(
            self.parent,
            title="Enter Value",
            message="Please enter a value:",
            default_value="Default text"
        )
        result = dialog.show()
        print(f"Input result: {result}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Dialog Examples")
    root.geometry("400x300")
    
    example = DialogExamples(root)
    root.mainloop()
'''
    
    def _create_advanced_features_example(self) -> str:
        """Create advanced features example."""
        return '''"""
Advanced Features Example

Demonstrates advanced UI features like drag & drop, multi-selection, etc.
"""

import tkinter as tk
from ui.advanced_ui_features import DragDropManager, MultiSelectionManager
from ui.input_components import CustomButton
from ui.layout_components import Panel

class AdvancedFeaturesExample:
    def __init__(self, parent):
        self.parent = parent
        self.create_advanced_demo()
    
    def create_advanced_demo(self):
        # Main panel
        main_panel = Panel(self.parent, title="Advanced Features Demo")
        main_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Drag & Drop demo
        self.create_drag_drop_demo(main_panel)
        
        # Multi-selection demo
        self.create_multi_selection_demo(main_panel)
        
        # Keyboard navigation demo
        self.create_keyboard_nav_demo(main_panel)
    
    def create_drag_drop_demo(self, parent):
        # Drag & Drop section
        dd_frame = tk.LabelFrame(parent, text="Drag & Drop Demo", padx=10, pady=10)
        dd_frame.pack(fill=tk.X, pady=10)
        
        # Source area
        source_frame = tk.Frame(dd_frame, bg="lightblue", height=100)
        source_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        source_frame.pack_propagate(False)
        
        tk.Label(source_frame, text="Drag from here", bg="lightblue").pack(expand=True)
        
        # Target area
        target_frame = tk.Frame(dd_frame, bg="lightgreen", height=100)
        target_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        target_frame.pack_propagate(False)
        
        tk.Label(target_frame, text="Drop here", bg="lightgreen").pack(expand=True)
        
        # Initialize drag & drop
        dd_manager = DragDropManager()
        dd_manager.make_draggable(source_frame)
        dd_manager.make_drop_target(target_frame, self.on_drop)
    
    def create_multi_selection_demo(self, parent):
        # Multi-selection section
        ms_frame = tk.LabelFrame(parent, text="Multi-Selection Demo", padx=10, pady=10)
        ms_frame.pack(fill=tk.X, pady=10)
        
        # List with multi-selection
        listbox = tk.Listbox(ms_frame, selectmode=tk.EXTENDED, height=6)
        listbox.pack(fill=tk.X, pady=5)
        
        for i in range(10):
            listbox.insert(tk.END, f"Selectable Item {i+1}")
        
        # Selection manager
        ms_manager = MultiSelectionManager()
        ms_manager.enable_multi_selection(listbox)
        
        # Button to get selected items
        get_selection_btn = CustomButton(
            ms_frame,
            text="Get Selected Items",
            command=lambda: self.show_selection(listbox)
        )
        get_selection_btn.pack(pady=5)
    
    def create_keyboard_nav_demo(self, parent):
        # Keyboard navigation section
        kb_frame = tk.LabelFrame(parent, text="Keyboard Navigation Demo", padx=10, pady=10)
        kb_frame.pack(fill=tk.X, pady=10)
        
        # Info label
        info_label = tk.Label(
            kb_frame,
            text="Use Tab/Shift+Tab to navigate, Enter/Space to activate",
            fg="blue"
        )
        info_label.pack(pady=5)
        
        # Navigable buttons
        button_frame = tk.Frame(kb_frame)
        button_frame.pack(pady=5)
        
        for i in range(3):
            btn = CustomButton(
                button_frame,
                text=f"Button {i+1}",
                command=lambda x=i: print(f"Button {x+1} activated")
            )
            btn.grid(row=0, column=i, padx=5)
            
            # Add keyboard bindings
            btn.bind('<Return>', lambda e, x=i: print(f"Button {x+1} activated via Enter"))
            btn.bind('<space>', lambda e, x=i: print(f"Button {x+1} activated via Space"))
    
    def on_drop(self, event):
        print("Item dropped!")
        tk.messagebox.showinfo("Drop Event", "Item was successfully dropped!")
    
    def show_selection(self, listbox):
        selected = [listbox.get(i) for i in listbox.curselection()]
        if selected:
            items = ", ".join(selected)
            tk.messagebox.showinfo("Selected Items", f"Selected: {items}")
        else:
            tk.messagebox.showinfo("Selected Items", "No items selected")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Advanced Features Example")
    root.geometry("600x700")
    
    example = AdvancedFeaturesExample(root)
    root.mainloop()
'''


def main():
    """Main entry point for documentation generation."""
    generator = ComponentDocumentationGenerator()
    generator.generate_all_documentation()


if __name__ == "__main__":
    main()
