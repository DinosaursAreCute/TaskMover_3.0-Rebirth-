"""
Pattern Management Tab for TaskMover
Provides comprehensive pattern management interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttkb
from typing import List, Dict, Any, Optional, Callable
import logging

from .components import SimpleDialog, Tooltip, TextInputDialog, ConfirmDialog
from ..core.pattern_library import PatternLibrary, Pattern
from ..core.rule_pattern_manager import RulePatternManager
from ..core.utils import center_window_on_parent


class PatternEditorDialog(SimpleDialog):
    """Dialog for creating/editing patterns."""
    
    def __init__(self, parent: tk.Widget, pattern_library: PatternLibrary, 
                 pattern: Optional[Pattern] = None):
        self.pattern_library = pattern_library
        self.pattern = pattern
        self.is_editing = pattern is not None
        
        # Form variables
        self.name_var = tk.StringVar()
        self.pattern_var = tk.StringVar()
        self.type_var = tk.StringVar(value="glob")
        self.description_var = tk.StringVar()
        self.examples_text = None
        self.tags_var = tk.StringVar()
        self.test_results_text = None
        
        # Load existing pattern data
        if self.is_editing:
            self.name_var.set(pattern.name)
            self.pattern_var.set(pattern.pattern)
            self.type_var.set(pattern.type)
            self.description_var.set(pattern.description)
            self.tags_var.set(", ".join(pattern.tags or []))
        
        title = f"Edit Pattern: {pattern.name}" if self.is_editing else "Create New Pattern"
        super().__init__(parent, title, 600, 500)
    
    def create_content(self):
        """Create the pattern editor form."""
        # Pattern name
        name_frame = ttkb.Frame(self.main_frame)
        name_frame.pack(fill="x", pady=(0, 10))
        
        ttkb.Label(name_frame, text="Pattern Name:", font=("", 10, "bold")).pack(anchor="w")
        name_entry = ttkb.Entry(name_frame, textvariable=self.name_var, font=("", 10))
        name_entry.pack(fill="x", pady=(5, 0))
        Tooltip(name_entry, "Enter a unique name for this pattern")
        
        if not self.is_editing:
            name_entry.focus()
        
        # Pattern string and type
        pattern_frame = ttkb.Frame(self.main_frame)
        pattern_frame.pack(fill="x", pady=(0, 10))
        
        ttkb.Label(pattern_frame, text="Pattern:", font=("", 10, "bold")).pack(anchor="w")
        
        pattern_input_frame = ttkb.Frame(pattern_frame)
        pattern_input_frame.pack(fill="x", pady=(5, 0))
        
        pattern_entry = ttkb.Entry(pattern_input_frame, textvariable=self.pattern_var, 
                                  font=("Consolas", 10))
        pattern_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        pattern_entry.bind('<KeyRelease>', self.on_pattern_changed)
        
        # Pattern type dropdown
        type_combo = ttk.Combobox(pattern_input_frame, textvariable=self.type_var,
                                 values=["glob", "regex", "exact"], state="readonly", width=8)
        type_combo.pack(side="right")
        type_combo.bind('<<ComboboxSelected>>', self.on_pattern_changed)
        Tooltip(type_combo, "Select pattern type:\nglob: *.txt, file_*.log\nregex: .*\\.log$\nexact: filename.txt")
        
        # Test pattern button
        test_btn = ttkb.Button(pattern_input_frame, text="Test", command=self.test_pattern)
        test_btn.pack(side="right", padx=(5, 5))
        
        # Description
        desc_frame = ttkb.Frame(self.main_frame)
        desc_frame.pack(fill="x", pady=(0, 10))
        
        ttkb.Label(desc_frame, text="Description:").pack(anchor="w")
        desc_entry = ttkb.Entry(desc_frame, textvariable=self.description_var)
        desc_entry.pack(fill="x", pady=(5, 0))
        
        # Tags
        tags_frame = ttkb.Frame(self.main_frame)
        tags_frame.pack(fill="x", pady=(0, 10))
        
        ttkb.Label(tags_frame, text="Tags (comma-separated):").pack(anchor="w")
        tags_entry = ttkb.Entry(tags_frame, textvariable=self.tags_var)
        tags_entry.pack(fill="x", pady=(5, 0))
        Tooltip(tags_entry, "Enter tags separated by commas (e.g., code, python, source)")
        
        # Examples
        examples_frame = ttkb.LabelFrame(self.main_frame, text="Examples", padding=5)
        examples_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.examples_text = tk.Text(examples_frame, height=4, font=("Consolas", 9))
        examples_scroll = ttkb.Scrollbar(examples_frame, orient="vertical", 
                                        command=self.examples_text.yview)
        self.examples_text.configure(yscrollcommand=examples_scroll.set)
        
        self.examples_text.pack(side="left", fill="both", expand=True)
        examples_scroll.pack(side="right", fill="y")
        
        if self.is_editing and self.pattern.examples:
            self.examples_text.insert("1.0", "\n".join(self.pattern.examples))
        
        Tooltip(self.examples_text, "Enter example filenames (one per line) that should match this pattern")
        
        # Test results
        test_frame = ttkb.LabelFrame(self.main_frame, text="Pattern Test Results", padding=5)
        test_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        self.test_results_text = tk.Text(test_frame, height=3, font=("Consolas", 9), 
                                        state="disabled", bg="#f8f9fa")
        test_scroll = ttkb.Scrollbar(test_frame, orient="vertical", 
                                    command=self.test_results_text.yview)
        self.test_results_text.configure(yscrollcommand=test_scroll.set)
        
        self.test_results_text.pack(side="left", fill="both", expand=True)
        test_scroll.pack(side="right", fill="y")
        
        # Validation on initial load
        self.on_pattern_changed()
    
    def create_buttons(self):
        """Create Save/Cancel buttons."""
        button_frame = ttkb.Frame(self.main_frame)
        button_frame.pack(fill="x", pady=(15, 0))
        
        cancel_btn = ttkb.Button(button_frame, text="Cancel", command=self.cancel)
        cancel_btn.pack(side="right", padx=(5, 0))
        
        save_btn = ttkb.Button(button_frame, text="Save Pattern", command=self.ok, 
                              bootstyle="success")
        save_btn.pack(side="right")
    
    def on_pattern_changed(self, event=None):
        """Validate pattern when it changes."""
        pattern_str = self.pattern_var.get().strip()
        pattern_type = self.type_var.get()
        
        if pattern_str:
            is_valid, error_msg = self.pattern_library.validate_pattern(pattern_str, pattern_type)
            if is_valid:
                self.test_results_text.config(state="normal")
                self.test_results_text.delete("1.0", tk.END)
                self.test_results_text.insert("1.0", "✅ Pattern is valid")
                self.test_results_text.config(state="disabled", bg="#d4edda")
            else:
                self.test_results_text.config(state="normal")
                self.test_results_text.delete("1.0", tk.END)
                self.test_results_text.insert("1.0", f"❌ {error_msg}")
                self.test_results_text.config(state="disabled", bg="#f8d7da")
        else:
            self.test_results_text.config(state="normal")
            self.test_results_text.delete("1.0", tk.END)
            self.test_results_text.config(state="disabled", bg="#f8f9fa")
    
    def test_pattern(self):
        """Test pattern against examples."""
        pattern_str = self.pattern_var.get().strip()
        pattern_type = self.type_var.get()
        
        if not pattern_str:
            messagebox.showwarning("No Pattern", "Please enter a pattern to test")
            return
        
        # Get examples from text widget
        examples_text = self.examples_text.get("1.0", tk.END).strip()
        if not examples_text:
            messagebox.showwarning("No Examples", "Please enter some example filenames to test against")
            return
        
        examples = [line.strip() for line in examples_text.split('\n') if line.strip()]
        
        # Test pattern
        matches = self.pattern_library._test_pattern_string(pattern_str, pattern_type, examples)
        
        # Display results
        self.test_results_text.config(state="normal")
        self.test_results_text.delete("1.0", tk.END)
        
        if matches:
            result = f"✅ Matches found ({len(matches)}/{len(examples)}):\n"
            result += "\n".join(f"  • {match}" for match in matches)
        else:
            result = "❌ No matches found"
        
        self.test_results_text.insert("1.0", result)
        self.test_results_text.config(state="disabled", bg="#d4edda" if matches else "#f8d7da")
    
    def validate(self) -> bool:
        """Validate form data."""
        name = self.name_var.get().strip()
        pattern_str = self.pattern_var.get().strip()
        pattern_type = self.type_var.get()
        
        if not name:
            messagebox.showerror("Validation Error", "Pattern name is required")
            return False
        
        if not pattern_str:
            messagebox.showerror("Validation Error", "Pattern is required")
            return False
        
        # Check for duplicate names (unless editing the same pattern)
        existing_pattern = self.pattern_library.get_pattern_by_name(name)
        if existing_pattern and (not self.is_editing or existing_pattern.id != self.pattern.id):
            messagebox.showerror("Validation Error", f"A pattern named '{name}' already exists")
            return False
        
        # Validate pattern syntax
        is_valid, error_msg = self.pattern_library.validate_pattern(pattern_str, pattern_type)
        if not is_valid:
            messagebox.showerror("Validation Error", f"Invalid pattern: {error_msg}")
            return False
        
        return True
    
    def get_result(self) -> Dict[str, Any]:
        """Get the pattern data from the form."""
        examples_text = self.examples_text.get("1.0", tk.END).strip()
        examples = [line.strip() for line in examples_text.split('\n') if line.strip()]
        
        tags_text = self.tags_var.get().strip()
        tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
        
        return {
            'name': self.name_var.get().strip(),
            'pattern': self.pattern_var.get().strip(),
            'type': self.type_var.get(),
            'description': self.description_var.get().strip(),
            'examples': examples,
            'tags': tags
        }


class PatternTestDialog(SimpleDialog):
    """Dialog for testing patterns against filenames."""
    
    def __init__(self, parent: tk.Widget, pattern_library: PatternLibrary):
        self.pattern_library = pattern_library
        self.test_files_text = None
        self.results_tree = None
        
        super().__init__(parent, "Test Patterns", 700, 500)
    
    def create_content(self):
        """Create the pattern testing interface."""
        # Instructions
        info_frame = ttkb.Frame(self.main_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        info_label = ttkb.Label(info_frame, 
                               text="Enter filenames to test against all patterns (one per line):",
                               font=("", 10))
        info_label.pack(anchor="w")
        
        # Test files input
        files_frame = ttkb.LabelFrame(self.main_frame, text="Test Filenames", padding=5)
        files_frame.pack(fill="x", pady=(0, 10))
        
        self.test_files_text = tk.Text(files_frame, height=6, font=("Consolas", 9))
        files_scroll = ttkb.Scrollbar(files_frame, orient="vertical", 
                                     command=self.test_files_text.yview)
        self.test_files_text.configure(yscrollcommand=files_scroll.set)
        
        self.test_files_text.pack(side="left", fill="both", expand=True)
        files_scroll.pack(side="right", fill="y")
        
        # Add some sample filenames
        sample_files = [
            "document.pdf", "photo.jpg", "script.py", "data.csv",
            "backup.zip", "app.log", "style.css", "index.html"
        ]
        self.test_files_text.insert("1.0", "\n".join(sample_files))
        
        # Test button
        test_btn_frame = ttkb.Frame(self.main_frame)
        test_btn_frame.pack(fill="x", pady=(0, 10))
        
        test_btn = ttkb.Button(test_btn_frame, text="Run Tests", 
                              command=self.run_tests, bootstyle="primary")
        test_btn.pack()
        
        # Results
        results_frame = ttkb.LabelFrame(self.main_frame, text="Test Results", padding=5)
        results_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Results tree
        columns = ("Pattern", "Type", "Matches", "Filenames")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
        
        self.results_tree.column("Pattern", width=150)
        self.results_tree.column("Type", width=60)
        self.results_tree.column("Matches", width=60)
        self.results_tree.column("Filenames", width=300)
        
        results_scroll = ttkb.Scrollbar(results_frame, orient="vertical", 
                                       command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scroll.set)
        
        self.results_tree.pack(side="left", fill="both", expand=True)
        results_scroll.pack(side="right", fill="y")
    
    def create_buttons(self):
        """Create Close button."""
        button_frame = ttkb.Frame(self.main_frame)
        button_frame.pack(fill="x", pady=(15, 0))
        
        close_btn = ttkb.Button(button_frame, text="Close", command=self.cancel)
        close_btn.pack(side="right")
    
    def run_tests(self):
        """Run pattern tests."""
        # Get test filenames
        files_text = self.test_files_text.get("1.0", tk.END).strip()
        if not files_text:
            messagebox.showwarning("No Files", "Please enter some filenames to test")
            return
        
        test_files = [line.strip() for line in files_text.split('\n') if line.strip()]
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Test each pattern
        patterns = self.pattern_library.get_all_patterns()
        
        for pattern in patterns:
            matches = self.pattern_library.test_pattern(pattern.id, test_files)
            
            match_count = len(matches)
            matches_str = ", ".join(matches) if matches else "No matches"
            
            # Insert result
            self.results_tree.insert("", "end", values=(
                pattern.name,
                pattern.type,
                f"{match_count}/{len(test_files)}",
                matches_str
            ))


class PatternManagementTab:
    """Main pattern management interface."""
    
    def __init__(self, parent_notebook: ttk.Notebook, pattern_library: PatternLibrary, 
                 rule_pattern_manager: RulePatternManager):
        self.pattern_library = pattern_library
        self.rule_pattern_manager = rule_pattern_manager
        self.logger = logging.getLogger(__name__)
        
        # Create tab frame
        self.frame = ttkb.Frame(parent_notebook)
        parent_notebook.add(self.frame, text="Patterns")
        
        # UI components
        self.search_var = tk.StringVar()
        self.pattern_tree = None
        
        self.create_ui()
        self.refresh_pattern_list()
    
    def create_ui(self):
        """Create the pattern management interface."""
        # Top toolbar
        toolbar = ttkb.Frame(self.frame)
        toolbar.pack(fill="x", padx=10, pady=5)
        
        # Pattern management buttons
        btn_frame = ttkb.Frame(toolbar)
        btn_frame.pack(side="left")
        
        ttkb.Button(btn_frame, text="New Pattern", 
                   command=self.create_pattern).pack(side="left", padx=(0, 5))
        ttkb.Button(btn_frame, text="Edit", 
                   command=self.edit_pattern).pack(side="left", padx=(0, 5))
        ttkb.Button(btn_frame, text="Delete", 
                   command=self.delete_pattern).pack(side="left", padx=(0, 5))
        ttkb.Button(btn_frame, text="Test Patterns", 
                   command=self.test_patterns).pack(side="left", padx=(0, 15))
        
        # Import/Export buttons
        io_frame = ttkb.Frame(toolbar)
        io_frame.pack(side="left")
        
        ttkb.Button(io_frame, text="Import", 
                   command=self.import_patterns).pack(side="left", padx=(0, 5))
        ttkb.Button(io_frame, text="Export", 
                   command=self.export_patterns).pack(side="left", padx=(0, 5))
        
        # Search box
        search_frame = ttkb.Frame(toolbar)
        search_frame.pack(side="right")
        
        ttkb.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        self.search_var.trace('w', self.filter_patterns)
        search_entry = ttkb.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left")
        
        # Pattern list
        list_frame = ttkb.Frame(self.frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Pattern tree with columns
        columns = ("Name", "Type", "Pattern", "Usage", "Description")
        self.pattern_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.pattern_tree.heading(col, text=col)
        
        self.pattern_tree.column("Name", width=150)
        self.pattern_tree.column("Type", width=60)
        self.pattern_tree.column("Pattern", width=200)
        self.pattern_tree.column("Usage", width=80)
        self.pattern_tree.column("Description", width=250)
        
        # Scrollbars
        v_scroll = ttkb.Scrollbar(list_frame, orient="vertical", command=self.pattern_tree.yview)
        h_scroll = ttkb.Scrollbar(list_frame, orient="horizontal", command=self.pattern_tree.xview)
        self.pattern_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Pack tree and scrollbars
        self.pattern_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Double-click to edit
        self.pattern_tree.bind("<Double-1>", self.on_pattern_double_click)
        
        # Context menu
        self.create_context_menu()
    
    def create_context_menu(self):
        """Create right-click context menu."""
        self.context_menu = tk.Menu(self.pattern_tree, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_pattern)
        self.context_menu.add_command(label="Delete", command=self.delete_pattern)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Show Usage", command=self.show_pattern_usage)
        self.context_menu.add_command(label="Test Pattern", command=self.test_selected_pattern)
        
        self.pattern_tree.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        """Show context menu on right-click."""
        item = self.pattern_tree.identify('item', event.x, event.y)
        if item:
            self.pattern_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_pattern_double_click(self, event):
        """Handle double-click on pattern."""
        self.edit_pattern()
    
    def refresh_pattern_list(self):
        """Refresh the pattern list display."""
        # Clear existing items
        for item in self.pattern_tree.get_children():
            self.pattern_tree.delete(item)
        
        # Get patterns (filtered if search query exists)
        search_query = self.search_var.get().strip()
        if search_query:
            patterns = self.pattern_library.search_patterns(search_query)
        else:
            patterns = self.pattern_library.get_all_patterns()
        
        # Populate tree
        for pattern in patterns:
            # Get usage count
            usage = self.rule_pattern_manager.get_pattern_usage(pattern.id)
            usage_count = len(usage)
            
            self.pattern_tree.insert("", "end", values=(
                pattern.name,
                pattern.type,
                pattern.pattern,
                f"{usage_count} rules",
                pattern.description
            ), tags=(pattern.id,))
    
    def filter_patterns(self, *args):
        """Filter patterns based on search query."""
        self.refresh_pattern_list()
    
    def get_selected_pattern_id(self) -> Optional[str]:
        """Get the ID of the currently selected pattern."""
        selection = self.pattern_tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        tags = self.pattern_tree.item(item, "tags")
        return tags[0] if tags else None
    
    def create_pattern(self):
        """Create a new pattern."""
        dialog = PatternEditorDialog(self.frame, self.pattern_library)
        result = dialog.show()
        
        if result:
            try:
                self.pattern_library.create_pattern(**result)
                self.refresh_pattern_list()
                messagebox.showinfo("Success", f"Pattern '{result['name']}' created successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create pattern: {str(e)}")
    
    def edit_pattern(self):
        """Edit the selected pattern."""
        pattern_id = self.get_selected_pattern_id()
        if not pattern_id:
            messagebox.showwarning("No Selection", "Please select a pattern to edit")
            return
        
        pattern = self.pattern_library.get_pattern(pattern_id)
        if not pattern:
            messagebox.showerror("Error", "Pattern not found")
            return
        
        dialog = PatternEditorDialog(self.frame, self.pattern_library, pattern)
        result = dialog.show()
        
        if result:
            try:
                self.pattern_library.update_pattern(pattern_id, **result)
                self.refresh_pattern_list()
                messagebox.showinfo("Success", f"Pattern '{result['name']}' updated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update pattern: {str(e)}")
    
    def delete_pattern(self):
        """Delete the selected pattern."""
        pattern_id = self.get_selected_pattern_id()
        if not pattern_id:
            messagebox.showwarning("No Selection", "Please select a pattern to delete")
            return
        
        pattern = self.pattern_library.get_pattern(pattern_id)
        if not pattern:
            messagebox.showerror("Error", "Pattern not found")
            return
        
        # Check usage
        can_delete, usage = self.rule_pattern_manager.can_delete_pattern(pattern_id)
        
        if not can_delete:
            usage_str = "\n".join([f"  • {u['ruleset']} / {u['rule_name']}" for u in usage])
            message = (f"Pattern '{pattern.name}' is used by {len(usage)} rule(s):\n\n{usage_str}\n\n"
                      "Do you want to remove it from all rules and delete it?")
            
            if not messagebox.askyesno("Pattern In Use", message):
                return
            
            # Remove from all rules
            removed_count = self.rule_pattern_manager.remove_pattern_from_rules(pattern_id)
            self.logger.info(f"Removed pattern from {removed_count} rules")
        else:
            if not messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to delete pattern '{pattern.name}'?"):
                return
        
        # Delete pattern
        if self.pattern_library.delete_pattern(pattern_id):
            self.refresh_pattern_list()
            messagebox.showinfo("Success", f"Pattern '{pattern.name}' deleted successfully")
        else:
            messagebox.showerror("Error", "Failed to delete pattern")
    
    def show_pattern_usage(self):
        """Show where the selected pattern is used."""
        pattern_id = self.get_selected_pattern_id()
        if not pattern_id:
            messagebox.showwarning("No Selection", "Please select a pattern")
            return
        
        pattern = self.pattern_library.get_pattern(pattern_id)
        usage = self.rule_pattern_manager.get_pattern_usage(pattern_id)
        
        if not usage:
            messagebox.showinfo("Pattern Usage", f"Pattern '{pattern.name}' is not used by any rules")
        else:
            usage_str = "\n".join([f"  • {u['ruleset']} / {u['rule_name']}" for u in usage])
            messagebox.showinfo("Pattern Usage", 
                              f"Pattern '{pattern.name}' is used by {len(usage)} rule(s):\n\n{usage_str}")
    
    def test_selected_pattern(self):
        """Test the selected pattern."""
        pattern_id = self.get_selected_pattern_id()
        if not pattern_id:
            messagebox.showwarning("No Selection", "Please select a pattern to test")
            return
        
        # Simple test dialog
        test_files = tk.simpledialog.askstring(
            "Test Pattern",
            "Enter filenames to test (separated by commas):",
            initialvalue="test.txt, example.py, data.csv, image.jpg"
        )
        
        if test_files:
            filenames = [f.strip() for f in test_files.split(',') if f.strip()]
            matches = self.pattern_library.test_pattern(pattern_id, filenames)
            
            pattern = self.pattern_library.get_pattern(pattern_id)
            if matches:
                matches_str = "\n".join([f"  • {match}" for match in matches])
                messagebox.showinfo("Test Results", 
                                  f"Pattern '{pattern.name}' matched {len(matches)} file(s):\n\n{matches_str}")
            else:
                messagebox.showinfo("Test Results", f"Pattern '{pattern.name}' matched no files")
    
    def test_patterns(self):
        """Open pattern testing dialog."""
        dialog = PatternTestDialog(self.frame, self.pattern_library)
        dialog.show()
    
    def import_patterns(self):
        """Import patterns from file."""
        file_path = filedialog.askopenfilename(
            title="Import Patterns",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            success, count = self.pattern_library.import_patterns(file_path)
            if success:
                self.refresh_pattern_list()
                messagebox.showinfo("Import Success", f"Successfully imported {count} patterns")
            else:
                messagebox.showerror("Import Failed", "Failed to import patterns")
    
    def export_patterns(self):
        """Export patterns to file."""
        file_path = filedialog.asksaveasfilename(
            title="Export Patterns",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.pattern_library.export_patterns(file_path):
                count = len(self.pattern_library.patterns)
                messagebox.showinfo("Export Success", f"Successfully exported {count} patterns")
            else:
                messagebox.showerror("Export Failed", "Failed to export patterns")
