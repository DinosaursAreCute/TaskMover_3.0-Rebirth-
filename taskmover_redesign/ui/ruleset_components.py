"""
Ruleset Management UI Components for TaskMover
Provides UI for managing and switching between multiple rulesets.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import ttkbootstrap as ttkb
from typing import List, Dict, Any, Optional, Callable
import os

from .components import SimpleDialog, Tooltip
from ..core import center_window_on_parent
from ..core.ruleset_manager import RulesetManager


class RulesetSwitcher(ttkb.Frame):
    """A compact ruleset switcher widget for the main toolbar."""
    
    def __init__(self, parent, ruleset_manager: RulesetManager, switch_callback: Callable[[str], None]):
        super().__init__(parent)
        self.ruleset_manager = ruleset_manager
        self.switch_callback = switch_callback
        
        self.setup_ui()
        self.refresh_rulesets()
    
    def setup_ui(self):
        """Set up the ruleset switcher UI."""
        # Label
        label = ttkb.Label(self, text="Ruleset:")
        label.pack(side="left", padx=(0, 5))
        
        # Dropdown
        self.ruleset_var = tk.StringVar(value=self.ruleset_manager.current_ruleset)
        self.ruleset_combo = ttkb.Combobox(
            self, 
            textvariable=self.ruleset_var,
            state="readonly",
            width=15
        )
        self.ruleset_combo.pack(side="left", padx=(0, 5))
        self.ruleset_combo.bind('<<ComboboxSelected>>', self.on_ruleset_selected)
        
        # Manage button
        manage_btn = ttkb.Button(
            self, 
            text="Manage", 
            style="secondary.TButton",
            command=self.open_ruleset_manager
        )
        manage_btn.pack(side="left")
        
        # Tooltips
        Tooltip(self.ruleset_combo, "Select active ruleset")
        Tooltip(manage_btn, "Manage rulesets (create, delete, import, export)")
    
    def refresh_rulesets(self):
        """Refresh the ruleset dropdown."""
        rulesets = self.ruleset_manager.get_available_rulesets()
        ruleset_names = [rs['name'] for rs in rulesets]
        
        self.ruleset_combo['values'] = ruleset_names
        
        # Ensure current ruleset is still valid
        if self.ruleset_manager.current_ruleset not in ruleset_names:
            if ruleset_names:
                self.ruleset_manager.current_ruleset = ruleset_names[0]
            else:
                self.ruleset_manager.current_ruleset = "Default"
        
        self.ruleset_var.set(self.ruleset_manager.current_ruleset)
    
    def on_ruleset_selected(self, event=None):
        """Handle ruleset selection."""
        selected = self.ruleset_var.get()
        if selected and selected != self.ruleset_manager.current_ruleset:
            if self.ruleset_manager.switch_ruleset(selected):
                self.switch_callback(selected)
    
    def open_ruleset_manager(self):
        """Open the ruleset management dialog."""
        dialog = RulesetManagerDialog(self.winfo_toplevel(), self.ruleset_manager)
        result = dialog.show()
        
        if result:
            self.refresh_rulesets()
            # If current ruleset was changed in dialog, trigger callback
            current = self.ruleset_var.get()
            if current != self.ruleset_manager.current_ruleset:
                self.ruleset_var.set(self.ruleset_manager.current_ruleset)
                self.switch_callback(self.ruleset_manager.current_ruleset)


class RulesetManagerDialog(SimpleDialog):
    """Dialog for managing rulesets (create, delete, import, export)."""
    
    def __init__(self, parent, ruleset_manager: RulesetManager):
        self.ruleset_manager = ruleset_manager
        self.selected_ruleset = None
        
        super().__init__(parent, "Manage Rulesets", 600, 500)
    
    def create_content(self):
        """Create the dialog content."""
        # Header
        header_frame = ttkb.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ttkb.Label(
            header_frame, 
            text="Ruleset Management", 
            font=("", 14, "bold")
        )
        title_label.pack(side="left")
        
        help_btn = ttkb.Button(
            header_frame,
            text="?",
            style="info.TButton",
            width=3,
            command=self.show_help
        )
        help_btn.pack(side="right")
        
        # Main content
        content_frame = ttkb.Frame(self.main_frame)
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Ruleset list
        list_frame = ttkb.LabelFrame(content_frame, text="Available Rulesets")
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create treeview
        columns = ("Name", "Description", "Rules", "Modified")
        self.tree = ttkb.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.tree.heading("Name", text="Name")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Rules", text="Rules")
        self.tree.heading("Modified", text="Last Modified")
        
        self.tree.column("Name", width=120)
        self.tree.column("Description", width=200)
        self.tree.column("Rules", width=60)
        self.tree.column("Modified", width=120)
        
        # Scrollbar
        scrollbar = ttkb.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self.on_selection_changed)
        self.tree.bind('<Double-1>', self.edit_selected_ruleset)
        
        # Buttons
        button_frame = ttkb.Frame(content_frame)
        button_frame.pack(fill="x")
        
        # Left side buttons
        left_buttons = ttkb.Frame(button_frame)
        left_buttons.pack(side="left")
        
        create_btn = ttkb.Button(
            left_buttons,
            text="Create New",
            style="success.TButton",
            command=self.create_ruleset
        )
        create_btn.pack(side="left", padx=(0, 5))
        
        duplicate_btn = ttkb.Button(
            left_buttons,
            text="Duplicate",
            command=self.duplicate_ruleset
        )
        duplicate_btn.pack(side="left", padx=(0, 5))
        
        edit_btn = ttkb.Button(
            left_buttons,
            text="Edit Details",
            command=self.edit_selected_ruleset
        )
        edit_btn.pack(side="left", padx=(0, 5))
        
        delete_btn = ttkb.Button(
            left_buttons,
            text="Delete",
            style="danger.TButton",
            command=self.delete_ruleset
        )
        delete_btn.pack(side="left", padx=(0, 5))
        
        # Right side buttons
        right_buttons = ttkb.Frame(button_frame)
        right_buttons.pack(side="right")
        
        import_btn = ttkb.Button(
            right_buttons,
            text="Import",
            command=self.import_ruleset
        )
        import_btn.pack(side="left", padx=(0, 5))
        
        export_btn = ttkb.Button(
            right_buttons,
            text="Export",
            command=self.export_ruleset
        )
        export_btn.pack(side="left")
        
        # Store button references for enabling/disabling
        self.duplicate_btn = duplicate_btn
        self.edit_btn = edit_btn
        self.delete_btn = delete_btn
        self.export_btn = export_btn
        
        # Initially disable buttons that require selection
        self.update_button_states()
        
        # Bottom buttons
        bottom_frame = ttkb.Frame(self.main_frame)
        bottom_frame.pack(fill="x", pady=(10, 0))
        
        close_btn = ttkb.Button(
            bottom_frame,
            text="Close",
            command=self.close_dialog
        )
        close_btn.pack(side="right")
        
        # Load rulesets
        self.refresh_rulesets()
    
    def refresh_rulesets(self):
        """Refresh the ruleset list."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load rulesets
        rulesets = self.ruleset_manager.get_available_rulesets()
        
        for ruleset in rulesets:
            # Format modified date
            modified = ruleset.get('modified', '')
            if modified:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                    modified = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            # Insert into tree
            item = self.tree.insert('', 'end', values=(
                ruleset['name'],
                ruleset['description'],
                ruleset['rule_count'],
                modified
            ))
            
            # Highlight current ruleset
            if ruleset['name'] == self.ruleset_manager.current_ruleset:
                self.tree.selection_set(item)
    
    def on_selection_changed(self, event=None):
        """Handle selection change."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            self.selected_ruleset = self.tree.item(item)['values'][0]
        else:
            self.selected_ruleset = None
        
        self.update_button_states()
    
    def update_button_states(self):
        """Update button enabled/disabled states."""
        has_selection = self.selected_ruleset is not None
        is_default = self.selected_ruleset == "Default"
        
        self.duplicate_btn.configure(state="normal" if has_selection else "disabled")
        self.edit_btn.configure(state="normal" if has_selection else "disabled")
        self.delete_btn.configure(state="normal" if (has_selection and not is_default) else "disabled")
        self.export_btn.configure(state="normal" if has_selection else "disabled")
    
    def create_ruleset(self):
        """Create a new ruleset."""
        dialog = RulesetEditDialog(self.dialog, "Create New Ruleset")
        result = dialog.show()
        
        if result:
            name, description = result
            if self.ruleset_manager.create_ruleset(name, description):
                self.refresh_rulesets()
                messagebox.showinfo("Success", f"Ruleset '{name}' created successfully.")
            else:
                messagebox.showerror("Error", f"Failed to create ruleset '{name}'. It may already exist.")
    
    def duplicate_ruleset(self):
        """Duplicate the selected ruleset."""
        if not self.selected_ruleset:
            return
        
        new_name = simpledialog.askstring(
            "Duplicate Ruleset",
            f"Enter name for duplicate of '{self.selected_ruleset}':",
            parent=self.dialog,
            initialvalue=f"{self.selected_ruleset} Copy"
        )
        
        if new_name:
            description = f"Copy of {self.selected_ruleset}"
            if self.ruleset_manager.duplicate_ruleset(self.selected_ruleset, new_name, description):
                self.refresh_rulesets()
                messagebox.showinfo("Success", f"Ruleset duplicated as '{new_name}'.")
            else:
                messagebox.showerror("Error", f"Failed to duplicate ruleset. Name '{new_name}' may already exist.")
    
    def edit_selected_ruleset(self, event=None):
        """Edit the selected ruleset's metadata."""
        if not self.selected_ruleset:
            return
        
        # Load current metadata
        metadata = self.ruleset_manager._load_ruleset_metadata(self.selected_ruleset)
        
        dialog = RulesetEditDialog(
            self.dialog, 
            f"Edit Ruleset: {self.selected_ruleset}",
            initial_name=self.selected_ruleset,
            initial_description=metadata.get('description', ''),
            name_editable=(self.selected_ruleset != "Default")
        )
        result = dialog.show()
        
        if result:
            name, description = result
            # For now, just update description (renaming requires more work)
            if name == self.selected_ruleset:
                # Update metadata file directly
                metadata['description'] = description
                metadata_path = os.path.join(
                    self.ruleset_manager.rulesets_dir, 
                    self.selected_ruleset, 
                    'metadata.json'
                )
                try:
                    import json
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2)
                    self.refresh_rulesets()
                    messagebox.showinfo("Success", "Ruleset updated successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update ruleset: {e}")
    
    def delete_ruleset(self):
        """Delete the selected ruleset."""
        if not self.selected_ruleset or self.selected_ruleset == "Default":
            return
        
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the ruleset '{self.selected_ruleset}'?\n\n"
            "This action cannot be undone.",
            parent=self.dialog
        )
        
        if result:
            if self.ruleset_manager.delete_ruleset(self.selected_ruleset):
                self.refresh_rulesets()
                messagebox.showinfo("Success", f"Ruleset '{self.selected_ruleset}' deleted.")
                self.selected_ruleset = None
            else:
                messagebox.showerror("Error", f"Failed to delete ruleset '{self.selected_ruleset}'.")
    
    def import_ruleset(self):
        """Import a ruleset from file."""
        file_path = filedialog.askopenfilename(
            title="Import Ruleset",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            parent=self.dialog
        )
        
        if file_path:
            if self.ruleset_manager.import_ruleset(file_path):
                self.refresh_rulesets()
                messagebox.showinfo("Success", "Ruleset imported successfully.")
            else:
                messagebox.showerror("Error", "Failed to import ruleset. Please check the file format.")
    
    def export_ruleset(self):
        """Export the selected ruleset."""
        if not self.selected_ruleset:
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Ruleset",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            parent=self.dialog
        )
        
        if file_path:
            if self.ruleset_manager.export_ruleset(self.selected_ruleset, file_path):
                messagebox.showinfo("Success", f"Ruleset exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export ruleset.")
    
    def show_help(self):
        """Show help information."""
        help_text = """RULESET MANAGEMENT HELP

WHAT ARE RULESETS?
Rulesets are collections of file organization rules for different scenarios.
For example:
• Work Documents
• Personal Files  
• Project Organization
• Downloads Cleanup

FEATURES:
• Create: New empty rulesets
• Duplicate: Copy existing rulesets
• Edit: Modify name and description
• Delete: Remove rulesets (except Default)
• Import/Export: Share rulesets between computers

QUICK SWITCH:
Use the dropdown in the main toolbar to quickly switch between rulesets without opening files manually.

The pattern library is shared across all rulesets."""
        
        messagebox.showinfo("Ruleset Management Help", help_text, parent=self.dialog)
    
    def close_dialog(self):
        """Close the dialog."""
        self.result = True
        self.dialog.destroy()


