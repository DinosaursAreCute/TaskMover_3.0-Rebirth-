"""
Execution Components
===================

Components for executing file organization operations with
progress tracking, preview capabilities, and real-time status updates.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox 
from typing import Dict, Optional, Any, List, Callable
import threading
import time
from pathlib import Path
from .base_component import BaseComponent, ModernButton, ModernCard
from .theme_manager import get_theme_manager
from .dialog_components import ProgressDialog, ConfirmationDialog, ConflictResolutionDialog
from .input_components import ModernEntry, ModernCombobox


class DirectorySelector(BaseComponent):
    """Component for selecting source and target directories."""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.source_path = tk.StringVar()
        self.target_path = tk.StringVar()
        self.callbacks: Dict[str, List[Callable]] = {"path_changed": []}
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create directory selector component."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main frame
        self.configure(bg=tokens.colors["background"])
        
        # Title
        title_label = tk.Label(
            self,
            text="Directory Selection",
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_2"]), "normal"),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        title_label.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        # Source directory
        source_frame = tk.Frame(self, bg=tokens.colors["background"])
        source_frame.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        tk.Label(
            source_frame,
            text="Source Directory:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), "normal"),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        source_input_frame = tk.Frame(source_frame, bg=tokens.colors["background"])
        source_input_frame.pack(fill="x")
        
        self.source_entry = ModernEntry(
            source_input_frame,
            textvariable=self.source_path,
            placeholder="Select source directory..."
        )
        self.source_entry.pack(side="left", fill="x", expand=True, padx=(0, tokens.spacing["sm"]))
        
        source_browse_btn = ModernButton(
            source_input_frame,
            text="Browse",
            command=self._browse_source,
            variant="secondary",
            width=80
        )
        source_browse_btn.pack(side="right")
        
        # Target directory
        target_frame = tk.Frame(self, bg=tokens.colors["background"])
        target_frame.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        tk.Label(
            target_frame,
            text="Target Directory:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), "normal"),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        target_input_frame = tk.Frame(target_frame, bg=tokens.colors["background"])
        target_input_frame.pack(fill="x")
        
        self.target_entry = ModernEntry(
            target_input_frame,
            textvariable=self.target_path,
            placeholder="Select target directory..."
        )
        self.target_entry.pack(side="left", fill="x", expand=True, padx=(0, tokens.spacing["sm"]))
        
        target_browse_btn = ModernButton(
            target_input_frame,
            text="Browse",
            command=self._browse_target,
            variant="secondary",
            width=80
        )
        target_browse_btn.pack(side="right")
        
        # Bind change events
        self.source_path.trace_add("write", self._on_path_changed)
        self.target_path.trace_add("write", self._on_path_changed)
    
    def _browse_source(self):
        """Browse for source directory."""
        directory = filedialog.askdirectory(
            title="Select Source Directory",
            initialdir=self.source_path.get() or "."
        )
        if directory:
            self.source_path.set(directory)
    
    def _browse_target(self):
        """Browse for target directory."""
        directory = filedialog.askdirectory(
            title="Select Target Directory", 
            initialdir=self.target_path.get() or "."
        )
        if directory:
            self.target_path.set(directory)
    
    def _on_path_changed(self, *args):
        """Handle path change."""
        for callback in self.callbacks["path_changed"]:
            callback()
    
    def add_callback(self, event: str, callback: Callable):
        """Add callback for events."""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def get_source_path(self) -> str:
        """Get source directory path."""
        return self.source_path.get()
    
    def get_target_path(self) -> str:
        """Get target directory path."""
        return self.target_path.get()
    
    def validate_paths(self) -> Dict[str, str]:
        """Validate selected paths."""
        errors = {}
        
        source = self.get_source_path()
        target = self.get_target_path()
        
        if not source:
            errors["source"] = "Source directory is required"
        elif not Path(source).exists():
            errors["source"] = "Source directory does not exist"
        elif not Path(source).is_dir():
            errors["source"] = "Source path is not a directory"
        
        if not target:
            errors["target"] = "Target directory is required"
        elif not Path(target).exists():
            errors["target"] = "Target directory does not exist"
        elif not Path(target).is_dir():
            errors["target"] = "Target path is not a directory"
        
        if source and target and Path(source).resolve() == Path(target).resolve():
            errors["general"] = "Source and target directories cannot be the same"
        
        return errors


class RulesetSelector(BaseComponent):
    """Component for selecting and configuring rulesets."""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.selected_ruleset = tk.StringVar()
        self.available_rulesets = [
            "Default Organization",
            "Media Files", 
            "Documents by Type",
            "Downloads Cleanup",
            "Development Projects"
        ]
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create ruleset selector component."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main frame
        self.configure(bg=tokens.colors["background"])
        
        # Title
        title_label = tk.Label(
            self,
            text="Ruleset Selection",
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_2"]), "normal"),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        title_label.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        # Ruleset selection
        selection_frame = tk.Frame(self, bg=tokens.colors["background"])
        selection_frame.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        tk.Label(
            selection_frame,
            text="Choose Ruleset:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), "normal"),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        self.ruleset_combo = ModernCombobox(
            selection_frame,
            textvariable=self.selected_ruleset,
            values=self.available_rulesets,
            state="readonly"
        )
        self.ruleset_combo.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        # Set default selection
        if self.available_rulesets:
            self.selected_ruleset.set(self.available_rulesets[0])
        
        # Ruleset description
        self.description_label = tk.Label(
            self,
            text=self._get_ruleset_description(),
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), "normal"),
            bg=tokens.colors["background"],
            fg=tokens.colors["text_secondary"],
            wraplength=400,
            justify="left"
        )
        self.description_label.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        # Bind selection change
        self.selected_ruleset.trace_add("write", self._on_ruleset_changed)
    
    def _get_ruleset_description(self) -> str:
        """Get description for selected ruleset."""
        descriptions = {
            "Default Organization": "General purpose file organization based on file types and common patterns.",
            "Media Files": "Specialized organization for photos, videos, and audio files with metadata-based sorting.",
            "Documents by Type": "Organizes documents by file type and content analysis.",
            "Downloads Cleanup": "Cleans up downloads folder with intelligent duplicate detection.",
            "Development Projects": "Organizes development files by project structure and programming language."
        }
        return descriptions.get(self.selected_ruleset.get(), "No description available.")
    
    def _on_ruleset_changed(self, *args):
        """Handle ruleset selection change."""
        self.description_label.config(text=self._get_ruleset_description())
    
    def get_selected_ruleset(self) -> str:
        """Get selected ruleset."""
        return self.selected_ruleset.get()


class FilePreview(BaseComponent):
    """Component for previewing file organization operations."""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.preview_data: List[Dict[str, Any]] = []
        self.tree: Optional[ttk.Treeview] = None
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create file preview component."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main frame
        self.configure(bg=tokens.colors["background"])
        
        # Title
        title_label = tk.Label(
            self,
            text="Preview Operations",
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_2"]), "normal"),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        title_label.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        # Tree frame with scrollbars
        tree_frame = tk.Frame(self, bg=tokens.colors["background"])
        tree_frame.pack(fill="both", expand=True)
        
        # Create treeview
        columns = ("source", "target", "action", "status")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=12,
            style="Modern.Treeview"
        )
        
        # Configure columns
        self.tree.heading("source", text="Source File")
        self.tree.heading("target", text="Target Location")
        self.tree.heading("action", text="Action")
        self.tree.heading("status", text="Status")
        
        self.tree.column("source", width=200, minwidth=150)
        self.tree.column("target", width=200, minwidth=150)
        self.tree.column("action", width=80, minwidth=60)
        self.tree.column("status", width=80, minwidth=60)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Status summary
        self.summary_label = tk.Label(
            self,
            text="No preview data available",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), "normal"),
            bg=tokens.colors["background"],
            fg=tokens.colors["text_secondary"]
        )
        self.summary_label.pack(fill="x", pady=(tokens.spacing["md"], 0))
    
    def update_preview(self, preview_data: List[Dict[str, Any]]):
        """Update preview with operation data."""
        self.preview_data = preview_data
        
        # Clear existing items
        if self.tree:
            for item in self.tree.get_children():
                self.tree.delete(item)
        
        # Add new items
        for item in preview_data:
            source = item.get("source", "")
            target = item.get("target", "")
            action = item.get("action", "move")
            status = item.get("status", "pending")
            
            # Insert into tree
            self.tree.insert("", "end", values=(
                Path(source).name if source else "",
                str(Path(target).parent) if target else "",
                action.title(),
                status.title()
            ))
        
        # Update summary
        total = len(preview_data)
        move_count = sum(1 for item in preview_data if item.get("action") == "move")
        copy_count = sum(1 for item in preview_data if item.get("action") == "copy")
        
        summary = f"Total: {total} files"
        if move_count:
            summary += f" | Move: {move_count}"
        if copy_count:
            summary += f" | Copy: {copy_count}"
        
        self.summary_label.config(text=summary)
    
    def get_preview_data(self) -> List[Dict[str, Any]]:
        """Get current preview data."""
        return self.preview_data


class ExecutionControls(BaseComponent):
    """Component for controlling file organization execution."""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.execution_callbacks: Dict[str, List[Callable]] = {
            "preview": [],
            "execute": [],
            "cancel": []
        }
        self.is_executing = False
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create execution controls component."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main frame
        self.configure(bg=tokens.colors["background"])
        
        # Button frame
        button_frame = tk.Frame(self, bg=tokens.colors["background"])
        button_frame.pack(fill="x", pady=tokens.spacing["lg"])
        
        # Preview button
        self.preview_btn = ModernButton(
            button_frame,
            text="🔍 Preview Operations",
            command=self._on_preview,
            variant="secondary",
            width=150
        )
        self.preview_btn.pack(side="left", padx=(0, tokens.spacing["md"]))
        
        # Execute button
        self.execute_btn = ModernButton(
            button_frame,
            text="▶️ Execute Organization",
            command=self._on_execute,
            variant="primary",
            width=150
        )
        self.execute_btn.pack(side="left", padx=(0, tokens.spacing["md"]))
        
        # Cancel button
        self.cancel_btn = ModernButton(
            button_frame,
            text="⏹️ Cancel",
            command=self._on_cancel,
            variant="danger",
            width=100,
            state="disabled"
        )
        self.cancel_btn.pack(side="left")
        
        # Options frame
        options_frame = tk.LabelFrame(
            self,
            text="Execution Options",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), "normal"),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        options_frame.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        # Checkboxes for options
        self.dry_run_var = tk.BooleanVar(value=False)
        self.backup_var = tk.BooleanVar(value=True)
        self.confirm_conflicts_var = tk.BooleanVar(value=True)
        
        dry_run_cb = tk.Checkbutton(
            options_frame,
            text="Dry run (preview only, no actual file operations)",
            variable=self.dry_run_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), "normal"),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            selectcolor=tokens.colors["background"],
            activebackground=tokens.colors["background"],
            activeforeground=tokens.colors["text"]
        )
        dry_run_cb.pack(anchor="w", padx=tokens.spacing["md"], pady=tokens.spacing["xs"])
        
        backup_cb = tk.Checkbutton(
            options_frame,
            text="Create backup before operations",
            variable=self.backup_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), "normal"),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            selectcolor=tokens.colors["background"],
            activebackground=tokens.colors["background"],
            activeforeground=tokens.colors["text"]
        )
        backup_cb.pack(anchor="w", padx=tokens.spacing["md"], pady=tokens.spacing["xs"])
        
        confirm_cb = tk.Checkbutton(
            options_frame,
            text="Confirm conflicts manually",
            variable=self.confirm_conflicts_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), "normal"),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            selectcolor=tokens.colors["background"],
            activebackground=tokens.colors["background"],
            activeforeground=tokens.colors["text"]
        )
        confirm_cb.pack(anchor="w", padx=tokens.spacing["md"], pady=(tokens.spacing["xs"], tokens.spacing["md"]))
    
    def _on_preview(self):
        """Handle preview button click."""
        for callback in self.execution_callbacks["preview"]:
            callback()
    
    def _on_execute(self):
        """Handle execute button click."""
        for callback in self.execution_callbacks["execute"]:
            callback()
    
    def _on_cancel(self):
        """Handle cancel button click."""
        for callback in self.execution_callbacks["cancel"]:
            callback()
    
    def add_callback(self, event: str, callback: Callable):
        """Add callback for execution events."""
        if event in self.execution_callbacks:
            self.execution_callbacks[event].append(callback)
    
    def set_execution_state(self, executing: bool):
        """Set execution state and update UI."""
        from .base_component import ComponentState
        
        self.is_executing = executing
        
        if executing:
            self.preview_btn.set_state(ComponentState.DISABLED)
            self.execute_btn.set_state(ComponentState.DISABLED)
            self.cancel_btn.set_state(ComponentState.DEFAULT)
        else:
            self.preview_btn.set_state(ComponentState.DEFAULT)
            self.execute_btn.set_state(ComponentState.DEFAULT)
            self.cancel_btn.set_state(ComponentState.DISABLED)
    
    def get_options(self) -> Dict[str, bool]:
        """Get current execution options."""
        return {
            "dry_run": self.dry_run_var.get(),
            "backup": self.backup_var.get(),
            "confirm_conflicts": self.confirm_conflicts_var.get()
        }


class ExecutionView(BaseComponent):
    """Complete execution view combining all execution components."""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.directory_selector: Optional[DirectorySelector] = None
        self.ruleset_selector: Optional[RulesetSelector] = None
        self.file_preview: Optional[FilePreview] = None
        self.execution_controls: Optional[ExecutionControls] = None
        self.current_operation: Optional[threading.Thread] = None
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create complete execution view."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main frame
        self.configure(bg=tokens.colors["background"])
        
        # Create scrollable content
        canvas = tk.Canvas(self, bg=tokens.colors["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=tokens.colors["background"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Directory selection
        self.directory_selector = DirectorySelector(scrollable_frame)
        self.directory_selector.pack(fill="x", padx=tokens.spacing["lg"], pady=(tokens.spacing["lg"], tokens.spacing["xl"]))
        
        # Ruleset selection
        self.ruleset_selector = RulesetSelector(scrollable_frame)
        self.ruleset_selector.pack(fill="x", padx=tokens.spacing["lg"], pady=(0, tokens.spacing["xl"]))
        
        # File preview
        self.file_preview = FilePreview(scrollable_frame)
        self.file_preview.pack(fill="both", expand=True, padx=tokens.spacing["lg"], pady=(0, tokens.spacing["xl"]))
        
        # Execution controls
        self.execution_controls = ExecutionControls(scrollable_frame)
        self.execution_controls.pack(fill="x", padx=tokens.spacing["lg"], pady=(0, tokens.spacing["lg"]))
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Setup callbacks between components."""
        if self.execution_controls:
            self.execution_controls.add_callback("preview", self._on_preview_requested)
            self.execution_controls.add_callback("execute", self._on_execute_requested)
            self.execution_controls.add_callback("cancel", self._on_cancel_requested)
    
    def _on_preview_requested(self):
        """Handle preview request."""
        if not self._validate_inputs():
            return
        
        # Simulate preview generation
        preview_data = self._generate_preview_data()
        if self.file_preview:
            self.file_preview.update_preview(preview_data)
    
    def _on_execute_requested(self):
        """Handle execution request."""
        if not self._validate_inputs():
            return
        
        # Confirm execution
        if not self._confirm_execution():
            return
        
        # Start execution
        self._start_execution()
    
    def _on_cancel_requested(self):
        """Handle cancel request."""
        if self.current_operation and self.current_operation.is_alive():
            # Note: In a real implementation, you'd need a proper way to signal
            # the thread to stop, as Python threads can't be forcibly killed
            pass
        
        if self.execution_controls:
            self.execution_controls.set_execution_state(False)
    
    def _validate_inputs(self) -> bool:
        """Validate all inputs before execution."""
        if not self.directory_selector or not self.ruleset_selector:
            return False
        
        # Validate paths
        path_errors = self.directory_selector.validate_paths()
        if path_errors:
            error_msg = "\\n".join(path_errors.values())
            messagebox.showerror("Validation Error", error_msg)
            return False
        
        # Validate ruleset
        if not self.ruleset_selector.get_selected_ruleset():
            messagebox.showerror("Validation Error", "Please select a ruleset")
            return False
        
        return True
    
    def _confirm_execution(self) -> bool:
        """Confirm execution with user."""
        if not self.directory_selector or not self.ruleset_selector or not self.execution_controls:
            return False
        
        source = self.directory_selector.get_source_path()
        target = self.directory_selector.get_target_path()
        ruleset = self.ruleset_selector.get_selected_ruleset()
        options = self.execution_controls.get_options()
        
        message = f"Execute file organization?\\n\\n"
        message += f"Source: {source}\\n"
        message += f"Target: {target}\\n"
        message += f"Ruleset: {ruleset}\\n\\n"
        
        if options["dry_run"]:
            message += "Mode: Dry run (no actual changes)\\n"
        if options["backup"]:
            message += "Backup: Enabled\\n"
        if options["confirm_conflicts"]:
            message += "Conflict resolution: Manual\\n"
        
        dialog = ConfirmationDialog(
            self,
            title="Confirm Execution",
            message=message,
            icon="🚀"
        )
        
        return dialog.show()
    
    def _generate_preview_data(self) -> List[Dict[str, Any]]:
        """Generate preview data (placeholder implementation)."""
        # This would be replaced with actual preview generation logic
        sample_data = [
            {
                "source": "/path/to/file1.jpg",
                "target": "/target/Photos/2023/file1.jpg",
                "action": "move",
                "status": "pending"
            },
            {
                "source": "/path/to/document.pdf",
                "target": "/target/Documents/PDFs/document.pdf",
                "action": "move",
                "status": "pending"
            },
            {
                "source": "/path/to/music.mp3",
                "target": "/target/Music/Various/music.mp3",
                "action": "copy",
                "status": "pending"
            }
        ]
        return sample_data
    
    def _start_execution(self):
        """Start execution in background thread."""
        if self.execution_controls:
            self.execution_controls.set_execution_state(True)
        
        # Create and start execution thread
        self.current_operation = threading.Thread(target=self._execute_operations)
        self.current_operation.daemon = True
        self.current_operation.start()
    
    def _execute_operations(self):
        """Execute file organization operations."""
        try:
            # Show progress dialog
            progress_dialog = ProgressDialog(
                self,
                title="Organizing Files",
                message="Processing files...",
                cancelable=True
            )
            
            # Simulate execution with progress updates
            operations = self._generate_preview_data()
            total_ops = len(operations)
            
            for i, operation in enumerate(operations):
                if progress_dialog.is_cancelled():
                    break
                
                # Simulate processing
                time.sleep(0.5)  # Replace with actual file operation
                
                # Update progress
                progress = ((i + 1) / total_ops) * 100
                status = f"Processing {Path(operation['source']).name}..."
                progress_dialog.update_progress(progress, status)
            
            # Close progress dialog
            if hasattr(progress_dialog, 'dialog_window') and progress_dialog.dialog_window:
                progress_dialog.dialog_window.destroy()
            
            # Show completion message
            if not progress_dialog.is_cancelled():
                messagebox.showinfo("Complete", "File organization completed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during execution: {str(e)}")
        
        finally:
            # Reset execution state
            if self.execution_controls:
                self.execution_controls.set_execution_state(False)
