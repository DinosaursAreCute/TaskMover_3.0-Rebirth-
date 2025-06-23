"""
TaskMover UI Framework - Rule Management Components
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, List, Any, Optional, Callable
from .base_component import BaseComponent, ComponentState
from .input_components import TextInput, Button
from .display_components import Label
from .layout_components import Panel
from .data_display_components import DataTable


class RuleEditor(BaseComponent):
    """
    Rule editor for creating and modifying file organization rules.
    """
    
    def __init__(self, parent: tk.Widget,
                 rule_data: Optional[Dict] = None,
                 available_patterns: Optional[List[Dict]] = None,
                 on_rule_change: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the rule editor.
        
        Args:
            parent: Parent widget
            rule_data: Existing rule data to edit
            available_patterns: List of available patterns
            on_rule_change: Callback when rule changes
            **kwargs: Additional widget options
        """
        self.rule_data = rule_data or {
            'name': '',
            'description': '',
            'pattern_id': None,
            'destination_path': '',
            'action': 'move',
            'conditions': [],
            'enabled': True,
            'priority': 0
        }
        self.available_patterns = available_patterns or []
        self.on_rule_change = on_rule_change
        self._validation_errors = []
        
        super().__init__(parent, **kwargs)
        
        self._setup_rule_editor()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the rule editor interface."""
        # Main container with notebook for organized sections
        main_frame = ttk.Frame(self.parent)
        
        # Create notebook for different rule configuration sections
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Basic Information Tab
        self._create_basic_info_tab()
        
        # Pattern and Destination Tab
        self._create_pattern_destination_tab()
        
        # Conditions Tab
        self._create_conditions_tab()
        
        # Advanced Settings Tab
        self._create_advanced_tab()
        
        # Rule Preview Section
        preview_frame = ttk.LabelFrame(main_frame, text="Rule Preview", padding=10)
        preview_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 0))
        
        self.preview_text = tk.Text(preview_frame, height=4, state='disabled',
                                   font=('Consolas', 9), wrap=tk.WORD)
        self.preview_text.pack(side=tk.TOP, fill=tk.X)
        
        # Update preview initially
        self._update_preview()
        
        return main_frame
    
    def _create_basic_info_tab(self):
        """Create the basic information tab."""
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="Basic Info")
        
        # Create scrollable frame
        canvas = tk.Canvas(basic_frame)
        scrollbar = ttk.Scrollbar(basic_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Rule name
        name_frame = ttk.LabelFrame(scrollable_frame, text="Rule Name", padding=10)
        name_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        self.name_var = tk.StringVar(value=self.rule_data.get('name', ''))
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var, font=('Arial', 10))
        name_entry.pack(side=tk.TOP, fill=tk.X)
        self.name_var.trace('w', self._on_rule_change)
        
        # Rule description
        desc_frame = ttk.LabelFrame(scrollable_frame, text="Description", padding=10)
        desc_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        self.desc_text = tk.Text(desc_frame, height=3, wrap=tk.WORD, font=('Arial', 10))
        self.desc_text.pack(side=tk.TOP, fill=tk.X)
        self.desc_text.insert(1.0, self.rule_data.get('description', ''))
        self.desc_text.bind('<KeyRelease>', self._on_rule_change)
        
        # Rule action
        action_frame = ttk.LabelFrame(scrollable_frame, text="Action", padding=10)
        action_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        self.action_var = tk.StringVar(value=self.rule_data.get('action', 'move'))
        
        actions = [
            ('Move files to destination', 'move'),
            ('Copy files to destination', 'copy'),
            ('Create symbolic links', 'symlink'),
            ('Delete matching files', 'delete'),
            ('Rename files only', 'rename')
        ]
        
        for text, value in actions:
            rb = ttk.Radiobutton(action_frame, text=text, variable=self.action_var, 
                               value=value, command=self._on_rule_change)
            rb.pack(anchor='w', pady=2)
        
        # Rule status
        status_frame = ttk.LabelFrame(scrollable_frame, text="Status", padding=10)
        status_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.enabled_var = tk.BooleanVar(value=self.rule_data.get('enabled', True))
        enabled_cb = ttk.Checkbutton(status_frame, text="Enable this rule",
                                   variable=self.enabled_var,
                                   command=self._on_rule_change)
        enabled_cb.pack(anchor='w')
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_pattern_destination_tab(self):
        """Create the pattern and destination tab."""
        pattern_frame = ttk.Frame(self.notebook)
        self.notebook.add(pattern_frame, text="Pattern & Destination")
        
        # Pattern selection
        pattern_select_frame = ttk.LabelFrame(pattern_frame, text="File Pattern", padding=10)
        pattern_select_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Pattern dropdown
        pattern_combo_frame = ttk.Frame(pattern_select_frame)
        pattern_combo_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        ttk.Label(pattern_combo_frame, text="Select Pattern:").pack(side=tk.LEFT)
        
        pattern_names = [p.get('name', 'Unnamed') for p in self.available_patterns]
        pattern_names.insert(0, "Select a pattern...")
        
        self.pattern_var = tk.StringVar(value="Select a pattern...")
        pattern_combo = ttk.Combobox(pattern_combo_frame, textvariable=self.pattern_var,
                                   values=pattern_names, state="readonly", width=30)
        pattern_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        pattern_combo.bind('<<ComboboxSelected>>', self._on_pattern_selected)
        
        # Pattern management buttons
        pattern_btn_frame = ttk.Frame(pattern_select_frame)
        pattern_btn_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Button(pattern_btn_frame, text="New Pattern",
                  command=self._new_pattern).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(pattern_btn_frame, text="Edit Pattern",
                  command=self._edit_pattern).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(pattern_btn_frame, text="Test Pattern",
                  command=self._test_pattern).pack(side=tk.LEFT)
        
        # Pattern preview
        pattern_preview_frame = ttk.Frame(pattern_select_frame)
        pattern_preview_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 0))
        
        ttk.Label(pattern_preview_frame, text="Pattern Details:").pack(anchor='w')
        self.pattern_preview_text = tk.Text(pattern_preview_frame, height=3, state='disabled',
                                           font=('Arial', 9), wrap=tk.WORD)
        self.pattern_preview_text.pack(side=tk.TOP, fill=tk.X)
        
        # Destination path
        dest_frame = ttk.LabelFrame(pattern_frame, text="Destination", padding=10)
        dest_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Destination path input
        dest_path_frame = ttk.Frame(dest_frame)
        dest_path_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        ttk.Label(dest_path_frame, text="Destination Path:").pack(side=tk.LEFT)
        
        self.dest_var = tk.StringVar(value=self.rule_data.get('destination_path', ''))
        dest_entry = ttk.Entry(dest_path_frame, textvariable=self.dest_var)
        dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))
        self.dest_var.trace('w', self._on_rule_change)
        
        ttk.Button(dest_path_frame, text="Browse",
                  command=self._browse_destination).pack(side=tk.LEFT)
        
        # Destination options
        dest_options_frame = ttk.Frame(dest_frame)
        dest_options_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.create_dest_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dest_options_frame, text="Create destination directory if it doesn't exist",
                       variable=self.create_dest_var).pack(anchor='w')
        
        self.preserve_structure_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dest_options_frame, text="Preserve source directory structure",
                       variable=self.preserve_structure_var).pack(anchor='w')
    
    def _create_conditions_tab(self):
        """Create the conditions tab."""
        conditions_frame = ttk.Frame(self.notebook)
        self.notebook.add(conditions_frame, text="Conditions")
        
        # Conditions explanation
        info_frame = ttk.Frame(conditions_frame)
        info_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        info_text = ("Additional conditions can be added to make the rule more specific. "
                    "All conditions must be met for the rule to apply.")
        ttk.Label(info_frame, text=info_text, wraplength=400, justify=tk.LEFT).pack(anchor='w')
        
        # Conditions toolbar
        conditions_toolbar = ttk.Frame(conditions_frame)
        conditions_toolbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        ttk.Button(conditions_toolbar, text="Add File Size Condition",
                  command=self._add_size_condition).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(conditions_toolbar, text="Add Date Condition",
                  command=self._add_date_condition).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(conditions_toolbar, text="Add Path Condition",
                  command=self._add_path_condition).pack(side=tk.LEFT)
        
        # Conditions list
        conditions_list_frame = ttk.LabelFrame(conditions_frame, text="Current Conditions", padding=10)
        conditions_list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Conditions treeview
        columns = ('type', 'operator', 'value', 'description')
        self.conditions_tree = ttk.Treeview(conditions_list_frame, columns=columns, show='tree headings')
        
        self.conditions_tree.heading('#0', text='#')
        self.conditions_tree.heading('type', text='Type')
        self.conditions_tree.heading('operator', text='Operator')
        self.conditions_tree.heading('value', text='Value')
        self.conditions_tree.heading('description', text='Description')
        
        self.conditions_tree.column('#0', width=30, minwidth=30)
        self.conditions_tree.column('type', width=100, minwidth=80)
        self.conditions_tree.column('operator', width=80, minwidth=60)
        self.conditions_tree.column('value', width=120, minwidth=100)
        self.conditions_tree.column('description', width=200, minwidth=150)
        
        conditions_scrollbar = ttk.Scrollbar(conditions_list_frame, orient=tk.VERTICAL,
                                           command=self.conditions_tree.yview)
        self.conditions_tree.configure(yscrollcommand=conditions_scrollbar.set)
        
        self.conditions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        conditions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Conditions buttons
        conditions_btn_frame = ttk.Frame(conditions_frame)
        conditions_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 0))
        
        ttk.Button(conditions_btn_frame, text="Edit Selected",
                  command=self._edit_condition).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(conditions_btn_frame, text="Remove Selected",
                  command=self._remove_condition).pack(side=tk.LEFT)
        
        # Load existing conditions
        self._load_conditions()
    
    def _create_advanced_tab(self):
        """Create the advanced settings tab."""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="Advanced")
        
        # Priority setting
        priority_frame = ttk.LabelFrame(advanced_frame, text="Rule Priority", padding=10)
        priority_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        priority_info = ("Higher priority rules are evaluated first. Range: 0 (lowest) to 100 (highest)")
        ttk.Label(priority_frame, text=priority_info, wraplength=400).pack(anchor='w', pady=(0, 10))
        
        priority_input_frame = ttk.Frame(priority_frame)
        priority_input_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Label(priority_input_frame, text="Priority:").pack(side=tk.LEFT)
        
        self.priority_var = tk.IntVar(value=self.rule_data.get('priority', 0))
        priority_spinbox = ttk.Spinbox(priority_input_frame, from_=0, to=100,
                                     textvariable=self.priority_var, width=10)
        priority_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        self.priority_var.trace('w', self._on_rule_change)
        
        # Conflict resolution
        conflict_frame = ttk.LabelFrame(advanced_frame, text="Conflict Resolution", padding=10)
        conflict_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        self.conflict_resolution_var = tk.StringVar(value="ask")
        
        conflict_options = [
            ("Ask user for each conflict", "ask"),
            ("Skip conflicting files", "skip"),
            ("Overwrite existing files", "overwrite"),
            ("Rename new files", "rename")
        ]
        
        for text, value in conflict_options:
            rb = ttk.Radiobutton(conflict_frame, text=text,
                               variable=self.conflict_resolution_var, value=value)
            rb.pack(anchor='w', pady=2)
        
        # Logging options
        logging_frame = ttk.LabelFrame(advanced_frame, text="Logging", padding=10)
        logging_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.log_operations_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(logging_frame, text="Log all operations performed by this rule",
                       variable=self.log_operations_var).pack(anchor='w')
        
        self.detailed_logging_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(logging_frame, text="Enable detailed logging (for debugging)",
                       variable=self.detailed_logging_var).pack(anchor='w')
    
    def _setup_rule_editor(self):
        """Setup rule editor event handling."""
        # Load existing pattern if specified
        if self.rule_data.get('pattern_id'):
            self._load_selected_pattern()
        
        # *Logic placeholder*: Connect to rule validation system
        # This would integrate with the TaskMover rule engine
    
    def _on_rule_change(self, *args):
        """Handle rule data changes."""
        self.rule_data['name'] = self.name_var.get()
        self.rule_data['description'] = self.desc_text.get(1.0, tk.END).strip()
        self.rule_data['action'] = self.action_var.get()
        self.rule_data['destination_path'] = self.dest_var.get()
        self.rule_data['enabled'] = self.enabled_var.get()
        self.rule_data['priority'] = self.priority_var.get()
        
        self._validate_rule()
        self._update_preview()
        
        if self.on_rule_change:
            self.on_rule_change(self.rule_data)
        
        self.trigger_event('rule_changed', self.rule_data)
    
    def _on_pattern_selected(self, event=None):
        """Handle pattern selection."""
        pattern_name = self.pattern_var.get()
        
        # Find the selected pattern
        selected_pattern = None
        for pattern in self.available_patterns:
            if pattern.get('name') == pattern_name:
                selected_pattern = pattern
                break
        
        if selected_pattern:
            self.rule_data['pattern_id'] = selected_pattern.get('id')
            self._update_pattern_preview(selected_pattern)
            self._on_rule_change()
    
    def _update_pattern_preview(self, pattern: Dict):
        """Update the pattern preview display."""
        preview_text = f"Pattern: {pattern.get('name', 'Unnamed')}\n"
        preview_text += f"Description: {pattern.get('description', 'No description')}\n"
        preview_text += f"Criteria: {len(pattern.get('criteria', []))} conditions"
        
        self.pattern_preview_text.configure(state='normal')
        self.pattern_preview_text.delete(1.0, tk.END)
        self.pattern_preview_text.insert(1.0, preview_text)
        self.pattern_preview_text.configure(state='disabled')
    
    def _load_selected_pattern(self):
        """Load the currently selected pattern."""
        pattern_id = self.rule_data.get('pattern_id')
        if pattern_id:
            for pattern in self.available_patterns:
                if pattern.get('id') == pattern_id:
                    self.pattern_var.set(pattern.get('name', 'Unnamed'))
                    self._update_pattern_preview(pattern)
                    break
    
    def _new_pattern(self):
        """Create a new pattern."""
        # *Logic placeholder*: Open pattern builder for new pattern
        self.trigger_event('new_pattern_requested')
    
    def _edit_pattern(self):
        """Edit the selected pattern."""
        pattern_name = self.pattern_var.get()
        if pattern_name == "Select a pattern...":
            messagebox.showwarning("No Pattern", "Please select a pattern to edit.")
            return
        
        # *Logic placeholder*: Open pattern builder for editing
        self.trigger_event('edit_pattern_requested', pattern_name)
    
    def _test_pattern(self):
        """Test the selected pattern."""
        pattern_name = self.pattern_var.get()
        if pattern_name == "Select a pattern...":
            messagebox.showwarning("No Pattern", "Please select a pattern to test.")
            return
        
        # *Logic placeholder*: Open pattern tester
        self.trigger_event('test_pattern_requested', pattern_name)
    
    def _browse_destination(self):
        """Browse for destination directory."""
        from tkinter import filedialog
        
        directory = filedialog.askdirectory(title="Select destination directory")
        if directory:
            self.dest_var.set(directory)
    
    def _add_size_condition(self):
        """Add a file size condition."""
        dialog = SizeConditionDialog(self._widget)
        result = dialog.show_modal()
        
        if result:
            condition = {
                'type': 'size',
                'operator': result['operator'],
                'value': result['value'],
                'unit': result['unit']
            }
            self._add_condition(condition)
    
    def _add_date_condition(self):
        """Add a date condition."""
        dialog = DateConditionDialog(self._widget)
        result = dialog.show_modal()
        
        if result:
            condition = {
                'type': 'date',
                'field': result['field'],
                'operator': result['operator'],
                'value': result['value']
            }
            self._add_condition(condition)
    
    def _add_path_condition(self):
        """Add a path condition."""
        dialog = PathConditionDialog(self._widget)
        result = dialog.show_modal()
        
        if result:
            condition = {
                'type': 'path',
                'operator': result['operator'],
                'value': result['value']
            }
            self._add_condition(condition)
    
    def _add_condition(self, condition: Dict):
        """Add a condition to the rule."""
        self.rule_data.setdefault('conditions', []).append(condition)
        self._load_conditions()
        self._on_rule_change()
    
    def _load_conditions(self):
        """Load conditions into the tree view."""
        # Clear existing items
        for item in self.conditions_tree.get_children():
            self.conditions_tree.delete(item)
        
        # Add conditions
        conditions = self.rule_data.get('conditions', [])
        for i, condition in enumerate(conditions):
            description = self._format_condition_description(condition)
            values = (
                condition.get('type', ''),
                condition.get('operator', ''),
                str(condition.get('value', '')),
                description
            )
            
            self.conditions_tree.insert('', tk.END, iid=f"condition_{i}",
                                      text=str(i+1), values=values)
    
    def _format_condition_description(self, condition: Dict) -> str:
        """Format condition for human-readable description."""
        condition_type = condition.get('type', '')
        operator = condition.get('operator', '')
        value = condition.get('value', '')
        
        if condition_type == 'size':
            unit = condition.get('unit', 'bytes')
            return f"File size {operator} {value} {unit}"
        elif condition_type == 'date':
            field = condition.get('field', 'modified')
            return f"File {field} date {operator} {value}"
        elif condition_type == 'path':
            return f"File path {operator} {value}"
        
        return f"{condition_type} {operator} {value}"
    
    def _edit_condition(self):
        """Edit the selected condition."""
        selection = self.conditions_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a condition to edit.")
            return
        
        # *Logic placeholder*: Open appropriate condition editor
        messagebox.showinfo("Edit Condition", "Condition editing functionality would be implemented here.")
    
    def _remove_condition(self):
        """Remove the selected condition."""
        selection = self.conditions_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a condition to remove.")
            return
        
        item_id = selection[0]
        index = int(item_id.split('_')[1])
        
        del self.rule_data['conditions'][index]
        self._load_conditions()
        self._on_rule_change()
    
    def _validate_rule(self):
        """Validate the current rule."""
        self._validation_errors = []
        
        # Validate name
        if not self.rule_data['name'].strip():
            self._validation_errors.append("Rule name is required")
        
        # Validate pattern
        if not self.rule_data.get('pattern_id'):
            self._validation_errors.append("A pattern must be selected")
        
        # Validate destination for move/copy actions
        action = self.rule_data.get('action', 'move')
        if action in ['move', 'copy'] and not self.rule_data.get('destination_path'):
            self._validation_errors.append("Destination path is required for move/copy actions")
        
        # *Logic placeholder*: Additional rule validation
        # This would validate rule logic and detect conflicts
    
    def _update_preview(self):
        """Update the rule preview display."""
        preview_text = self._generate_rule_preview()
        
        self.preview_text.configure(state='normal')
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview_text)
        self.preview_text.configure(state='disabled')
    
    def _generate_rule_preview(self) -> str:
        """Generate a text preview of the rule."""
        if not self.rule_data.get('name'):
            return "Rule configuration in progress..."
        
        preview_lines = []
        preview_lines.append(f"Rule: {self.rule_data['name']}")
        
        if self.rule_data.get('description'):
            preview_lines.append(f"Description: {self.rule_data['description']}")
        
        # Pattern info
        pattern_name = self.pattern_var.get()
        if pattern_name != "Select a pattern...":
            preview_lines.append(f"Pattern: {pattern_name}")
        
        # Action and destination
        action = self.rule_data.get('action', 'move')
        if action in ['move', 'copy']:
            dest = self.rule_data.get('destination_path', 'Not specified')
            preview_lines.append(f"Action: {action.title()} files to {dest}")
        else:
            preview_lines.append(f"Action: {action.title()} files")
        
        # Conditions
        conditions = self.rule_data.get('conditions', [])
        if conditions:
            preview_lines.append(f"Additional conditions: {len(conditions)}")
        
        # Status
        status = "Enabled" if self.rule_data.get('enabled', True) else "Disabled"
        priority = self.rule_data.get('priority', 0)
        preview_lines.append(f"Status: {status}, Priority: {priority}")
        
        return "\n".join(preview_lines)
    
    def get_rule_data(self) -> Dict:
        """Get the current rule data."""
        return self.rule_data.copy()
    
    def set_rule_data(self, rule_data: Dict):
        """Set the rule data."""
        self.rule_data = rule_data.copy()
        
        # Update all UI elements
        self.name_var.set(rule_data.get('name', ''))
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(1.0, rule_data.get('description', ''))
        self.action_var.set(rule_data.get('action', 'move'))
        self.dest_var.set(rule_data.get('destination_path', ''))
        self.enabled_var.set(rule_data.get('enabled', True))
        self.priority_var.set(rule_data.get('priority', 0))
        
        self._load_selected_pattern()
        self._load_conditions()
        self._update_preview()
    
    def is_valid(self) -> bool:
        """Check if the current rule is valid."""
        self._validate_rule()
        return len(self._validation_errors) == 0
    
    def get_validation_errors(self) -> List[str]:
        """Get current validation errors."""
        return self._validation_errors.copy()


class RuleList(BaseComponent):
    """
    Rule list management interface with drag-and-drop reordering.
    """
    
    def __init__(self, parent: tk.Widget,
                 rules: Optional[List[Dict]] = None,
                 on_rule_select: Optional[Callable] = None,
                 on_rule_edit: Optional[Callable] = None,
                 on_rule_delete: Optional[Callable] = None,
                 on_rule_reorder: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the rule list.
        
        Args:
            parent: Parent widget
            rules: List of rule data
            on_rule_select: Callback when rule is selected
            on_rule_edit: Callback when rule is edited
            on_rule_delete: Callback when rule is deleted
            on_rule_reorder: Callback when rules are reordered
            **kwargs: Additional widget options
        """
        self.rules = rules or []
        self.on_rule_select = on_rule_select
        self.on_rule_edit = on_rule_edit
        self.on_rule_delete = on_rule_delete
        self.on_rule_reorder = on_rule_reorder
        self._selected_rule = None
        self._drag_start_index = None
        
        super().__init__(parent, **kwargs)
        
        self._setup_rule_list()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the rule list interface."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        
        # Toolbar
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar_frame, text="New Rule",
                  command=self._new_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Edit Rule",
                  command=self._edit_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Duplicate Rule",
                  command=self._duplicate_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Delete Rule",
                  command=self._delete_rule).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(toolbar_frame, text="Move Up",
                  command=self._move_rule_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Move Down",
                  command=self._move_rule_down).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(toolbar_frame, text="Test Rules",
                  command=self._test_rules).pack(side=tk.RIGHT)
        
        # Rule list
        list_frame = ttk.LabelFrame(main_frame, text="Rules (in order of execution)", padding=10)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Configure treeview for rule list
        columns = ('priority', 'name', 'pattern', 'action', 'destination', 'enabled', 'last_used')
        self.rule_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        
        # Configure column headings
        self.rule_tree.heading('#0', text='Order')
        self.rule_tree.heading('priority', text='Priority')
        self.rule_tree.heading('name', text='Rule Name')
        self.rule_tree.heading('pattern', text='Pattern')
        self.rule_tree.heading('action', text='Action')
        self.rule_tree.heading('destination', text='Destination')
        self.rule_tree.heading('enabled', text='Enabled')
        self.rule_tree.heading('last_used', text='Last Used')
        
        # Configure column widths
        self.rule_tree.column('#0', width=60, minwidth=50)
        self.rule_tree.column('priority', width=70, minwidth=60)
        self.rule_tree.column('name', width=150, minwidth=120)
        self.rule_tree.column('pattern', width=120, minwidth=100)
        self.rule_tree.column('action', width=80, minwidth=60)
        self.rule_tree.column('destination', width=200, minwidth=150)
        self.rule_tree.column('enabled', width=70, minwidth=60)
        self.rule_tree.column('last_used', width=100, minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.rule_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.rule_tree.xview)
        
        self.rule_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.rule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.rule_tree.bind('<<TreeviewSelect>>', self._on_rule_select)
        self.rule_tree.bind('<Double-1>', self._on_rule_double_click)
        self.rule_tree.bind('<Button-1>', self._on_drag_start)
        self.rule_tree.bind('<B1-Motion>', self._on_drag_motion)
        self.rule_tree.bind('<ButtonRelease-1>', self._on_drag_end)
        
        # Context menu
        self._create_context_menu()
        self.rule_tree.bind('<Button-3>', self._show_context_menu)
        
        # Load rules
        self._load_rules()
        
        return main_frame
    
    def _setup_rule_list(self):
        """Setup rule list event handling."""
        # *Logic placeholder*: Connect to rule data source
        # This would connect to the TaskMover rule storage system
        pass
    
    def _create_context_menu(self):
        """Create context menu for rule items."""
        self.context_menu = tk.Menu(self._widget, tearoff=0)
        self.context_menu.add_command(label="Edit Rule", command=self._edit_rule)
        self.context_menu.add_command(label="Duplicate Rule", command=self._duplicate_rule)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Enable/Disable", command=self._toggle_rule)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Test Rule", command=self._test_single_rule)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Rule", command=self._delete_rule)
    
    def _load_rules(self):
        """Load rules into the tree view."""
        # Clear existing items
        for item in self.rule_tree.get_children():
            self.rule_tree.delete(item)
        
        # Sort rules by priority (highest first)
        sorted_rules = sorted(self.rules, key=lambda r: r.get('priority', 0), reverse=True)
        
        # Add rules
        for i, rule in enumerate(sorted_rules):
            pattern_name = self._get_pattern_name(rule.get('pattern_id'))
            
            values = (
                rule.get('priority', 0),
                rule.get('name', ''),
                pattern_name,
                rule.get('action', '').title(),
                rule.get('destination_path', '')[:30] + '...' if len(rule.get('destination_path', '')) > 30 else rule.get('destination_path', ''),
                'Yes' if rule.get('enabled', True) else 'No',
                rule.get('last_used', 'Never')
            )
            
            item_id = f"rule_{i}"
            item = self.rule_tree.insert('', tk.END, iid=item_id, text=str(i+1), values=values)
            
            # Color code disabled rules
            if not rule.get('enabled', True):
                self.rule_tree.set(item, 'enabled', '✗ No')
            else:
                self.rule_tree.set(item, 'enabled', '✓ Yes')
    
    def _get_pattern_name(self, pattern_id: Optional[str]) -> str:
        """Get pattern name by ID."""
        # *Logic placeholder*: Look up pattern name
        # This would query the pattern storage to get the pattern name
        return f"Pattern {pattern_id}" if pattern_id else "No pattern"
    
    def _on_rule_select(self, event):
        """Handle rule selection."""
        selection = self.rule_tree.selection()
        if selection:
            item_id = selection[0]
            index = int(item_id.split('_')[1])
            self._selected_rule = self.rules[index]
            
            if self.on_rule_select:
                self.on_rule_select(self._selected_rule)
            
            self.trigger_event('rule_selected', self._selected_rule)
    
    def _on_rule_double_click(self, event):
        """Handle rule double-click (edit)."""
        self._edit_rule()
    
    def _show_context_menu(self, event):
        """Show context menu."""
        item = self.rule_tree.identify_row(event.y)
        if item:
            self.rule_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _on_drag_start(self, event):
        """Handle start of drag operation."""
        item = self.rule_tree.identify_row(event.y)
        if item:
            self._drag_start_index = int(item.split('_')[1])
    
    def _on_drag_motion(self, event):
        """Handle drag motion."""
        # *Logic placeholder*: Implement visual drag feedback
        # This would show visual indicators during drag operation
        pass
    
    def _on_drag_end(self, event):
        """Handle end of drag operation."""
        if self._drag_start_index is not None:
            target_item = self.rule_tree.identify_row(event.y)
            if target_item:
                target_index = int(target_item.split('_')[1])
                
                if target_index != self._drag_start_index:
                    # Move rule
                    rule = self.rules.pop(self._drag_start_index)
                    self.rules.insert(target_index, rule)
                    
                    self._load_rules()
                    
                    if self.on_rule_reorder:
                        self.on_rule_reorder(self.rules)
                    
                    self.trigger_event('rules_reordered', self.rules)
        
        self._drag_start_index = None
    
    def _new_rule(self):
        """Create a new rule."""
        # *Logic placeholder*: Open rule editor for new rule
        if self.on_rule_edit:
            self.on_rule_edit(None)
        self.trigger_event('rule_new')
    
    def _edit_rule(self):
        """Edit the selected rule."""
        if not self._selected_rule:
            messagebox.showwarning("No Selection", "Please select a rule to edit.")
            return
        
        # *Logic placeholder*: Open rule editor for editing
        if self.on_rule_edit:
            self.on_rule_edit(self._selected_rule)
        self.trigger_event('rule_edit', self._selected_rule)
    
    def _duplicate_rule(self):
        """Duplicate the selected rule."""
        if not self._selected_rule:
            messagebox.showwarning("No Selection", "Please select a rule to duplicate.")
            return
        
        # *Logic placeholder*: Create duplicate rule
        duplicate = self._selected_rule.copy()
        duplicate['name'] = f"{duplicate['name']} (Copy)"
        
        self.trigger_event('rule_duplicate', duplicate)
    
    def _delete_rule(self):
        """Delete the selected rule."""
        if not self._selected_rule:
            messagebox.showwarning("No Selection", "Please select a rule to delete.")
            return
        
        result = messagebox.askyesno("Confirm Delete",
                                   f"Are you sure you want to delete the rule '{self._selected_rule['name']}'?\n\n"
                                   "This action cannot be undone.")
        
        if result:
            if self.on_rule_delete:
                self.on_rule_delete(self._selected_rule)
            self.trigger_event('rule_delete', self._selected_rule)
    
    def _move_rule_up(self):
        """Move selected rule up in priority."""
        if not self._selected_rule:
            messagebox.showwarning("No Selection", "Please select a rule to move.")
            return
        
        # Find rule index
        for i, rule in enumerate(self.rules):
            if rule == self._selected_rule:
                if i > 0:
                    # Swap with previous rule
                    self.rules[i], self.rules[i-1] = self.rules[i-1], self.rules[i]
                    self._load_rules()
                    
                    if self.on_rule_reorder:
                        self.on_rule_reorder(self.rules)
                break
    
    def _move_rule_down(self):
        """Move selected rule down in priority."""
        if not self._selected_rule:
            messagebox.showwarning("No Selection", "Please select a rule to move.")
            return
        
        # Find rule index
        for i, rule in enumerate(self.rules):
            if rule == self._selected_rule:
                if i < len(self.rules) - 1:
                    # Swap with next rule
                    self.rules[i], self.rules[i+1] = self.rules[i+1], self.rules[i]
                    self._load_rules()
                    
                    if self.on_rule_reorder:
                        self.on_rule_reorder(self.rules)
                break
    
    def _toggle_rule(self):
        """Toggle the enabled state of the selected rule."""
        if not self._selected_rule:
            messagebox.showwarning("No Selection", "Please select a rule to toggle.")
            return
        
        self._selected_rule['enabled'] = not self._selected_rule.get('enabled', True)
        self._load_rules()
        
        self.trigger_event('rule_toggled', self._selected_rule)
    
    def _test_single_rule(self):
        """Test the selected rule."""
        if not self._selected_rule:
            messagebox.showwarning("No Selection", "Please select a rule to test.")
            return
        
        # *Logic placeholder*: Open rule tester for single rule
        self.trigger_event('rule_test', self._selected_rule)
    
    def _test_rules(self):
        """Test all rules."""
        # *Logic placeholder*: Open rule tester for all rules
        self.trigger_event('rules_test_all')
    
    def add_rule(self, rule: Dict):
        """Add a new rule to the list."""
        self.rules.append(rule)
        self._load_rules()
    
    def update_rule(self, rule: Dict):
        """Update an existing rule."""
        # Find and update the rule
        for i, existing in enumerate(self.rules):
            if existing.get('id') == rule.get('id'):
                self.rules[i] = rule
                break
        self._load_rules()
    
    def remove_rule(self, rule: Dict):
        """Remove a rule from the list."""
        self.rules = [r for r in self.rules if r.get('id') != rule.get('id')]
        self._load_rules()
    
    def get_selected_rule(self) -> Optional[Dict]:
        """Get the currently selected rule."""
        return self._selected_rule
    
    def set_rules(self, rules: List[Dict]):
        """Set the rule list."""
        self.rules = rules
        self._load_rules()


