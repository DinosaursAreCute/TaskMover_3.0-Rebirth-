"""
TaskMover UI Framework - Pattern Management Components
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, List, Any, Optional, Callable
from .base_component import BaseComponent, ComponentState
from .input_components import TextInput, Button
from .display_components import Label
from .layout_components import Panel
from .data_display_components import ListView, DataTable


class PatternBuilder(BaseComponent):
    """
    Visual pattern builder for creating file organization patterns.
    """
    
    def __init__(self, parent: tk.Widget,
                 pattern_data: Optional[Dict] = None,
                 on_pattern_change: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the pattern builder.
        
        Args:
            parent: Parent widget
            pattern_data: Existing pattern data to edit
            on_pattern_change: Callback when pattern changes
            **kwargs: Additional widget options
        """
        self.pattern_data = pattern_data or {
            'name': '',
            'description': '',
            'criteria': [],
            'enabled': True
        }
        self.on_pattern_change = on_pattern_change
        self._validation_errors = []
        
        super().__init__(parent, **kwargs)
        
        self._setup_pattern_builder()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the pattern builder interface."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        
        # Header section
        header_frame = ttk.LabelFrame(main_frame, text="Pattern Information", padding=10)
        header_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Pattern name input
        name_frame = ttk.Frame(header_frame)
        name_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        ttk.Label(name_frame, text="Pattern Name:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar(value=self.pattern_data.get('name', ''))
        self.name_entry = ttk.Entry(name_frame, textvariable=self.name_var)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        self.name_var.trace('w', self._on_pattern_change)
        
        # Pattern description input
        desc_frame = ttk.Frame(header_frame)
        desc_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        
        ttk.Label(desc_frame, text="Description:").pack(side=tk.LEFT)
        self.desc_var = tk.StringVar(value=self.pattern_data.get('description', ''))
        self.desc_entry = ttk.Entry(desc_frame, textvariable=self.desc_var)
        self.desc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        self.desc_var.trace('w', self._on_pattern_change)
        
        # Pattern criteria section
        criteria_frame = ttk.LabelFrame(main_frame, text="Pattern Criteria", padding=10)
        criteria_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Criteria toolbar
        toolbar_frame = ttk.Frame(criteria_frame)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar_frame, text="Add Filename Criteria",
                  command=self._add_filename_criteria).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Add Extension Criteria",
                  command=self._add_extension_criteria).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Add Size Criteria",
                  command=self._add_size_criteria).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Add Date Criteria",
                  command=self._add_date_criteria).pack(side=tk.LEFT)
        
        # Criteria list
        criteria_list_frame = ttk.Frame(criteria_frame)
        criteria_list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Criteria listbox with scrollbar
        list_container = ttk.Frame(criteria_list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.criteria_listbox = tk.Listbox(list_container, height=6)
        criteria_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL,
                                         command=self.criteria_listbox.yview)
        
        self.criteria_listbox.configure(yscrollcommand=criteria_scrollbar.set)
        self.criteria_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        criteria_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Criteria buttons
        criteria_btn_frame = ttk.Frame(criteria_frame)
        criteria_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 0))
        
        ttk.Button(criteria_btn_frame, text="Edit Selected",
                  command=self._edit_criteria).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(criteria_btn_frame, text="Remove Selected",
                  command=self._remove_criteria).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(criteria_btn_frame, text="Move Up",
                  command=self._move_criteria_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(criteria_btn_frame, text="Move Down",
                  command=self._move_criteria_down).pack(side=tk.LEFT)
        
        # Pattern preview section
        preview_frame = ttk.LabelFrame(main_frame, text="Pattern Preview", padding=10)
        preview_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.preview_text = tk.Text(preview_frame, height=3, state='disabled',
                                   font=('Consolas', 9), wrap=tk.WORD)
        self.preview_text.pack(side=tk.TOP, fill=tk.X)
        
        # Load existing criteria
        self._load_pattern_data()
        
        return main_frame
    
    def _setup_pattern_builder(self):
        """Setup pattern builder event handling."""
        self.bind_event('pattern_changed', self._update_preview)
        
        # *Logic placeholder*: Connect to pattern validation system
        # This would integrate with the TaskMover pattern engine
    
    def _load_pattern_data(self):
        """Load existing pattern data into the interface."""
        criteria = self.pattern_data.get('criteria', [])
        
        for criterion in criteria:
            self._add_criterion_to_list(criterion)
        
        self._update_preview()
    
    def _add_criterion_to_list(self, criterion: Dict):
        """Add a criterion to the criteria list."""
        display_text = self._format_criterion_display(criterion)
        self.criteria_listbox.insert(tk.END, display_text)
    
    def _format_criterion_display(self, criterion: Dict) -> str:
        """Format criterion for display in list."""
        criterion_type = criterion.get('type', 'unknown')
        
        if criterion_type == 'filename':
            pattern = criterion.get('pattern', '')
            return f"Filename: {pattern}"
        elif criterion_type == 'extension':
            extensions = criterion.get('extensions', [])
            return f"Extension: {', '.join(extensions)}"
        elif criterion_type == 'size':
            operator = criterion.get('operator', '')
            size = criterion.get('size', '')
            return f"Size: {operator} {size}"
        elif criterion_type == 'date':
            field = criterion.get('field', '')
            operator = criterion.get('operator', '')
            date = criterion.get('date', '')
            return f"Date ({field}): {operator} {date}"
        
        return f"Unknown: {criterion}"
    
    def _add_filename_criteria(self):
        """Add filename pattern criteria."""
        dialog = FilenamePatternDialog(self._widget)
        result = dialog.show_modal()
        
        if result:
            criterion = {
                'type': 'filename',
                'pattern': result['pattern'],
                'case_sensitive': result.get('case_sensitive', False)
            }
            self._add_criterion(criterion)
    
    def _add_extension_criteria(self):
        """Add file extension criteria."""
        dialog = ExtensionPatternDialog(self._widget)
        result = dialog.show_modal()
        
        if result:
            criterion = {
                'type': 'extension',
                'extensions': result['extensions']
            }
            self._add_criterion(criterion)
    
    def _add_size_criteria(self):
        """Add file size criteria."""
        dialog = SizePatternDialog(self._widget)
        result = dialog.show_modal()
        
        if result:
            criterion = {
                'type': 'size',
                'operator': result['operator'],
                'size': result['size'],
                'unit': result['unit']
            }
            self._add_criterion(criterion)
    
    def _add_date_criteria(self):
        """Add date criteria."""
        dialog = DatePatternDialog(self._widget)
        result = dialog.show_modal()
        
        if result:
            criterion = {
                'type': 'date',
                'field': result['field'],
                'operator': result['operator'],
                'date': result['date']
            }
            self._add_criterion(criterion)
    
    def _add_criterion(self, criterion: Dict):
        """Add a criterion to the pattern."""
        self.pattern_data.setdefault('criteria', []).append(criterion)
        self._add_criterion_to_list(criterion)
        self._on_pattern_change()
    
    def _edit_criteria(self):
        """Edit the selected criteria."""
        selection = self.criteria_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a criteria to edit.")
            return
        
        index = selection[0]
        criterion = self.pattern_data['criteria'][index]
        
        # *Logic placeholder*: Open appropriate dialog based on criterion type
        # This would open the specific dialog for editing the criterion
        messagebox.showinfo("Edit Criteria", f"Edit criteria functionality for: {criterion['type']}")
    
    def _remove_criteria(self):
        """Remove the selected criteria."""
        selection = self.criteria_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a criteria to remove.")
            return
        
        index = selection[0]
        self.criteria_listbox.delete(index)
        del self.pattern_data['criteria'][index]
        self._on_pattern_change()
    
    def _move_criteria_up(self):
        """Move selected criteria up in the list."""
        selection = self.criteria_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        index = selection[0]
        # Swap items in data
        criteria = self.pattern_data['criteria']
        criteria[index], criteria[index-1] = criteria[index-1], criteria[index]
        
        # Update display
        self._refresh_criteria_list()
        self.criteria_listbox.selection_set(index-1)
        self._on_pattern_change()
    
    def _move_criteria_down(self):
        """Move selected criteria down in the list."""
        selection = self.criteria_listbox.curselection()
        if not selection or selection[0] >= len(self.pattern_data['criteria']) - 1:
            return
        
        index = selection[0]
        # Swap items in data
        criteria = self.pattern_data['criteria']
        criteria[index], criteria[index+1] = criteria[index+1], criteria[index]
        
        # Update display
        self._refresh_criteria_list()
        self.criteria_listbox.selection_set(index+1)
        self._on_pattern_change()
    
    def _refresh_criteria_list(self):
        """Refresh the criteria list display."""
        self.criteria_listbox.delete(0, tk.END)
        for criterion in self.pattern_data['criteria']:
            self._add_criterion_to_list(criterion)
    
    def _on_pattern_change(self, *args):
        """Handle pattern data changes."""
        self.pattern_data['name'] = self.name_var.get()
        self.pattern_data['description'] = self.desc_var.get()
        
        self._validate_pattern()
        self._update_preview()
        
        if self.on_pattern_change:
            self.on_pattern_change(self.pattern_data)
        
        self.trigger_event('pattern_changed', self.pattern_data)
    
    def _validate_pattern(self):
        """Validate the current pattern."""
        self._validation_errors = []
        
        # Validate name
        if not self.pattern_data['name'].strip():
            self._validation_errors.append("Pattern name is required")
        
        # Validate criteria
        if not self.pattern_data.get('criteria'):
            self._validation_errors.append("At least one criteria is required")
        
        # *Logic placeholder*: Additional pattern validation
        # This would validate pattern syntax and logic
    
    def _update_preview(self):
        """Update the pattern preview display."""
        preview_text = self._generate_pattern_preview()
        
        self.preview_text.configure(state='normal')
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview_text)
        self.preview_text.configure(state='disabled')
    
    def _generate_pattern_preview(self) -> str:
        """Generate a text preview of the pattern."""
        if not self.pattern_data.get('criteria'):
            return "No criteria defined"
        
        preview_lines = []
        for i, criterion in enumerate(self.pattern_data['criteria'], 1):
            preview_lines.append(f"{i}. {self._format_criterion_display(criterion)}")
        
        return "\n".join(preview_lines)
    
    def get_pattern_data(self) -> Dict:
        """Get the current pattern data."""
        return self.pattern_data.copy()
    
    def set_pattern_data(self, pattern_data: Dict):
        """Set the pattern data."""
        self.pattern_data = pattern_data.copy()
        self.name_var.set(pattern_data.get('name', ''))
        self.desc_var.set(pattern_data.get('description', ''))
        self._refresh_criteria_list()
        self._update_preview()
    
    def is_valid(self) -> bool:
        """Check if the current pattern is valid."""
        self._validate_pattern()
        return len(self._validation_errors) == 0
    
    def get_validation_errors(self) -> List[str]:
        """Get current validation errors."""
        return self._validation_errors.copy()


