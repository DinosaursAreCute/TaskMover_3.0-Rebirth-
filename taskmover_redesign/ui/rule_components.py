"""
Modern rule management components for TaskMover Redesigned.
Clean, independent rule editing with full pattern integration.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttkb
from typing import Dict, Any, Optional, List
import uuid
import os

from .components import SimpleDialog, Tooltip, get_text_input
from .pattern_tab import PatternEditorDialog
from ..core.rules import RuleManager
from ..core.config import ConfigManager
from ..core.pattern_library import PatternLibrary
from ..core.rule_pattern_manager import RulePatternManager


class RuleEditor(SimpleDialog):
    """Modern rule editing dialog with full pattern library integration."""
    
    def __init__(self, parent: tk.Widget, rules: Dict[str, Any], config_directory: str, 
                 rule_name: Optional[str] = None, pattern_library: Optional[PatternLibrary] = None,
                 rule_pattern_manager: Optional[RulePatternManager] = None,
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
        
        # Load existing rule if editing
        if self.is_editing and rule_name in rules:
            rule = rules[rule_name]
            self.name_var.set(rule_name)
            self.path_var.set(rule.get("path", ""))
            self.active_var.set(rule.get("active", True))
            self.unzip_var.set(rule.get("unzip", False))
            self.selected_pattern_ids = rule.get("pattern_ids", []).copy()
        
        # Track changes
        self.name_var.trace('w', self.on_change)
        self.path_var.trace('w', self.on_change)
        self.active_var.trace('w', self.on_change)
        self.unzip_var.trace('w', self.on_change)
        
        title = f"Edit Rule: {rule_name}" if self.is_editing else "Add New Rule"
        super().__init__(parent, title, 750, 650)
    
    def on_change(self, *args):
        """Track when form has unsaved changes."""
        self.has_changes = True
    
    def create_content(self):
        """Create the rule editing form."""
        # Rule name
        name_frame = ttkb.Frame(self.main_frame)
        name_frame.pack(fill="x", pady=(0, 10))
        
        ttkb.Label(name_frame, text="Rule Name:", font=("", 10, "bold")).pack(anchor="w")
        name_entry = ttkb.Entry(name_frame, textvariable=self.name_var, font=("", 10))
        name_entry.pack(fill="x", pady=(5, 0))
        Tooltip(name_entry, "Enter a unique name for this rule")
        
        if not self.is_editing:
            name_entry.focus()
        else:
            name_entry.config(state="readonly")
        
        # Destination path
        path_frame = ttkb.Frame(self.main_frame)
        path_frame.pack(fill="x", pady=(0, 10))
        
        ttkb.Label(path_frame, text="Destination Folder:", font=("", 10, "bold")).pack(anchor="w")
        
        path_input_frame = ttkb.Frame(path_frame)
        path_input_frame.pack(fill="x", pady=(5, 0))
        
        path_entry = ttkb.Entry(path_input_frame, textvariable=self.path_var, font=("", 10))
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_btn = ttkb.Button(path_input_frame, text="Browse...", command=self.browse_path)
        browse_btn.pack(side="right")
        Tooltip(browse_btn, "Browse for destination folder")
        
        # Rule options
        options_frame = ttkb.Frame(self.main_frame)
        options_frame.pack(fill="x", pady=(0, 15))
        
        ttkb.Checkbutton(options_frame, text="Rule is active", 
                        variable=self.active_var).pack(side="left", padx=(0, 20))
        ttkb.Checkbutton(options_frame, text="Unzip archives", 
                        variable=self.unzip_var).pack(side="left")
        
        # File patterns section
        patterns_frame = ttkb.LabelFrame(self.main_frame, text="File Patterns", padding=10)
        patterns_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        if self.pattern_library:
            self._create_pattern_section(patterns_frame)
        else:
            self._create_legacy_pattern_section(patterns_frame)
    
    def _create_pattern_section(self, parent):
        """Create modern pattern selection section."""
        # Pattern selection area
        selection_frame = ttkb.Frame(parent)
        selection_frame.pack(fill="x", pady=(0, 10))
        
        ttkb.Label(selection_frame, text="Add patterns to this rule:", 
                  font=("", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Pattern selection controls
        pattern_controls = ttkb.Frame(selection_frame)
        pattern_controls.pack(fill="x")
        
        # Available patterns dropdown
        self.pattern_dropdown = ttk.Combobox(pattern_controls, state="readonly", width=30)
        self.pattern_dropdown.pack(side="left", padx=(0, 5))
        
        add_pattern_btn = ttkb.Button(pattern_controls, text="Add to Rule", 
                                     command=self.add_pattern_to_rule)
        add_pattern_btn.pack(side="left", padx=(0, 10))
        
        # Create new pattern button
        new_pattern_btn = ttkb.Button(pattern_controls, text="Create New Pattern", 
                                     command=self.create_new_pattern, bootstyle="success")
        new_pattern_btn.pack(side="left")
        
        # Selected patterns section
        selected_frame = ttkb.Frame(parent)
        selected_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        ttkb.Label(selected_frame, text="Patterns in this rule:", 
                  font=("", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Selected patterns tree
        tree_frame = ttkb.Frame(selected_frame)
        tree_frame.pack(fill="both", expand=True)
        
        columns = ("Name", "Type", "Pattern")
        self.selected_patterns_tree = ttk.Treeview(tree_frame, columns=columns, 
                                                  show="headings", height=8)
        
        for col in columns:
            self.selected_patterns_tree.heading(col, text=col)
        
        self.selected_patterns_tree.column("Name", width=150)
        self.selected_patterns_tree.column("Type", width=60)
        self.selected_patterns_tree.column("Pattern", width=200)
        
        # Scrollbar for patterns tree
        patterns_scroll = ttkb.Scrollbar(tree_frame, orient="vertical", 
                                        command=self.selected_patterns_tree.yview)
        self.selected_patterns_tree.configure(yscrollcommand=patterns_scroll.set)
        
        self.selected_patterns_tree.pack(side="left", fill="both", expand=True)
        patterns_scroll.pack(side="right", fill="y")
        
        # Pattern management buttons
        pattern_btn_frame = ttkb.Frame(selected_frame)
        pattern_btn_frame.pack(fill="x", pady=(5, 0))
        
        remove_btn = ttkb.Button(pattern_btn_frame, text="Remove", 
                                command=self.remove_pattern_from_rule)
        remove_btn.pack(side="left", padx=(0, 5))
        
        test_btn = ttkb.Button(pattern_btn_frame, text="Test Patterns", 
                              command=self.test_rule_patterns)
        test_btn.pack(side="left")
        
        # Initialize pattern controls
        self.refresh_pattern_dropdown()
        self.refresh_selected_patterns()
    
    def _create_legacy_pattern_section(self, parent):
        """Create legacy pattern section for when pattern library is not available."""
        ttkb.Label(parent, text="Pattern library not available. Using basic pattern entry.", 
                  foreground="orange").pack(anchor="w", pady=(0, 10))
        
        self.patterns_listbox = tk.Listbox(parent, height=6, font=("Consolas", 9))
        self.patterns_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttkb.Scrollbar(parent, orient="vertical", command=self.patterns_listbox.yview)
        self.patterns_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Load legacy patterns if editing
        if self.is_editing and self.rule_name in self.rules:
            legacy_patterns = self.rules[self.rule_name].get("patterns", [])
            for pattern in legacy_patterns:
                self.patterns_listbox.insert(tk.END, pattern)
    
    def create_buttons(self):
        """Create Save/Cancel buttons."""
        button_frame = ttkb.Frame(self.main_frame)
        button_frame.pack(fill="x", pady=(15, 0))
        
        cancel_btn = ttkb.Button(button_frame, text="Cancel", command=self.cancel)
        cancel_btn.pack(side="right", padx=(5, 0))
        
        save_btn = ttkb.Button(button_frame, text="Save Rule", command=self.save_rule, 
                              bootstyle="success")
        save_btn.pack(side="right")
    
    def refresh_pattern_dropdown(self):
        """Refresh the pattern dropdown with available patterns."""
        if not self.pattern_library:
            return
        
        patterns = self.pattern_library.get_all_patterns()
        pattern_names = [f"{p.name} ({p.type})" for p in patterns]
        
        self.pattern_dropdown['values'] = pattern_names
        if pattern_names:
            self.pattern_dropdown.set("Select a pattern...")
    
    def refresh_selected_patterns(self):
        """Refresh the selected patterns tree."""
        if not self.pattern_library or not self.selected_patterns_tree:
            return
        
        # Clear existing items
        for item in self.selected_patterns_tree.get_children():
            self.selected_patterns_tree.delete(item)
        
        # Populate with selected patterns
        for pattern_id in self.selected_pattern_ids:
            pattern = self.pattern_library.get_pattern(pattern_id)
            if pattern:
                self.selected_patterns_tree.insert("", "end", values=(
                    pattern.name,
                    pattern.type,
                    pattern.pattern
                ), tags=(pattern_id,))
    
    def add_pattern_to_rule(self):
        """Add selected pattern to the rule."""
        if not self.pattern_library:
            return
        
        selection = self.pattern_dropdown.get()
        if not selection or selection == "Select a pattern...":
            messagebox.showwarning("No Selection", "Please select a pattern to add")
            return
        
        # Extract pattern name from dropdown selection
        pattern_name = selection.split(" (")[0]
        pattern = self.pattern_library.get_pattern_by_name(pattern_name)
        
        if not pattern:
            messagebox.showerror("Error", "Selected pattern not found")
            return
        
        if pattern.id in self.selected_pattern_ids:
            messagebox.showwarning("Duplicate", "This pattern is already added to the rule")
            return
        
        self.selected_pattern_ids.append(pattern.id)
        self.refresh_selected_patterns()
        self.on_change()
        
        # Reset dropdown
        self.pattern_dropdown.set("Select a pattern...")
    
    def remove_pattern_from_rule(self):
        """Remove selected pattern from the rule."""
        if not self.selected_patterns_tree:
            return
        
        selection = self.selected_patterns_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a pattern to remove")
            return
        
        item = selection[0]
        tags = self.selected_patterns_tree.item(item, "tags")
        pattern_id = tags[0] if tags else None
        
        if pattern_id and pattern_id in self.selected_pattern_ids:
            self.selected_pattern_ids.remove(pattern_id)
            self.refresh_selected_patterns()
            self.on_change()
    
    def create_new_pattern(self):
        """Create a new pattern and add it to the rule."""
        if not self.pattern_library:
            messagebox.showerror("Error", "Pattern library not available")
            return
        
        dialog = PatternEditorDialog(self.dialog, self.pattern_library)
        result = dialog.show()
        
        if result:
            try:
                pattern_id = self.pattern_library.create_pattern(**result)
                self.selected_pattern_ids.append(pattern_id)
                self.refresh_pattern_dropdown()
                self.refresh_selected_patterns()
                self.on_change()
                messagebox.showinfo("Success", f"Pattern '{result['name']}' created and added to rule")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create pattern: {str(e)}")
    
    def test_rule_patterns(self):
        """Test the patterns in this rule."""
        if not self.rule_pattern_manager or not self.selected_pattern_ids:
            messagebox.showwarning("No Patterns", "No patterns to test")
            return
        
        # Simple test dialog
        test_files = tk.simpledialog.askstring(
            "Test Rule Patterns",
            "Enter filenames to test (separated by commas):",
            initialvalue="document.pdf, script.py, image.jpg, data.csv"
        )
        
        if test_files:
            filenames = [f.strip() for f in test_files.split(',') if f.strip()]
            results = []
            
            for pattern_id in self.selected_pattern_ids:
                pattern = self.pattern_library.get_pattern(pattern_id)
                if pattern:
                    matches = self.pattern_library.test_pattern(pattern_id, filenames)
                    results.append(f"{pattern.name}: {len(matches)} matches")
                    if matches:
                        results.extend([f"  • {match}" for match in matches])
            
            if results:
                messagebox.showinfo("Test Results", "\n".join(results))
            else:
                messagebox.showinfo("Test Results", "No matches found")
    
    def browse_path(self):
        """Browse for destination folder."""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.path_var.set(folder)
    
    def validate_form(self) -> bool:
        """Validate the form data."""
        name = self.name_var.get().strip()
        path = self.path_var.get().strip()
        
        if not name:
            messagebox.showerror("Validation Error", "Rule name is required")
            return False
        
        if not path:
            messagebox.showerror("Validation Error", "Destination path is required")
            return False
        
        # Check for duplicate names (unless editing the same rule)
        if name in self.rules and (not self.is_editing or name != self.rule_name):
            messagebox.showerror("Validation Error", f"A rule named '{name}' already exists")
            return False
        
        # Validate patterns
        if self.pattern_library and self.rule_pattern_manager:
            if not self.selected_pattern_ids:
                messagebox.showerror("Validation Error", "At least one pattern is required")
                return False
            
            is_valid, errors = self.rule_pattern_manager.validate_rule_patterns(self.selected_pattern_ids)
            if not is_valid:
                error_msg = "Pattern validation errors:\n\n" + "\n".join(errors)
                messagebox.showerror("Validation Error", error_msg)
                return False
        
        return True
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self.has_changes
    
    def save_rule(self):
        """Save the rule."""
        if not self.validate_form():
            return
        
        # Create rule data
        if self.pattern_library:
            # Modern format with pattern IDs
            rule_data = {
                "path": self.path_var.get().strip(),
                "pattern_ids": self.selected_pattern_ids.copy(),
                "active": self.active_var.get(),
                "unzip": self.unzip_var.get()
            }
        else:
            # Legacy format with pattern strings
            patterns = []
            for i in range(self.patterns_listbox.size()):
                patterns.append(self.patterns_listbox.get(i))
            
            rule_data = {
                "path": self.path_var.get().strip(),
                "patterns": patterns,
                "active": self.active_var.get(),
                "unzip": self.unzip_var.get()
            }
        
        # Set result and close
        self.result = {
            "name": self.name_var.get().strip(),
            "data": rule_data
        }
        self.destroy()
    
    def cancel(self):
        """Cancel the dialog."""
        if self.has_unsaved_changes():
            if not messagebox.askyesno("Unsaved Changes", 
                                     "You have unsaved changes. Are you sure you want to cancel?"):
                return
        
        self.result = None
        self.destroy()


class RuleListWidget:
    """Modern rule list component (placeholder for now)."""
    pass


def add_rule_button(rules: Dict[str, Any], config_directory: str, rule_frame, 
                   logger, root, update_callback, pattern_library=None, 
                   rule_pattern_manager=None, ruleset_name="Default"):
    """Add a new rule using modern dialog."""
    editor = RuleEditor(
        root, rules, config_directory, 
        pattern_library=pattern_library,
        rule_pattern_manager=rule_pattern_manager,
        ruleset_name=ruleset_name
    )
    result = editor.show()
    
    if result:
        rule_name = result["name"]
        rule_data = result["data"]
        
        rules[rule_name] = rule_data
        logger.info(f"Added new rule: {rule_name}")
        
        if update_callback:
            update_callback()


def edit_rule(rule_key: str, rules: Dict[str, Any], config_directory: str, logger, 
             rule_frame, pattern_library=None, rule_pattern_manager=None, 
             ruleset_name="Default"):
    """Edit an existing rule using modern dialog."""
    if rule_key not in rules:
        messagebox.showerror("Error", f"Rule '{rule_key}' not found")
        return
    
    # Get root window
    root = rule_frame.winfo_toplevel()
    
    editor = RuleEditor(
        root, rules, config_directory, rule_key,
        pattern_library=pattern_library,
        rule_pattern_manager=rule_pattern_manager,
        ruleset_name=ruleset_name
    )
    result = editor.show()
    
    if result:
        rule_name = result["name"]
        rule_data = result["data"]
        
        # If name changed, remove old entry
        if rule_name != rule_key:
            del rules[rule_key]
        
        rules[rule_name] = rule_data
        logger.info(f"Updated rule: {rule_name}")


def enable_all_rules(rules: Dict[str, Any], config_directory: str, rule_frame, 
                    logger, update_callback):
    """Enable all rules."""
    count = 0
    for rule_data in rules.values():
        if not rule_data.get("active", True):
            rule_data["active"] = True
            count += 1
    
    if count > 0:
        logger.info(f"Enabled {count} rules")
        if update_callback:
            update_callback()


def disable_all_rules(rules: Dict[str, Any], config_directory: str, rule_frame, 
                     logger, update_callback):
    """Disable all rules."""
    count = 0
    for rule_data in rules.values():
        if rule_data.get("active", True):
            rule_data["active"] = False
            count += 1
    
    if count > 0:
        logger.info(f"Disabled {count} rules")
        if update_callback:
            update_callback()
        pattern_btn_frame.pack(fill="x")
        
        add_pattern_btn = ttkb.Button(pattern_btn_frame, text="Add Pattern", command=self.add_pattern)
        add_pattern_btn.pack(side="left", padx=(0, 5))
        Tooltip(add_pattern_btn, "Add a new file pattern (e.g., *.pdf, *.jpg)")
        
        remove_pattern_btn = ttkb.Button(pattern_btn_frame, text="Remove Pattern", command=self.remove_pattern)
        remove_pattern_btn.pack(side="left", padx=(0, 5))
        Tooltip(remove_pattern_btn, "Remove selected pattern")
        
        # Pattern library integration
        if self.pattern_library:
            from_library_btn = ttkb.Button(pattern_btn_frame, text="📋 From Library", 
                                          style="info.TButton", command=self.add_from_library)
            from_library_btn.pack(side="left", padx=(0, 5))
            Tooltip(from_library_btn, "Add patterns from your pattern library")
            
            build_pattern_btn = ttkb.Button(pattern_btn_frame, text="🔧 Build Pattern", 
                                           style="success.TButton", command=self.build_new_pattern)
            build_pattern_btn.pack(side="left", padx=(0, 5))
            Tooltip(build_pattern_btn, "Create a new pattern using the pattern builder")
        
        # Add some common patterns
        common_btn = ttkb.Button(pattern_btn_frame, text="Common Patterns...", command=self.show_common_patterns)
        common_btn.pack(side="right")
        Tooltip(common_btn, "Choose from common file patterns")
        
        # Options
        options_frame = ttkb.LabelFrame(self.main_frame, text="Options", padding=10)
        options_frame.pack(fill="x", pady=(0, 10))
        
        active_cb = ttkb.Checkbutton(options_frame, text="Rule is active", variable=self.active_var)
        active_cb.pack(anchor="w")
        Tooltip(active_cb, "Enable/disable this rule")
        
        unzip_cb = ttkb.Checkbutton(options_frame, text="Unzip files after moving", variable=self.unzip_var)
        unzip_cb.pack(anchor="w")
        Tooltip(unzip_cb, "Automatically extract zip files after moving")
    
    def browse_path(self):
        """Browse for destination folder."""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.path_var.set(folder)
    
    def add_pattern(self):
        """Add a new file pattern."""
        pattern = get_text_input(self.dialog, "Add Pattern", "Enter file pattern (e.g., *.pdf):")
        if pattern:
            # Basic validation
            if not pattern.strip():
                messagebox.showerror("Error", "Pattern cannot be empty.")
                return
            
            pattern = pattern.strip()
            if pattern not in self.patterns:
                self.patterns.append(pattern)
                self.patterns_listbox.insert(tk.END, pattern)
            else:
                messagebox.showwarning("Warning", "Pattern already exists.")
    
    def remove_pattern(self):
        """Remove selected pattern."""
        selection = self.patterns_listbox.curselection()
        if selection:
            index = selection[0]
            pattern = self.patterns[index]
            self.patterns.remove(pattern)
            self.patterns_listbox.delete(index)
        else:
            messagebox.showwarning("Warning", "Please select a pattern to remove.")
    
    def show_common_patterns(self):
        """Show dialog with common file patterns."""
        common_patterns = {
            "Documents": ["*.pdf", "*.doc", "*.docx", "*.txt", "*.rtf"],
            "Images": ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff"],
            "Videos": ["*.mp4", "*.avi", "*.mkv", "*.mov", "*.wmv", "*.flv"],
            "Audio": ["*.mp3", "*.wav", "*.flac", "*.aac", "*.ogg"],
            "Archives": ["*.zip", "*.rar", "*.7z", "*.tar", "*.gz"],
            "Code": ["*.py", "*.js", "*.html", "*.css", "*.java", "*.cpp"],
            "Spreadsheets": ["*.xlsx", "*.xls", "*.csv", "*.ods"],
            "Presentations": ["*.pptx", "*.ppt", "*.odp"]
        }
        
        # Create pattern selection dialog
        pattern_dialog = tk.Toplevel(self.dialog)
        pattern_dialog.title("Common Patterns")
        pattern_dialog.geometry("500x400")
        pattern_dialog.transient(self.dialog)
        pattern_dialog.grab_set()
        
        main_frame = ttkb.Frame(pattern_dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        ttkb.Label(main_frame, text="Select patterns to add:", font=("", 10, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Create notebook for categories
        notebook = ttkb.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        for category, patterns in common_patterns.items():
            frame = ttkb.Frame(notebook)
            notebook.add(frame, text=category)
            
            # Add checkboxes for each pattern
            for pattern in patterns:
                var = tk.BooleanVar()
                cb = ttkb.Checkbutton(frame, text=pattern, variable=var)
                cb.pack(anchor="w", padx=10, pady=2)
                cb.var = var  # Store reference
        
        # Buttons
        btn_frame = ttkb.Frame(main_frame)
        btn_frame.pack(fill="x")
        
        def add_selected():
            added_count = 0
            for tab_id in notebook.tabs():
                tab_frame = notebook.nametowidget(tab_id)
                for widget in tab_frame.winfo_children():
                    if isinstance(widget, ttkb.Checkbutton) and widget.var.get():
                        pattern = widget.cget("text")
                        if pattern not in self.patterns:
                            self.patterns.append(pattern)
                            self.patterns_listbox.insert(tk.END, pattern)
                            added_count += 1
            
            if added_count > 0:
                messagebox.showinfo("Success", f"Added {added_count} patterns.")
            pattern_dialog.destroy()
        
        ttkb.Button(btn_frame, text="Add Selected", command=add_selected).pack(side="right", padx=(5, 0))
        ttkb.Button(btn_frame, text="Cancel", command=pattern_dialog.destroy).pack(side="right")
    
    def validate(self) -> bool:
        """Validate the rule input."""
        name = self.name_var.get().strip()
        path = self.path_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Rule name is required.")
            return False
        
        if not self.is_editing and name in self.rules:
            messagebox.showerror("Error", f"Rule '{name}' already exists.")
            return False
        
        if not path:
            messagebox.showerror("Error", "Destination folder is required.")
            return False
        
        if not self.patterns:
            result = messagebox.askyesno("Warning", "No file patterns specified. Continue anyway?")
            if not result:
                return False
        
        return True
    
    def get_result(self) -> Dict[str, Any]:
        """Return the rule data."""
        return {
            "name": self.name_var.get().strip(),
            "path": self.path_var.get().strip(),
            "patterns": self.patterns.copy(),
            "active": self.active_var.get(),
            "unzip": self.unzip_var.get(),
            "priority": self.rules.get(self.rule_name, {}).get("priority", 0) if self.is_editing else 0,
            "id": self.rules.get(self.rule_name, {}).get("id", str(uuid.uuid4()))        }
    
    def add_from_library(self):
        """Add patterns from the pattern library."""
        if not self.pattern_library:
            return
        
        from .pattern_manager import PatternLibrarySelectDialog
        dialog = PatternLibrarySelectDialog(self.dialog, self.pattern_library)
        dialog.dialog.wait_window()
        
        if dialog.selected_patterns:
            for pattern_rule in dialog.selected_patterns:
                pattern_str = pattern_rule.pattern
                if pattern_str not in self.patterns:
                    self.patterns.append(pattern_str)
                    if self.patterns_listbox:
                        self.patterns_listbox.insert(tk.END, pattern_str)
    
    def build_new_pattern(self):
        """Build a new pattern using the pattern builder."""
        if not self.pattern_library:
            return
        
        from .pattern_manager import PatternBuilderDialog
        dialog = PatternBuilderDialog(self.dialog, self.pattern_library)
        dialog.dialog.wait_window()
        
        if dialog.result_pattern:
            pattern_str = dialog.result_pattern.pattern
            if pattern_str not in self.patterns:
                self.patterns.append(pattern_str)
                if self.patterns_listbox:
                    self.patterns_listbox.insert(tk.END, pattern_str)
                
                # Ask if user wants to save to library
                if messagebox.askyesno("Save to Library", 
                                     "Would you like to save this pattern to your pattern library for reuse?"):
                    self.pattern_library.add_pattern(dialog.result_pattern)

class RuleListWidget:
    """Modern rule list component (placeholder)."""
    pass


def add_rule_button(rules: Dict[str, Any], config_directory: str, rule_frame, 
                   logger, root, update_callback, pattern_library=None):
    """Add a new rule using modern dialog."""
    editor = RuleEditor(root, rules, config_directory, pattern_library=pattern_library)
    result = editor.show()
    
    if result:
        rule_data = result
        rule_name = rule_data.pop("name")
        
        # Assign priority
        max_priority = max((r.get('priority', 0) for r in rules.values()), default=-1)
        rule_data['priority'] = max_priority + 1
        
        # Add rule
        rules[rule_name] = rule_data
        
        # Save rules
        config_manager = ConfigManager(config_directory)
        rule_manager = RuleManager(config_manager)
        rule_manager._rules = rules
        rule_manager.save_rules()
        
        # Update UI
        if update_callback:
            update_callback()
        
        logger.info(f"Added rule: {rule_name}")


def edit_rule(rule_key: str, rules: Dict[str, Any], config_directory: str, logger, rule_frame, pattern_library=None):
    """Edit an existing rule using modern dialog."""
    if rule_key not in rules:
        messagebox.showerror("Error", f"Rule '{rule_key}' not found.")
        return
    
    # Get root window
    root = rule_frame if rule_frame else tk._default_root
    
    editor = RuleEditor(root, rules, config_directory, rule_key, pattern_library=pattern_library)
    result = editor.show()
    
    if result:
        rule_data = result
        rule_name = rule_data.pop("name")
        
        # If name changed, remove old and add new
        if rule_name != rule_key:
            del rules[rule_key]
        
        rules[rule_name] = rule_data
        
        # Save rules
        config_manager = ConfigManager(config_directory)
        rule_manager = RuleManager(config_manager)
        rule_manager._rules = rules
        rule_manager.save_rules()
        
        logger.info(f"Updated rule: {rule_key} -> {rule_name}")


def enable_all_rules(rules: Dict[str, Any], config_directory: str, rule_frame, 
                    logger, update_callback):
    """Enable all rules."""
    for rule in rules.values():
        rule['active'] = True
    
    # Save rules
    config_manager = ConfigManager(config_directory)
    rule_manager = RuleManager(config_manager)
    rule_manager._rules = rules
    rule_manager.save_rules()
    
    if update_callback:
        update_callback()
    
    logger.info("Enabled all rules")


def disable_all_rules(rules: Dict[str, Any], config_directory: str, rule_frame, 
                     logger, update_callback):
    """Disable all rules."""
    for rule in rules.values():
        rule['active'] = False
    
    # Save rules
    config_manager = ConfigManager(config_directory)
    rule_manager = RuleManager(config_manager)
    rule_manager._rules = rules
    rule_manager.save_rules()
    
    if update_callback:
        update_callback()
    
    logger.info("Disabled all rules")
