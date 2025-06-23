"""
TaskMover UI Framework - Dialog and Modal Components
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Callable, Optional, List, Union, Dict
from .base_component import BaseComponent, ComponentState


class BaseDialog(BaseComponent):
    """
    Base dialog component with modal overlay and positioning.
    """
    
    def __init__(self, parent: tk.Widget,
                 title: str = "Dialog",
                 modal: bool = True,
                 resizable: bool = False,
                 size: tuple = (400, 300),
                 **kwargs):
        """
        Initialize the base dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            modal: Whether dialog is modal
            resizable: Whether dialog can be resized
            size: Dialog size (width, height)
            **kwargs: Additional widget options
        """
        self.title = title
        self.modal = modal
        self.resizable = resizable
        self.size = size
        self._result = None
        self._closed = False
        
        # Store original parent focus
        self._original_focus = parent.focus_get()
        
        super().__init__(parent, **kwargs)
        
        self._setup_modal()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the dialog structure."""
        # Create toplevel window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry(f"{self.size[0]}x{self.size[1]}")
        self.dialog.resizable(self.resizable, self.resizable)
        
        # Center on parent
        self._center_on_parent()
        
        # Main container
        self.main_frame = ttk.Frame(self.dialog, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Content area (to be overridden by subclasses)
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Button area
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Default buttons
        self._create_default_buttons()
        
        # Bind events
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
        self.dialog.bind("<Escape>", lambda e: self._on_close())
        
        return self.dialog  # type: ignore
    
    def _setup_modal(self):
        """Setup modal behavior."""
        if self.modal:
            if isinstance(self.parent, (tk.Tk, tk.Toplevel)):
                self.dialog.transient(self.parent)
                self.dialog.grab_set()
    
    def _center_on_parent(self):
        """Center the dialog on its parent."""
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - self.size[0]) // 2
        y = parent_y + (parent_height - self.size[1]) // 2
        
        self.dialog.geometry(f"{self.size[0]}x{self.size[1]}+{x}+{y}")
    
    def _create_default_buttons(self):
        """Create default OK/Cancel buttons."""
        ttk.Button(self.button_frame, text="Cancel", 
                  command=self._on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(self.button_frame, text="OK", 
                  command=self._on_ok).pack(side=tk.RIGHT)
    
    def _on_ok(self):
        """Handle OK button click."""
        if self._validate():
            self._result = self._get_result()
            self._on_close()
    
    def _on_cancel(self):
        """Handle Cancel button click."""
        self._result = None
        self._on_close()
    
    def _on_close(self):
        """Handle window close."""
        if not self._closed:
            self._closed = True
            if self.modal:
                self.dialog.grab_release()
            if self._original_focus:
                self._original_focus.focus_set()
            self.dialog.destroy()
    
    def _validate(self) -> bool:
        """Validate dialog inputs. Override in subclasses."""
        return True
    
    def _get_result(self) -> Any:
        """Get dialog result. Override in subclasses."""
        return True
    
    def show_modal(self) -> Any:
        """Show dialog modally and return result."""
        self.dialog.wait_window()
        return self._result
    
    def show(self):
        """Show dialog non-modally."""
        self.dialog.deiconify()
    
    def hide(self):
        """Hide dialog."""
        self.dialog.withdraw()


class MessageDialog(BaseDialog):
    """
    Message dialog with icon and configurable buttons.
    """
    
    def __init__(self, parent: tk.Widget,
                 title: str = "Message",
                 message: str = "",
                 message_type: str = "info",  # info, warning, error, question
                 buttons: Optional[List[str]] = None,
                 default_button: Optional[str] = None,
                 **kwargs):
        """
        Initialize the message dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Message text
            message_type: Type of message (info, warning, error, question)
            buttons: List of button labels
            default_button: Default button label
            **kwargs: Additional dialog options
        """
        self.message = message
        self.message_type = message_type
        self.buttons = buttons or ["OK"]
        self.default_button = default_button or self.buttons[0]
        self._button_result = None
        
        super().__init__(parent, title=title, size=(350, 150), **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the message dialog structure."""
        dialog = super()._create_widget(**kwargs)
        
        # Clear default content and buttons
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Main container with icon and message
        main_container = ttk.Frame(self.content_frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Icon (placeholder for now)
        icon_frame = ttk.Frame(main_container, width=50)
        icon_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        icon_frame.pack_propagate(False)
        
        icon_label = tk.Label(icon_frame, text="ℹ", font=('Arial', 24),
                             foreground=self._get_icon_color())
        icon_label.pack(side=tk.TOP, anchor='n', pady=10)
        
        # Message
        message_frame = ttk.Frame(main_container)
        message_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        message_label = tk.Label(message_frame, text=self.message, 
                               wraplength=250, justify=tk.LEFT)
        message_label.pack(side=tk.TOP, anchor='nw', pady=10)
        
        # Custom buttons
        self._create_message_buttons()
        
        return dialog
    
    def _get_icon_color(self) -> str:
        """Get icon color based on message type."""
        colors = {
            'info': 'blue',
            'warning': 'orange',
            'error': 'red',
            'question': 'blue'
        }
        return colors.get(self.message_type, 'blue')
    
    def _create_message_buttons(self):
        """Create message dialog buttons."""
        for button_text in reversed(self.buttons):
            button = ttk.Button(self.button_frame, text=button_text,
                              command=lambda t=button_text: self._on_button_click(t))
            button.pack(side=tk.RIGHT, padx=(5, 0))
            
            if button_text == self.default_button:
                button.focus_set()
    
    def _on_button_click(self, button_text: str):
        """Handle button click."""
        self._button_result = button_text
        self._on_close()
    
    def _get_result(self) -> str:
        """Get the clicked button text."""
        return self._button_result or self.buttons[0]


class ConfirmationDialog(MessageDialog):
    """
    Confirmation dialog with Yes/No or OK/Cancel buttons.
    """
    
    def __init__(self, parent: tk.Widget,
                 title: str = "Confirm",
                 message: str = "Are you sure?",
                 confirm_button: str = "Yes",
                 cancel_button: str = "No",
                 **kwargs):
        """
        Initialize the confirmation dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Confirmation message
            confirm_button: Confirm button label
            cancel_button: Cancel button label
            **kwargs: Additional dialog options
        """
        buttons = [cancel_button, confirm_button]
        super().__init__(parent, title=title, message=message, 
                        message_type="question", buttons=buttons,
                        default_button=confirm_button, **kwargs)
        
        self.confirm_button = confirm_button
        self.cancel_button = cancel_button
    
    def get_confirmation_result(self) -> bool:
        """Get confirmation result as boolean."""
        return self._button_result == self.confirm_button


class InputDialog(BaseDialog):
    """
    Input dialog for collecting user input.
    """
    
    def __init__(self, parent: tk.Widget,
                 title: str = "Input",
                 prompt: str = "Enter value:",
                 default_value: str = "",
                 input_type: str = "text",  # text, password, number
                 validation_func: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the input dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            prompt: Input prompt text
            default_value: Default input value
            input_type: Type of input (text, password, number)
            validation_func: Optional validation function
            **kwargs: Additional dialog options
        """
        self.prompt = prompt
        self.default_value = default_value
        self.input_type = input_type
        self.validation_func = validation_func
        
        super().__init__(parent, title=title, size=(400, 180), **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the input dialog structure."""
        dialog = super()._create_widget(**kwargs)
        
        # Clear default content and buttons
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Prompt label
        prompt_label = tk.Label(self.content_frame, text=self.prompt)
        prompt_label.pack(side=tk.TOP, anchor='w', pady=(0, 10))
        
        # Input field
        self.input_var = tk.StringVar(value=self.default_value)
        
        if self.input_type == "password":
            self.input_entry = ttk.Entry(self.content_frame, textvariable=self.input_var, 
                                       show="*")
        else:
            self.input_entry = ttk.Entry(self.content_frame, textvariable=self.input_var)
        
        self.input_entry.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        self.input_entry.focus_set()
        self.input_entry.select_range(0, tk.END)
        
        # Validation label
        self.validation_label = tk.Label(self.content_frame, text="", 
                                       foreground='red', font=('Arial', 9))
        self.validation_label.pack(side=tk.TOP, anchor='w')
        
        # Buttons
        ttk.Button(self.button_frame, text="Cancel", 
                  command=self._on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(self.button_frame, text="OK", 
                  command=self._on_ok).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.input_entry.bind("<Return>", lambda e: self._on_ok())
        
        return dialog
    
    def _validate(self) -> bool:
        """Validate input."""
        value = self.input_var.get()
        
        if self.validation_func:
            try:
                result = self.validation_func(value)
                if result is not True:
                    self.validation_label.configure(text=str(result))
                    return False
            except Exception as e:
                self.validation_label.configure(text=str(e))
                return False
        
        self.validation_label.configure(text="")
        return True
    
    def _get_result(self) -> Union[str, float]:
        """Get the input value."""
        value = self.input_var.get()
        if self.input_type == "number":
            try:
                return float(value)
            except ValueError:
                return value
        return value


class FileConflictDialog(BaseDialog):
    """
    File conflict resolution dialog.
    """
    
    def __init__(self, parent: tk.Widget,
                 source_file: str,
                 target_file: str,
                 source_info: Optional[Dict] = None,
                 target_info: Optional[Dict] = None,
                 **kwargs):
        """
        Initialize the file conflict dialog.
        
        Args:
            parent: Parent widget
            source_file: Source file path
            target_file: Target file path
            source_info: Source file information
            target_info: Target file information
            **kwargs: Additional dialog options
        """
        self.source_file = source_file
        self.target_file = target_file
        self.source_info = source_info or {}
        self.target_info = target_info or {}
        self.apply_to_all = False
        
        super().__init__(parent, title="File Conflict", size=(600, 400), **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the file conflict dialog structure."""
        dialog = super()._create_widget(**kwargs)
        
        # Clear default content and buttons
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Message
        message = f"A file with the name '{os.path.basename(self.target_file)}' already exists."
        message_label = tk.Label(self.content_frame, text=message, font=('Arial', 10, 'bold'))
        message_label.pack(side=tk.TOP, anchor='w', pady=(0, 15))
        
        # File comparison
        comparison_frame = ttk.Frame(self.content_frame)
        comparison_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Source file info
        source_frame = ttk.LabelFrame(comparison_frame, text="Source File", padding=10)
        source_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self._create_file_info(source_frame, self.source_file, self.source_info)
        
        # Target file info
        target_frame = ttk.LabelFrame(comparison_frame, text="Existing File", padding=10)
        target_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self._create_file_info(target_frame, self.target_file, self.target_info)
        
        # Options
        options_frame = ttk.LabelFrame(self.content_frame, text="Resolution", padding=10)
        options_frame.pack(side=tk.TOP, fill=tk.X, pady=(15, 0))
        
        self.resolution_var = tk.StringVar(value="replace")
        
        ttk.Radiobutton(options_frame, text="Replace the existing file", 
                       variable=self.resolution_var, value="replace").pack(anchor='w')
        ttk.Radiobutton(options_frame, text="Keep both files (rename new file)", 
                       variable=self.resolution_var, value="keep_both").pack(anchor='w')
        ttk.Radiobutton(options_frame, text="Skip this file", 
                       variable=self.resolution_var, value="skip").pack(anchor='w')
        
        # Custom name option
        custom_frame = ttk.Frame(options_frame)
        custom_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Radiobutton(custom_frame, text="Use custom name:", 
                       variable=self.resolution_var, value="custom").pack(side=tk.LEFT)
        
        self.custom_name_var = tk.StringVar(value=os.path.basename(self.source_file))
        self.custom_name_entry = ttk.Entry(custom_frame, textvariable=self.custom_name_var)
        self.custom_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Apply to all checkbox
        self.apply_all_var = tk.BooleanVar()
        apply_all_cb = ttk.Checkbutton(options_frame, text="Apply to all conflicts",
                                     variable=self.apply_all_var)
        apply_all_cb.pack(anchor='w', pady=(10, 0))
        
        # Buttons
        self._create_conflict_buttons()
        
        return dialog
    
    def _create_file_info(self, parent: tk.Widget, file_path: str, file_info: Dict):
        """Create file information display."""
        import time
        
        # File name
        name_label = tk.Label(parent, text=os.path.basename(file_path), 
                            font=('Arial', 9, 'bold'))
        name_label.pack(anchor='w')
        
        # File details
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            size = self._format_file_size(stat.st_size)
            modified = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
            
            details = f"Size: {size}\nModified: {modified}"
        else:
            details = "File information not available"
        
        details_label = tk.Label(parent, text=details, justify=tk.LEFT, 
                               font=('Arial', 8), foreground='gray')
        details_label.pack(anchor='w', pady=(5, 0))
        
        # File preview (placeholder)
        preview_label = tk.Label(parent, text="[File Preview]", 
                                justify=tk.CENTER, foreground='lightgray',
                                relief='sunken', height=3)
        preview_label.pack(fill=tk.X, pady=(10, 0))
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size_float = float(size_bytes)
        while size_float >= 1024 and i < len(size_names) - 1:
            size_float /= 1024.0
            i += 1
        
        return f"{size_float:.1f} {size_names[i]}"
    
    def _create_conflict_buttons(self):
        """Create conflict resolution buttons."""
        ttk.Button(self.button_frame, text="Cancel", 
                  command=self._on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(self.button_frame, text="Apply", 
                  command=self._on_ok).pack(side=tk.RIGHT)
    
    def _validate(self) -> bool:
        """Validate conflict resolution."""
        if self.resolution_var.get() == "custom":
            custom_name = self.custom_name_var.get().strip()
            if not custom_name:
                messagebox.showerror("Error", "Please enter a custom file name")
                return False
        return True
    
    def _get_result(self) -> Dict:
        """Get the conflict resolution result."""
        result = {
            'resolution': self.resolution_var.get(),
            'apply_to_all': self.apply_all_var.get()
        }
        
        if result['resolution'] == 'custom':
            result['custom_name'] = self.custom_name_var.get().strip()
        
        return result


class ProgressDialog(BaseDialog):
    """Progress dialog for long-running operations."""
    
    def __init__(self, parent: tk.Widget,
                 title: str = "Progress",
                 operation_name: str = "Operation in progress...",
                 cancellable: bool = True,
                 show_details: bool = False,
                 **kwargs):
        """
        Initialize the progress dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            operation_name: Name of the operation
            cancellable: Whether operation can be cancelled
            show_details: Whether to show detailed progress log
            **kwargs: Additional dialog options
        """
        self.operation_name = operation_name
        self.cancellable = cancellable
        self.show_details = show_details
        self._cancelled = False
        self._progress_value = 0
        self._progress_max = 100
        self._status_text = ""
        self._details = []
        
        size = (500, 300) if show_details else (400, 150)
        
        super().__init__(parent, title=title, size=size, modal=False, **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the progress dialog structure."""
        dialog = super()._create_widget(**kwargs)
        
        # Clear default content and buttons
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Operation label
        self.operation_label = tk.Label(self.content_frame, text=self.operation_name,
                                      font=('Arial', 10, 'bold'))
        self.operation_label.pack(side=tk.TOP, anchor='w', pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(self.content_frame, mode='determinate',
                                          maximum=self._progress_max)
        self.progress_bar.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Status label
        self.status_label = tk.Label(self.content_frame, text=self._status_text,
                                    font=('Arial', 9))
        self.status_label.pack(side=tk.TOP, anchor='w', pady=(0, 10))
        
        # Details (if enabled)
        if self.show_details:
            details_frame = ttk.LabelFrame(self.content_frame, text="Details", padding=5)
            details_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            # Details text widget with scrollbar
            text_frame = ttk.Frame(details_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            self.details_text = tk.Text(text_frame, height=8, font=('Consolas', 8))
            details_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                                            command=self.details_text.yview)
            
            self.details_text.configure(yscrollcommand=details_scrollbar.set)
            self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        if self.cancellable:
            self.cancel_btn = ttk.Button(self.button_frame, text="Cancel",
                                       command=self._on_cancel)
            self.cancel_btn.pack(side=tk.RIGHT)
        
        self.background_btn = ttk.Button(self.button_frame, text="Run in Background",
                                       command=self._on_background)
        self.background_btn.pack(side=tk.RIGHT, padx=(0, 5) if self.cancellable else 0)
        
        return dialog
    
    def _on_cancel(self):
        """Handle cancel button click."""
        if self.cancellable:
            self._cancelled = True
            self.trigger_event('operation_cancelled')
    
    def _on_background(self):
        """Handle background button click."""
        self.hide()
        self.trigger_event('run_in_background')
    
    def set_progress(self, value: int, maximum: Optional[int] = None, status: Optional[str] = None):
        """Update progress."""
        if maximum is not None:
            self._progress_max = maximum
            self.progress_bar.configure(maximum=maximum)
        
        self._progress_value = value
        self.progress_bar.configure(value=value)
        
        if status is not None:
            self._status_text = status
            self.status_label.configure(text=status)
        
        # Update dialog to refresh display
        self.dialog.update_idletasks()
    
    def add_detail(self, detail: str):
        """Add a detail message."""
        import time
        
        timestamp = time.strftime('%H:%M:%S')
        detail_line = f"[{timestamp}] {detail}\n"
        
        self._details.append(detail_line)
        
        if self.show_details and hasattr(self, 'details_text'):
            self.details_text.insert(tk.END, detail_line)
            self.details_text.see(tk.END)
            self.dialog.update_idletasks()
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self._cancelled
    
    def complete(self, success: bool = True, message: Optional[str] = None):
        """Mark operation as complete."""
        if success:
            self.set_progress(self._progress_max, status=message or "Operation completed successfully")
        else:
            self.status_label.configure(text=message or "Operation failed", foreground='red')
        
        # Update buttons
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.configure(text="Close", command=self._on_close)
        if hasattr(self, 'background_btn'):
            self.background_btn.destroy()
    
    def _validate(self) -> bool:
        """Progress dialogs don't need validation."""
        return True


class SettingsDialog(BaseDialog):
    """Settings dialog with categorized options."""
    
    def __init__(self, parent: tk.Widget,
                 settings: Optional[Dict[str, Any]] = None,
                 categories: Optional[Dict[str, List[str]]] = None,
                 **kwargs):
        """
        Initialize the settings dialog.
        
        Args:
            parent: Parent widget
            settings: Settings dictionary
            categories: Settings categories
            **kwargs: Additional dialog options
        """
        self.settings = settings or {}
        self.categories = categories or {'General': list(self.settings.keys())}
        self._original_settings = self.settings.copy()
        self._setting_widgets = {}
        
        super().__init__(parent, title="Settings", size=(600, 450), **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the settings dialog structure."""
        dialog = super()._create_widget(**kwargs)
        
        # Clear default content and buttons
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Main container with sidebar
        main_container = ttk.Frame(self.content_frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Category sidebar
        sidebar_frame = ttk.Frame(main_container, width=150)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar_frame.pack_propagate(False)
        
        # Category listbox
        self.category_listbox = tk.Listbox(sidebar_frame)
        self.category_listbox.pack(fill=tk.BOTH, expand=True)
        
        for category in self.categories.keys():
            self.category_listbox.insert(tk.END, category)
        
        self.category_listbox.bind('<<ListboxSelect>>', self._on_category_selected)
        self.category_listbox.selection_set(0)
        
        # Settings content
        content_container = ttk.Frame(main_container)
        content_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Content with scrollbar
        canvas = tk.Canvas(content_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_container, orient=tk.VERTICAL, command=canvas.yview)
        self.settings_frame = ttk.Frame(canvas)
        
        self.settings_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.settings_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        self._create_settings_buttons()
        
        # Load first category
        self._on_category_selected()
        
        return dialog
    
    def _create_settings_buttons(self):
        """Create settings dialog buttons."""
        ttk.Button(self.button_frame, text="Cancel", 
                  command=self._on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(self.button_frame, text="Reset", 
                  command=self._on_reset).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(self.button_frame, text="Apply", 
                  command=self._on_apply).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(self.button_frame, text="OK", 
                  command=self._on_ok).pack(side=tk.RIGHT)
    
    def _on_category_selected(self, event=None):
        """Handle category selection."""
        selection = self.category_listbox.curselection()
        if not selection:
            return
        
        category = list(self.categories.keys())[selection[0]]
        self._load_category_settings(category)
    
    def _load_category_settings(self, category: str):
        """Load settings for a category."""
        # Clear current settings
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        
        # Create settings widgets for this category
        settings_in_category = self.categories.get(category, [])
        
        for setting_name in settings_in_category:
            if setting_name in self.settings:
                self._create_setting_widget(setting_name, self.settings[setting_name])
    
    def _create_setting_widget(self, setting_name: str, setting_value: Any):
        """Create a widget for a single setting."""
        setting_frame = ttk.Frame(self.settings_frame)
        setting_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        # Setting label
        label = tk.Label(setting_frame, text=setting_name, width=20, anchor='w')
        label.pack(side=tk.LEFT)
        
        # Setting widget based on type
        if isinstance(setting_value, bool):
            var = tk.BooleanVar(value=setting_value)
            widget = ttk.Checkbutton(setting_frame, variable=var)
            setattr(widget, '_var', var)
        elif isinstance(setting_value, int):
            var = tk.IntVar(value=setting_value)
            widget = ttk.Spinbox(setting_frame, from_=-999999, to=999999, textvariable=var)
            setattr(widget, '_var', var)
        elif isinstance(setting_value, float):
            var = tk.DoubleVar(value=setting_value)
            widget = ttk.Entry(setting_frame, textvariable=var)
            setattr(widget, '_var', var)
        else:
            var = tk.StringVar(value=str(setting_value))
            widget = ttk.Entry(setting_frame, textvariable=var)
            setattr(widget, '_var', var)
        
        widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        self._setting_widgets[setting_name] = widget
    
    def _on_apply(self):
        """Apply settings without closing."""
        self._apply_settings()
    
    def _on_reset(self):
        """Reset settings to original values."""
        self.settings = self._original_settings.copy()
        # Reload current category
        self._on_category_selected()
    
    def _apply_settings(self):
        """Apply current settings."""
        for setting_name, widget in self._setting_widgets.items():
            if hasattr(widget, '_var'):
                self.settings[setting_name] = widget._var.get()
        
        self.trigger_event('settings_applied', self.settings)
    
    def _validate(self) -> bool:
        """Validate settings."""
        # Apply settings on OK
        self._apply_settings()
        return True
    
    def _get_result(self) -> Dict[str, Any]:
        """Get the settings result."""
        return self.settings
