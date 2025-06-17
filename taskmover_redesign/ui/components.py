"""
Modern UI components for TaskMover Redesigned.
Clean, independent components with no legacy dependencies.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from typing import Optional, Callable, Any

from ..core.utils import center_window_on_parent


class Tooltip:
    """Modern tooltip implementation."""
    
    def __init__(self, widget: tk.Widget, text: str, delay: int = 500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.timer = None
        
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<ButtonPress>", self._on_leave)
    
    def _on_enter(self, event=None):
        """Start timer for showing tooltip."""
        self._cancel_timer()
        self.timer = self.widget.after(self.delay, self._show_tooltip)
    
    def _on_leave(self, event=None):
        """Hide tooltip and cancel timer."""
        self._cancel_timer()
        self._hide_tooltip()
    
    def _cancel_timer(self):
        """Cancel the tooltip timer."""
        if self.timer:
            self.widget.after_cancel(self.timer)
            self.timer = None
    
    def _show_tooltip(self):
        """Show the tooltip window."""
        if self.tooltip_window:
            return
            
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#ffffe0",
            foreground="#000000",
            relief="solid",
            borderwidth=1,
            font=("Arial", 9)
        )
        label.pack()
    
    def _hide_tooltip(self):
        """Hide the tooltip window."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class SimpleDialog:
    """Base class for simple dialogs."""
    
    def __init__(self, parent: tk.Widget, title: str, width: int = 400, height: int = 300, 
                 proportional: bool = False, width_ratio: float = 0.4, height_ratio: float = 0.5):
        self.result = None
        self.parent = parent
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent.winfo_toplevel())
        self.dialog.grab_set()
        
        # Calculate dimensions and center the dialog
        if proportional:
            # Use proportional sizing based on parent or screen
            center_window_on_parent(
                self.dialog, parent, 
                proportional=True, 
                width_ratio=width_ratio, 
                height_ratio=height_ratio
            )
        else:
            # Use fixed dimensions
            self.dialog.geometry(f"{width}x{height}")
            self._center_dialog(width, height)
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # Create main frame
        self.main_frame = ttkb.Frame(self.dialog, padding=20)
        self.main_frame.pack(fill="both", expand=True)
        
        # Create content
        self.create_content()
        
        # Create buttons
        self.create_buttons()
    
    def _center_dialog(self, width: int, height: int):
        """Center the dialog on the parent window with proportional sizing."""
        center_window_on_parent(
            self.dialog, self.parent, 
            width=width, height=height
        )
    
    def create_content(self):
        """Override this method to create dialog content."""
        pass
    
    def create_buttons(self):
        """Create standard OK/Cancel buttons."""
        button_frame = ttkb.Frame(self.main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ok_btn = ttkb.Button(button_frame, text="OK", command=self.ok)
        ok_btn.pack(side="right", padx=(5, 0))
        
        cancel_btn = ttkb.Button(button_frame, text="Cancel", command=self.cancel)
        cancel_btn.pack(side="right")
        
        # Make OK button default
        self.dialog.bind("<Return>", lambda e: self.ok())
        self.dialog.bind("<Escape>", lambda e: self.cancel())
        ok_btn.focus()
    
    def ok(self):
        """Handle OK button."""
        if self.validate():
            self.result = self.get_result()
            self.dialog.destroy()
    
    def cancel(self):
        """Handle Cancel button."""
        self.result = None
        self.dialog.destroy()
    
    def validate(self) -> bool:
        """Override this method to validate input."""
        return True
    
    def get_result(self) -> Any:
        """Override this method to return dialog result."""
        return True
    
    def show(self) -> Any:
        """Show dialog and return result."""
        self.dialog.wait_window()
        return self.result


class TextInputDialog(SimpleDialog):
    """Simple text input dialog."""
    
    def __init__(self, parent: tk.Widget, title: str, prompt: str, initial_value: str = ""):
        self.prompt = prompt
        self.initial_value = initial_value
        self.entry = None
        super().__init__(parent, title, 400, 150)
    
    def create_content(self):
        """Create the text input content."""
        ttkb.Label(self.main_frame, text=self.prompt).pack(pady=(0, 10))
        
        self.entry = ttkb.Entry(self.main_frame, width=40)
        self.entry.pack(fill="x")
        self.entry.insert(0, self.initial_value)
        self.entry.focus()
        self.entry.select_range(0, tk.END)
    
    def validate(self) -> bool:
        """Validate that text is not empty."""
        text = self.entry.get().strip()
        if not text:
            messagebox.showerror("Error", "Please enter a value.")
            return False
        return True
    
    def get_result(self) -> str:
        """Return the entered text."""
        return self.entry.get().strip()


class ConfirmDialog(SimpleDialog):
    """Simple confirmation dialog."""
    
    def __init__(self, parent: tk.Widget, title: str, message: str, 
                 ok_text: str = "OK", cancel_text: str = "Cancel"):
        self.message = message
        self.ok_text = ok_text
        self.cancel_text = cancel_text
        super().__init__(parent, title, 400, 150)
    
    def create_content(self):
        """Create the confirmation message."""
        ttkb.Label(
            self.main_frame, 
            text=self.message, 
            wraplength=350,
            justify="center"
        ).pack(expand=True)
    
    def create_buttons(self):
        """Create custom OK/Cancel buttons."""
        button_frame = ttkb.Frame(self.main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ok_btn = ttkb.Button(button_frame, text=self.ok_text, command=self.ok)
        ok_btn.pack(side="right", padx=(5, 0))
        
        cancel_btn = ttkb.Button(button_frame, text=self.cancel_text, command=self.cancel)
        cancel_btn.pack(side="right")
        
        # Make OK button default
        self.dialog.bind("<Return>", lambda e: self.ok())
        self.dialog.bind("<Escape>", lambda e: self.cancel())
        ok_btn.focus()


class ProgressDialog:
    """Modern progress dialog with cancellation support."""
    
    def __init__(self, parent: tk.Widget, title: str = "Progress", 
                 message: str = "Please wait...", cancelable: bool = True):
        self.parent = parent
        self.canceled = False
        self.cancel_callback = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x200")
        self.dialog.transient(parent.winfo_toplevel())
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Handle window close
        if cancelable:
            self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        else:
            self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Create content
        self._create_content(message, cancelable)
    
    def _center_dialog(self):
        """Center the dialog on the parent."""
        center_window_on_parent(
            self.dialog, self.parent, 
            width=450, height=200
        )
    
    def _create_content(self, message: str, cancelable: bool):
        """Create dialog content."""
        main_frame = ttkb.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Message
        self.message_label = ttkb.Label(
            main_frame, 
            text=message, 
            font=("Arial", 10, "bold")
        )
        self.message_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress_bar = ttkb.Progressbar(
            main_frame, 
            mode="indeterminate", 
            length=400
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # Status label
        self.status_label = ttkb.Label(main_frame, text="Starting...")
        self.status_label.pack(pady=(0, 15))
        
        # Cancel button
        if cancelable:
            self.cancel_btn = ttkb.Button(
                main_frame, 
                text="Cancel", 
                command=self.cancel
            )
            self.cancel_btn.pack()
    
    def start_progress(self):
        """Start the progress animation."""
        self.progress_bar.start(10)
    
    def stop_progress(self):
        """Stop the progress animation."""
        self.progress_bar.stop()
    
    def update_status(self, status: str):
        """Update the status message."""
        self.status_label.config(text=status)
        self.dialog.update()
    
    def update_message(self, message: str):
        """Update the main message."""
        self.message_label.config(text=message)
        self.dialog.update()
    
    def set_progress(self, value: int):
        """Set progress bar to determinate mode with value (0-100)."""
        self.progress_bar.config(mode="determinate", maximum=100, value=value)
    
    def cancel(self):
        """Cancel the operation."""
        self.canceled = True
        if self.cancel_callback:
            self.cancel_callback()
    
    def set_cancel_callback(self, callback: Callable):
        """Set callback for cancel operation."""
        self.cancel_callback = callback
    
    def close(self):
        """Close the dialog."""
        self.stop_progress()
        self.dialog.destroy()
    
    def is_canceled(self) -> bool:
        """Check if operation was canceled."""
        return self.canceled
    
    def set_completed(self, message: str = "✅ Operation completed successfully!", 
                     title: str = "Complete"):
        """Set the progress dialog to completed state with detailed message."""
        self.stop_progress()
        self.progress_bar.config(mode="determinate", maximum=100, value=100)
        self.update_status(message)
        
        # Update dialog title to indicate completion
        self.dialog.title(title)
        
        # Enable cancel button and change it to "Close"
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.config(text="Close", state="normal")
    
    def set_error(self, message: str = "❌ An error occurred during the operation", 
                  title: str = "Error"):
        """Set the progress dialog to error state with detailed message."""
        self.stop_progress()
        self.progress_bar.config(mode="determinate", maximum=100, value=0)
        self.update_status(message)
        
        # Update dialog title to indicate error
        self.dialog.title(title)
        
        # Enable cancel button and change it to "Close"
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.config(text="Close", state="normal")


# Dummy classes for compatibility
class RuleEditor:
    pass

class RuleListWidget:
    pass

class SettingsDialog:
    pass


# Helper functions for common dialogs
def show_info(parent: tk.Widget, title: str, message: str):
    """Show information dialog."""
    messagebox.showinfo(title, message, parent=parent)

def show_warning(parent: tk.Widget, title: str, message: str):
    """Show warning dialog."""
    messagebox.showwarning(title, message, parent=parent)

def show_error(parent: tk.Widget, title: str, message: str):
    """Show error dialog."""
    messagebox.showerror(title, message, parent=parent)

def ask_yes_no(parent: tk.Widget, title: str, message: str) -> bool:
    """Ask yes/no question."""
    return messagebox.askyesno(title, message, parent=parent)

def ask_ok_cancel(parent: tk.Widget, title: str, message: str) -> bool:
    """Ask OK/Cancel question."""
    return messagebox.askokcancel(title, message, parent=parent)

def get_text_input(parent: tk.Widget, title: str, prompt: str, initial: str = "") -> Optional[str]:
    """Get text input from user."""
    dialog = TextInputDialog(parent, title, prompt, initial)
    return dialog.show()
