"""
Modern rule management components for TaskMover Redesigned.
Clean, independent rule editing with full pattern integration.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import ttkbootstrap as ttkb
from typing import Dict, Any, Optional, List, Callable, Union
import uuid
import os

from .components import SimpleDialog, Tooltip, get_text_input
from ..core.rules import RuleManager
from ..core.config import ConfigManager


class RuleEditor(SimpleDialog):
    """Modern rule editing dialog with full pattern library integration."""
    
    def __init__(self, parent: Union[tk.Widget, tk.Tk], rules: Dict[str, Any], config_directory: str, 
                 rule_name: Optional[str] = None, pattern_library=None,
                 rule_pattern_manager=None,
                 ruleset_name: str = "Default"):
        self.rules = rules
        self.config_directory = config_directory
        self.rule_name = rule_name
        self.is_editing = rule_name is not None
        self.pattern_library = pattern_library
        self.rule_pattern_manager = rule_pattern_manager
        self.ruleset_name = ruleset_name
        self.has_changes = False
        
        # Form fields
        self.name_var = tk.StringVar()
        self.path_var = tk.StringVar()
        self.active_var = tk.BooleanVar(value=True)
        self.unzip_var = tk.BooleanVar(value=False)
        self.pattern_dropdown = None
        self.selected_patterns_tree = None
        self.selected_pattern_ids = []
        self.pattern_id_map = {}  # Maps display names to pattern IDs
        
        # For backwards compatibility with legacy patterns
        self.patterns = []  # Legacy pattern list
        
        # Load existing rule if editing
        if self.is_editing and rule_name in rules:
            rule = rules[rule_name]
            self.name_var.set(rule_name)
            self.path_var.set(rule.get("path", ""))
            self.active_var.set(rule.get("active", True))
            self.unzip_var.set(rule.get("unzip", False))
            
            # Handle both legacy patterns and new pattern_ids
            if "pattern_ids" in rule:
                self.selected_pattern_ids = rule.get("pattern_ids", []).copy()
            else:
                # Legacy patterns - convert to simple pattern list
                self.patterns = rule.get("patterns", []).copy()
        
        title = f"Edit Rule: {rule_name}" if self.is_editing else "Add New Rule"
        super().__init__(parent, title, 700, 600)
        
        # Track changes
        self.name_var.trace('w', self._mark_changed)
        self.path_var.trace('w', self._mark_changed)
        self.active_var.trace('w', self._mark_changed)
        self.unzip_var.trace('w', self._mark_changed)
    
    def _mark_changed(self, *args):
        """Mark that changes have been made"""
        self.has_changes = True
    
    def create_content(self):
        """Create the complete rule editing form with pattern integration."""
        # Rule name section
        name_frame = ttkb.Frame(self.main_frame)
        name_frame.pack(fill="x", pady=(0, 15))
        
        ttkb.Label(name_frame, text="Rule Name:", font=("", 10, "bold")).pack(anchor="w")
        name_entry = ttkb.Entry(name_frame, textvariable=self.name_var, font=("", 10))
        name_entry.pack(fill="x", pady=(5, 0))
        Tooltip(name_entry, "Enter a unique name for this rule")
        
        if not self.is_editing:
            name_entry.focus()
        else:
            name_entry.config(state="readonly")
        
        # Destination path section
        path_frame = ttkb.Frame(self.main_frame)
        path_frame.pack(fill="x", pady=(0, 15))
        
        ttkb.Label(path_frame, text="Destination Folder:", font=("", 10, "bold")).pack(anchor="w")
        
        path_input_frame = ttkb.Frame(path_frame)
        path_input_frame.pack(fill="x", pady=(5, 0))
        
        path_entry = ttkb.Entry(path_input_frame, textvariable=self.path_var, font=("", 10))
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_btn = ttkb.Button(path_input_frame, text="Browse...", command=self.browse_path)
        browse_btn.pack(side="right")
        Tooltip(browse_btn, "Browse for destination folder")
        
        # Pattern section with both new and legacy support
        pattern_frame = ttkb.LabelFrame(self.main_frame, text="File Patterns", padding=10)
        pattern_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        if self.pattern_library:
            self.create_modern_pattern_section(pattern_frame)
        else:
            self.create_legacy_pattern_section(pattern_frame)
        
        # Options section
        options_frame = ttkb.LabelFrame(self.main_frame, text="Options", padding=10)
        options_frame.pack(fill="x", pady=(0, 15))
        
        active_check = ttkb.Checkbutton(options_frame, text="Rule is active", 
                                       variable=self.active_var)
        active_check.pack(anchor="w", pady=(0, 5))
        Tooltip(active_check, "Enable or disable this rule")
        
        unzip_check = ttkb.Checkbutton(options_frame, text="Automatically unzip archived files", 
                                      variable=self.unzip_var)
        unzip_check.pack(anchor="w")
        Tooltip(unzip_check, "Automatically extract zip, tar, and other archive files")
        
        # Save/Cancel buttons
        button_frame = ttkb.Frame(self.main_frame)
        button_frame.pack(fill="x", pady=(15, 0))
        
        cancel_btn = ttkb.Button(button_frame, text="Cancel", command=self.cancel)
        cancel_btn.pack(side="right", padx=(5, 0))
        
        save_btn = ttkb.Button(button_frame, text="Save Rule", command=self.save_rule, 
                              style="Accent.TButton")
        save_btn.pack(side="right")
    
    def create_modern_pattern_section(self, parent):
        """Create pattern section with pattern library integration"""
        # Pattern selection controls
        selection_frame = ttkb.Frame(parent)
        selection_frame.pack(fill="x", pady=(0, 10))
        
        ttkb.Label(selection_frame, text="Select Patterns:").pack(anchor="w")
        
        pattern_select_frame = ttkb.Frame(selection_frame)
        pattern_select_frame.pack(fill="x", pady=(5, 0))
        
        self.pattern_dropdown = ttk.Combobox(pattern_select_frame, state="readonly")
        self.pattern_dropdown.pack(side="left", fill="x", expand=True, padx=(0, 5))
        Tooltip(self.pattern_dropdown, "Select an existing pattern from the library")
        
        add_pattern_btn = ttkb.Button(pattern_select_frame, text="Add to Rule", 
                                     command=self.add_pattern_to_rule)
        add_pattern_btn.pack(side="left", padx=(0, 5))
        
        new_pattern_btn = ttkb.Button(pattern_select_frame, text="Create New Pattern", 
                                     command=self.create_new_pattern)
        new_pattern_btn.pack(side="left")
        Tooltip(new_pattern_btn, "Create a new pattern and add it to this rule")
        
        # Selected patterns display
        ttkb.Label(parent, text="Patterns in this rule:").pack(anchor="w", pady=(10, 5))
        
        patterns_list_frame = ttkb.Frame(parent)
        patterns_list_frame.pack(fill="both", expand=True)
        
        # Patterns treeview
        columns = ("Name", "Pattern", "Type")
        self.selected_patterns_tree = ttk.Treeview(patterns_list_frame, columns=columns, 
                                                  show="headings", height=6)
        
        for col in columns:
            self.selected_patterns_tree.heading(col, text=col)
            self.selected_patterns_tree.column(col, width=150)
        
        self.selected_patterns_tree.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Scrollbar for patterns tree
        patterns_scroll = ttkb.Scrollbar(patterns_list_frame, orient="vertical", 
                                        command=self.selected_patterns_tree.yview)
        self.selected_patterns_tree.configure(yscrollcommand=patterns_scroll.set)
        patterns_scroll.pack(side="right", fill="y")
        
        # Pattern management buttons
        pattern_btn_frame = ttkb.Frame(parent)
        pattern_btn_frame.pack(fill="x", pady=(10, 0))
        
        remove_pattern_btn = ttkb.Button(pattern_btn_frame, text="Remove Pattern", 
                                        command=self.remove_pattern_from_rule)
        remove_pattern_btn.pack(side="left", padx=(0, 5))
        
        # Initialize UI state
        self.refresh_pattern_dropdown()
        self.refresh_selected_patterns()
    
    def create_legacy_pattern_section(self, parent):
        """Create legacy pattern section for backwards compatibility"""
        ttkb.Label(parent, text="File Patterns (one per line):").pack(anchor="w", pady=(0, 5))
        
        # Patterns list
        list_frame = ttkb.Frame(parent)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.patterns_listbox = tk.Listbox(list_frame, height=6, font=("Consolas", 9))
        self.patterns_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttkb.Scrollbar(list_frame, orient="vertical", command=self.patterns_listbox.yview)
        self.patterns_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Populate patterns
        for pattern in self.patterns:
            self.patterns_listbox.insert(tk.END, pattern)
        
        # Pattern buttons
        pattern_btn_frame = ttkb.Frame(parent)
        pattern_btn_frame.pack(fill="x", pady=(10, 0))
        
        add_btn = ttkb.Button(pattern_btn_frame, text="Add Pattern", command=self.add_legacy_pattern)
        add_btn.pack(side="left", padx=(0, 5))
        
        edit_btn = ttkb.Button(pattern_btn_frame, text="Edit Pattern", command=self.edit_legacy_pattern)
        edit_btn.pack(side="left", padx=(0, 5))
        
        remove_btn = ttkb.Button(pattern_btn_frame, text="Remove Pattern", command=self.remove_legacy_pattern)
        remove_btn.pack(side="left")
    
    def browse_path(self):
        """Open file dialog to select destination folder"""
        folder = filedialog.askdirectory(
            title="Select Destination Folder",
            initialdir=self.path_var.get() or os.path.expanduser("~")
        )
        if folder:
            self.path_var.set(folder)
    
    def refresh_pattern_dropdown(self):
        """Refresh the pattern dropdown with all available patterns"""
        if not self.pattern_library or self.pattern_dropdown is None:
            return
            
        # Get all patterns
        patterns = self.pattern_library.get_all_patterns()
        
        # Create display names and map to pattern IDs
        pattern_names = []
        self.pattern_id_map = {}
        
        for pattern in patterns:
            pattern_id = pattern.id
            if pattern:
                display_name = f"{pattern.name} ({pattern.type})"
                pattern_names.append(display_name)
                self.pattern_id_map[display_name] = pattern_id
        
        # Update dropdown values or create a configuration dictionary
        if hasattr(self.pattern_dropdown, 'configure'):
            self.pattern_dropdown.configure(values=pattern_names)
        else:
            # Create a dictionary reference if needed
            self.pattern_dropdown_values = pattern_names
    
    def refresh_selected_patterns(self):
        """Refresh the selected patterns display"""
        if self.selected_patterns_tree is None or self.pattern_library is None:
            return
        
        # Clear tree
        for item in self.selected_patterns_tree.get_children():
            self.selected_patterns_tree.delete(item)
        
        # Add selected patterns
        for pattern_id in self.selected_pattern_ids:
            pattern = self.pattern_library.get_pattern(pattern_id)
            if pattern:
                self.selected_patterns_tree.insert('', 'end', iid=pattern_id, values=(
                    pattern.name,
                    pattern.pattern,
                    pattern.type
                ))
    
    def add_pattern_to_rule(self):
        """Add selected pattern from dropdown to the rule"""
        if not self.pattern_dropdown:
            return
            
        selection = self.pattern_dropdown.get()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a pattern to add.")
            return
        
        pattern_id = self.pattern_id_map.get(selection)
        if pattern_id and pattern_id not in self.selected_pattern_ids:
            self.selected_pattern_ids.append(pattern_id)
            self.refresh_selected_patterns()
            self._mark_changed()
        elif pattern_id in self.selected_pattern_ids:
            messagebox.showinfo("Already Added", "This pattern is already added to the rule.")
    
    def remove_pattern_from_rule(self):
        """Remove selected pattern from the rule"""
        if not self.selected_patterns_tree:
            return
            
        selection = self.selected_patterns_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a pattern to remove.")
            return
        
        pattern_id = selection[0]
        if pattern_id in self.selected_pattern_ids:
            self.selected_pattern_ids.remove(pattern_id)
            self.refresh_selected_patterns()
            self._mark_changed()
    
    def create_new_pattern(self):
        """Open pattern editor to create a new pattern"""
        if not self.pattern_library:
            messagebox.showerror("Error", "Pattern library not available.")
            return
        
        # Simple pattern creation dialog for now
        from .pattern_tab import PatternEditorDialog
        try:
            dialog = PatternEditorDialog(self.main_frame, self.pattern_library)
            if dialog.result:
                # Pattern was created, refresh dropdown and optionally add to rule
                self.refresh_pattern_dropdown()
                
                # Ask if user wants to add the new pattern to this rule
                if messagebox.askyesno("Add Pattern", 
                                     "Would you like to add the new pattern to this rule?"):
                    new_pattern_id = dialog.result
                    if new_pattern_id not in self.selected_pattern_ids:
                        self.selected_pattern_ids.append(new_pattern_id)
                        self.refresh_selected_patterns()
                        self._mark_changed()
        except ImportError:
            # Fallback to simple pattern input
            pattern = simpledialog.askstring("New Pattern", "Enter file pattern (e.g., *.pdf):", parent=self.main_frame)
            if pattern:
                try:
                    pattern_id = self.pattern_library.create_pattern(
                        name=pattern,
                        pattern=pattern,
                        pattern_type="glob"
                    )
                    if pattern_id not in self.selected_pattern_ids:
                        self.selected_pattern_ids.append(pattern_id)
                        self.refresh_pattern_dropdown()
                        self.refresh_selected_patterns()
                        self._mark_changed()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create pattern: {e}")
    
    # Legacy pattern methods
    def add_legacy_pattern(self):
        """Add a legacy pattern"""
        pattern = simpledialog.askstring("Add Pattern", "Enter file pattern (e.g., *.pdf):", parent=self.main_frame)
        if pattern and pattern not in self.patterns:
            self.patterns.append(pattern)
            self.patterns_listbox.insert(tk.END, pattern)
            self._mark_changed()
    
    def edit_legacy_pattern(self):
        """Edit selected legacy pattern"""
        selection = self.patterns_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a pattern to edit.")
            return
        
        index = selection[0]
        old_pattern = self.patterns[index]
        new_pattern = simpledialog.askstring("Edit Pattern", "Edit file pattern:", parent=self.main_frame, initialvalue=old_pattern)
        
        if new_pattern and new_pattern != old_pattern:
            self.patterns[index] = new_pattern
            self.patterns_listbox.delete(index)
            self.patterns_listbox.insert(index, new_pattern)
            self.patterns_listbox.selection_set(index)
            self._mark_changed()
    
    def remove_legacy_pattern(self):
        """Remove selected legacy pattern"""
        selection = self.patterns_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a pattern to remove.")
            return
        
        index = selection[0]
        del self.patterns[index]
        self.patterns_listbox.delete(index)
        self._mark_changed()
    
    def validate_form(self) -> bool:
        """Validate the form before saving"""
        if not self.name_var.get().strip():
            messagebox.showerror("Validation Error", "Rule name is required.")
            return False
        
        if not self.path_var.get().strip():
            messagebox.showerror("Validation Error", "Destination path is required.")
            return False
        
        # Check patterns
        if self.pattern_library:
            if not self.selected_pattern_ids:
                messagebox.showerror("Validation Error", "At least one pattern must be selected.")
                return False
        else:
            if not self.patterns:
                messagebox.showerror("Validation Error", "At least one pattern must be added.")
                return False
        
        # Check if rule name already exists (for new rules)
        if not self.is_editing and self.name_var.get() in self.rules:
            messagebox.showerror("Validation Error", 
                               f"A rule named '{self.name_var.get()}' already exists.")
            return False
        
        return True
    
    def save_rule(self):
        """Save the rule and close dialog"""
        if not self.validate_form():
            return
        
        # Create rule data
        rule_data = {
            "path": self.path_var.get().strip(),
            "active": self.active_var.get(),
            "unzip": self.unzip_var.get()
        }
        
        # Add patterns based on which system is being used
        if self.pattern_library and self.selected_pattern_ids:
            rule_data["pattern_ids"] = self.selected_pattern_ids.copy()
        else:
            rule_data["patterns"] = self.patterns.copy()
        
        # Return result
        self.result = {
            "name": self.name_var.get().strip(),
            "data": rule_data
        }
        self.destroy()
    
    def cancel(self):
        """Cancel editing with unsaved changes check"""
        if self.has_changes:
            if not messagebox.askyesno("Unsaved Changes", 
                                     "You have unsaved changes. Are you sure you want to cancel?"):
                return
        
        self.result = None
        self.destroy()
    
    def destroy(self):
        """Close the dialog."""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.destroy()


def add_rule_button(parent_frame: Union[tk.Widget, tk.Tk], rules: Dict[str, Any], 
                   config_directory: str, update_callback: Callable[[], None],
                   pattern_library=None,
                   rule_pattern_manager=None,
                   ruleset_name: str = "Default"):
    """Create and show rule editor dialog for adding a new rule"""
    dialog = RuleEditor(parent_frame, rules, config_directory, 
                       pattern_library=pattern_library,
                       rule_pattern_manager=rule_pattern_manager,
                       ruleset_name=ruleset_name)
    
    if dialog.result:
        rule_name = dialog.result["name"]
        rule_data = dialog.result["data"]
        rules[rule_name] = rule_data
        update_callback()


def edit_rule(parent_frame: Union[tk.Widget, tk.Tk], rules: Dict[str, Any], 
              config_directory: str, rule_name: str, update_callback: Callable[[], None],
              pattern_library=None,
              rule_pattern_manager=None,
              ruleset_name: str = "Default"):
    """Create and show rule editor dialog for editing an existing rule"""
    dialog = RuleEditor(parent_frame, rules, config_directory, rule_name,
                       pattern_library=pattern_library,
                       rule_pattern_manager=rule_pattern_manager,
                       ruleset_name=ruleset_name)
    
    if dialog.result:
        new_name = dialog.result["name"]
        rule_data = dialog.result["data"]
        
        # Handle rule rename
        if new_name != rule_name:
            del rules[rule_name]
        
        rules[new_name] = rule_data
        update_callback()


def enable_all_rules(rules: Dict[str, Any], update_callback: Callable[[], None]):
    """Enable all rules in the ruleset"""
    for rule_data in rules.values():
        rule_data["active"] = True
    update_callback()


def disable_all_rules(rules: Dict[str, Any], update_callback: Callable[[], None]):
    """Disable all rules in the ruleset"""
    for rule_data in rules.values():
        rule_data["active"] = False
    update_callback()
