#!/usr/bin/env python3
"""
TaskMover UI Prototype - Redesigned Interface
This demonstrates the improved UI/UX concepts with standard conventions.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *

class TaskMoverPrototype:
    def __init__(self):
        self.root = ttkb.Window(themename="flatly")
        self.root.title("TaskMover - Redesigned UI Prototype")
        self.root.geometry("800x600")
        
        # Sample data
        self.rules = [
            {
                "name": "Documents to Documents/",
                "patterns": ["*.pdf", "*.doc", "*.docx"],
                "destination": "C:\\Users\\Documents\\",
                "active": True,
                "unzip": False
            },
            {
                "name": "Images to Pictures/",
                "patterns": ["*.jpg", "*.png", "*.gif", "*.bmp"],
                "destination": "C:\\Users\\Pictures\\",
                "active": False,
                "unzip": False
            },
            {
                "name": "Downloads Cleanup",
                "patterns": ["*.zip", "*.rar", "*.7z"],
                "destination": "C:\\Users\\Archives\\",
                "active": True,
                "unzip": True
            }
        ]
        
        self.organization_folder = "C:\\Users\\Downloads"
        self.last_run = "Today at 2:30 PM"
        
        self.setup_ui()
        
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
        file_menu.add_command(label="New Rule Set", accelerator="Ctrl+N")
        file_menu.add_command(label="Open Rule Set...", accelerator="Ctrl+O")
        file_menu.add_command(label="Save Rule Set", accelerator="Ctrl+S")
        file_menu.add_command(label="Save Rule Set As...")
        file_menu.add_separator()
        recent_menu = tk.Menu(file_menu, tearoff=0)
        recent_menu.add_command(label="Documents Rules.json")
        recent_menu.add_command(label="Photo Organization.json")
        file_menu.add_cascade(label="Recent Rule Sets", menu=recent_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Import Rules...")
        file_menu.add_command(label="Export Rules...")
        file_menu.add_separator()
        file_menu.add_command(label="Start Organization", accelerator="F5", command=self.start_organization)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Add Rule", command=self.add_rule)
        edit_menu.add_command(label="Duplicate Rule")
        edit_menu.add_command(label="Delete Rule", accelerator="Delete")
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
        dev_menu = tk.Menu(view_menu, tearoff=0)
        dev_menu.add_command(label="Developer Log")
        dev_menu.add_command(label="Widget Inspector")
        view_menu.add_cascade(label="Developer Tools", menu=dev_menu)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Start Organization", command=self.start_organization)
        tools_menu.add_command(label="Test Rules (Dry Run)", command=self.test_rules)
        tools_menu.add_separator()
        tools_menu.add_command(label="Create Test Files")
        tools_menu.add_command(label="Organization History...")
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Quick Start Guide")
        help_menu.add_command(label="Documentation")
        help_menu.add_separator()
        help_menu.add_command(label="Check for Updates")
        help_menu.add_command(label="About TaskMover")
        menubar.add_cascade(label="Help", menu=help_menu)
        
    def create_toolbar(self):
        """Create the main toolbar with primary actions"""
        toolbar = ttkb.Frame(self.root)
        toolbar.pack(fill=X, padx=10, pady=(10, 0))
        
        # Primary action buttons
        ttkb.Button(toolbar, text="+ Add Rule", style="success.TButton", 
                   command=self.add_rule).pack(side=LEFT, padx=(0, 10))
        
        ttkb.Button(toolbar, text="▶ Start Organization", style="primary.TButton",
                   command=self.start_organization).pack(side=LEFT, padx=(0, 10))
        
        ttkb.Button(toolbar, text="⚙ Settings", style="secondary.TButton",
                   command=self.show_preferences).pack(side=LEFT, padx=(0, 10))
        
        # Right-aligned buttons
        ttkb.Button(toolbar, text="Test Run", style="info.TButton",
                   command=self.test_rules).pack(side=RIGHT)
        
    def create_status_section(self):
        """Create the status/info section"""
        status_frame = ttkb.LabelFrame(self.root, text="Status", padding=10)
        status_frame.pack(fill=X, padx=10, pady=10)
        
        # Organization folder
        folder_frame = ttkb.Frame(status_frame)
        folder_frame.pack(fill=X, pady=(0, 5))
        
        ttkb.Label(folder_frame, text="Organization Folder:", 
                  font=("", 10, "bold")).pack(side=LEFT)
        
        folder_var = tk.StringVar(value=self.organization_folder)
        folder_entry = ttkb.Entry(folder_frame, textvariable=folder_var, width=50)
        folder_entry.pack(side=LEFT, padx=(10, 5), fill=X, expand=True)
        
        ttkb.Button(folder_frame, text="Browse...", 
                   command=self.browse_folder).pack(side=RIGHT)
        
        # Status info
        info_frame = ttkb.Frame(status_frame)
        info_frame.pack(fill=X)
        
        active_count = sum(1 for rule in self.rules if rule["active"])
        status_text = f"Ready ({active_count} active rules)"
        
        ttkb.Label(info_frame, text="Status:", 
                  font=("", 10, "bold")).pack(side=LEFT)
        ttkb.Label(info_frame, text=status_text, foreground="green").pack(side=LEFT, padx=(10, 0))
        
        ttkb.Label(info_frame, text="Last run:", 
                  font=("", 10, "bold")).pack(side=RIGHT, padx=(20, 5))
        ttkb.Label(info_frame, text=self.last_run).pack(side=RIGHT)
        
    def create_main_content(self):
        """Create the main content area with rules and activity"""
        # Create notebook for tabbed interface
        notebook = ttkb.Notebook(self.root)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Rules tab
        rules_frame = ttkb.Frame(notebook)
        notebook.add(rules_frame, text="Rules")
        
        self.create_rules_list(rules_frame)
        
        # Recent Activity tab
        activity_frame = ttkb.Frame(notebook)
        notebook.add(activity_frame, text="Recent Activity")
        
        self.create_activity_section(activity_frame)
        
    def create_rules_list(self, parent):
        """Create the simplified rules list"""
        # Rules list with scrollbar
        list_frame = ttkb.Frame(parent)
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for rules
        columns = ("Active", "Rule Name", "Patterns", "Destination")
        self.rules_tree = ttkb.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.rules_tree.heading("Active", text="Active")
        self.rules_tree.heading("Rule Name", text="Rule Name")
        self.rules_tree.heading("Patterns", text="File Patterns")
        self.rules_tree.heading("Destination", text="Destination")
        
        self.rules_tree.column("Active", width=60, anchor=CENTER)
        self.rules_tree.column("Rule Name", width=150)
        self.rules_tree.column("Patterns", width=200)
        self.rules_tree.column("Destination", width=250)
        
        # Add scrollbar
        scrollbar = ttkb.Scrollbar(list_frame, orient=VERTICAL, command=self.rules_tree.yview)
        self.rules_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.rules_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Populate rules
        self.populate_rules()
        
        # Context menu
        self.create_context_menu()
        
        # Action buttons frame
        actions_frame = ttkb.Frame(parent)
        actions_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        ttkb.Button(actions_frame, text="Edit Rule", 
                   command=self.edit_selected_rule).pack(side=LEFT, padx=(0, 5))
        ttkb.Button(actions_frame, text="Duplicate Rule", 
                   command=self.duplicate_rule).pack(side=LEFT, padx=(0, 5))
        ttkb.Button(actions_frame, text="Delete Rule", style="danger.TButton",
                   command=self.delete_rule).pack(side=LEFT, padx=(0, 15))
        
        ttkb.Button(actions_frame, text="Enable All", style="success.TButton",
                   command=self.enable_all_rules).pack(side=RIGHT, padx=(5, 0))
        ttkb.Button(actions_frame, text="Disable All", style="warning.TButton",
                   command=self.disable_all_rules).pack(side=RIGHT, padx=(5, 0))
        
    def create_activity_section(self, parent):
        """Create the recent activity section"""
        activity_text = ttkb.Text(parent, height=15, wrap=tk.WORD)
        activity_text.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Sample activity log
        activity_log = """Organization completed successfully
