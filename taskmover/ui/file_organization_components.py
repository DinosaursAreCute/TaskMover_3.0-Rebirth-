"""
TaskMover UI Framework - File Organization Components
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Any, Optional, Callable, Tuple
import os
import time
from pathlib import Path
from .base_component import BaseComponent, ComponentState
from .input_components import TextInput, Button
from .display_components import Label, Badge, ProgressBar
from .layout_components import Panel
from .data_display_components import DataTable, TreeView


class OrganizationDashboard(BaseComponent):
    """
    Main dashboard for file organization operations.
    """
    
    def __init__(self, parent: tk.Widget,
                 on_organize: Optional[Callable] = None,
                 on_preview: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the organization dashboard.
        
        Args:
            parent: Parent widget
            on_organize: Callback for organization execution
            on_preview: Callback for organization preview
            **kwargs: Additional widget options
        """
        self.on_organize = on_organize
        self.on_preview = on_preview
        self._source_directory = ""
        self._selected_ruleset = None
        self._recent_activities = []
        
        super().__init__(parent, **kwargs)
        
        self._setup_dashboard()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the organization dashboard interface."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(header_frame, text="File Organization Dashboard",
                 font=('TkDefaultFont', 14, 'bold')).pack(side=tk.LEFT)
        
        return main_frame
    
    def _setup_dashboard(self):
        """Set up the dashboard interface."""
        # Main content area
        content_frame = ttk.Frame(self._widget)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Configuration
        config_frame = ttk.LabelFrame(content_frame, text="Configuration", padding=10)
        config_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        self._create_config_panel(config_frame)
        
        # Center panel - Actions
        actions_frame = ttk.LabelFrame(content_frame, text="Actions", padding=10)
        actions_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self._create_actions_panel(actions_frame)
        
        # Right panel - Recent Activity
        activity_frame = ttk.LabelFrame(content_frame, text="Recent Activity", padding=10)
        activity_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        self._create_activity_panel(activity_frame)
    
    def _create_config_panel(self, parent):
        """Create the configuration panel."""
        # Source directory selection
        ttk.Label(parent, text="Source Directory:",
                 font=('TkDefaultFont', 9, 'bold')).pack(anchor=tk.W)
        
        dir_frame = ttk.Frame(parent)
        dir_frame.pack(fill=tk.X, pady=(2, 10))
        
        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(dir_frame, textvariable=self.source_var, width=30)
        source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(dir_frame, text="Browse...",
                  command=self._browse_source_directory).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Ruleset selection
        ttk.Label(parent, text="Ruleset:",
                 font=('TkDefaultFont', 9, 'bold')).pack(anchor=tk.W, pady=(10, 2))
        
        self.ruleset_var = tk.StringVar()
        self.ruleset_combo = ttk.Combobox(parent, textvariable=self.ruleset_var,
                                         state="readonly", width=27)
        self.ruleset_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Quick filters
        filters_frame = ttk.LabelFrame(parent, text="Quick Filters", padding=5)
        filters_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.filter_vars = {}
        filters = [
            ('include_hidden', 'Include hidden files'),
            ('include_system', 'Include system files'),
            ('recursive', 'Include subdirectories')
        ]
        
        for key, text in filters:
            var = tk.BooleanVar(value=True if key == 'recursive' else False)
            self.filter_vars[key] = var
            ttk.Checkbutton(filters_frame, text=text, variable=var).pack(anchor=tk.W)
    
    def _create_actions_panel(self, parent):
        """Create the actions panel."""
        # Quick stats
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.stats_labels = {}
        stats = [
            ('total_files', 'Total Files', '0'),
            ('matching_files', 'Matching Files', '0'),
            ('target_dirs', 'Target Directories', '0')
        ]
        
        for i, (key, label, default) in enumerate(stats):
            stat_frame = ttk.Frame(stats_frame)
            stat_frame.grid(row=i//3, column=i%3, sticky=tk.W, padx=(0, 20), pady=2)
            
            ttk.Label(stat_frame, text=f"{label}:",
                     font=('TkDefaultFont', 8, 'bold')).pack(side=tk.LEFT)
            
            self.stats_labels[key] = ttk.Label(stat_frame, text=default,
                                              font=('TkDefaultFont', 8))
            self.stats_labels[key].pack(side=tk.LEFT, padx=(5, 0))
        
        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(expand=True)
        
        # Preview button
        self.preview_btn = ttk.Button(button_frame, text="Preview Organization",
                                     command=self._preview_organization,
                                     style='Accent.TButton')
        self.preview_btn.pack(pady=5, ipadx=20, ipady=10)
        
        # Execute button
        self.execute_btn = ttk.Button(button_frame, text="Execute Organization",
                                     command=self._execute_organization,
                                     state=tk.DISABLED)
        self.execute_btn.pack(pady=5, ipadx=20, ipady=10)
        
        # Separator
        ttk.Separator(button_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # Quick actions
        quick_frame = ttk.LabelFrame(button_frame, text="Quick Actions", padding=10)
        quick_frame.pack(fill=tk.X)
        
        quick_actions = [
            ("Scan Directory", self._scan_directory),
            ("Open File Explorer", self._open_explorer),
            ("View Organization History", self._view_history)
        ]
        
        for text, command in quick_actions:
            ttk.Button(quick_frame, text=text, command=command).pack(fill=tk.X, pady=2)
    
    def _create_activity_panel(self, parent):
        """Create the recent activity panel."""
        # Activity list
        self.activity_listbox = tk.Listbox(parent, height=15, width=25)
        activity_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL,
                                       command=self.activity_listbox.yview)
        self.activity_listbox.configure(yscrollcommand=activity_scroll.set)
        
        self.activity_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        activity_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate with sample activities
        self._populate_recent_activities()
        
        # Clear button
        ttk.Button(parent, text="Clear History",
                  command=self._clear_history).pack(fill=tk.X, pady=(10, 0))
    
    def _browse_source_directory(self):
        """Browse for source directory."""
        directory = filedialog.askdirectory(title="Select Source Directory")
        if directory:
            self.source_var.set(directory)
            self._source_directory = directory
            self._scan_directory()
    
    def _scan_directory(self):
        """Scan the source directory for files."""
        if not self._source_directory:
            return
        
        # *Logic placeholder*: Implement directory scanning
        # This would scan the directory and update statistics
        
        # Mock data for demonstration
        self.stats_labels['total_files'].config(text="1,234")
        self.stats_labels['matching_files'].config(text="856")
        self.stats_labels['target_dirs'].config(text="12")
    
    def _preview_organization(self):
        """Preview the organization operation."""
        if not self._validate_inputs():
            return
        
        # Enable execute button after preview
        self.execute_btn.config(state=tk.NORMAL)
        
        if self.on_preview:
            self.on_preview({
                'source_directory': self._source_directory,
                'ruleset': self.ruleset_var.get(),
                'filters': {k: v.get() for k, v in self.filter_vars.items()}
            })
        
        # Add to recent activities
        self._add_activity(f"Previewed organization of {os.path.basename(self._source_directory)}")
    
    def _execute_organization(self):
        """Execute the organization operation."""
        if not self._validate_inputs():
            return
        
        # Confirm execution
        result = messagebox.askyesno(
            "Confirm Organization",
            f"This will organize files in:\n{self._source_directory}\n\n"
            f"Using ruleset: {self.ruleset_var.get()}\n\n"
            "Are you sure you want to continue?"
        )
        
        if result:
            if self.on_organize:
                self.on_organize({
                    'source_directory': self._source_directory,
                    'ruleset': self.ruleset_var.get(),
                    'filters': {k: v.get() for k, v in self.filter_vars.items()}
                })
            
            # Add to recent activities
            self._add_activity(f"Organized {os.path.basename(self._source_directory)}")
    
    def _validate_inputs(self) -> bool:
        """Validate the input configuration."""
        if not self._source_directory or not os.path.exists(self._source_directory):
            messagebox.showerror("Invalid Directory", "Please select a valid source directory.")
            return False
        
        if not self.ruleset_var.get():
            messagebox.showerror("No Ruleset", "Please select a ruleset.")
            return False
        
        return True
    
    def _open_explorer(self):
        """Open file explorer for the source directory."""
        if self._source_directory and os.path.exists(self._source_directory):
            os.startfile(self._source_directory)
        else:
            messagebox.showwarning("No Directory", "Please select a source directory first.")
    
    def _view_history(self):
        """View organization history."""
        # *Logic placeholder*: Open history viewer
        messagebox.showinfo("History", "Organization history viewer will open here.")
    
    def _populate_recent_activities(self):
        """Populate recent activities list."""
        # Sample activities
        activities = [
            "Organized Downloads folder",
            "Previewed Documents organization",
            "Executed Photos ruleset",
            "Scanned Desktop directory",
            "Created new ruleset: Media Files"
        ]
        
        for activity in activities:
            self.activity_listbox.insert(tk.END, activity)
    
    def _add_activity(self, activity: str):
        """Add an activity to the recent list."""
        self.activity_listbox.insert(0, activity)
        
        # Keep only last 20 activities
        if self.activity_listbox.size() > 20:
            self.activity_listbox.delete(tk.END)
    
    def _clear_history(self):
        """Clear the activity history."""
        self.activity_listbox.delete(0, tk.END)
    
    def update_rulesets(self, rulesets: List[Dict]):
        """Update available rulesets."""
        ruleset_names = [rs.get('name', 'Unnamed') for rs in rulesets]
        self.ruleset_combo['values'] = ruleset_names
    
    def set_source_directory(self, directory: str):
        """Set the source directory."""
        self._source_directory = directory
        self.source_var.set(directory)
        self._scan_directory()


class FileExplorer(BaseComponent):
    """
    File explorer for browsing and selecting files.
    """
    
    def __init__(self, parent: tk.Widget,
                 root_directory: Optional[str] = None,
                 on_file_select: Optional[Callable] = None,
                 on_directory_change: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the file explorer.
        
        Args:
            parent: Parent widget
            root_directory: Root directory to start browsing from
            on_file_select: Callback when file is selected
            on_directory_change: Callback when directory changes
            **kwargs: Additional widget options
        """
        self.root_directory = root_directory or str(Path.home())
        self.on_file_select = on_file_select
        self.on_directory_change = on_directory_change
        self._current_directory = self.root_directory
        self._selected_files = set()
        
        super().__init__(parent, **kwargs)
        
        self._setup_explorer()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the file explorer interface."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        
        # Toolbar
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Navigation buttons
        ttk.Button(toolbar_frame, text="⬅", width=3,
                  command=self._go_back).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar_frame, text="⬆", width=3,
                  command=self._go_up).pack(side=tk.LEFT, padx=(0, 5))
        
        # Current path
        self.path_var = tk.StringVar(value=self._current_directory)
        path_entry = ttk.Entry(toolbar_frame, textvariable=self.path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        path_entry.bind('<Return>', self._navigate_to_path)
        
        # Refresh button
        ttk.Button(toolbar_frame, text="🔄", width=3,
                  command=self._refresh).pack(side=tk.RIGHT)
        
        return main_frame
    
    def _setup_explorer(self):
        """Set up the explorer interface."""
        # Content area
        content_frame = ttk.Frame(self._widget)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Left panel - Directory tree
        tree_frame = ttk.LabelFrame(content_frame, text="Directories", padding=5)
        tree_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Directory tree
        self.dir_tree = ttk.Treeview(tree_frame, show='tree')
        self.dir_tree.configure(height=15)  # Set height instead of width
        dir_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                  command=self.dir_tree.yview)
        self.dir_tree.configure(yscrollcommand=dir_scroll.set)
        
        self.dir_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dir_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.dir_tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        
        # Right panel - File list
        file_frame = ttk.LabelFrame(content_frame, text="Files", padding=5)
        file_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # File list with details
        columns = ('name', 'size', 'modified', 'type')
        self.file_tree = ttk.Treeview(file_frame, columns=columns, show='headings')
        
        # Configure columns
        self.file_tree.heading('name', text='Name')
        self.file_tree.heading('size', text='Size')
        self.file_tree.heading('modified', text='Modified')
        self.file_tree.heading('type', text='Type')
        
        self.file_tree.column('name', width=200)
        self.file_tree.column('size', width=80)
        self.file_tree.column('modified', width=120)
        self.file_tree.column('type', width=80)
        
        file_scroll = ttk.Scrollbar(file_frame, orient=tk.VERTICAL,
                                   command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scroll.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_tree.bind('<<TreeviewSelect>>', self._on_file_select)
        self.file_tree.bind('<Double-1>', self._on_file_double_click)
        
        # Status bar
        status_frame = ttk.Frame(self._widget)
        status_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        self.selection_label = ttk.Label(status_frame, text="")
        self.selection_label.pack(side=tk.RIGHT)
        
        # Initialize
        self._populate_directory_tree()
        self._populate_file_list()
    
    def _populate_directory_tree(self):
        """Populate the directory tree."""
        # Clear existing items
        self.dir_tree.delete(*self.dir_tree.get_children())
        
        # Add root directory
        root_id = self.dir_tree.insert('', 'end', text=os.path.basename(self.root_directory),
                                      values=[self.root_directory], open=True)
        
        # Add subdirectories
        self._add_directory_children(root_id, self.root_directory)
        
        # Expand to current directory
        self._expand_to_current()
    
    def _add_directory_children(self, parent_id: str, directory: str):
        """Add child directories to tree item."""
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    child_id = self.dir_tree.insert(parent_id, 'end', text=item,
                                                   values=[item_path])
                    
                    # Check if this directory has subdirectories
                    try:
                        has_subdirs = any(os.path.isdir(os.path.join(item_path, sub))
                                        for sub in os.listdir(item_path)
                                        if not sub.startswith('.'))
                        if has_subdirs:
                            # Add placeholder for expansion
                            self.dir_tree.insert(child_id, 'end', text='...')
                    except (PermissionError, OSError):
                        pass
        except (PermissionError, OSError):
            pass
    
    def _expand_to_current(self):
        """Expand tree to show current directory."""
        # *Logic placeholder*: Implement tree expansion to current directory
        pass
    
    def _populate_file_list(self):
        """Populate the file list for current directory."""
        # Clear existing items
        self.file_tree.delete(*self.file_tree.get_children())
        
        try:
            items = []
            for item in os.listdir(self._current_directory):
                item_path = os.path.join(self._current_directory, item)
                
                if os.path.isfile(item_path):
                    # Get file information
                    stat = os.stat(item_path)
                    size = self._format_file_size(stat.st_size)
                    modified = self._format_date(stat.st_mtime)
                    file_type = os.path.splitext(item)[1][1:].upper() or 'File'
                    
                    items.append((item, size, modified, file_type, item_path))
            
            # Sort by name
            items.sort(key=lambda x: x[0].lower())
            
            # Add to tree
            for name, size, modified, file_type, path in items:
                self.file_tree.insert('', 'end', values=(name, size, modified, file_type),
                                     tags=[path])
            
            # Update status
            file_count = len(items)
            self.status_label.config(text=f"{file_count} files")
            
        except (PermissionError, OSError) as e:
            self.status_label.config(text=f"Error: {e}")
    
    def _format_file_size(self, size: int) -> str:
        """Format file size in human readable format."""
        size_float = float(size)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_float < 1024:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024
        return f"{size_float:.1f} TB"
    
    def _format_date(self, timestamp: float) -> str:
        """Format timestamp as date string."""
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M')
    
    def _on_tree_select(self, event):
        """Handle directory tree selection."""
        selection = self.dir_tree.selection()
        if selection:
            item = selection[0]
            values = self.dir_tree.item(item, 'values')
            if values:
                directory = values[0]
                self._navigate_to_directory(directory)
    
    def _on_file_select(self, event):
        """Handle file selection."""
        selection = self.file_tree.selection()
        self._selected_files = set()
        
        for item in selection:
            tags = self.file_tree.item(item, 'tags')
            if tags:
                self._selected_files.add(tags[0])
        
        # Update selection display
        count = len(self._selected_files)
        if count == 0:
            self.selection_label.config(text="")
        elif count == 1:
            self.selection_label.config(text="1 file selected")
        else:
            self.selection_label.config(text=f"{count} files selected")
        
        # Notify callback
        if self.on_file_select and self._selected_files:
            self.on_file_select(list(self._selected_files))
    
    def _on_file_double_click(self, event):
        """Handle file double-click."""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            tags = self.file_tree.item(item, 'tags')
            if tags:
                file_path = tags[0]
                # *Logic placeholder*: Open file with default application
                os.startfile(file_path)
    
    def _navigate_to_directory(self, directory: str):
        """Navigate to a specific directory."""
        if os.path.exists(directory) and os.path.isdir(directory):
            self._current_directory = directory
            self.path_var.set(directory)
            self._populate_file_list()
            
            if self.on_directory_change:
                self.on_directory_change(directory)
    
    def _navigate_to_path(self, event):
        """Navigate to path entered in path bar."""
        path = self.path_var.get()
        self._navigate_to_directory(path)
    
    def _go_back(self):
        """Go back to previous directory."""
        # *Logic placeholder*: Implement navigation history
        pass
    
    def _go_up(self):
        """Go up one directory level."""
        parent = os.path.dirname(self._current_directory)
        if parent != self._current_directory:
            self._navigate_to_directory(parent)
    
    def _refresh(self):
        """Refresh the current view."""
        self._populate_file_list()
        self._populate_directory_tree()
    
    def get_selected_files(self) -> List[str]:
        """Get list of selected files."""
        return list(self._selected_files)
    
    def set_directory(self, directory: str):
        """Set the current directory."""
        self._navigate_to_directory(directory)


class OrganizationPreview(BaseComponent):
    """
    Preview of file organization operations before execution.
    """
    
    def __init__(self, parent: tk.Widget,
                 preview_data: Optional[Dict] = None,
                 on_execute: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the organization preview.
        
        Args:
            parent: Parent widget
            preview_data: Preview operation data
            on_execute: Callback to execute the organization
            **kwargs: Additional widget options
        """
        self.preview_data = preview_data or {}
        self.on_execute = on_execute
        self._conflicts = []
        self._summary_stats = {}
        
        super().__init__(parent, **kwargs)
        
        self._setup_preview()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the preview interface."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        
        # Header with actions
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(header_frame, text="Organization Preview",
                 font=('TkDefaultFont', 12, 'bold')).pack(side=tk.LEFT)
        
        # Action buttons
        actions_frame = ttk.Frame(header_frame)
        actions_frame.pack(side=tk.RIGHT)
        
        ttk.Button(actions_frame, text="Refresh Preview",
                  command=self._refresh_preview).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Execute Organization",
                  command=self._execute_organization,
                  style='Accent.TButton').pack(side=tk.LEFT)
        
        return main_frame
    
    def _setup_preview(self):
        """Set up the preview interface."""
        # Summary frame
        summary_frame = ttk.LabelFrame(self._widget, text="Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self._create_summary_section(summary_frame)
        
        # Content notebook
        self.notebook = ttk.Notebook(self._widget)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # File operations tab
        self._create_operations_tab()
        
        # Conflicts tab
        self._create_conflicts_tab()
        
        # Impact analysis tab
        self._create_impact_tab()
        
        # Load preview data
        self._load_preview_data()
    
    def _create_summary_section(self, parent):
        """Create the summary section."""
        # Statistics grid
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X)
        
        self.summary_labels = {}
        stats = [
            ('total_files', 'Total Files'),
            ('files_to_move', 'Files to Move'),
            ('new_directories', 'New Directories'),
            ('conflicts', 'Conflicts'),
            ('errors', 'Errors'),
            ('disk_space', 'Disk Space Used')
        ]
        
        for i, (key, label) in enumerate(stats):
            row = i // 3
            col = i % 3
            
            stat_frame = ttk.Frame(stats_frame)
            stat_frame.grid(row=row, column=col, sticky=tk.W, padx=(0, 20), pady=2)
            
            ttk.Label(stat_frame, text=f"{label}:",
                     font=('TkDefaultFont', 8, 'bold')).pack(side=tk.LEFT)
            
            self.summary_labels[key] = ttk.Label(stat_frame, text="0",
                                                font=('TkDefaultFont', 8))
            self.summary_labels[key].pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_operations_tab(self):
        """Create the file operations tab."""
        operations_frame = ttk.Frame(self.notebook)
        self.notebook.add(operations_frame, text="File Operations")
        
        # Operations tree
        columns = ('source', 'destination', 'action', 'rule')
        self.operations_tree = ttk.Treeview(operations_frame, columns=columns,
                                           show='headings', height=15)
        
        # Configure columns
        self.operations_tree.heading('source', text='Source')
        self.operations_tree.heading('destination', text='Destination')
        self.operations_tree.heading('action', text='Action')
        self.operations_tree.heading('rule', text='Rule')
        
        self.operations_tree.column('source', width=250)
        self.operations_tree.column('destination', width=250)
        self.operations_tree.column('action', width=80)
        self.operations_tree.column('rule', width=150)
        
        # Scrollbars
        ops_v_scroll = ttk.Scrollbar(operations_frame, orient=tk.VERTICAL,
                                    command=self.operations_tree.yview)
        ops_h_scroll = ttk.Scrollbar(operations_frame, orient=tk.HORIZONTAL,
                                    command=self.operations_tree.xview)
        
        self.operations_tree.configure(yscrollcommand=ops_v_scroll.set,
                                      xscrollcommand=ops_h_scroll.set)
        
        # Pack widgets
        self.operations_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ops_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        ops_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_conflicts_tab(self):
        """Create the conflicts tab."""
        conflicts_frame = ttk.Frame(self.notebook)
        self.notebook.add(conflicts_frame, text="Conflicts")
        
        # Conflicts tree
        columns = ('file', 'conflict_type', 'existing_file', 'resolution')
        self.conflicts_tree = ttk.Treeview(conflicts_frame, columns=columns,
                                          show='headings', height=15)
        
        # Configure columns
        self.conflicts_tree.heading('file', text='File')
        self.conflicts_tree.heading('conflict_type', text='Conflict Type')
        self.conflicts_tree.heading('existing_file', text='Existing File')
        self.conflicts_tree.heading('resolution', text='Resolution')
        
        self.conflicts_tree.column('file', width=200)
        self.conflicts_tree.column('conflict_type', width=120)
        self.conflicts_tree.column('existing_file', width=200)
        self.conflicts_tree.column('resolution', width=120)
        
        # Scrollbars
        conf_v_scroll = ttk.Scrollbar(conflicts_frame, orient=tk.VERTICAL,
                                     command=self.conflicts_tree.yview)
        conf_h_scroll = ttk.Scrollbar(conflicts_frame, orient=tk.HORIZONTAL,
                                     command=self.conflicts_tree.xview)
        
        self.conflicts_tree.configure(yscrollcommand=conf_v_scroll.set,
                                     xscrollcommand=conf_h_scroll.set)
        
        # Pack widgets
        self.conflicts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        conf_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        conf_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Resolution controls
        resolution_frame = ttk.Frame(conflicts_frame)
        resolution_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(resolution_frame, text="Resolve Selected",
                  command=self._resolve_conflicts).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(resolution_frame, text="Resolve All",
                  command=self._resolve_all_conflicts).pack(side=tk.LEFT)
    
    def _create_impact_tab(self):
        """Create the impact analysis tab."""
        impact_frame = ttk.Frame(self.notebook)
        self.notebook.add(impact_frame, text="Impact Analysis")
        
        # Directory structure changes
        structure_frame = ttk.LabelFrame(impact_frame, text="Directory Structure Changes", padding=10)
        structure_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Before/After comparison
        comparison_frame = ttk.Frame(structure_frame)
        comparison_frame.pack(fill=tk.BOTH, expand=True)
        
        # Before
        before_frame = ttk.LabelFrame(comparison_frame, text="Before", padding=5)
        before_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.before_tree = ttk.Treeview(before_frame, show='tree')
        before_scroll = ttk.Scrollbar(before_frame, orient=tk.VERTICAL,
                                     command=self.before_tree.yview)
        self.before_tree.configure(yscrollcommand=before_scroll.set)
        
        self.before_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        before_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # After
        after_frame = ttk.LabelFrame(comparison_frame, text="After", padding=5)
        after_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.after_tree = ttk.Treeview(after_frame, show='tree')
        after_scroll = ttk.Scrollbar(after_frame, orient=tk.VERTICAL,
                                    command=self.after_tree.yview)
        self.after_tree.configure(yscrollcommand=after_scroll.set)
        
        self.after_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        after_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Risk assessment
        risk_frame = ttk.LabelFrame(impact_frame, text="Risk Assessment", padding=10)
        risk_frame.pack(fill=tk.X)
        
        self.risk_text = tk.Text(risk_frame, height=4, wrap=tk.WORD)
        risk_scroll = ttk.Scrollbar(risk_frame, orient=tk.VERTICAL,
                                   command=self.risk_text.yview)
        self.risk_text.configure(yscrollcommand=risk_scroll.set)
        
        self.risk_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        risk_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _load_preview_data(self):
        """Load and display preview data."""
        if not self.preview_data:
            return
        
        # Update summary
        self._update_summary()
        
        # Load operations
        self._load_operations()
        
        # Load conflicts
        self._load_conflicts()
        
        # Load impact analysis
        self._load_impact_analysis()
    
    def _update_summary(self):
        """Update the summary statistics."""
        # *Logic placeholder*: Calculate summary statistics from preview data
        
        # Mock data for demonstration
        summary = {
            'total_files': 1234,
            'files_to_move': 856,
            'new_directories': 12,
            'conflicts': 3,
            'errors': 0,
            'disk_space': '2.3 GB'
        }
        
        for key, value in summary.items():
            if key in self.summary_labels:
                self.summary_labels[key].config(text=str(value))
    
    def _load_operations(self):
        """Load file operations into the tree."""
        # *Logic placeholder*: Load actual operation data
        
        # Mock data for demonstration
        operations = [
            ('C:\\Downloads\\photo1.jpg', 'C:\\Photos\\2023\\photo1.jpg', 'Move', 'Photo Rule'),
            ('C:\\Downloads\\document.pdf', 'C:\\Documents\\PDF\\document.pdf', 'Move', 'Document Rule'),
            ('C:\\Downloads\\music.mp3', 'C:\\Music\\2023\\music.mp3', 'Move', 'Music Rule')
        ]
        
        for source, dest, action, rule in operations:
            self.operations_tree.insert('', 'end', values=(source, dest, action, rule))
    
    def _load_conflicts(self):
        """Load conflicts into the tree."""
        # *Logic placeholder*: Load actual conflict data
        
        # Mock data for demonstration
        conflicts = [
            ('photo1.jpg', 'File exists', 'C:\\Photos\\2023\\photo1.jpg', 'Prompt'),
            ('document.pdf', 'File exists', 'C:\\Documents\\document.pdf', 'Rename'),
        ]
        
        for file, conflict_type, existing, resolution in conflicts:
            self.conflicts_tree.insert('', 'end', values=(file, conflict_type, existing, resolution))
    
    def _load_impact_analysis(self):
        """Load impact analysis data."""
        # *Logic placeholder*: Generate before/after directory structures
        
        # Mock before structure
        self.before_tree.insert('', 'end', 'downloads', text='Downloads', open=True)
        self.before_tree.insert('downloads', 'end', text='photo1.jpg')
        self.before_tree.insert('downloads', 'end', text='document.pdf')
        self.before_tree.insert('downloads', 'end', text='music.mp3')
        
        # Mock after structure
        photos_id = self.after_tree.insert('', 'end', text='Photos', open=True)
        docs_id = self.after_tree.insert('', 'end', text='Documents', open=True)
        music_id = self.after_tree.insert('', 'end', text='Music', open=True)
        
        photos_2023 = self.after_tree.insert(photos_id, 'end', text='2023', open=True)
        self.after_tree.insert(photos_2023, 'end', text='photo1.jpg')
        
        pdf_folder = self.after_tree.insert(docs_id, 'end', text='PDF', open=True)
        self.after_tree.insert(pdf_folder, 'end', text='document.pdf')
        
        music_2023 = self.after_tree.insert(music_id, 'end', text='2023', open=True)
        self.after_tree.insert(music_2023, 'end', text='music.mp3')
        
        # Risk assessment
        risk_text = (
            "Risk Assessment:\n"
            "• Low risk operation - no system files affected\n"
            "• 3 file conflicts require attention\n"
            "• Backup recommended before execution\n"
            "• Estimated completion time: 2 minutes"
        )
        self.risk_text.insert(1.0, risk_text)
    
    def _refresh_preview(self):
        """Refresh the preview data."""
        # *Logic placeholder*: Regenerate preview data
        messagebox.showinfo("Refresh", "Preview data refreshed.")
    
    def _execute_organization(self):
        """Execute the organization operation."""
        if self.on_execute:
            self.on_execute(self.preview_data)
    
    def _resolve_conflicts(self):
        """Resolve selected conflicts."""
        # *Logic placeholder*: Implement conflict resolution
        messagebox.showinfo("Resolve", "Conflict resolution dialog will open here.")
    
    def _resolve_all_conflicts(self):
        """Resolve all conflicts automatically."""
        # *Logic placeholder*: Implement automatic conflict resolution
        messagebox.showinfo("Resolve All", "All conflicts resolved automatically.")
    
    def update_preview_data(self, data: Dict):
        """Update the preview data."""
        self.preview_data = data
        self._load_preview_data()


class ExecutionMonitor(BaseComponent):
    """
    Real-time monitoring of organization execution.
    """
    
    def __init__(self, parent: tk.Widget,
                 on_pause: Optional[Callable] = None,
                 on_stop: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the execution monitor.
        
        Args:
            parent: Parent widget
            on_pause: Callback to pause execution
            on_stop: Callback to stop execution
            **kwargs: Additional widget options
        """
        self.on_pause = on_pause
        self.on_stop = on_stop
        self._execution_state = 'stopped'
        self._start_time = None
        self._current_operation = ""
        self._progress_data = {}
        
        super().__init__(parent, **kwargs)
        
        self._setup_monitor()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the execution monitor interface."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        
        # Header with controls
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(header_frame, text="Execution Monitor",
                 font=('TkDefaultFont', 12, 'bold')).pack(side=tk.LEFT)
        
        # Control buttons
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT)
        
        self.pause_btn = ttk.Button(controls_frame, text="Pause",
                                   command=self._pause_execution)
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(controls_frame, text="Stop",
                                  command=self._stop_execution)
        self.stop_btn.pack(side=tk.LEFT)
        
        return main_frame
    
    def _setup_monitor(self):
        """Set up the monitor interface."""
        # Progress section
        progress_frame = ttk.LabelFrame(self._widget, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Overall progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           mode='determinate', length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to start...")
        self.progress_label.pack(anchor=tk.W)
        
        # Current operation
        self.operation_label = ttk.Label(progress_frame, text="",
                                        font=('TkDefaultFont', 8))
        self.operation_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Statistics
        stats_frame = ttk.LabelFrame(self._widget, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create statistics grid
        self.stats_labels = {}
        stats_layout = [
            [('processed', 'Processed'), ('remaining', 'Remaining'), ('rate', 'Rate')],
            [('elapsed', 'Elapsed'), ('estimated', 'Estimated'), ('errors', 'Errors')]
        ]
        
        for row_idx, row in enumerate(stats_layout):
            row_frame = ttk.Frame(stats_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            for col_idx, (key, label) in enumerate(row):
                stat_frame = ttk.Frame(row_frame)
                stat_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                ttk.Label(stat_frame, text=f"{label}:",
                         font=('TkDefaultFont', 8, 'bold')).pack(side=tk.LEFT)
                
                self.stats_labels[key] = ttk.Label(stat_frame, text="0",
                                                  font=('TkDefaultFont', 8))
                self.stats_labels[key].pack(side=tk.LEFT, padx=(5, 20))
        
        # Operation queue
        queue_frame = ttk.LabelFrame(self._widget, text="Operation Queue", padding=5)
        queue_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Queue list
        columns = ('operation', 'file', 'status')
        self.queue_tree = ttk.Treeview(queue_frame, columns=columns,
                                      show='headings', height=8)
        
        # Configure columns
        self.queue_tree.heading('operation', text='Operation')
        self.queue_tree.heading('file', text='File')
        self.queue_tree.heading('status', text='Status')
        
        self.queue_tree.column('operation', width=100)
        self.queue_tree.column('file', width=300)
        self.queue_tree.column('status', width=100)
        
        # Scrollbar
        queue_scroll = ttk.Scrollbar(queue_frame, orient=tk.VERTICAL,
                                    command=self.queue_tree.yview)
        self.queue_tree.configure(yscrollcommand=queue_scroll.set)
        
        self.queue_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        queue_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Log section
        log_frame = ttk.LabelFrame(self._widget, text="Execution Log", padding=5)
        log_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Log text
        self.log_text = tk.Text(log_frame, height=6, wrap=tk.WORD,
                               font=('Courier', 8))
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL,
                                  command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def start_execution(self, operations: List[Dict]):
        """Start monitoring execution."""
        self._execution_state = 'running'
        self._start_time = time.time()
        
        # Populate operation queue
        self._populate_queue(operations)
        
        # Update UI state
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        
        self._add_log("Execution started")
    
    def _populate_queue(self, operations: List[Dict]):
        """Populate the operation queue."""
        # Clear existing items
        self.queue_tree.delete(*self.queue_tree.get_children())
        
        # Add operations
        for op in operations:
            operation = op.get('action', 'Move')
            file_path = op.get('source', '')
            status = op.get('status', 'Pending')
            
            self.queue_tree.insert('', 'end', values=(operation, file_path, status))
    
    def update_progress(self, progress_data: Dict):
        """Update progress information."""
        self._progress_data.update(progress_data)
        
        # Update progress bar
        progress = progress_data.get('progress', 0)
        self.progress_var.set(progress)
        
        # Update labels
        self.progress_label.config(text=f"Progress: {progress:.1f}%")
        
        current_op = progress_data.get('current_operation', '')
        if current_op:
            self.operation_label.config(text=f"Current: {current_op}")
        
        # Update statistics
        for key in ['processed', 'remaining', 'rate', 'elapsed', 'estimated', 'errors']:
            if key in progress_data and key in self.stats_labels:
                value = progress_data[key]
                if key in ['elapsed', 'estimated']:
                    # Format time
                    if isinstance(value, (int, float)):
                        minutes, seconds = divmod(int(value), 60)
                        hours, minutes = divmod(minutes, 60)
                        value = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                elif key == 'rate':
                    value = f"{value} files/sec"
                
                self.stats_labels[key].config(text=str(value))
    
    def update_operation_status(self, operation_id: str, status: str):
        """Update the status of a specific operation."""
        # Find and update the operation in the queue
        for item in self.queue_tree.get_children():
            # *Logic placeholder*: Match operation by ID and update status
            pass
    
    def _add_log(self, message: str, level: str = 'info'):
        """Add a message to the execution log."""
        import datetime
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level.upper()}: {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def _pause_execution(self):
        """Pause execution."""
        if self._execution_state == 'running':
            self._execution_state = 'paused'
            self.pause_btn.config(text="Resume")
            self._add_log("Execution paused")
            
            if self.on_pause:
                self.on_pause()
        else:
            self._execution_state = 'running'
            self.pause_btn.config(text="Pause")
            self._add_log("Execution resumed")
    
    def _stop_execution(self):
        """Stop execution."""
        self._execution_state = 'stopped'
        
        # Update UI state
        self.pause_btn.config(state=tk.DISABLED, text="Pause")
        self.stop_btn.config(state=tk.DISABLED)
        
        self._add_log("Execution stopped")
        
        if self.on_stop:
            self.on_stop()
    
    def add_log_message(self, message: str, level: str = 'info'):
        """Add a message to the log."""
        self._add_log(message, level)
    
    def get_execution_state(self) -> str:
        """Get the current execution state."""
        return self._execution_state
