"""
Rule management UI components for TaskMover Redesigned.
Clean, maintainable rule editing and management interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttkb
from typing import Dict, Any, Optional, Callable, List
import logging

from .components import Tooltip, TextInputDialog, ConfirmDialog
from ..core.rules import RuleManager
from ..core.config import ConfigManager

logger = logging.getLogger("TaskMover.UI.Rules")


class RuleEditor:
    """Rule editing dialog with validation and user-friendly interface."""
    
    def __init__(self, parent: tk.Widget, rule_manager: RuleManager, 
                 rule_name: Optional[str] = None):
        self.parent = parent
        self.rule_manager = rule_manager
        self.rule_name = rule_name
        self.result = None
        
        # Create dialog
        self.dialog = ttkb.Toplevel(parent)
        self.dialog.title("Add Rule" if rule_name is None else f"Edit Rule: {rule_name}")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        from ..core.utils import center_window
        center_window(self.dialog, 500, 400)
        
        self._create_widgets()
        self._load_rule_data()
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        main_frame = ttkb.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Rule name
        name_frame = ttkb.Frame(main_frame)
        name_frame.pack(fill="x", pady=(0, 15))
        
        ttkb.Label(name_frame, text="Rule Name:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.name_var = tk.StringVar()
        name_entry = ttkb.Entry(name_frame, textvariable=self.name_var, font=("Arial", 10))
        name_entry.pack(fill="x", pady=(5, 0))
        Tooltip(name_entry, "Enter a descriptive name for this rule")
        
        # File patterns
        patterns_frame = ttkb.Frame(main_frame)
        patterns_frame.pack(fill="x", pady=(0, 15))
        
        ttkb.Label(patterns_frame, text="File Patterns:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        patterns_help = ttkb.Label(
            patterns_frame, 
            text="Examples: *.pdf, *.docx, report_*.txt (one per line)",
            font=("Arial", 9),
            foreground="gray"
        )
        patterns_help.pack(anchor="w")
        
        # Patterns text area with scrollbar
        patterns_text_frame = ttkb.Frame(patterns_frame)
        patterns_text_frame.pack(fill="both", expand=True, pady=(5, 0))
        
        self.patterns_text = tk.Text(patterns_text_frame, height=5, font=("Arial", 10))
        patterns_scrollbar = ttkb.Scrollbar(patterns_text_frame, orient="vertical", 
                                           command=self.patterns_text.yview)
        self.patterns_text.configure(yscrollcommand=patterns_scrollbar.set)
        
        self.patterns_text.pack(side="left", fill="both", expand=True)
        patterns_scrollbar.pack(side="right", fill="y")
        
        Tooltip(self.patterns_text, "Enter file patterns that this rule should match\\n"
                                   "Use * as wildcard (e.g., *.pdf for all PDF files)")
        
        # Destination path
        path_frame = ttkb.Frame(main_frame)
        path_frame.pack(fill="x", pady=(0, 15))
        
        ttkb.Label(path_frame, text="Destination Folder:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        path_entry_frame = ttkb.Frame(path_frame)
        path_entry_frame.pack(fill="x", pady=(5, 0))
        
        self.path_var = tk.StringVar()
        path_entry = ttkb.Entry(path_entry_frame, textvariable=self.path_var, font=("Arial", 10))
        path_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = ttkb.Button(path_entry_frame, text="Browse...", command=self._browse_path)
        browse_btn.pack(side="right", padx=(10, 0))
        
        Tooltip(path_entry, "Folder where matching files will be moved")
        Tooltip(browse_btn, "Browse for destination folder")
        
        # Options
        options_frame = ttkb.LabelFrame(main_frame, text="Options", padding=10)
        options_frame.pack(fill="x", pady=(0, 15))
        
        self.active_var = tk.BooleanVar(value=True)
        active_cb = ttkb.Checkbutton(options_frame, text="Rule is active", variable=self.active_var)
        active_cb.pack(anchor="w", pady=2)
        Tooltip(active_cb, "Inactive rules are ignored during organization")
        
        self.unzip_var = tk.BooleanVar(value=False)
        unzip_cb = ttkb.Checkbutton(options_frame, text="Automatically unzip archives", variable=self.unzip_var)
        unzip_cb.pack(anchor="w", pady=2)
        Tooltip(unzip_cb, "Extract ZIP files after moving them")
        
        # Buttons
        button_frame = ttkb.Frame(main_frame)
        button_frame.pack(fill="x", pady=(15, 0))
        
        cancel_btn = ttkb.Button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_btn.pack(side="right", padx=(10, 0))
        
        save_btn = ttkb.Button(button_frame, text="Save", command=self._on_save, 
                              style="success.TButton")
        save_btn.pack(side="right")
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda e: self._on_save())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
    
    def _load_rule_data(self):
        """Load existing rule data if editing."""
        if self.rule_name and self.rule_name in self.rule_manager.rules:
            rule_data = self.rule_manager.rules[self.rule_name]
            
            self.name_var.set(self.rule_name)
            self.path_var.set(rule_data.get('path', ''))
            self.active_var.set(rule_data.get('active', True))
            self.unzip_var.set(rule_data.get('unzip', False))
            
            # Load patterns (one per line)
            patterns = rule_data.get('patterns', [])
            self.patterns_text.insert("1.0", "\\n".join(patterns))
    
    def _browse_path(self):
        """Browse for destination folder."""
        folder = filedialog.askdirectory(
            title="Select Destination Folder",
            initialdir=self.path_var.get() or "/"
        )
        if folder:
            self.path_var.set(folder)
    
    def _validate_input(self) -> tuple[bool, str]:
        """Validate user input."""
        name = self.name_var.get().strip()
        if not name:
            return False, "Rule name is required"
        
        # Check for duplicate names (except when editing the same rule)
        if name != self.rule_name and name in self.rule_manager.rules:
            return False, f"Rule '{name}' already exists"
        
        path = self.path_var.get().strip()
        if not path:
            return False, "Destination folder is required"
        
        patterns_text = self.patterns_text.get("1.0", tk.END).strip()
        if not patterns_text:
            return False, "At least one file pattern is required"
        
        return True, ""
    
    def _on_save(self):
        """Handle save button."""
        valid, error_msg = self._validate_input()
        if not valid:
            messagebox.showerror("Validation Error", error_msg, parent=self.dialog)
            return
        
        # Get values
        name = self.name_var.get().strip()
        path = self.path_var.get().strip()
        active = self.active_var.get()
        unzip = self.unzip_var.get()
        
        # Parse patterns
        patterns_text = self.patterns_text.get("1.0", tk.END).strip()
        patterns = [p.strip() for p in patterns_text.split("\\n") if p.strip()]
        
        try:
            if self.rule_name is None:
                # Adding new rule
                success = self.rule_manager.add_rule(name, patterns, path, active, unzip)
            elif name == self.rule_name:
                # Updating existing rule (same name)
                success = self.rule_manager.update_rule(
                    name, patterns=patterns, path=path, active=active, unzip=unzip
                )
            else:
                # Renaming rule
                success = self.rule_manager.rename_rule(self.rule_name, name)
                if success:
                    success = self.rule_manager.update_rule(
                        name, patterns=patterns, path=path, active=active, unzip=unzip
                    )
            
            if success:
                self.result = name
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to save rule", parent=self.dialog)
                
        except Exception as e:
            logger.error(f"Error saving rule: {e}")
            messagebox.showerror("Error", f"Failed to save rule: {str(e)}", parent=self.dialog)
    
    def _on_cancel(self):
        """Handle cancel button."""
        self.result = None
        self.dialog.destroy()
    
    def show(self) -> Optional[str]:
        """Show dialog and return result."""
        self.dialog.wait_window()
        return self.result


class RuleListWidget:
    """Enhanced rule list widget with sorting and filtering."""
    
    def __init__(self, parent: tk.Widget, rule_manager: RuleManager):
        self.parent = parent
        self.rule_manager = rule_manager
        self.callbacks = {
            'selection_changed': [],
            'rule_changed': []
        }
        
        self._create_widgets()
        self.refresh()
    
    def _create_widgets(self):
        """Create the rule list widgets."""
        # Create main frame
        self.frame = ttkb.Frame(self.parent)
        
        # Search/filter frame
        filter_frame = ttkb.Frame(self.frame)
        filter_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ttkb.Label(filter_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_changed)
        search_entry = ttkb.Entry(filter_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left", padx=(5, 10))
        Tooltip(search_entry, "Search rules by name or pattern")
        
        # Show only active checkbox
        self.show_active_only_var = tk.BooleanVar()
        self.show_active_only_var.trace("w", self._on_filter_changed)
        active_cb = ttkb.Checkbutton(filter_frame, text="Active only", 
                                    variable=self.show_active_only_var)
        active_cb.pack(side="left")
        
        # Treeview frame
        tree_frame = ttkb.Frame(self.frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create treeview
        columns = ("Priority", "Active", "Name", "Patterns", "Destination")
        self.tree = ttkb.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        self.tree.heading("Priority", text="#")
        self.tree.heading("Active", text="Active")
        self.tree.heading("Name", text="Rule Name")
        self.tree.heading("Patterns", text="File Patterns")
        self.tree.heading("Destination", text="Destination")
        
        self.tree.column("Priority", width=40, anchor="center")
        self.tree.column("Active", width=60, anchor="center")
        self.tree.column("Name", width=150)
        self.tree.column("Patterns", width=200)
        self.tree.column("Destination", width=250)
        
        # Scrollbars
        v_scrollbar = ttkb.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttkb.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_changed)
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Context menu
        self._create_context_menu()
    
    def _create_context_menu(self):
        """Create right-click context menu."""
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Edit...", command=self._edit_selected)
        self.context_menu.add_command(label="Duplicate", command=self._duplicate_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Toggle Active", command=self._toggle_selected_active)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Move Up", command=self._move_selected_up)
        self.context_menu.add_command(label="Move Down", command=self._move_selected_down)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self._delete_selected)
        
        self.tree.bind("<Button-3>", self._show_context_menu)
    
    def pack(self, **kwargs):
        """Pack the widget."""
        self.frame.pack(**kwargs)
    
    def refresh(self):
        """Refresh the rule list."""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get filtered rules
        rules = self._get_filtered_rules()
        sorted_keys = self.rule_manager.get_sorted_rule_keys()
        
        # Filter by search and active status
        for i, rule_key in enumerate(sorted_keys):
            if rule_key not in rules:
                continue
                
            rule = rules[rule_key]
            active_text = "✓" if rule.get("active", True) else "○"
            priority = i + 1
            patterns_text = ", ".join(rule.get("patterns", []))[:50]  # Truncate long patterns
            if len(patterns_text) == 50:
                patterns_text += "..."
            destination = rule.get("path", "")
            
            self.tree.insert("", tk.END, values=(
                priority,
                active_text,
                rule_key,
                patterns_text,
                destination
            ))
    
    def _get_filtered_rules(self) -> Dict[str, Any]:
        """Get rules filtered by search and active status."""
        rules = self.rule_manager.rules.copy()
        
        # Filter by search term
        search_term = self.search_var.get().lower()
        if search_term:
            filtered_rules = {}
            for name, rule in rules.items():
                if (search_term in name.lower() or 
                    any(search_term in pattern.lower() for pattern in rule.get('patterns', []))):
                    filtered_rules[name] = rule
            rules = filtered_rules
        
        # Filter by active status
        if self.show_active_only_var.get():
            rules = {name: rule for name, rule in rules.items() if rule.get('active', True)}
        
        return rules
    
    def _on_search_changed(self, *args):
        """Handle search text change."""
        self.refresh()
    
    def _on_filter_changed(self, *args):
        """Handle filter change."""
        self.refresh()
    
    def _on_selection_changed(self, event):
        """Handle selection change."""
        selected_rule = self.get_selected_rule()
        for callback in self.callbacks['selection_changed']:
            callback(selected_rule)
    
    def _on_double_click(self, event):
        """Handle double-click."""
        self._edit_selected()
    
    def _show_context_menu(self, event):
        """Show context menu."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def get_selected_rule(self) -> Optional[str]:
        """Get the name of the selected rule."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            return values[2] if len(values) > 2 else None
        return None
    
    def _edit_selected(self):
        """Edit the selected rule."""
        rule_name = self.get_selected_rule()
        if rule_name:
            editor = RuleEditor(self.parent, self.rule_manager, rule_name)
            result = editor.show()
            if result:
                self.refresh()
                self._notify_rule_changed()
    
    def _duplicate_selected(self):
        """Duplicate the selected rule."""
        rule_name = self.get_selected_rule()
        if rule_name:
            success = self.rule_manager.duplicate_rule(rule_name)
            if success:
                self.refresh()
                self._notify_rule_changed()
    
    def _toggle_selected_active(self):
        """Toggle active state of selected rule."""
        rule_name = self.get_selected_rule()
        if rule_name:
            self.rule_manager.toggle_rule_active(rule_name)
            self.refresh()
            self._notify_rule_changed()
    
    def _move_selected_up(self):
        """Move selected rule up in priority."""
        rule_name = self.get_selected_rule()
        if rule_name:
            self.rule_manager.move_rule_priority(rule_name, -1)
            self.refresh()
            self._notify_rule_changed()
    
    def _move_selected_down(self):
        """Move selected rule down in priority."""
        rule_name = self.get_selected_rule()
        if rule_name:
            self.rule_manager.move_rule_priority(rule_name, 1)
            self.refresh()
            self._notify_rule_changed()
    
    def _delete_selected(self):
        """Delete the selected rule."""
        rule_name = self.get_selected_rule()
        if rule_name:
            dialog = ConfirmDialog(
                self.parent,
                "Confirm Delete",
                f"Are you sure you want to delete the rule '{rule_name}'?",
                "Delete", "Cancel"
            )
            if dialog.show():
                self.rule_manager.delete_rule(rule_name)
                self.refresh()
                self._notify_rule_changed()
    
    def add_callback(self, event_type: str, callback: Callable):
        """Add a callback for events."""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def _notify_rule_changed(self):
        """Notify that rules have changed."""
        for callback in self.callbacks['rule_changed']:
            callback()


# Standalone functions for backward compatibility
def add_rule_button(rules: Dict[str, Any], config_directory: str, rule_frame, 
                   logger, root, update_callback: Callable):
    """Legacy function for backward compatibility."""
    config_manager = ConfigManager(config_directory)
    rule_manager = RuleManager(config_manager)
    rule_manager._rules = rules  # Use existing rules
    
    editor = RuleEditor(root, rule_manager)
    result = editor.show()
    if result:
        # Update the passed rules dict
        rules.clear()
        rules.update(rule_manager.rules)
        if update_callback:
            update_callback(rules, config_directory, logger)


def edit_rule(rule_key: str, rules: Dict[str, Any], config_directory: str, logger, rule_frame):
    """Legacy function for backward compatibility."""
    config_manager = ConfigManager(config_directory)
    rule_manager = RuleManager(config_manager)
    rule_manager._rules = rules  # Use existing rules
    
    # Get the root window
    root = rule_frame.winfo_toplevel() if rule_frame else None
    
    editor = RuleEditor(root, rule_manager, rule_key)
    result = editor.show()
    if result:
        # Update the passed rules dict
        rules.clear()
        rules.update(rule_manager.rules)
        rule_manager.save_rules()


def enable_all_rules(rules: Dict[str, Any], config_directory: str, rule_frame, 
                    logger, update_callback: Callable):
    """Legacy function for backward compatibility."""
    config_manager = ConfigManager(config_directory)
    rule_manager = RuleManager(config_manager)
    rule_manager._rules = rules
    
    rule_manager.enable_all_rules()
    rules.clear()
    rules.update(rule_manager.rules)
    rule_manager.save_rules()
    
    if update_callback:
        update_callback(rules, config_directory, logger)


def disable_all_rules(rules: Dict[str, Any], config_directory: str, rule_frame, 
                     logger, update_callback: Callable):
    """Legacy function for backward compatibility."""
    config_manager = ConfigManager(config_directory)
    rule_manager = RuleManager(config_manager)
    rule_manager._rules = rules
    
    rule_manager.disable_all_rules()
    rules.clear()
    rules.update(rule_manager.rules)
    rule_manager.save_rules()
    
    if update_callback:
        update_callback(rules, config_directory, logger)