class RulesetEditDialog(SimpleDialog):
    """Dialog for editing ruleset details."""
    
    def __init__(self, parent, title: str, initial_name: str = "", initial_description: str = "", name_editable: bool = True):
        self.initial_name = initial_name
        self.initial_description = initial_description
        self.name_editable = name_editable
        
        super().__init__(parent, title, 400, 200)
    
    def create_content(self):
        """Create the dialog content."""
        # Name field
        name_frame = ttkb.Frame(self.main_frame)
        name_frame.pack(fill="x", pady=(0, 10))
        
        ttkb.Label(name_frame, text="Name:").pack(anchor="w")
        self.name_var = tk.StringVar(value=self.initial_name)
        name_entry = ttkb.Entry(name_frame, textvariable=self.name_var)
        name_entry.pack(fill="x", pady=(5, 0))
        
        if not self.name_editable:
            name_entry.configure(state="disabled")
        
        # Description field
        desc_frame = ttkb.Frame(self.main_frame)
        desc_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        ttkb.Label(desc_frame, text="Description:").pack(anchor="w")
        self.desc_text = tk.Text(desc_frame, height=4, wrap="word")
        self.desc_text.pack(fill="both", expand=True, pady=(5, 0))
        self.desc_text.insert("1.0", self.initial_description)
        
        # Focus and bindings
        if self.name_editable:
            name_entry.focus()
            name_entry.select_range(0, "end")
        else:
            self.desc_text.focus()
        
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def create_buttons(self):
        """Override to create custom buttons."""
        button_frame = ttkb.Frame(self.main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        cancel_btn = ttkb.Button(button_frame, text="Cancel", command=self.dialog.destroy)
        cancel_btn.pack(side="right", padx=(5, 0))
        
        ok_btn = ttkb.Button(button_frame, text="OK", style="success.TButton", command=self.ok_clicked)
        ok_btn.pack(side="right")
    
    def ok_clicked(self):
        """Handle OK button click."""
        name = self.name_var.get().strip()
        description = self.desc_text.get("1.0", "end-1c").strip()
        
        if not name:
            messagebox.showerror("Error", "Name cannot be empty.", parent=self.dialog)
            return
        
        self.result = (name, description)
        self.dialog.destroy()


class RulesetCreationDialog(SimpleDialog):
    """Dialog for creating a new ruleset."""
    
    def __init__(self, parent, ruleset_manager: RulesetManager):
        self.ruleset_manager = ruleset_manager
        self.result = None  # Will be the name of created ruleset if successful
        self.switch_after_create = False
        self.available_rulesets = ruleset_manager.get_available_rulesets()
        
        # Initialize creation mode to standard (not merge)
        self.creation_mode = "standard"
        
        super().__init__(parent, "Create New Ruleset", 500, 400)
    
    def create_content(self):
        """Create the dialog content."""
        # Creation mode selection
        mode_frame = ttkb.Frame(self.main_frame)
        mode_frame.pack(fill="x", pady=(0, 10))
        
        self.mode_var = tk.StringVar(value="standard")
        
        # Standard creation option
        standard_radio = ttkb.Radiobutton(
            mode_frame, 
            text="Create empty ruleset",
            variable=self.mode_var,
            value="standard",
            command=self.update_ui_based_on_mode
        )
        standard_radio.pack(anchor="w")
        
        # Merge option
        merge_radio = ttkb.Radiobutton(
            mode_frame,
            text="Create by merging existing rulesets",
            variable=self.mode_var,
            value="merge",
            command=self.update_ui_based_on_mode
        )
        merge_radio.pack(anchor="w")
        
        # Input fields frame
        self.input_frame = ttkb.Frame(self.main_frame)
        self.input_frame.pack(fill="x", pady=(10, 0))
        
        # Basic fields - name and description
        basic_frame = ttkb.LabelFrame(self.input_frame, text="Ruleset Details")
        basic_frame.pack(fill="x", expand=True, pady=(0, 10))
        
        # Name field
        name_frame = ttkb.Frame(basic_frame)
        name_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ttkb.Label(name_frame, text="Name:").pack(side="left", padx=(0, 10))
        self.name_var = tk.StringVar()
        name_entry = ttkb.Entry(name_frame, textvariable=self.name_var)
        name_entry.pack(side="left", fill="x", expand=True)
        
        # Description field
        desc_frame = ttkb.Frame(basic_frame)
        desc_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttkb.Label(desc_frame, text="Description:").pack(side="left", padx=(0, 10))
        self.desc_var = tk.StringVar()
        desc_entry = ttkb.Entry(desc_frame, textvariable=self.desc_var)
        desc_entry.pack(side="left", fill="x", expand=True)
        
        # Merge section
        self.merge_frame = ttkb.LabelFrame(self.input_frame, text="Merge Options")
        
        # Ruleset selection for merge
        ruleset_frame = ttkb.Frame(self.merge_frame)
        ruleset_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Available rulesets list with checkboxes
        list_frame = ttkb.Frame(ruleset_frame)
        list_frame.pack(fill="both", expand=True)
        
        # Create treeview with checkboxes
        columns = ("Select", "Name", "Description", "Rules")
        self.tree = ttkb.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.tree.heading("Select", text="")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Rules", text="Rules")
        
        self.tree.column("Select", width=30, anchor="center")
        self.tree.column("Name", width=120)
        self.tree.column("Description", width=200)
        self.tree.column("Rules", width=50, anchor="center")
        
        # Scrollbar
        scrollbar = ttkb.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add rulesets to the tree
        self.selected_rulesets = {}
        for ruleset in self.available_rulesets:
            ruleset_name = ruleset['name']
            item_id = self.tree.insert("", "end", values=(
                "☐",  # Unchecked checkbox
                ruleset_name,
                ruleset['description'],
                ruleset['rule_count']
            ))
            self.selected_rulesets[item_id] = {
                'name': ruleset_name,
                'selected': False
            }
        
        # Bind click on the checkbox column
        self.tree.bind("<ButtonRelease-1>", self.toggle_ruleset_selection)
        
        # Conflict handling options
        conflict_frame = ttkb.Frame(self.merge_frame)
        conflict_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttkb.Label(conflict_frame, text="Conflict Strategy:").pack(side="left", padx=(0, 10))
        
        self.conflict_var = tk.StringVar(value="keep_first")
        conflict_combo = ttkb.Combobox(
            conflict_frame,
            textvariable=self.conflict_var,
            state="readonly",
            width=20
        )
        conflict_combo["values"] = [
            "Keep first ruleset's rules",
            "Keep all rules (rename conflicts)",
            "Skip conflicting rules"
        ]
        conflict_combo.pack(side="left")
        
        # Map dropdown display values to internal values
        self.conflict_strategies = {
            "Keep first ruleset's rules": "keep_first",
            "Keep all rules (rename conflicts)": "keep_all",
            "Skip conflicting rules": "keep_none"
        }
        
        conflict_combo.bind("<<ComboboxSelected>>", self.on_conflict_strategy_change)
        
        # Switch to new ruleset checkbox
        self.switch_var = tk.BooleanVar(value=True)
        switch_check = ttkb.Checkbutton(
            self.main_frame,
            text="Switch to new ruleset after creation",
            variable=self.switch_var
        )
        switch_check.pack(anchor="w", pady=10)
        
        # Initial mode setup
        self.update_ui_based_on_mode()
        
        # Focus name field
        name_entry.focus()
    
    def update_ui_based_on_mode(self):
        """Update UI elements based on creation mode."""
        mode = self.mode_var.get()
        self.creation_mode = mode
        
        if mode == "standard":
            if self.merge_frame.winfo_ismapped():
                self.merge_frame.pack_forget()
        else:  # merge mode
            if not self.merge_frame.winfo_ismapped():
                self.merge_frame.pack(fill="both", expand=True, pady=(10, 0))
    
    def toggle_ruleset_selection(self, event):
        """Toggle selection of a ruleset when checkbox column is clicked."""
        # Get region that was clicked
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        
        # Get the column that was clicked
        column = self.tree.identify_column(event.x)
        if column != "#1":  # First column (checkbox)
            return
        
        # Get the item that was clicked
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        # Toggle selection
        current_values = self.tree.item(item, "values")
        is_selected = current_values[0] == "☑"
        
        new_values = list(current_values)
        if is_selected:
            new_values[0] = "☐"  # Unchecked
            self.selected_rulesets[item]['selected'] = False
        else:
            new_values[0] = "☑"  # Checked
            self.selected_rulesets[item]['selected'] = True
        
        self.tree.item(item, values=new_values)
    
    def on_conflict_strategy_change(self, event):
        """Handle conflict strategy selection."""
        selected_display = self.conflict_var.get()
        self.conflict_var.set(selected_display)
    
    def create_buttons(self):
        """Create dialog buttons."""
        button_frame = ttkb.Frame(self.main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        cancel_btn = ttkb.Button(
            button_frame,
            text="Cancel", 
            command=self.dialog.destroy
        )
        cancel_btn.pack(side="right", padx=(5, 0))
        
        create_btn = ttkb.Button(
            button_frame,
            text="Create", 
            style="success.TButton",
            command=self.create_ruleset
        )
        create_btn.pack(side="right")
    
    def create_ruleset(self):
        """Create a new ruleset based on the selected mode."""
        name = self.name_var.get().strip()
        description = self.desc_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a name for the ruleset.", parent=self.dialog)
            return
        
        if self.creation_mode == "standard":
            # Create a standard empty ruleset
            if self.ruleset_manager.create_ruleset(name, description):
                self.result = name
                self.switch_after_create = self.switch_var.get()
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", 
                                   f"Failed to create ruleset '{name}'. It may already exist.",
                                   parent=self.dialog)
        else:  # merge mode
            # Get selected rulesets
            selected = [info['name'] for info in self.selected_rulesets.values() if info['selected']]
            
            if not selected:
                messagebox.showerror("Error", 
                                   "Please select at least one ruleset to merge.",
                                   parent=self.dialog)
                return
            
            # Map display conflict strategy to internal value
            selected_display = self.conflict_var.get()
            conflict_strategy = self.conflict_strategies.get(selected_display, "keep_first")
            
            # Perform the merge
            if self.ruleset_manager.merge_rulesets(selected, name, description, conflict_strategy):
                self.result = name
                self.switch_after_create = self.switch_var.get()
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", 
                                   f"Failed to create merged ruleset '{name}'.",
                                   parent=self.dialog)
