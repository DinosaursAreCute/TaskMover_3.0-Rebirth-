"""
Modern rule management components for TaskMover Redesigned.
Clean, independent rule editing without legacy dependencies.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttkb
from typing import Dict, Any, Optional, List
import uuid
import os

from .components import SimpleDialog, Tooltip, get_text_input
from ..core.rules import RuleManager
from ..core.config import ConfigManager


class RuleEditor(SimpleDialog):
    """Modern rule editing dialog."""
    
    def __init__(self, parent: tk.Widget, rules: Dict[str, Any], config_directory: str, 
                 rule_name: Optional[str] = None):
        self.rules = rules
        self.config_directory = config_directory
        self.rule_name = rule_name
        self.is_editing = rule_name is not None
        
        # Form fields
        self.name_var = tk.StringVar()
        self.path_var = tk.StringVar()
        self.active_var = tk.BooleanVar(value=True)
        self.unzip_var = tk.BooleanVar(value=False)
        self.patterns_listbox = None
        self.patterns = []
        
        # Load existing rule if editing
        if self.is_editing and rule_name in rules:
            rule = rules[rule_name]
            self.name_var.set(rule_name)
            self.path_var.set(rule.get("path", ""))
            self.active_var.set(rule.get("active", True))
            self.unzip_var.set(rule.get("unzip", False))
            self.patterns = rule.get("patterns", []).copy()
        
        title = f"Edit Rule: {rule_name}" if self.is_editing else "Add New Rule"
        super().__init__(parent, title, 600, 500)
    
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
        
        # File patterns
        patterns_frame = ttkb.LabelFrame(self.main_frame, text="File Patterns", padding=10)
        patterns_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Patterns list
        list_frame = ttkb.Frame(patterns_frame)
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
        pattern_btn_frame = ttkb.Frame(patterns_frame)
        pattern_btn_frame.pack(fill="x")
        
        add_pattern_btn = ttkb.Button(pattern_btn_frame, text="Add Pattern", command=self.add_pattern)
        add_pattern_btn.pack(side="left", padx=(0, 5))
        Tooltip(add_pattern_btn, "Add a new file pattern (e.g., *.pdf, *.jpg)")
        
        remove_pattern_btn = ttkb.Button(pattern_btn_frame, text="Remove Pattern", command=self.remove_pattern)
        remove_pattern_btn.pack(side="left", padx=(0, 5))
        Tooltip(remove_pattern_btn, "Remove selected pattern")
        
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
            "id": self.rules.get(self.rule_name, {}).get("id", str(uuid.uuid4()))
        }


class RuleListWidget:
    """Modern rule list component (placeholder)."""
    pass


def add_rule_button(rules: Dict[str, Any], config_directory: str, rule_frame, 
                   logger, root, update_callback):
    """Add a new rule using modern dialog."""
    editor = RuleEditor(root, rules, config_directory)
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


def edit_rule(rule_key: str, rules: Dict[str, Any], config_directory: str, logger, rule_frame):
    """Edit an existing rule using modern dialog."""
    if rule_key not in rules:
        messagebox.showerror("Error", f"Rule '{rule_key}' not found.")
        return
    
    # Get root window
    root = rule_frame if rule_frame else tk._default_root
    
    editor = RuleEditor(root, rules, config_directory, rule_key)
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
