"""
TaskMover UI Framework - Ruleset Management Components
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import Dict, List, Any, Optional, Callable
import json
from datetime import datetime
from .base_component import BaseComponent, ComponentState
from .input_components import TextInput, Button
from .display_components import Label, Badge
from .layout_components import Panel
from .data_display_components import DataTable, ListView


class RulesetOverview(BaseComponent):
    """
    Overview display for rulesets with statistics and management options.
    """
    
    def __init__(self, parent: tk.Widget,
                 rulesets: Optional[List[Dict]] = None,
                 on_ruleset_select: Optional[Callable] = None,
                 on_ruleset_action: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the ruleset overview.
        
        Args:
            parent: Parent widget
            rulesets: List of ruleset data
            on_ruleset_select: Callback when ruleset is selected
            on_ruleset_action: Callback when action is performed on ruleset
            **kwargs: Additional widget options
        """
        self.rulesets = rulesets or []
        self.on_ruleset_select = on_ruleset_select
        self.on_ruleset_action = on_ruleset_action
        self._selected_ruleset = None
        self._filter_text = ""
        self._sort_by = "name"
        
        super().__init__(parent, **kwargs)
        
        self._setup_overview()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the ruleset overview interface."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        
        # Header with actions
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(header_frame, text="Rulesets", 
                 font=('TkDefaultFont', 12, 'bold')).pack(side=tk.LEFT)
        
        # Action buttons
        actions_frame = ttk.Frame(header_frame)
        actions_frame.pack(side=tk.RIGHT)
        
        ttk.Button(actions_frame, text="New Ruleset",
                  command=self._create_new_ruleset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Import",
                  command=self._import_ruleset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Export",
                  command=self._export_selected).pack(side=tk.LEFT)
        
        return main_frame
    
    def _setup_overview(self):
        """Set up the overview interface."""
        # Filter and search frame
        filter_frame = ttk.Frame(self._widget)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Search entry
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        
        # Sort options
        ttk.Label(filter_frame, text="Sort by:").pack(side=tk.LEFT, padx=(10, 5))
        self.sort_var = tk.StringVar(value=self._sort_by)
        sort_combo = ttk.Combobox(filter_frame, textvariable=self.sort_var,
                                 values=["name", "created", "modified", "rules"],
                                 state="readonly", width=10)
        sort_combo.pack(side=tk.LEFT)
        sort_combo.bind('<<ComboboxSelected>>', self._on_sort_change)
        
        # Ruleset cards container
        self._create_cards_container()
        
        # Details panel
        self._create_details_panel()
        
        # Refresh display
        self._refresh_display()
    
    def _create_cards_container(self):
        """Create the scrollable cards container."""
        # Cards frame with scrollbar
        cards_frame = ttk.Frame(self._widget)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Canvas for scrolling
        self.cards_canvas = tk.Canvas(cards_frame, highlightthickness=0)
        cards_scrollbar = ttk.Scrollbar(cards_frame, orient=tk.VERTICAL,
                                       command=self.cards_canvas.yview)
        self.cards_content = ttk.Frame(self.cards_canvas)
        
        self.cards_content.bind('<Configure>',
                               lambda e: self.cards_canvas.configure(
                                   scrollregion=self.cards_canvas.bbox('all')))
        
        self.cards_canvas.create_window((0, 0), window=self.cards_content,
                                       anchor='nw')
        self.cards_canvas.configure(yscrollcommand=cards_scrollbar.set)
        
        self.cards_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cards_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_details_panel(self):
        """Create the ruleset details panel."""
        details_frame = ttk.LabelFrame(self._widget, text="Ruleset Details",
                                      padding=10)
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Details content
        self.details_content = ttk.Frame(details_frame)
        self.details_content.pack(fill=tk.BOTH, expand=True)
        
        # Initially show no selection message
        self._show_no_selection()
    
    def _refresh_display(self):
        """Refresh the ruleset display."""
        # Clear existing cards
        for widget in self.cards_content.winfo_children():
            widget.destroy()
        
        # Filter and sort rulesets
        filtered_rulesets = self._get_filtered_rulesets()
        
        # Create cards for each ruleset
        for i, ruleset in enumerate(filtered_rulesets):
            self._create_ruleset_card(ruleset, i)
    
    def _get_filtered_rulesets(self) -> List[Dict]:
        """Get filtered and sorted rulesets."""
        filtered = self.rulesets
        
        # Apply search filter
        if self._filter_text:
            filtered = [rs for rs in filtered 
                       if self._filter_text.lower() in rs.get('name', '').lower()
                       or self._filter_text.lower() in rs.get('description', '').lower()]
        
        # Apply sorting
        sort_key_map = {
            'name': lambda rs: rs.get('name', '').lower(),
            'created': lambda rs: rs.get('created_date', ''),
            'modified': lambda rs: rs.get('modified_date', ''),
            'rules': lambda rs: len(rs.get('rules', []))
        }
        
        if self._sort_by in sort_key_map:
            filtered.sort(key=sort_key_map[self._sort_by])
        
        return filtered
    
    def _create_ruleset_card(self, ruleset: Dict, index: int):
        """Create a card for a ruleset."""
        # Card frame
        card_frame = ttk.Frame(self.cards_content, relief=tk.RIDGE, 
                              borderwidth=1, padding=10)
        card_frame.pack(fill=tk.X, pady=2)
        
        # Header with name and status
        header_frame = ttk.Frame(card_frame)
        header_frame.pack(fill=tk.X)
        
        # Ruleset name
        name_label = ttk.Label(header_frame, text=ruleset.get('name', 'Unnamed'),
                              font=('TkDefaultFont', 10, 'bold'))
        name_label.pack(side=tk.LEFT)
        
        # Status badge
        status = ruleset.get('status', 'inactive')
        status_color = {'active': 'green', 'inactive': 'gray', 'error': 'red'}.get(status, 'gray')
        status_badge = ttk.Label(header_frame, text=status.upper(),
                                foreground=status_color,
                                font=('TkDefaultFont', 8, 'bold'))
        status_badge.pack(side=tk.RIGHT)
        
        # Description
        desc_text = ruleset.get('description', 'No description')
        if len(desc_text) > 80:
            desc_text = desc_text[:77] + "..."
        desc_label = ttk.Label(card_frame, text=desc_text, 
                              foreground='gray')
        desc_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Statistics frame
        stats_frame = ttk.Frame(card_frame)
        stats_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Rule count
        rule_count = len(ruleset.get('rules', []))
        ttk.Label(stats_frame, text=f"Rules: {rule_count}",
                 font=('TkDefaultFont', 8)).pack(side=tk.LEFT)
        
        # Last executed
        last_exec = ruleset.get('last_executed', 'Never')
        ttk.Label(stats_frame, text=f"Last run: {last_exec}",
                 font=('TkDefaultFont', 8)).pack(side=tk.LEFT, padx=(20, 0))
        
        # Actions frame
        actions_frame = ttk.Frame(card_frame)
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Action buttons
        ttk.Button(actions_frame, text="Edit",
                  command=lambda: self._edit_ruleset(ruleset)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Execute",
                  command=lambda: self._execute_ruleset(ruleset)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Duplicate",
                  command=lambda: self._duplicate_ruleset(ruleset)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Delete",
                  command=lambda: self._delete_ruleset(ruleset)).pack(side=tk.RIGHT)
        
        # Bind click to select
        card_frame.bind("<Button-1>", lambda e: self._select_ruleset(ruleset))
        for child in card_frame.winfo_children():
            child.bind("<Button-1>", lambda e: self._select_ruleset(ruleset))
    
    def _select_ruleset(self, ruleset: Dict):
        """Select a ruleset and show its details."""
        self._selected_ruleset = ruleset
        self._show_ruleset_details(ruleset)
        
        if self.on_ruleset_select:
            self.on_ruleset_select(ruleset)
    
    def _show_ruleset_details(self, ruleset: Dict):
        """Show detailed information about a ruleset."""
        # Clear existing details
        for widget in self.details_content.winfo_children():
            widget.destroy()
        
        # Ruleset info
        info_frame = ttk.Frame(self.details_content)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Name and description
        ttk.Label(info_frame, text=ruleset.get('name', 'Unnamed'),
                 font=('TkDefaultFont', 12, 'bold')).pack(anchor=tk.W)
        ttk.Label(info_frame, text=ruleset.get('description', 'No description'),
                 foreground='gray').pack(anchor=tk.W, pady=(2, 0))
        
        # Statistics
        stats_frame = ttk.Frame(self.details_content)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create statistics grid
        stats = [
            ("Rules", len(ruleset.get('rules', []))),
            ("Created", ruleset.get('created_date', 'Unknown')),
            ("Modified", ruleset.get('modified_date', 'Unknown')),
            ("Last Executed", ruleset.get('last_executed', 'Never')),
            ("Files Processed", ruleset.get('files_processed', 0)),
            ("Success Rate", f"{ruleset.get('success_rate', 0):.1f}%")
        ]
        
        for i, (label, value) in enumerate(stats):
            row = i // 2
            col = i % 2
            
            stat_frame = ttk.Frame(stats_frame)
            stat_frame.grid(row=row, column=col, sticky=tk.W, padx=(0, 20), pady=2)
            
            ttk.Label(stat_frame, text=f"{label}:", 
                     font=('TkDefaultFont', 8, 'bold')).pack(side=tk.LEFT)
            ttk.Label(stat_frame, text=str(value),
                     font=('TkDefaultFont', 8)).pack(side=tk.LEFT, padx=(5, 0))
    
    def _show_no_selection(self):
        """Show message when no ruleset is selected."""
        for widget in self.details_content.winfo_children():
            widget.destroy()
        
        ttk.Label(self.details_content, 
                 text="Select a ruleset to view details",
                 foreground='gray').pack(expand=True)
    
    def _on_search_change(self, *args):
        """Handle search text changes."""
        self._filter_text = self.search_var.get()
        self._refresh_display()
    
    def _on_sort_change(self, event):
        """Handle sort option changes."""
        self._sort_by = self.sort_var.get()
        self._refresh_display()
    
    def _create_new_ruleset(self):
        """Create a new ruleset."""
        # *Logic placeholder*: Open ruleset editor for new ruleset
        if self.on_ruleset_action:
            self.on_ruleset_action('create', None)
    
    def _import_ruleset(self):
        """Import a ruleset from file."""
        # *Logic placeholder*: Implement ruleset import
        filename = filedialog.askopenfilename(
            title="Import Ruleset",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            if self.on_ruleset_action:
                self.on_ruleset_action('import', {'filename': filename})
    
    def _export_selected(self):
        """Export the selected ruleset."""
        if not self._selected_ruleset:
            messagebox.showwarning("No Selection", "Please select a ruleset to export.")
            return
        
        # *Logic placeholder*: Implement ruleset export
        filename = filedialog.asksaveasfilename(
            title="Export Ruleset",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            if self.on_ruleset_action:
                self.on_ruleset_action('export', {
                    'ruleset': self._selected_ruleset,
                    'filename': filename
                })
    
    def _edit_ruleset(self, ruleset: Dict):
        """Edit a ruleset."""
        if self.on_ruleset_action:
            self.on_ruleset_action('edit', ruleset)
    
    def _execute_ruleset(self, ruleset: Dict):
        """Execute a ruleset."""
        if self.on_ruleset_action:
            self.on_ruleset_action('execute', ruleset)
    
    def _duplicate_ruleset(self, ruleset: Dict):
        """Duplicate a ruleset."""
        if self.on_ruleset_action:
            self.on_ruleset_action('duplicate', ruleset)
    
    def _delete_ruleset(self, ruleset: Dict):
        """Delete a ruleset."""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete ruleset '{ruleset.get('name', 'Unnamed')}'?\n\n"
            "This action cannot be undone."
        )
        
        if result:
            if self.on_ruleset_action:
                self.on_ruleset_action('delete', ruleset)
    
    def update_rulesets(self, rulesets: List[Dict]):
        """Update the rulesets list."""
        self.rulesets = rulesets
        self._refresh_display()
    
    def refresh(self):
        """Refresh the entire display."""
        self._refresh_display()


class RulesetEditor(BaseComponent):
    """
    Editor for creating and modifying rulesets.
    """
    
    def __init__(self, parent: tk.Widget,
                 ruleset_data: Optional[Dict] = None,
                 available_rules: Optional[List[Dict]] = None,
                 on_ruleset_save: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the ruleset editor.
        
        Args:
            parent: Parent widget
            ruleset_data: Existing ruleset data to edit
            available_rules: List of available rules
            on_ruleset_save: Callback when ruleset is saved
            **kwargs: Additional widget options
        """
        self.ruleset_data = ruleset_data or {
            'name': '',
            'description': '',
            'rules': [],
            'settings': {
                'conflict_resolution': 'prompt',
                'create_backup': True,
                'dry_run': False
            }
        }
        self.available_rules = available_rules or []
        self.on_ruleset_save = on_ruleset_save
        self._is_modified = False
        
        super().__init__(parent, **kwargs)
        
        self._setup_editor()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the ruleset editor interface."""
        # Main container with notebook
        main_frame = ttk.Frame(self.parent)
        
        # Toolbar
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Save and cancel buttons
        ttk.Button(toolbar_frame, text="Save Ruleset",
                  command=self._save_ruleset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Test Ruleset",
                  command=self._test_ruleset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Cancel",
                  command=self._cancel_edit).pack(side=tk.RIGHT)
        
        return main_frame
    
    def _setup_editor(self):
        """Set up the editor interface."""
        # Create notebook for different sections
        self.notebook = ttk.Notebook(self._widget)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Basic info tab
        self._create_basic_info_tab()
        
        # Rules tab
        self._create_rules_tab()
        
        # Settings tab
        self._create_settings_tab()
        
        # Load initial data
        self._load_ruleset_data()
    
    def _create_basic_info_tab(self):
        """Create the basic information tab."""
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="Basic Info")
        
        # Form container
        form_frame = ttk.Frame(basic_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Name field
        ttk.Label(form_frame, text="Ruleset Name:").pack(anchor=tk.W)
        self.name_var = tk.StringVar()
        self.name_var.trace('w', self._on_field_change)
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, font=('TkDefaultFont', 10))
        name_entry.pack(fill=tk.X, pady=(2, 10))
        
        # Description field
        ttk.Label(form_frame, text="Description:").pack(anchor=tk.W)
        self.desc_text = tk.Text(form_frame, height=6, wrap=tk.WORD)
        self.desc_text.pack(fill=tk.BOTH, expand=True, pady=(2, 10))
        self.desc_text.bind('<KeyPress>', self._on_field_change)
        
        # Metadata frame
        meta_frame = ttk.LabelFrame(form_frame, text="Metadata", padding=10)
        meta_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Created/modified info
        self.created_label = ttk.Label(meta_frame, text="Created: Not saved")
        self.created_label.pack(anchor=tk.W)
        
        self.modified_label = ttk.Label(meta_frame, text="Modified: Not saved")
        self.modified_label.pack(anchor=tk.W)
    
    def _create_rules_tab(self):
        """Create the rules management tab."""
        rules_frame = ttk.Frame(self.notebook)
        self.notebook.add(rules_frame, text="Rules")
        
        # Rules container
        rules_container = ttk.Frame(rules_frame)
        rules_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Available rules frame
        available_frame = ttk.LabelFrame(rules_container, text="Available Rules", padding=5)
        available_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Available rules list
        self.available_listbox = tk.Listbox(available_frame, selectmode=tk.EXTENDED)
        available_scroll = ttk.Scrollbar(available_frame, orient=tk.VERTICAL,
                                        command=self.available_listbox.yview)
        self.available_listbox.configure(yscrollcommand=available_scroll.set)
        
        self.available_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        available_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons frame
        controls_frame = ttk.Frame(rules_container)
        controls_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="Add →",
                  command=self._add_selected_rules).pack(pady=2)
        ttk.Button(controls_frame, text="← Remove",
                  command=self._remove_selected_rules).pack(pady=2)
        ttk.Button(controls_frame, text="Add All →",
                  command=self._add_all_rules).pack(pady=(10, 2))
        ttk.Button(controls_frame, text="← Remove All",
                  command=self._remove_all_rules).pack(pady=2)
        
        # Selected rules frame
        selected_frame = ttk.LabelFrame(rules_container, text="Selected Rules", padding=5)
        selected_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Selected rules list
        self.selected_listbox = tk.Listbox(selected_frame, selectmode=tk.EXTENDED)
        selected_scroll = ttk.Scrollbar(selected_frame, orient=tk.VERTICAL,
                                       command=self.selected_listbox.yview)
        self.selected_listbox.configure(yscrollcommand=selected_scroll.set)
        
        self.selected_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        selected_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Reorder buttons
        reorder_frame = ttk.Frame(selected_frame)
        reorder_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(reorder_frame, text="↑ Up",
                  command=self._move_rule_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(reorder_frame, text="↓ Down",
                  command=self._move_rule_down).pack(side=tk.LEFT)
    
    def _create_settings_tab(self):
        """Create the settings tab."""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Settings container
        settings_container = ttk.Frame(settings_frame)
        settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Conflict resolution
        conflict_frame = ttk.LabelFrame(settings_container, text="Conflict Resolution", padding=10)
        conflict_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.conflict_var = tk.StringVar()
        ttk.Radiobutton(conflict_frame, text="Prompt for each conflict",
                       variable=self.conflict_var, value="prompt").pack(anchor=tk.W)
        ttk.Radiobutton(conflict_frame, text="Skip conflicting files",
                       variable=self.conflict_var, value="skip").pack(anchor=tk.W)
        ttk.Radiobutton(conflict_frame, text="Overwrite existing files",
                       variable=self.conflict_var, value="overwrite").pack(anchor=tk.W)
        ttk.Radiobutton(conflict_frame, text="Rename new files",
                       variable=self.conflict_var, value="rename").pack(anchor=tk.W)
        
        # Backup options
        backup_frame = ttk.LabelFrame(settings_container, text="Backup Options", padding=10)
        backup_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.backup_var = tk.BooleanVar()
        ttk.Checkbutton(backup_frame, text="Create backup before moving files",
                       variable=self.backup_var).pack(anchor=tk.W)
        
        # Execution options
        exec_frame = ttk.LabelFrame(settings_container, text="Execution Options", padding=10)
        exec_frame.pack(fill=tk.X)
        
        self.dry_run_var = tk.BooleanVar()
        ttk.Checkbutton(exec_frame, text="Dry run (preview only, don't move files)",
                       variable=self.dry_run_var).pack(anchor=tk.W)
        
        self.verbose_var = tk.BooleanVar()
        ttk.Checkbutton(exec_frame, text="Verbose logging",
                       variable=self.verbose_var).pack(anchor=tk.W)
    
    def _load_ruleset_data(self):
        """Load ruleset data into the editor."""
        # Load basic info
        self.name_var.set(self.ruleset_data.get('name', ''))
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(1.0, self.ruleset_data.get('description', ''))
        
        # Load metadata
        created = self.ruleset_data.get('created_date', 'Not saved')
        modified = self.ruleset_data.get('modified_date', 'Not saved')
        self.created_label.config(text=f"Created: {created}")
        self.modified_label.config(text=f"Modified: {modified}")
        
        # Load rules
        self._populate_available_rules()
        self._populate_selected_rules()
        
        # Load settings
        settings = self.ruleset_data.get('settings', {})
        self.conflict_var.set(settings.get('conflict_resolution', 'prompt'))
        self.backup_var.set(settings.get('create_backup', True))
        self.dry_run_var.set(settings.get('dry_run', False))
        self.verbose_var.set(settings.get('verbose_logging', False))
        
        self._is_modified = False
    
    def _populate_available_rules(self):
        """Populate the available rules list."""
        self.available_listbox.delete(0, tk.END)
        
        selected_rule_ids = {rule.get('id') for rule in self.ruleset_data.get('rules', [])}
        
        for rule in self.available_rules:
            if rule.get('id') not in selected_rule_ids:
                display_text = f"{rule.get('name', 'Unnamed')} - {rule.get('description', '')[:50]}"
                self.available_listbox.insert(tk.END, display_text)
    
    def _populate_selected_rules(self):
        """Populate the selected rules list."""
        self.selected_listbox.delete(0, tk.END)
        
        for rule in self.ruleset_data.get('rules', []):
            display_text = f"{rule.get('name', 'Unnamed')} - {rule.get('description', '')[:50]}"
            self.selected_listbox.insert(tk.END, display_text)
    
    def _add_selected_rules(self):
        """Add selected rules to the ruleset."""
        selection = self.available_listbox.curselection()
        if not selection:
            return
        
        # Get available rules not in ruleset
        selected_rule_ids = {rule.get('id') for rule in self.ruleset_data.get('rules', [])}
        available = [rule for rule in self.available_rules 
                    if rule.get('id') not in selected_rule_ids]
        
        # Add selected rules
        for index in selection:
            if index < len(available):
                rule = available[index]
                self.ruleset_data.setdefault('rules', []).append(rule)
        
        self._populate_available_rules()
        self._populate_selected_rules()
        self._mark_modified()
    
    def _remove_selected_rules(self):
        """Remove selected rules from the ruleset."""
        selection = self.selected_listbox.curselection()
        if not selection:
            return
        
        # Remove in reverse order to maintain indices
        for index in reversed(selection):
            if index < len(self.ruleset_data.get('rules', [])):
                del self.ruleset_data['rules'][index]
        
        self._populate_available_rules()
        self._populate_selected_rules()
        self._mark_modified()
    
    def _add_all_rules(self):
        """Add all available rules to the ruleset."""
        selected_rule_ids = {rule.get('id') for rule in self.ruleset_data.get('rules', [])}
        
        for rule in self.available_rules:
            if rule.get('id') not in selected_rule_ids:
                self.ruleset_data.setdefault('rules', []).append(rule)
        
        self._populate_available_rules()
        self._populate_selected_rules()
        self._mark_modified()
    
    def _remove_all_rules(self):
        """Remove all rules from the ruleset."""
        self.ruleset_data['rules'] = []
        self._populate_available_rules()
        self._populate_selected_rules()
        self._mark_modified()
    
    def _move_rule_up(self):
        """Move selected rule up in priority."""
        selection = self.selected_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        index = selection[0]
        rules = self.ruleset_data.get('rules', [])
        rules[index], rules[index - 1] = rules[index - 1], rules[index]
        
        self._populate_selected_rules()
        self.selected_listbox.selection_set(index - 1)
        self._mark_modified()
    
    def _move_rule_down(self):
        """Move selected rule down in priority."""
        selection = self.selected_listbox.curselection()
        rules = self.ruleset_data.get('rules', [])
        
        if not selection or selection[0] >= len(rules) - 1:
            return
        
        index = selection[0]
        rules[index], rules[index + 1] = rules[index + 1], rules[index]
        
        self._populate_selected_rules()
        self.selected_listbox.selection_set(index + 1)
        self._mark_modified()
    
    def _on_field_change(self, *args):
        """Handle field changes."""
        self._mark_modified()
    
    def _mark_modified(self):
        """Mark the ruleset as modified."""
        self._is_modified = True
    
    def _save_ruleset(self):
        """Save the ruleset."""
        # Validate required fields
        if not self.name_var.get().strip():
            messagebox.showerror("Validation Error", "Ruleset name is required.")
            return
        
        # Update ruleset data
        self.ruleset_data['name'] = self.name_var.get()
        self.ruleset_data['description'] = self.desc_text.get(1.0, tk.END).strip()
        
        # Update settings
        self.ruleset_data['settings'] = {
            'conflict_resolution': self.conflict_var.get(),
            'create_backup': self.backup_var.get(),
            'dry_run': self.dry_run_var.get(),
            'verbose_logging': self.verbose_var.get()
        }
        
        # Update timestamps
        if 'created_date' not in self.ruleset_data:
            self.ruleset_data['created_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.ruleset_data['modified_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save via callback
        if self.on_ruleset_save:
            self.on_ruleset_save(self.ruleset_data)
        
        self._is_modified = False
        messagebox.showinfo("Saved", "Ruleset saved successfully!")
    
    def _test_ruleset(self):
        """Test the ruleset."""
        # *Logic placeholder*: Implement ruleset testing
        messagebox.showinfo("Test Ruleset", "Ruleset testing functionality will be implemented here.")
    
    def _cancel_edit(self):
        """Cancel editing."""
        if self._is_modified:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?"
            )
            
            if result is True:  # Yes, save
                self._save_ruleset()
            elif result is None:  # Cancel
                return
        
        # *Logic placeholder*: Close editor or navigate back
        pass


class RulesetExecutionDashboard(BaseComponent):
    """
    Dashboard for monitoring ruleset execution.
    """
    
    def __init__(self, parent: tk.Widget,
                 execution_data: Optional[Dict] = None,
                 on_execution_control: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the execution dashboard.
        
        Args:
            parent: Parent widget
            execution_data: Current execution data
            on_execution_control: Callback for execution control actions
            **kwargs: Additional widget options
        """
        self.execution_data = execution_data or {}
        self.on_execution_control = on_execution_control
        self._update_timer = None
        
        super().__init__(parent, **kwargs)
        
        self._setup_dashboard()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the execution dashboard interface."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        
        # Header with controls
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(header_frame, text="Execution Dashboard",
                 font=('TkDefaultFont', 12, 'bold')).pack(side=tk.LEFT)
        
        # Control buttons
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT)
        
        self.start_btn = ttk.Button(controls_frame, text="Start",
                                   command=self._start_execution)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.pause_btn = ttk.Button(controls_frame, text="Pause",
                                   command=self._pause_execution, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(controls_frame, text="Stop",
                                  command=self._stop_execution, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        return main_frame
    
    def _setup_dashboard(self):
        """Set up the dashboard interface."""
        # Status frame
        status_frame = ttk.LabelFrame(self._widget, text="Execution Status", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Status indicators
        self.status_label = ttk.Label(status_frame, text="Ready",
                                     font=('TkDefaultFont', 10, 'bold'))
        self.status_label.pack(anchor=tk.W)
        
        # Progress frame
        progress_frame = ttk.Frame(status_frame)
        progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Overall progress
        ttk.Label(progress_frame, text="Overall Progress:").pack(anchor=tk.W)
        self.overall_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.overall_progress.pack(fill=tk.X, pady=(2, 5))
        
        self.progress_label = ttk.Label(progress_frame, text="0% complete")
        self.progress_label.pack(anchor=tk.W)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(self._widget, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create statistics grid
        self.stats_labels = {}
        stats_items = [
            ('files_processed', 'Files Processed'),
            ('files_moved', 'Files Moved'),
            ('files_skipped', 'Files Skipped'),
            ('errors', 'Errors'),
            ('elapsed_time', 'Elapsed Time'),
            ('estimated_remaining', 'Time Remaining')
        ]
        
        for i, (key, label) in enumerate(stats_items):
            row = i // 2
            col = i % 2
            
            stat_frame = ttk.Frame(stats_frame)
            stat_frame.grid(row=row, column=col, sticky=tk.W, padx=(0, 20), pady=2)
            
            ttk.Label(stat_frame, text=f"{label}:",
                     font=('TkDefaultFont', 8, 'bold')).pack(side=tk.LEFT)
            
            self.stats_labels[key] = ttk.Label(stat_frame, text="0",
                                              font=('TkDefaultFont', 8))
            self.stats_labels[key].pack(side=tk.LEFT, padx=(5, 0))
        
        # Log frame
        log_frame = ttk.LabelFrame(self._widget, text="Execution Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Log text with scrollbar
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_container, height=10, wrap=tk.WORD,
                               font=('Courier', 9))
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL,
                                     command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize display
        self._update_display()
    
    def _start_execution(self):
        """Start execution."""
        if self.on_execution_control:
            self.on_execution_control('start')
        
        # Update button states
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Start update timer
        self._start_update_timer()
    
    def _pause_execution(self):
        """Pause execution."""
        if self.on_execution_control:
            self.on_execution_control('pause')
        
        # Update button states
        self.start_btn.config(state=tk.NORMAL, text="Resume")
        self.pause_btn.config(state=tk.DISABLED)
    
    def _stop_execution(self):
        """Stop execution."""
        if self.on_execution_control:
            self.on_execution_control('stop')
        
        # Update button states
        self.start_btn.config(state=tk.NORMAL, text="Start")
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        
        # Stop update timer
        self._stop_update_timer()
    
    def _start_update_timer(self):
        """Start the update timer."""
        self._update_display()
        self._update_timer = self._widget.after(1000, self._start_update_timer)
    
    def _stop_update_timer(self):
        """Stop the update timer."""
        if self._update_timer:
            self._widget.after_cancel(self._update_timer)
            self._update_timer = None
    
    def _update_display(self):
        """Update the dashboard display."""
        if not self.execution_data:
            return
        
        # Update status
        status = self.execution_data.get('status', 'Ready')
        self.status_label.config(text=status)
        
        # Update progress
        progress = self.execution_data.get('progress', 0)
        self.overall_progress['value'] = progress
        self.progress_label.config(text=f"{progress:.1f}% complete")
        
        # Update statistics
        for key, label_widget in self.stats_labels.items():
            value = self.execution_data.get(key, 0)
            if key in ['elapsed_time', 'estimated_remaining']:
                # Format time values
                if isinstance(value, (int, float)):
                    minutes, seconds = divmod(int(value), 60)
                    hours, minutes = divmod(minutes, 60)
                    value = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            label_widget.config(text=str(value))
    
    def update_execution_data(self, data: Dict):
        """Update execution data."""
        self.execution_data.update(data)
        self._update_display()
    
    def add_log_entry(self, message: str, level: str = 'info'):
        """Add an entry to the execution log."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level.upper()}: {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear the execution log."""
        self.log_text.delete(1.0, tk.END)
