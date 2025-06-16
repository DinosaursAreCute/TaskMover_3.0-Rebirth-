#!/usr/bin/env python3
"""
TaskMover - Redesigned Main Application
Integrates the new UI design with existing functionality.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import logging

# Import existing TaskMover modules
from .config import load_rules, save_rules, load_settings, save_settings, load_or_initialize_rules
from .file_operations import start_organization
from .logging_config import configure_logger
from .utils import center_window
from .rule_priority import get_sorted_rule_keys, move_rule_priority
from .ui_helpers import Tooltip

class TaskMoverApp:
    def __init__(self):
        # Initialize logging
        self.logger = configure_logger("TaskMover", developer_mode=True)
        
        # Initialize main window
        self.root = ttkb.Window(themename="flatly")
        self.root.title("TaskMover - File Organization Assistant")
        self.root.geometry("900x700")
        center_window(self.root)
        
        # Load configuration
        self.base_directory = os.path.expanduser("~/default_dir")
        self.config_directory = os.path.join(self.base_directory, "config")
        os.makedirs(self.config_directory, exist_ok=True)
        
        # Load rules and settings
        self.rules = load_or_initialize_rules(self.config_directory, self.logger)
        self.settings = load_settings(self.logger)
        
        # Apply theme from settings
        if "theme" in self.settings:
            try:
                self.root.style.theme_use(self.settings["theme"])
            except Exception as e:
                self.logger.warning(f"Could not apply theme {self.settings['theme']}: {e}")
        
        # Organization folder from settings
        self.organization_folder = self.settings.get("organisation_folder", os.path.expanduser("~/Downloads"))
        
        # UI state
        self.selected_rule_index = None
        
        self.setup_ui()
        self.bind_shortcuts()
        
    def setup_ui(self):
        """Set up the main UI components"""
        self.create_menu()
        self.create_toolbar()
        self.create_status_section()
        self.create_main_content()
        self.create_status_bar()
        
    def create_menu(self):
        """Create the standard menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Rule Set", accelerator="Ctrl+N", command=self.new_rule_set)
        file_menu.add_command(label="Open Rule Set...", accelerator="Ctrl+O", command=self.open_rule_set)
        file_menu.add_command(label="Save Rule Set", accelerator="Ctrl+S", command=self.save_rule_set)
        file_menu.add_command(label="Save Rule Set As...", command=self.save_rule_set_as)
        file_menu.add_separator()
        
        # Recent files submenu (placeholder)
        recent_menu = tk.Menu(file_menu, tearoff=0)
        recent_menu.add_command(label="(No recent files)")
        file_menu.add_cascade(label="Recent Rule Sets", menu=recent_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Import Rules...", command=self.import_rules)
        file_menu.add_command(label="Export Rules...", command=self.export_rules)
        file_menu.add_separator()
        file_menu.add_command(label="Start Organization", accelerator="F5", command=self.start_organization)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Add Rule", accelerator="Ctrl+Shift+N", command=self.add_rule)
        edit_menu.add_command(label="Duplicate Rule", command=self.duplicate_rule)
        edit_menu.add_command(label="Delete Rule", accelerator="Delete", command=self.delete_rule)
        edit_menu.add_separator()
        edit_menu.add_command(label="Enable All Rules", command=self.enable_all_rules)
        edit_menu.add_command(label="Disable All Rules", command=self.disable_all_rules)
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences...", command=self.show_preferences)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(label="Show Rule Details")
        view_menu.add_checkbutton(label="Show Rule Priorities")
        view_menu.add_separator()
        view_menu.add_command(label="Collapse All Rules")
        view_menu.add_command(label="Expand All Rules")
        view_menu.add_separator()
        
        # Developer tools submenu
        dev_menu = tk.Menu(view_menu, tearoff=0)
        dev_menu.add_command(label="Developer Log", command=self.open_developer_log)
        dev_menu.add_command(label="Widget Inspector")
        view_menu.add_cascade(label="Developer Tools", menu=dev_menu)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Start Organization", command=self.start_organization)
        tools_menu.add_command(label="Test Rules (Dry Run)", command=self.test_rules)
        tools_menu.add_separator()
        tools_menu.add_command(label="Create Test Files", command=self.create_test_files)
        tools_menu.add_command(label="Organization History...", command=self.show_organization_history)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Quick Start Guide", command=self.show_quick_start)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_separator()
        help_menu.add_command(label="Check for Updates", command=self.check_updates)
        help_menu.add_command(label="About TaskMover", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
    def create_toolbar(self):
        """Create the main toolbar with primary actions"""
        toolbar = ttkb.Frame(self.root)
        toolbar.pack(fill=X, padx=10, pady=(10, 0))
        
        # Primary action buttons
        add_btn = ttkb.Button(toolbar, text="+ Add Rule", style="success.TButton", command=self.add_rule)
        add_btn.pack(side=LEFT, padx=(0, 10))
        Tooltip(add_btn, "Create a new file organization rule")
        
        start_btn = ttkb.Button(toolbar, text="▶ Start Organization", style="primary.TButton", command=self.start_organization)
        start_btn.pack(side=LEFT, padx=(0, 10))
        Tooltip(start_btn, "Begin organizing files based on active rules")
        
        settings_btn = ttkb.Button(toolbar, text="⚙ Settings", style="secondary.TButton", command=self.show_preferences)
        settings_btn.pack(side=LEFT, padx=(0, 10))
        Tooltip(settings_btn, "Configure application settings")
        
        # Right-aligned buttons
        test_btn = ttkb.Button(toolbar, text="Test Run", style="info.TButton", command=self.test_rules)
        test_btn.pack(side=RIGHT)
        Tooltip(test_btn, "Preview what would happen without moving files")
        
    def create_status_section(self):
        """Create the status/info section"""
        status_frame = ttkb.LabelFrame(self.root, text="Status", padding=10)
        status_frame.pack(fill=X, padx=10, pady=10)
        
        # Organization folder
        folder_frame = ttkb.Frame(status_frame)
        folder_frame.pack(fill=X, pady=(0, 5))
        
        ttkb.Label(folder_frame, text="Organization Folder:", font=("", 10, "bold")).pack(side=LEFT)
        
        self.folder_var = tk.StringVar(value=self.organization_folder)
        folder_entry = ttkb.Entry(folder_frame, textvariable=self.folder_var, width=50)
        folder_entry.pack(side=LEFT, padx=(10, 5), fill=X, expand=True)
        
        browse_btn = ttkb.Button(folder_frame, text="Browse...", command=self.browse_organization_folder)
        browse_btn.pack(side=RIGHT)
        Tooltip(browse_btn, "Select the folder to organize")
        
        # Status info
        info_frame = ttkb.Frame(status_frame)
        info_frame.pack(fill=X)
        
        ttkb.Label(info_frame, text="Status:", font=("", 10, "bold")).pack(side=LEFT)
        self.status_label = ttkb.Label(info_frame, text="Ready", foreground="green")
        self.status_label.pack(side=LEFT, padx=(10, 0))
        
        ttkb.Label(info_frame, text="Last run:", font=("", 10, "bold")).pack(side=RIGHT, padx=(20, 5))
        self.last_run_label = ttkb.Label(info_frame, text="Never")
        self.last_run_label.pack(side=RIGHT)
        
        self.update_status_display()
        
    def create_main_content(self):
        """Create the main content area with rules and activity"""
        # Create notebook for tabbed interface
        self.notebook = ttkb.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Rules tab
        rules_frame = ttkb.Frame(self.notebook)
        self.notebook.add(rules_frame, text="Rules")
        
        self.create_rules_list(rules_frame)
        
        # Recent Activity tab  
        activity_frame = ttkb.Frame(self.notebook)
        self.notebook.add(activity_frame, text="Recent Activity")
        
        self.create_activity_section(activity_frame)
        
    def create_rules_list(self, parent):
        """Create the rules list interface"""
        # Rules list with scrollbar
        list_frame = ttkb.Frame(parent)
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for rules
        columns = ("Active", "Priority", "Rule Name", "Patterns", "Destination")
        self.rules_tree = ttkb.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        self.rules_tree.heading("Active", text="Active")
        self.rules_tree.heading("Priority", text="#")
        self.rules_tree.heading("Rule Name", text="Rule Name")
        self.rules_tree.heading("Patterns", text="File Patterns")
        self.rules_tree.heading("Destination", text="Destination")
        
        self.rules_tree.column("Active", width=60, anchor=CENTER)
        self.rules_tree.column("Priority", width=40, anchor=CENTER)
        self.rules_tree.column("Rule Name", width=150)
        self.rules_tree.column("Patterns", width=200)
        self.rules_tree.column("Destination", width=250)
        
        # Add scrollbar
        scrollbar = ttkb.Scrollbar(list_frame, orient=VERTICAL, command=self.rules_tree.yview)
        self.rules_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.rules_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Bind events
        self.rules_tree.bind("<Double-1>", self.on_rule_double_click)
        self.rules_tree.bind("<<TreeviewSelect>>", self.on_rule_select)
        
        # Populate rules
        self.refresh_rules_display()
        
        # Context menu
        self.create_context_menu()
        
        # Action buttons frame
        actions_frame = ttkb.Frame(parent)
        actions_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        edit_btn = ttkb.Button(actions_frame, text="Edit Rule", command=self.edit_selected_rule)
        edit_btn.pack(side=LEFT, padx=(0, 5))
        Tooltip(edit_btn, "Edit the selected rule")
        
        duplicate_btn = ttkb.Button(actions_frame, text="Duplicate Rule", command=self.duplicate_rule)
        duplicate_btn.pack(side=LEFT, padx=(0, 5))
        Tooltip(duplicate_btn, "Create a copy of the selected rule")
        
        delete_btn = ttkb.Button(actions_frame, text="Delete Rule", style="danger.TButton", command=self.delete_rule)
        delete_btn.pack(side=LEFT, padx=(0, 15))
        Tooltip(delete_btn, "Delete the selected rule")
        
        # Rule management buttons (right side)
        enable_all_btn = ttkb.Button(actions_frame, text="Enable All", style="success.TButton", command=self.enable_all_rules)
        enable_all_btn.pack(side=RIGHT, padx=(5, 0))
        Tooltip(enable_all_btn, "Enable all rules")
        
        disable_all_btn = ttkb.Button(actions_frame, text="Disable All", style="warning.TButton", command=self.disable_all_rules)
        disable_all_btn.pack(side=RIGHT, padx=(5, 0))
        Tooltip(disable_all_btn, "Disable all rules")
        
    def create_activity_section(self, parent):
        """Create the recent activity section"""
        self.activity_text = ttkb.Text(parent, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.activity_text.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Add initial message
        self.activity_text.config(state=tk.NORMAL)
        self.activity_text.insert(tk.END, "No organization activity yet.\n\nClick 'Start Organization' to begin organizing files based on your rules.")
        self.activity_text.config(state=tk.DISABLED)
        
    def create_context_menu(self):
        """Create right-click context menu for rules"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit Rule...", command=self.edit_selected_rule)
        self.context_menu.add_command(label="Duplicate Rule", command=self.duplicate_rule)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Toggle Active/Inactive", command=self.toggle_rule_active)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Move Up", command=self.move_rule_up)
        self.context_menu.add_command(label="Move Down", command=self.move_rule_down)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Rule", command=self.delete_rule)
        
        self.rules_tree.bind("<Button-3>", self.show_context_menu)
        
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        status_bar = ttkb.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_bar.pack(fill=X, side=BOTTOM)
        
        # Status indicator
        self.status_indicator = ttkb.Label(status_bar, text="● Ready")
        self.status_indicator.pack(side=LEFT, padx=5)
        
        ttkb.Separator(status_bar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5)
        
        # Rules count
        self.rules_count_label = ttkb.Label(status_bar, text="0 rules")
        self.rules_count_label.pack(side=LEFT, padx=5)
        
        ttkb.Separator(status_bar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5)
        
        # Last run
        self.status_last_run = ttkb.Label(status_bar, text="Last run: Never")
        self.status_last_run.pack(side=LEFT, padx=5)
        
        # Folder indicator
        self.folder_indicator = ttkb.Label(status_bar, text="📁 Downloads")
        self.folder_indicator.pack(side=RIGHT, padx=5)
        
        self.update_status_bar()
        
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Control-n>', lambda e: self.new_rule_set())
        self.root.bind('<Control-o>', lambda e: self.open_rule_set())
        self.root.bind('<Control-s>', lambda e: self.save_rule_set())
        self.root.bind('<Control-Shift-N>', lambda e: self.add_rule())
        self.root.bind('<F5>', lambda e: self.start_organization())
        self.root.bind('<Delete>', lambda e: self.delete_rule())
        self.root.bind('<F2>', lambda e: self.edit_selected_rule())
        
    # ===== UI EVENT HANDLERS =====
    
    def on_rule_double_click(self, event):
        """Handle double-click on rule"""
        self.edit_selected_rule()
        
    def on_rule_select(self, event):
        """Handle rule selection"""
        selection = self.rules_tree.selection()
        if selection:
            self.selected_rule_index = self.rules_tree.index(selection[0])
        else:
            self.selected_rule_index = None
            
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.rules_tree.identify_row(event.y)
        if item:
            self.rules_tree.selection_set(item)
            self.selected_rule_index = self.rules_tree.index(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    # ===== RULE MANAGEMENT =====
    
    def refresh_rules_display(self):
        """Refresh the rules display"""
        # Clear current items
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
            
        # Get sorted rule keys
        sorted_keys = get_sorted_rule_keys(self.rules)
        
        # Populate rules
        for i, rule_key in enumerate(sorted_keys):
            rule = self.rules[rule_key]
            active_text = "✓" if rule.get("active", True) else "○"
            priority = rule.get("priority", 0) + 1  # Display 1-based priority
            patterns_text = ", ".join(rule.get("patterns", []))
            destination = rule.get("path", "")
            
            self.rules_tree.insert("", tk.END, values=(
                active_text,
                priority,
                rule_key,
                patterns_text,
                destination
            ))
            
        self.update_status_display()
        self.update_status_bar()
        
    def get_selected_rule_key(self):
        """Get the key of the currently selected rule"""
        if self.selected_rule_index is None:
            return None
            
        sorted_keys = get_sorted_rule_keys(self.rules)
        if 0 <= self.selected_rule_index < len(sorted_keys):
            return sorted_keys[self.selected_rule_index]
        return None
        
    def add_rule(self):
        """Add a new rule"""
        from .ui_rule_helpers import add_rule_button
        add_rule_button(self.rules, self.config_directory, None, self.logger, self.root, self.refresh_rules_display)
        
    def edit_selected_rule(self):
        """Edit the selected rule"""
        rule_key = self.get_selected_rule_key()
        if not rule_key:
            messagebox.showwarning("No Selection", "Please select a rule to edit.")
            return
            
        from .ui_rule_helpers import edit_rule
        edit_rule(rule_key, self.rules, self.config_directory, self.logger, None)
        self.refresh_rules_display()
        
    def duplicate_rule(self):
        """Duplicate the selected rule"""
        rule_key = self.get_selected_rule_key()
        if not rule_key:
            messagebox.showwarning("No Selection", "Please select a rule to duplicate.")
            return
            
        # Create duplicate
        original_rule = self.rules[rule_key].copy()
        new_name = f"{rule_key} (Copy)"
        
        # Ensure unique name
        counter = 1
        while new_name in self.rules:
            new_name = f"{rule_key} (Copy {counter})"
            counter += 1
            
        # Add new rule with highest priority
        max_priority = max((r.get('priority', 0) for r in self.rules.values()), default=-1)
        original_rule['priority'] = max_priority + 1
        
        # Ensure it has an ID
        if 'id' not in original_rule:
            import uuid
            original_rule['id'] = str(uuid.uuid4())
        
        self.rules[new_name] = original_rule
        save_rules(self.config_directory, self.rules)
        
        self.refresh_rules_display()
        self.logger.info(f"Duplicated rule: {rule_key} → {new_name}")
        
    def delete_rule(self):
        """Delete the selected rule"""
        rule_key = self.get_selected_rule_key()
        if not rule_key:
            messagebox.showwarning("No Selection", "Please select a rule to delete.")
            return
            
        if messagebox.askyesno("Confirm Delete", f'Are you sure you want to delete the rule "{rule_key}"?'):
            del self.rules[rule_key]
            save_rules(self.config_directory, self.rules)
            self.refresh_rules_display()
            self.logger.info(f"Deleted rule: {rule_key}")
            
    def toggle_rule_active(self):
        """Toggle the active state of selected rule"""
        rule_key = self.get_selected_rule_key()
        if not rule_key:
            return
            
        self.rules[rule_key]['active'] = not self.rules[rule_key].get('active', True)
        save_rules(self.config_directory, self.rules)
        self.refresh_rules_display()
        
    def enable_all_rules(self):
        """Enable all rules"""
        from .ui_rule_helpers import enable_all_rules
        enable_all_rules(self.rules, self.config_directory, None, self.logger, self.refresh_rules_display)
        
    def disable_all_rules(self):
        """Disable all rules"""
        from .ui_rule_helpers import disable_all_rules
        disable_all_rules(self.rules, self.config_directory, None, self.logger, self.refresh_rules_display)
        
    def move_rule_up(self):
        """Move selected rule up in priority"""
        rule_key = self.get_selected_rule_key()
        if not rule_key:
            return
            
        move_rule_priority(self.rules, rule_key, -1)
        save_rules(self.config_directory, self.rules)
        self.refresh_rules_display()
        
    def move_rule_down(self):
        """Move selected rule down in priority"""
        rule_key = self.get_selected_rule_key()
        if not rule_key:
            return
            
        move_rule_priority(self.rules, rule_key, 1)
        save_rules(self.config_directory, self.rules)
        self.refresh_rules_display()
        
    # ===== ORGANIZATION =====
    
    def start_organization(self):
        """Start the organization process"""
        # Update organization folder from UI
        self.organization_folder = self.folder_var.get()
        self.settings["organisation_folder"] = self.organization_folder
        save_settings(os.path.join(self.config_directory, "settings.yml"), self.settings, self.logger)
        
        active_rules = {k: v for k, v in self.rules.items() if v.get("active", True)}
        if not active_rules:
            messagebox.showwarning("No Active Rules", "Please enable at least one rule before starting organization.")
            return
            
        result = messagebox.askyesno(
            "Start Organization", 
            f"This will organize files in:\n{self.organization_folder}\n\n"
            f"Using {len(active_rules)} active rules.\n\n"
            "Do you want to continue?"
        )
        
        if result:
            self.show_progress_dialog()
            
    def show_progress_dialog(self):
        """Show organization progress"""
        progress_dialog = ttkb.Toplevel(self.root)
        progress_dialog.title("Organizing Files...")
        progress_dialog.geometry("600x400")
        progress_dialog.transient(self.root)
        progress_dialog.grab_set()
        center_window(progress_dialog)
        
        ttkb.Label(progress_dialog, text="Organizing files...", font=("", 12, "bold")).pack(pady=20)
        
        progress = ttkb.Progressbar(progress_dialog, mode="indeterminate", length=500)
        progress.pack(pady=10)
        progress.start()
        
        status_label = ttkb.Label(progress_dialog, text="Starting organization...")
        status_label.pack(pady=10)
        
        # File list
        list_frame = ttkb.Frame(progress_dialog)
        list_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        file_listbox = tk.Listbox(list_frame, height=10)
        file_listbox.pack(fill=BOTH, expand=True)
        
        def progress_callback(index, total, file_name):
            status_label.config(text=f"Processing {file_name} ({index}/{total})")
            progress_dialog.update()
            
        def file_moved_callback(file_name, target_folder):
            file_listbox.insert(tk.END, f"{file_name} → {target_folder}")
            file_listbox.yview_moveto(1)
            progress_dialog.update()
            
        def close_dialog():
            progress.stop()
            progress_dialog.destroy()
            self.update_activity_log("Organization completed successfully")
            
        close_btn = ttkb.Button(progress_dialog, text="Close", command=close_dialog)
        close_btn.pack(pady=10)
        
        # Run organization in background
        try:
            start_organization(self.settings, self.rules, self.logger, 
                             progress_callback=progress_callback, 
                             file_moved_callback=file_moved_callback)
            status_label.config(text="Organization completed!")
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}")
            self.logger.error(f"Organization failed: {e}")
            
    def test_rules(self):
        """Test rules without moving files (placeholder)"""
        messagebox.showinfo("Test Run", "Test run functionality will be implemented in a future update.\n\nThis would show what files would be moved without actually moving them.")
        
    # ===== UTILITY METHODS =====
    
    def update_status_display(self):
        """Update the status display"""
        active_count = sum(1 for rule in self.rules.values() if rule.get("active", True))
        total_count = len(self.rules)
        
        if active_count == 0:
            status_text = f"No active rules ({total_count} total)"
            self.status_label.config(text=status_text, foreground="orange")
        else:
            status_text = f"Ready ({active_count} active rules)"
            self.status_label.config(text=status_text, foreground="green")
            
    def update_status_bar(self):
        """Update the status bar"""
        active_count = sum(1 for rule in self.rules.values() if rule.get("active", True))
        total_count = len(self.rules)
        
        self.rules_count_label.config(text=f"{active_count}/{total_count} rules active")
        
        # Update folder indicator
        folder_name = os.path.basename(self.organization_folder) or "Root"
        self.folder_indicator.config(text=f"📁 {folder_name}")
        
    def update_activity_log(self, message):
        """Update the activity log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.activity_text.config(state=tk.NORMAL)
        self.activity_text.insert(tk.END, f"\n[{timestamp}] {message}")
        self.activity_text.see(tk.END)
        self.activity_text.config(state=tk.DISABLED)
        
        # Update last run display
        self.last_run_label.config(text=datetime.datetime.now().strftime("Today at %I:%M %p"))
        self.status_last_run.config(text=f"Last run: {datetime.datetime.now().strftime('%I:%M %p')}")
        
    def browse_organization_folder(self):
        """Browse for organization folder"""
        folder = filedialog.askdirectory(initialdir=self.organization_folder, title="Select Organization Folder")
        if folder:
            self.folder_var.set(folder)
            self.organization_folder = folder
            self.settings["organisation_folder"] = folder
            save_settings(os.path.join(self.config_directory, "settings.yml"), self.settings, self.logger)
            self.update_status_bar()
            
    # ===== PLACEHOLDER METHODS (NOT YET IMPLEMENTED) =====
    
    def new_rule_set(self):
        """Create a new rule set"""
        messagebox.showinfo("Not Implemented", "New rule set functionality will be implemented in a future update.")
        
    def open_rule_set(self):
        """Open an existing rule set"""
        messagebox.showinfo("Not Implemented", "Open rule set functionality will be implemented in a future update.")
        
    def save_rule_set(self):
        """Save the current rule set"""
        messagebox.showinfo("Not Implemented", "Save rule set functionality will be implemented in a future update.")
        
    def save_rule_set_as(self):
        """Save the current rule set with a new name"""
        messagebox.showinfo("Not Implemented", "Save rule set as functionality will be implemented in a future update.")
        
    def import_rules(self):
        """Import rules from a file"""
        messagebox.showinfo("Not Implemented", "Import rules functionality will be implemented in a future update.")
        
    def export_rules(self):
        """Export rules to a file"""
        messagebox.showinfo("Not Implemented", "Export rules functionality will be implemented in a future update.")
        
    def show_preferences(self):
        """Show preferences dialog"""
        from .ui_settings_helpers import open_settings_window
        open_settings_window(self.root, self.settings, save_settings, self.logger)
        
    def open_developer_log(self):
        """Open developer log window"""
        messagebox.showinfo("Not Implemented", "Developer log window will be implemented in a future update.")
        
    def create_test_files(self):
        """Create test files for testing rules"""
        messagebox.showinfo("Not Implemented", "Create test files functionality will be implemented in a future update.")
        
    def show_organization_history(self):
        """Show organization history"""
        messagebox.showinfo("Not Implemented", "Organization history will be implemented in a future update.")
        
    def show_quick_start(self):
        """Show quick start guide"""
        messagebox.showinfo("Not Implemented", "Quick start guide will be implemented in a future update.")
        
    def show_documentation(self):
        """Show documentation"""
        messagebox.showinfo("Not Implemented", "Documentation will be implemented in a future update.")
        
    def check_updates(self):
        """Check for updates"""
        messagebox.showinfo("Not Implemented", "Update checking will be implemented in a future update.")
        
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About TaskMover", "TaskMover v3.0\nFile Organization Assistant\n\nCopyright (c) 2025")

def main():
    """Main entry point"""
    app = TaskMoverApp()
    app.root.mainloop()

if __name__ == "__main__":
    main()