# Simplified dialog classes for condition input

class SizeConditionDialog:
    """Dialog for creating file size conditions."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
    
    def show_modal(self):
        """Show dialog and return result."""
        # *Logic placeholder*: Implement full size condition dialog
        # This would show a dialog with operator and size inputs
        
        # Simplified implementation for demonstration
        condition = simpledialog.askstring("Size Condition", "Enter size condition (e.g., >10MB):")
        if condition:
            self.result = {'operator': '>', 'value': '10', 'unit': 'MB'}
        return self.result


class DateConditionDialog:
    """Dialog for creating date conditions."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
    
    def show_modal(self):
        """Show dialog and return result."""
        # *Logic placeholder*: Implement full date condition dialog
        # This would show a dialog with date field, operator, and date picker
        
        # Simplified implementation for demonstration
        condition = simpledialog.askstring("Date Condition", "Enter date condition:")
        if condition:
            self.result = {'field': 'modified', 'operator': 'after', 'value': '2023-01-01'}
        return self.result


class PathConditionDialog:
    """Dialog for creating path conditions."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
    
    def show_modal(self):
        """Show dialog and return result."""
        # *Logic placeholder*: Implement full path condition dialog
        # This would show a dialog for entering path patterns
        
        # Simplified implementation for demonstration
        condition = simpledialog.askstring("Path Condition", "Enter path condition:")
        if condition:
            self.result = {'operator': 'contains', 'value': condition}
        return self.result


class RulePriorityManager(BaseComponent):
    """
    Rule priority manager for visual priority ordering and management.
    """
    
    def __init__(self, parent: tk.Widget,
                 rules: Optional[List[Dict]] = None,
                 on_priority_change: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the rule priority manager.
        
        Args:
            parent: Parent widget
            rules: List of rules to manage priorities for
            on_priority_change: Callback when priority order changes
            **kwargs: Additional widget options
        """
        self.rules = rules or []
        self.on_priority_change = on_priority_change
        self._dragging_item = None
        self._drag_start_y = 0
        
        super().__init__(parent, **kwargs)
        
        self._setup_priority_manager()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the priority manager interface."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(header_frame, text="Rule Priority Order", 
                 font=('TkDefaultFont', 10, 'bold')).pack(side=tk.LEFT)
        
        # Help text
        help_label = ttk.Label(header_frame, 
                              text="(Drag to reorder • Higher = First)", 
                              foreground='gray')
        help_label.pack(side=tk.RIGHT)
        
        return main_frame
    
    def _setup_priority_manager(self):
        """Set up the priority manager interface."""
        # Priority list frame
        self.priority_frame = ttk.Frame(self._widget)
        self.priority_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollable priority list
        self._create_priority_list()
        
        # Controls frame
        controls_frame = ttk.Frame(self._widget)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Auto-prioritize button
        auto_btn = ttk.Button(controls_frame, text="Auto-Prioritize",
                             command=self._auto_prioritize)
        auto_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Reset priorities button
        reset_btn = ttk.Button(controls_frame, text="Reset Priorities",
                              command=self._reset_priorities)
        reset_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Save button
        save_btn = ttk.Button(controls_frame, text="Save Order",
                             command=self._save_priorities)
        save_btn.pack(side=tk.RIGHT)
    
    def _create_priority_list(self):
        """Create the scrollable priority list."""
        # Create canvas and scrollbar for custom list
        canvas_frame = ttk.Frame(self.priority_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.priority_canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, 
                                 command=self.priority_canvas.yview)
        self.priority_list_frame = ttk.Frame(self.priority_canvas)
        
        self.priority_list_frame.bind('<Configure>', 
                                     lambda e: self.priority_canvas.configure(
                                         scrollregion=self.priority_canvas.bbox('all')))
        
        self.priority_canvas.create_window((0, 0), window=self.priority_list_frame, 
                                          anchor='nw')
        self.priority_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.priority_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate the list
        self._refresh_priority_list()
    
    def _refresh_priority_list(self):
        """Refresh the priority list display."""
        # Clear existing items
        for widget in self.priority_list_frame.winfo_children():
            widget.destroy()
        
        # Sort rules by priority (highest first)
        sorted_rules = sorted(self.rules, key=lambda r: r.get('priority', 0), 
                             reverse=True)
        
        for i, rule in enumerate(sorted_rules):
            self._create_priority_item(rule, i)
    
    def _create_priority_item(self, rule: Dict, index: int):
        """Create a priority item widget."""
        # Item frame
        item_frame = ttk.Frame(self.priority_list_frame, relief=tk.RIDGE, 
                              borderwidth=1)
        item_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Drag handle
        drag_handle = ttk.Label(item_frame, text="⋮⋮", cursor="hand2",
                               foreground='gray')
        drag_handle.pack(side=tk.LEFT, padx=(5, 10))
        
        # Priority number
        priority_label = ttk.Label(item_frame, text=f"#{index + 1}",
                                  width=4, anchor=tk.CENTER,
                                  font=('TkDefaultFont', 9, 'bold'))
        priority_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Rule info frame
        info_frame = ttk.Frame(item_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Rule name
        name_label = ttk.Label(info_frame, text=rule.get('name', 'Unnamed Rule'),
                              font=('TkDefaultFont', 9, 'bold'))
        name_label.pack(anchor=tk.W)
        
        # Rule description
        desc_text = rule.get('description', 'No description')
        if len(desc_text) > 50:
            desc_text = desc_text[:47] + "..."
        desc_label = ttk.Label(info_frame, text=desc_text,
                              foreground='gray', font=('TkDefaultFont', 8))
        desc_label.pack(anchor=tk.W)
        
        # Priority controls
        controls_frame = ttk.Frame(item_frame)
        controls_frame.pack(side=tk.RIGHT, padx=5)
        
        # Up button
        up_btn = ttk.Button(controls_frame, text="↑", width=3,
                           command=lambda: self._move_rule_up(rule))
        up_btn.pack(side=tk.TOP)
        
        # Down button
        down_btn = ttk.Button(controls_frame, text="↓", width=3,
                             command=lambda: self._move_rule_down(rule))
        down_btn.pack(side=tk.TOP)
        
        # Bind drag events to item frame
        item_frame.bind("<Button-1>", lambda e: self._start_drag(e, rule))
        item_frame.bind("<B1-Motion>", self._on_drag)
        item_frame.bind("<ButtonRelease-1>", self._end_drag)
        
        # Store rule reference for later use
        # Note: Using a custom attribute tracking approach
    
    def _start_drag(self, event, rule: Dict):
        """Start dragging a rule item."""
        self._dragging_item = rule
        self._drag_start_y = event.y_root
        event.widget.configure(relief=tk.RAISED)
    
    def _on_drag(self, event):
        """Handle rule item dragging."""
        if self._dragging_item:
            # *Logic placeholder*: Implement visual drag feedback
            # This would show drag indicators and potential drop positions
            pass
    
    def _end_drag(self, event):
        """End dragging and update positions."""
        if self._dragging_item:
            # *Logic placeholder*: Implement drop logic
            # This would calculate new position based on drop location
            event.widget.configure(relief=tk.RIDGE)
            self._dragging_item = None
    
    def _move_rule_up(self, rule: Dict):
        """Move rule up in priority."""
        current_priority = rule.get('priority', 0)
        rule['priority'] = current_priority + 1
        self._refresh_priority_list()
        self._notify_priority_change()
    
    def _move_rule_down(self, rule: Dict):
        """Move rule down in priority."""
        current_priority = rule.get('priority', 0)
        if current_priority > 0:
            rule['priority'] = current_priority - 1
            self._refresh_priority_list()
            self._notify_priority_change()
    
    def _auto_prioritize(self):
        """Auto-prioritize rules based on specificity."""
        # *Logic placeholder*: Implement smart prioritization
        # This would analyze rule patterns and assign priorities automatically
        
        # Simple implementation: prioritize by pattern complexity
        for i, rule in enumerate(self.rules):
            pattern_complexity = len(rule.get('pattern', ''))
            rule['priority'] = pattern_complexity
        
        self._refresh_priority_list()
        self._notify_priority_change()
    
    def _reset_priorities(self):
        """Reset all priorities to default values."""
        for i, rule in enumerate(self.rules):
            rule['priority'] = len(self.rules) - i
        
        self._refresh_priority_list()
        self._notify_priority_change()
    
    def _save_priorities(self):
        """Save the current priority order."""
        # *Logic placeholder*: Implement priority persistence
        self._notify_priority_change()
        
        # Show confirmation
        messagebox.showinfo("Priority Order", 
                              "Rule priority order has been saved!")
    
    def _notify_priority_change(self):
        """Notify parent of priority changes."""
        if self.on_priority_change:
            self.on_priority_change(self.rules)
    
    def update_rules(self, rules: List[Dict]):
        """Update the rules list."""
        self.rules = rules
        self._refresh_priority_list()
    
    def get_prioritized_rules(self) -> List[Dict]:
        """Get rules sorted by priority."""
        return sorted(self.rules, key=lambda r: r.get('priority', 0), 
                     reverse=True)