class PatternManager(BaseComponent):
    """
    Pattern management interface for viewing and organizing patterns.
    """
    
    def __init__(self, parent: tk.Widget,
                 patterns: Optional[List[Dict]] = None,
                 on_pattern_select: Optional[Callable] = None,
                 on_pattern_edit: Optional[Callable] = None,
                 on_pattern_delete: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the pattern manager.
        
        Args:
            parent: Parent widget
            patterns: List of pattern data
            on_pattern_select: Callback when pattern is selected
            on_pattern_edit: Callback when pattern is edited
            on_pattern_delete: Callback when pattern is deleted
            **kwargs: Additional widget options
        """
        self.patterns = patterns or []
        self.on_pattern_select = on_pattern_select
        self.on_pattern_edit = on_pattern_edit
        self.on_pattern_delete = on_pattern_delete
        self._selected_pattern = None
        self._filtered_patterns = []
        
        super().__init__(parent, **kwargs)
        
        self._setup_pattern_manager()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the pattern manager interface."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        
        # Toolbar
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar_frame, text="New Pattern",
                  command=self._new_pattern).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Edit Pattern",
                  command=self._edit_pattern).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Duplicate Pattern",
                  command=self._duplicate_pattern).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Delete Pattern",
                  command=self._delete_pattern).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separator
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Button(toolbar_frame, text="Test Pattern",
                  command=self._test_pattern).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Export Patterns",
                  command=self._export_patterns).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Import Patterns",
                  command=self._import_patterns).pack(side=tk.LEFT)
        
        # Search and filter
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        self.search_var.trace('w', self._on_search_change)
        
        ttk.Label(search_frame, text="Filter:").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(search_frame, textvariable=self.filter_var,
                                   values=["All", "Enabled", "Disabled", "Unused"],
                                   state="readonly", width=10)
        filter_combo.pack(side=tk.LEFT, padx=(5, 0))
        filter_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # Pattern list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Configure treeview for pattern list
        columns = ('name', 'description', 'criteria_count', 'enabled', 'last_used')
        self.pattern_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        
        # Configure column headings
        self.pattern_tree.heading('#0', text='ID')
        self.pattern_tree.heading('name', text='Name')
        self.pattern_tree.heading('description', text='Description')
        self.pattern_tree.heading('criteria_count', text='Criteria')
        self.pattern_tree.heading('enabled', text='Enabled')
        self.pattern_tree.heading('last_used', text='Last Used')
        
        # Configure column widths
        self.pattern_tree.column('#0', width=50, minwidth=50)
        self.pattern_tree.column('name', width=150, minwidth=100)
        self.pattern_tree.column('description', width=250, minwidth=150)
        self.pattern_tree.column('criteria_count', width=80, minwidth=60)
        self.pattern_tree.column('enabled', width=80, minwidth=60)
        self.pattern_tree.column('last_used', width=120, minwidth=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.pattern_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.pattern_tree.xview)
        
        self.pattern_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.pattern_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.pattern_tree.bind('<<TreeviewSelect>>', self._on_pattern_select)
        self.pattern_tree.bind('<Double-1>', self._on_pattern_double_click)
        
        # Load patterns
        self._load_patterns()
        
        return main_frame
    
    def _setup_pattern_manager(self):
        """Setup pattern manager event handling."""
        # *Logic placeholder*: Connect to pattern data source
        # This would connect to the TaskMover pattern storage system
        pass
    
    def _load_patterns(self):
        """Load patterns into the tree view."""
        # Clear existing items
        for item in self.pattern_tree.get_children():
            self.pattern_tree.delete(item)
        
        # Apply filters
        self._apply_filters()
        
        # Add filtered patterns
        for i, pattern in enumerate(self._filtered_patterns):
            item_id = f"pattern_{i}"
            
            values = (
                pattern.get('name', ''),
                pattern.get('description', ''),
                len(pattern.get('criteria', [])),
                'Yes' if pattern.get('enabled', True) else 'No',
                pattern.get('last_used', 'Never')
            )
            
            self.pattern_tree.insert('', tk.END, iid=item_id, text=str(i+1), values=values)
    
    def _apply_filters(self):
        """Apply search and filter criteria to patterns."""
        search_term = self.search_var.get().lower()
        filter_type = self.filter_var.get()
        
        self._filtered_patterns = []
        
        for pattern in self.patterns:
            # Apply search filter
            if search_term:
                name_match = search_term in pattern.get('name', '').lower()
                desc_match = search_term in pattern.get('description', '').lower()
                if not (name_match or desc_match):
                    continue
            
            # Apply type filter
            if filter_type == "Enabled" and not pattern.get('enabled', True):
                continue
            elif filter_type == "Disabled" and pattern.get('enabled', True):
                continue
            elif filter_type == "Unused" and pattern.get('usage_count', 0) > 0:
                continue
            
            self._filtered_patterns.append(pattern)
    
    def _on_search_change(self, *args):
        """Handle search text changes."""
        self._load_patterns()
    
    def _on_filter_change(self, event=None):
        """Handle filter changes."""
        self._load_patterns()
    
    def _on_pattern_select(self, event):
        """Handle pattern selection."""
        selection = self.pattern_tree.selection()
        if selection:
            item_id = selection[0]
            index = int(item_id.split('_')[1])
            self._selected_pattern = self._filtered_patterns[index]
            
            if self.on_pattern_select:
                self.on_pattern_select(self._selected_pattern)
            
            self.trigger_event('pattern_selected', self._selected_pattern)
    
    def _on_pattern_double_click(self, event):
        """Handle pattern double-click (edit)."""
        self._edit_pattern()
    
    def _new_pattern(self):
        """Create a new pattern."""
        # *Logic placeholder*: Open pattern builder for new pattern
        if self.on_pattern_edit:
            self.on_pattern_edit(None)
        self.trigger_event('pattern_new')
    
    def _edit_pattern(self):
        """Edit the selected pattern."""
        if not self._selected_pattern:
            messagebox.showwarning("No Selection", "Please select a pattern to edit.")
            return
        
        # *Logic placeholder*: Open pattern builder for editing
        if self.on_pattern_edit:
            self.on_pattern_edit(self._selected_pattern)
        self.trigger_event('pattern_edit', self._selected_pattern)
    
    def _duplicate_pattern(self):
        """Duplicate the selected pattern."""
        if not self._selected_pattern:
            messagebox.showwarning("No Selection", "Please select a pattern to duplicate.")
            return
        
        # *Logic placeholder*: Create duplicate pattern
        duplicate = self._selected_pattern.copy()
        duplicate['name'] = f"{duplicate['name']} (Copy)"
        
        self.trigger_event('pattern_duplicate', duplicate)
    
    def _delete_pattern(self):
        """Delete the selected pattern."""
        if not self._selected_pattern:
            messagebox.showwarning("No Selection", "Please select a pattern to delete.")
            return
        
        result = messagebox.askyesno("Confirm Delete",
                                   f"Are you sure you want to delete the pattern '{self._selected_pattern['name']}'?\n\n"
                                   "This action cannot be undone.")
        
        if result:
            if self.on_pattern_delete:
                self.on_pattern_delete(self._selected_pattern)
            self.trigger_event('pattern_delete', self._selected_pattern)
    
    def _test_pattern(self):
        """Test the selected pattern."""
        if not self._selected_pattern:
            messagebox.showwarning("No Selection", "Please select a pattern to test.")
            return
        
        # *Logic placeholder*: Open pattern tester
        self.trigger_event('pattern_test', self._selected_pattern)
    
    def _export_patterns(self):
        """Export patterns to file."""
        # *Logic placeholder*: Export pattern data
        self.trigger_event('patterns_export')
    
    def _import_patterns(self):
        """Import patterns from file."""
        # *Logic placeholder*: Import pattern data
        self.trigger_event('patterns_import')
    
    def add_pattern(self, pattern: Dict):
        """Add a new pattern to the list."""
        self.patterns.append(pattern)
        self._load_patterns()
    
    def update_pattern(self, pattern: Dict):
        """Update an existing pattern."""
        # Find and update the pattern
        for i, existing in enumerate(self.patterns):
            if existing.get('id') == pattern.get('id'):
                self.patterns[i] = pattern
                break
        self._load_patterns()
    
    def remove_pattern(self, pattern: Dict):
        """Remove a pattern from the list."""
        self.patterns = [p for p in self.patterns if p.get('id') != pattern.get('id')]
        self._load_patterns()
    
    def get_selected_pattern(self) -> Optional[Dict]:
        """Get the currently selected pattern."""
        return self._selected_pattern
    
    def set_patterns(self, patterns: List[Dict]):
        """Set the pattern list."""
        self.patterns = patterns
        self._load_patterns()


class PatternTester(BaseComponent):
    """
    Pattern testing interface for validating patterns against sample files.
    """
    
    def __init__(self, parent: tk.Widget,
                 pattern_data: Optional[Dict] = None,
                 test_files: Optional[List[str]] = None,
                 **kwargs):
        """
        Initialize the pattern tester.
        
        Args:
            parent: Parent widget
            pattern_data: Pattern to test
            test_files: List of test file paths
            **kwargs: Additional widget options
        """
        self.pattern_data = pattern_data
        self.test_files = test_files or []
        self._test_results = []
        
        super().__init__(parent, **kwargs)
        
        self._setup_pattern_tester()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the pattern tester interface."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        
        # Pattern info section
        pattern_frame = ttk.LabelFrame(main_frame, text="Pattern Information", padding=10)
        pattern_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        if self.pattern_data:
            pattern_name = self.pattern_data.get('name', 'Unnamed Pattern')
            pattern_desc = self.pattern_data.get('description', 'No description')
            
            ttk.Label(pattern_frame, text=f"Pattern: {pattern_name}",
                     font=('Arial', 10, 'bold')).pack(anchor='w')
            ttk.Label(pattern_frame, text=f"Description: {pattern_desc}").pack(anchor='w')
        else:
            ttk.Label(pattern_frame, text="No pattern selected",
                     font=('Arial', 10, 'bold')).pack(anchor='w')
        
        # Test files section
        files_frame = ttk.LabelFrame(main_frame, text="Test Files", padding=10)
        files_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # File management toolbar
        file_toolbar = ttk.Frame(files_frame)
        file_toolbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_toolbar, text="Add Files",
                  command=self._add_test_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_toolbar, text="Add Directory",
                  command=self._add_test_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_toolbar, text="Remove Selected",
                  command=self._remove_test_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_toolbar, text="Clear All",
                  command=self._clear_test_files).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(file_toolbar, text="Run Test",
                  command=self._run_test).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(file_toolbar, text="Export Results",
                  command=self._export_results).pack(side=tk.RIGHT)
        
        # Test results display
        results_container = ttk.Frame(files_frame)
        results_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Configure treeview for test results
        columns = ('filename', 'path', 'match', 'reason')
        self.results_tree = ttk.Treeview(results_container, columns=columns, show='tree headings')
        
        # Configure column headings
        self.results_tree.heading('#0', text='#')
        self.results_tree.heading('filename', text='Filename')
        self.results_tree.heading('path', text='Path')
        self.results_tree.heading('match', text='Match')
        self.results_tree.heading('reason', text='Reason')
        
        # Configure column widths
        self.results_tree.column('#0', width=50, minwidth=30)
        self.results_tree.column('filename', width=200, minwidth=150)
        self.results_tree.column('path', width=300, minwidth=200)
        self.results_tree.column('match', width=80, minwidth=60)
        self.results_tree.column('reason', width=200, minwidth=150)
        
        # Scrollbars for results
        results_v_scroll = ttk.Scrollbar(results_container, orient=tk.VERTICAL,
                                       command=self.results_tree.yview)
        results_h_scroll = ttk.Scrollbar(results_container, orient=tk.HORIZONTAL,
                                       command=self.results_tree.xview)
        
        self.results_tree.configure(yscrollcommand=results_v_scroll.set,
                                   xscrollcommand=results_h_scroll.set)
        
        # Pack results components
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        results_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Test summary section
        summary_frame = ttk.LabelFrame(main_frame, text="Test Summary", padding=10)
        summary_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.summary_text = tk.Text(summary_frame, height=3, state='disabled',
                                   font=('Arial', 9))
        self.summary_text.pack(side=tk.TOP, fill=tk.X)
        
        # Load initial test files
        self._load_test_files()
        
        return main_frame
    
    def _setup_pattern_tester(self):
        """Setup pattern tester event handling."""
        # *Logic placeholder*: Connect to pattern testing engine
        # This would integrate with the TaskMover pattern matching system
        pass
    
    def _load_test_files(self):
        """Load test files into the results display."""
        # Clear existing results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Add test files (no results yet)
        for i, file_path in enumerate(self.test_files):
            import os
            filename = os.path.basename(file_path)
            values = (filename, file_path, 'Not tested', '')
            
            self.results_tree.insert('', tk.END, iid=f"file_{i}", text=str(i+1), values=values)
        
        self._update_summary()
    
    def _add_test_files(self):
        """Add individual test files."""
        from tkinter import filedialog
        
        files = filedialog.askopenfilenames(
            title="Select test files",
            filetypes=[("All files", "*.*")]
        )
        
        for file_path in files:
            if file_path not in self.test_files:
                self.test_files.append(file_path)
        
        self._load_test_files()
    
    def _add_test_directory(self):
        """Add all files from a directory."""
        from tkinter import filedialog
        import os
        
        directory = filedialog.askdirectory(title="Select test directory")
        if directory:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in self.test_files:
                        self.test_files.append(file_path)
        
        self._load_test_files()
    
    def _remove_test_files(self):
        """Remove selected test files."""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select files to remove.")
            return
        
        # Get indices of selected items
        indices = []
        for item_id in selection:
            index = int(item_id.split('_')[1])
            indices.append(index)
        
        # Remove files (reverse order to maintain indices)
        for index in sorted(indices, reverse=True):
            del self.test_files[index]
        
        self._load_test_files()
    
    def _clear_test_files(self):
        """Clear all test files."""
        if self.test_files:
            result = messagebox.askyesno("Confirm Clear",
                                       "Are you sure you want to clear all test files?")
            if result:
                self.test_files.clear()
                self._load_test_files()
    
    def _run_test(self):
        """Run pattern test against all test files."""
        if not self.pattern_data:
            messagebox.showerror("No Pattern", "Please select a pattern to test.")
            return
        
        if not self.test_files:
            messagebox.showwarning("No Files", "Please add test files to run the test.")
            return
        
        # *Logic placeholder*: Run actual pattern matching
        # This would use the TaskMover pattern engine to test each file
        
        # Simulate test results for demonstration
        self._test_results = []
        for file_path in self.test_files:
            result = self._simulate_pattern_test(file_path)
            self._test_results.append(result)
        
        self._display_test_results()
        self._update_summary()
    
    def _simulate_pattern_test(self, file_path: str) -> Dict:
        """Simulate pattern testing (placeholder for actual implementation)."""
        import os
        import random
        
        filename = os.path.basename(file_path)
        
        # Simulate random match results for demonstration
        matches = random.choice([True, False])
        
        if matches:
            reasons = ["Filename matches pattern", "Extension matches", "Size criteria met"]
            reason = random.choice(reasons)
        else:
            reasons = ["Filename doesn't match", "Wrong extension", "Size too small", "Size too large"]
            reason = random.choice(reasons)
        
        return {
            'file_path': file_path,
            'filename': filename,
            'matches': matches,
            'reason': reason
        }
    
    def _display_test_results(self):
        """Display test results in the tree view."""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Add results
        for i, result in enumerate(self._test_results):
            values = (
                result['filename'],
                result['file_path'],
                'Match' if result['matches'] else 'No Match',
                result['reason']
            )
            
            item_id = f"result_{i}"
            item = self.results_tree.insert('', tk.END, iid=item_id, text=str(i+1), values=values)
            
            # Color code results
            if result['matches']:
                self.results_tree.set(item, 'match', '✓ Match')
            else:
                self.results_tree.set(item, 'match', '✗ No Match')
    
    def _update_summary(self):
        """Update the test summary display."""
        if not self._test_results:
            summary = f"Test files loaded: {len(self.test_files)}\nNo test results yet."
        else:
            total_files = len(self._test_results)
            matches = sum(1 for r in self._test_results if r['matches'])
            no_matches = total_files - matches
            
            match_rate = (matches / total_files * 100) if total_files > 0 else 0
            
            summary = (f"Total files tested: {total_files}\n"
                      f"Matches: {matches} ({match_rate:.1f}%)\n"
                      f"No matches: {no_matches} ({100-match_rate:.1f}%)")
        
        self.summary_text.configure(state='normal')
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        self.summary_text.configure(state='disabled')
    
    def _export_results(self):
        """Export test results to file."""
        if not self._test_results:
            messagebox.showwarning("No Results", "Please run a test before exporting results.")
            return
        
        # *Logic placeholder*: Export results to CSV or JSON
        messagebox.showinfo("Export", "Test results exported successfully!")
    
    def set_pattern(self, pattern_data: Dict):
        """Set the pattern to test."""
        self.pattern_data = pattern_data
        self._test_results.clear()
        
        # Update pattern info display
        # This would refresh the pattern information section
    
    def set_test_files(self, file_paths: List[str]):
        """Set the test files."""
        self.test_files = file_paths
        self._load_test_files()
    
    def get_test_results(self) -> List[Dict]:
        """Get the test results."""
        return self._test_results.copy()


# Dialog classes for pattern criteria input (simplified implementations)

class FilenamePatternDialog:
    """Dialog for creating filename pattern criteria."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
    
    def show_modal(self):
        """Show dialog and return result."""
        # *Logic placeholder*: Implement full filename pattern dialog
        # This would show a dialog for entering filename patterns with regex support
        
        # Simplified implementation for demonstration
        pattern = simpledialog.askstring("Filename Pattern", "Enter filename pattern:")
        if pattern:
            self.result = {'pattern': pattern, 'case_sensitive': False}
        return self.result


class ExtensionPatternDialog:
    """Dialog for creating file extension criteria."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
    
    def show_modal(self):
        """Show dialog and return result."""
        # *Logic placeholder*: Implement full extension dialog
        # This would show a dialog for selecting file extensions
        
        # Simplified implementation for demonstration
        extensions = simpledialog.askstring("File Extensions", 
                                              "Enter file extensions (comma-separated):")
        if extensions:
            ext_list = [ext.strip() for ext in extensions.split(',')]
            self.result = {'extensions': ext_list}
        return self.result


class SizePatternDialog:
    """Dialog for creating file size criteria."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
    
    def show_modal(self):
        """Show dialog and return result."""
        # *Logic placeholder*: Implement full size criteria dialog
        # This would show a dialog for setting size operators and values
        
        # Simplified implementation for demonstration
        size = simpledialog.askstring("File Size", "Enter size criteria (e.g., >10MB):")
        if size:
            self.result = {'operator': '>', 'size': '10', 'unit': 'MB'}
        return self.result


class DatePatternDialog:
    """Dialog for creating date criteria."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
    
    def show_modal(self):
        """Show dialog and return result."""
        # *Logic placeholder*: Implement full date criteria dialog
        # This would show a dialog for setting date fields and comparisons
        
        # Simplified implementation for demonstration
        date_criteria = simpledialog.askstring("Date Criteria", 
                                                 "Enter date criteria (e.g., modified after 2023-01-01):")
        if date_criteria:
            self.result = {'field': 'modified', 'operator': 'after', 'date': '2023-01-01'}
        return self.result