Time: Today at 2:30 PM
Duration: 3.2 seconds

Files processed: 23
Files moved: 18
Files skipped: 5

Rule: Documents to Documents/
  → report_2025.pdf moved to C:\\Users\\Documents\\
  → manual.docx moved to C:\\Users\\Documents\\
  → invoice.pdf moved to C:\\Users\\Documents\\

Rule: Images to Pictures/
  → vacation.jpg moved to C:\\Users\\Pictures\\
  → screenshot.png moved to C:\\Users\\Pictures\\

Rule: Downloads Cleanup
  → archive.zip moved to C:\\Users\\Archives\\
  → backup.rar moved to C:\\Users\\Archives\\

Skipped files:
  → temp.tmp (no matching rule)
  → readme.txt (no matching rule)
  → install.exe (no matching rule)
  → config.ini (no matching rule)
  → data.log (no matching rule)

Organization completed at 2:30:17 PM"""
        
        activity_text.insert(tk.END, activity_log)
        activity_text.config(state=tk.DISABLED)
        
    def create_context_menu(self):
        """Create right-click context menu for rules"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit Rule...", command=self.edit_selected_rule)
        self.context_menu.add_command(label="Duplicate Rule", command=self.duplicate_rule)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Enable Rule", command=self.toggle_rule)
        self.context_menu.add_command(label="Disable Rule", command=self.toggle_rule)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Move Up")
        self.context_menu.add_command(label="Move Down")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Rule", command=self.delete_rule)
        
        self.rules_tree.bind("<Button-3>", self.show_context_menu)
        
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        status_bar = ttkb.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_bar.pack(fill=X, side=BOTTOM)
        
        # Status indicator
        ttkb.Label(status_bar, text="● Ready").pack(side=LEFT, padx=5)
        
        ttkb.Separator(status_bar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5)
        
        # Rules count
        active_count = sum(1 for rule in self.rules if rule["active"])
        ttkb.Label(status_bar, text=f"{active_count} rules active").pack(side=LEFT, padx=5)
        
        ttkb.Separator(status_bar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5)
        
        # Last run
        ttkb.Label(status_bar, text=f"Last run: {self.last_run}").pack(side=LEFT, padx=5)
        
        # Folder indicator
        ttkb.Label(status_bar, text="📁 Downloads").pack(side=RIGHT, padx=5)
        
    def populate_rules(self):
        """Populate the rules treeview"""
        for i, rule in enumerate(self.rules):
            active_text = "✓" if rule["active"] else "○"
            patterns_text = ", ".join(rule["patterns"])
            
            self.rules_tree.insert("", tk.END, values=(
                active_text,
                rule["name"],
                patterns_text,
                rule["destination"]
            ))
            
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.rules_tree.identify_row(event.y)
        if item:
            self.rules_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def edit_selected_rule(self):
        """Edit the selected rule"""
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a rule to edit.")
            return
            
        # Get the index of selected item
        item_index = self.rules_tree.index(selection[0])
        rule = self.rules[item_index]
        
        self.show_edit_dialog(rule, item_index)
        
    def show_edit_dialog(self, rule, index):
        """Show the rule editing dialog"""
        dialog = ttkb.Toplevel(self.root)
        dialog.title(f'Edit Rule: "{rule["name"]}"')
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Rule name
        ttkb.Label(dialog, text="Rule Name:", font=("", 10, "bold")).pack(anchor=W, padx=20, pady=(20, 5))
        name_var = tk.StringVar(value=rule["name"])
        name_entry = ttkb.Entry(dialog, textvariable=name_var, width=50)
        name_entry.pack(padx=20, pady=(0, 15), fill=X)
        
        # File patterns
        ttkb.Label(dialog, text="What files to match:", font=("", 10, "bold")).pack(anchor=W, padx=20, pady=(0, 5))
        
        patterns_frame = ttkb.LabelFrame(dialog, text="File Patterns", padding=10)
        patterns_frame.pack(fill=X, padx=20, pady=(0, 15))
        
        patterns_list = tk.Listbox(patterns_frame, height=4)
        patterns_list.pack(fill=X, pady=(0, 10))
        
        for pattern in rule["patterns"]:
            patterns_list.insert(tk.END, pattern)
            
        patterns_buttons = ttkb.Frame(patterns_frame)
        patterns_buttons.pack(fill=X)
        
        def add_pattern():
            pattern = tk.simpledialog.askstring("Add Pattern", "Enter file pattern (e.g., *.pdf):")
            if pattern:
                patterns_list.insert(tk.END, pattern)
                
        def remove_pattern():
            selection = patterns_list.curselection()
            if selection:
                patterns_list.delete(selection[0])
        
        ttkb.Button(patterns_buttons, text="Add Pattern", command=add_pattern).pack(side=LEFT, padx=(0, 5))
        ttkb.Button(patterns_buttons, text="Remove", command=remove_pattern).pack(side=LEFT)
        
        # Destination
        ttkb.Label(dialog, text="Where to move them:", font=("", 10, "bold")).pack(anchor=W, padx=20, pady=(0, 5))
        
        dest_frame = ttkb.Frame(dialog)
        dest_frame.pack(fill=X, padx=20, pady=(0, 15))
        
        dest_var = tk.StringVar(value=rule["destination"])
        dest_entry = ttkb.Entry(dest_frame, textvariable=dest_var)
        dest_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        def browse_destination():
            folder = filedialog.askdirectory(initialdir=dest_var.get())
            if folder:
                dest_var.set(folder)
                
        ttkb.Button(dest_frame, text="Browse...", command=browse_destination).pack(side=RIGHT)
        
        # Options
        ttkb.Label(dialog, text="Options:", font=("", 10, "bold")).pack(anchor=W, padx=20, pady=(0, 5))
        
        options_frame = ttkb.Frame(dialog)
        options_frame.pack(fill=X, padx=20, pady=(0, 20))
        
        active_var = tk.BooleanVar(value=rule["active"])
        ttkb.Checkbutton(options_frame, text="Rule is active", variable=active_var).pack(anchor=W)
        
        unzip_var = tk.BooleanVar(value=rule["unzip"])
        ttkb.Checkbutton(options_frame, text="Automatically unzip archives", variable=unzip_var).pack(anchor=W)
        
        # Buttons
        button_frame = ttkb.Frame(dialog)
        button_frame.pack(fill=X, padx=20, pady=(0, 20))
        
        def save_changes():
            # Update rule
            rule["name"] = name_var.get()
            rule["patterns"] = [patterns_list.get(i) for i in range(patterns_list.size())]
            rule["destination"] = dest_var.get()
            rule["active"] = active_var.get()
            rule["unzip"] = unzip_var.get()
            
            # Refresh display
            self.refresh_rules_display()
            dialog.destroy()
            
        ttkb.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=RIGHT, padx=(5, 0))
        ttkb.Button(button_frame, text="Save Changes", style="primary.TButton", command=save_changes).pack(side=RIGHT)
        
    def refresh_rules_display(self):
        """Refresh the rules display"""
        # Clear current items
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
            
        # Repopulate
        self.populate_rules()
        
    def add_rule(self):
        """Add a new rule"""
        new_rule = {
            "name": "New Rule",
            "patterns": ["*.*"],
            "destination": "C:\\Users\\NewFolder\\",
            "active": True,
            "unzip": False
        }
        self.rules.append(new_rule)
        self.show_edit_dialog(new_rule, len(self.rules) - 1)
        
    def duplicate_rule(self):
        """Duplicate the selected rule"""
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a rule to duplicate.")
            return
            
        item_index = self.rules_tree.index(selection[0])
        original_rule = self.rules[item_index]
        
        # Create duplicate
        new_rule = original_rule.copy()
        new_rule["name"] = f"{original_rule['name']} (Copy)"
        new_rule["patterns"] = original_rule["patterns"].copy()
        
        self.rules.append(new_rule)
        self.refresh_rules_display()
        
    def delete_rule(self):
        """Delete the selected rule"""
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a rule to delete.")
            return
            
        item_index = self.rules_tree.index(selection[0])
        rule_name = self.rules[item_index]["name"]
        
        if messagebox.askyesno("Confirm Delete", f'Are you sure you want to delete the rule "{rule_name}"?'):
            del self.rules[item_index]
            self.refresh_rules_display()
            
    def toggle_rule(self):
        """Toggle the active state of selected rule"""
        selection = self.rules_tree.selection()
        if not selection:
            return
            
        item_index = self.rules_tree.index(selection[0])
        self.rules[item_index]["active"] = not self.rules[item_index]["active"]
        self.refresh_rules_display()
        
    def enable_all_rules(self):
        """Enable all rules"""
        for rule in self.rules:
            rule["active"] = True
        self.refresh_rules_display()
        
    def disable_all_rules(self):
        """Disable all rules"""
        for rule in self.rules:
            rule["active"] = False
        self.refresh_rules_display()
        
    def start_organization(self):
        """Start the organization process"""
        active_rules = [rule for rule in self.rules if rule["active"]]
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
        progress_dialog.geometry("500x300")
        progress_dialog.transient(self.root)
        progress_dialog.grab_set()
        
        # Center dialog
        progress_dialog.update_idletasks()
        x = (progress_dialog.winfo_screenwidth() // 2) - (progress_dialog.winfo_width() // 2)
        y = (progress_dialog.winfo_screenheight() // 2) - (progress_dialog.winfo_height() // 2)
        progress_dialog.geometry(f"+{x}+{y}")
        
        ttkb.Label(progress_dialog, text="Organizing files...", font=("", 12, "bold")).pack(pady=20)
        
        progress = ttkb.Progressbar(progress_dialog, mode="determinate", length=400)
        progress.pack(pady=10)
        
        status_label = ttkb.Label(progress_dialog, text="Scanning files...")
        status_label.pack(pady=10)
        
        # Simulate progress
        def update_progress(value, text):
            progress['value'] = value
            status_label['text'] = text
            progress_dialog.update()
            
        import time
        
        def run_organization():
            steps = [
                (10, "Scanning files..."),
                (30, "Processing documents..."),
                (50, "Moving images..."),
                (70, "Handling archives..."),
                (90, "Cleaning up..."),
                (100, "Organization complete!")
            ]
            
            for value, text in steps:
                update_progress(value, text)
                time.sleep(0.5)
                
            time.sleep(1)
            progress_dialog.destroy()
            messagebox.showinfo("Complete", "File organization completed successfully!\n\n18 files moved\n5 files skipped")
            
        # Start in a separate thread (simplified for demo)
        self.root.after(100, run_organization)
        
    def test_rules(self):
        """Test rules without moving files"""
        messagebox.showinfo("Test Run", "Test run completed!\n\nWould move 18 files:\n• 8 documents\n• 6 images\n• 4 archives\n\nNo files were actually moved.")
        
    def browse_folder(self):
        """Browse for organization folder"""
        folder = filedialog.askdirectory(initialdir=self.organization_folder)
        if folder:
            self.organization_folder = folder
            
    def show_preferences(self):
        """Show preferences dialog"""
        prefs_dialog = ttkb.Toplevel(self.root)
        prefs_dialog.title("Preferences")
        prefs_dialog.geometry("400x300")
        prefs_dialog.transient(self.root)
        prefs_dialog.grab_set()
        
        # Center dialog
        prefs_dialog.update_idletasks()
        x = (prefs_dialog.winfo_screenwidth() // 2) - (prefs_dialog.winfo_width() // 2)
        y = (prefs_dialog.winfo_screenheight() // 2) - (prefs_dialog.winfo_height() // 2)
        prefs_dialog.geometry(f"+{x}+{y}")
        
        notebook = ttkb.Notebook(prefs_dialog)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # General tab
        general_frame = ttkb.Frame(notebook)
        notebook.add(general_frame, text="General")
        
        ttkb.Label(general_frame, text="Theme:", font=("", 10, "bold")).pack(anchor=W, padx=10, pady=(10, 5))
        theme_combo = ttkb.Combobox(general_frame, values=["flatly", "darkly", "cosmo", "litera"])
        theme_combo.pack(fill=X, padx=10, pady=(0, 15))
        theme_combo.set("flatly")
        
        ttkb.Label(general_frame, text="Startup Behavior:", font=("", 10, "bold")).pack(anchor=W, padx=10, pady=(0, 5))
        ttkb.Checkbutton(general_frame, text="Start minimized").pack(anchor=W, padx=20)
        ttkb.Checkbutton(general_frame, text="Check for updates on startup").pack(anchor=W, padx=20)
        
        # Rules tab
        rules_frame = ttkb.Frame(notebook)
        notebook.add(rules_frame, text="Rules")
        
        ttkb.Label(rules_frame, text="Default Behavior:", font=("", 10, "bold")).pack(anchor=W, padx=10, pady=(10, 5))
        ttkb.Checkbutton(rules_frame, text="Confirm before moving files").pack(anchor=W, padx=20)
        ttkb.Checkbutton(rules_frame, text="Create destination folders automatically").pack(anchor=W, padx=20)
        ttkb.Checkbutton(rules_frame, text="Skip files in use").pack(anchor=W, padx=20)
        
        # Advanced tab
        advanced_frame = ttkb.Frame(notebook)
        notebook.add(advanced_frame, text="Advanced")
        
        ttkb.Label(advanced_frame, text="Developer Options:", font=("", 10, "bold")).pack(anchor=W, padx=10, pady=(10, 5))
        ttkb.Checkbutton(advanced_frame, text="Enable developer mode").pack(anchor=W, padx=20)
        ttkb.Checkbutton(advanced_frame, text="Show debug information").pack(anchor=W, padx=20)
        
        # Buttons
        button_frame = ttkb.Frame(prefs_dialog)
        button_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        ttkb.Button(button_frame, text="Cancel", command=prefs_dialog.destroy).pack(side=RIGHT, padx=(5, 0))
        ttkb.Button(button_frame, text="Apply", style="primary.TButton", command=prefs_dialog.destroy).pack(side=RIGHT)

def main():
    """Run the prototype"""
    app = TaskMoverPrototype()
    
    # Bind keyboard shortcuts
    app.root.bind('<Control-n>', lambda e: app.add_rule())
    app.root.bind('<F5>', lambda e: app.start_organization())
    app.root.bind('<Delete>', lambda e: app.delete_rule())
    
    # Center window
    app.root.update_idletasks()
    x = (app.root.winfo_screenwidth() // 2) - (app.root.winfo_width() // 2)
    y = (app.root.winfo_screenheight() // 2) - (app.root.winfo_height() // 2)
    app.root.geometry(f"+{x}+{y}")
    
    app.root.mainloop()

if __name__ == "__main__":
    main()
