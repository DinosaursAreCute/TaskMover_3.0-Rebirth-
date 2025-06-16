"""
UI components and helpers for TaskMover Redesigned.
Clean, reusable UI components with better organization.
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from typing import Optional, Callable, Any


class Tooltip:
    """Simple tooltip implementation for widgets."""
    
    def __init__(self, widget: tk.Widget, text: str, delay: int = 500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.timer_id = None
        
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<Motion>", self._on_motion)
    
    def _on_enter(self, event=None):
        """Handle mouse enter event."""
        if self.timer_id:
            self.widget.after_cancel(self.timer_id)
        self.timer_id = self.widget.after(self.delay, self._show_tooltip)
    
    def _on_leave(self, event=None):
        """Handle mouse leave event."""
        if self.timer_id:
            self.widget.after_cancel(self.timer_id)
            self.timer_id = None
        self._hide_tooltip()
    
    def _on_motion(self, event=None):
        """Handle mouse motion event."""
        if self.tooltip_window:
            self._hide_tooltip()
        if self.timer_id:
            self.widget.after_cancel(self.timer_id)
        self.timer_id = self.widget.after(self.delay, self._show_tooltip)
    
    def _show_tooltip(self):
        """Show the tooltip."""
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
            relief="solid",
            borderwidth=1,
            font=("Arial", 9)
        )
        label.pack()
    
    def _hide_tooltip(self):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class ProgressDialog:
    """Reusable progress dialog for long-running operations."""
    
    def __init__(self, parent: tk.Widget, title: str = "Progress", 
                 message: str = "Please wait...", cancelable: bool = True):
        self.parent = parent
        self.canceled = False
        self.cancel_callback = None
        
        # Create dialog
        self.dialog = ttkb.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        from ..core.utils import center_window
        center_window(self.dialog, 400, 150)
        
        # Main message
        self.message_label = ttkb.Label(
            self.dialog, 
            text=message, 
            font=("Arial", 10, "bold")
        )
        self.message_label.pack(pady=20)
        
        # Progress bar
        self.progress = ttkb.Progressbar(
            self.dialog, 
            mode="determinate", 
            length=300
        )
        self.progress.pack(pady=10)
        
        # Status label
        self.status_label = ttkb.Label(self.dialog, text="")
        self.status_label.pack(pady=5)
        
        # Cancel button
        if cancelable:
            self.cancel_btn = ttkb.Button(
                self.dialog, 
                text="Cancel", 
                command=self._on_cancel
            )
            self.cancel_btn.pack(pady=10)
    
    def update_progress(self, current: int, total: int, status: str = ""):
        """Update the progress bar and status."""
        if total > 0:
            percentage = (current / total) * 100
            self.progress['value'] = percentage
        
        if status:
            self.status_label.config(text=status)
        
        self.dialog.update()
    
    def set_cancel_callback(self, callback: Callable):
        """Set callback for cancel button."""
        self.cancel_callback = callback
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self.canceled = True
        if self.cancel_callback:
            self.cancel_callback()
    
    def close(self):
        """Close the dialog."""
        if self.dialog:
            self.dialog.destroy()


class ConfirmDialog:
    """Reusable confirmation dialog."""
    
    def __init__(self, parent: tk.Widget, title: str, message: str,
                 confirm_text: str = "Yes", cancel_text: str = "No"):
        self.result = False
        
        # Create dialog
        self.dialog = ttkb.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("350x120")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        from ..core.utils import center_window
        center_window(self.dialog, 350, 120)
        
        # Message
        message_label = ttkb.Label(
            self.dialog, 
            text=message, 
            wraplength=300,
            justify="center"
        )
        message_label.pack(pady=20)
        
        # Buttons
        button_frame = ttkb.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        confirm_btn = ttkb.Button(
            button_frame, 
            text=confirm_text, 
            command=self._on_confirm,
            style="success.TButton"
        )
        confirm_btn.pack(side="left", padx=10)
        
        cancel_btn = ttkb.Button(
            button_frame, 
            text=cancel_text, 
            command=self._on_cancel
        )
        cancel_btn.pack(side="left", padx=10)
        
        # Bind Enter and Escape keys
        self.dialog.bind('<Return>', lambda e: self._on_confirm())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
        
        # Focus on confirm button
        confirm_btn.focus_set()
    
    def _on_confirm(self):
        """Handle confirm button."""
        self.result = True
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle cancel button."""
        self.result = False
        self.dialog.destroy()
    
    def show(self) -> bool:
        """Show dialog and return result."""
        self.dialog.wait_window()
        return self.result


class TextInputDialog:
    """Reusable text input dialog."""
    
    def __init__(self, parent: tk.Widget, title: str, prompt: str,
                 initial_value: str = "", validate_callback: Optional[Callable] = None):
        self.result = None
        self.validate_callback = validate_callback
        
        # Create dialog
        self.dialog = ttkb.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        from ..core.utils import center_window
        center_window(self.dialog, 400, 150)
        
        # Prompt
        prompt_label = ttkb.Label(self.dialog, text=prompt)
        prompt_label.pack(pady=10)
        
        # Entry
        self.entry_var = tk.StringVar(value=initial_value)
        self.entry = ttkb.Entry(
            self.dialog, 
            textvariable=self.entry_var, 
            width=40
        )
        self.entry.pack(pady=10)
        self.entry.focus_set()
        self.entry.select_range(0, tk.END)
        
        # Buttons
        button_frame = ttkb.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ok_btn = ttkb.Button(
            button_frame, 
            text="OK", 
            command=self._on_ok,
            style="success.TButton"
        )
        ok_btn.pack(side="left", padx=10)
        
        cancel_btn = ttkb.Button(
            button_frame, 
            text="Cancel", 
            command=self._on_cancel
        )
        cancel_btn.pack(side="left", padx=10)
        
        # Bind Enter and Escape keys
        self.dialog.bind('<Return>', lambda e: self._on_ok())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
    
    def _on_ok(self):
        """Handle OK button."""
        value = self.entry_var.get().strip()
        
        # Validate if callback provided
        if self.validate_callback and not self.validate_callback(value):
            return  # Don't close dialog if validation fails
        
        self.result = value
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle cancel button."""
        self.result = None
        self.dialog.destroy()
    
    def show(self) -> Optional[str]:
        """Show dialog and return result."""
        self.dialog.wait_window()
        return self.result


class StatusBar:
    """Reusable status bar component."""
    
    def __init__(self, parent: tk.Widget):
        self.frame = ttkb.Frame(parent, relief="sunken", borderwidth=1)
        
        # Status indicator
        self.status_label = ttkb.Label(self.frame, text="● Ready")
        self.status_label.pack(side="left", padx=5)
        
        # Separator
        ttkb.Separator(self.frame, orient="vertical").pack(side="left", fill="y", padx=5)
        
        # Additional info sections
        self.info_sections = {}
    
    def pack(self, **kwargs):
        """Pack the status bar."""
        self.frame.pack(**kwargs)
    
    def set_status(self, message: str, color: str = "black"):
        """Set the main status message."""
        self.status_label.config(text=f"● {message}", foreground=color)
    
    def add_section(self, name: str, text: str = ""):
        """Add a new info section."""
        if name not in self.info_sections:
            # Add separator
            ttkb.Separator(self.frame, orient="vertical").pack(side="left", fill="y", padx=5)
            
            # Add label
            label = ttkb.Label(self.frame, text=text)
            label.pack(side="left", padx=5)
            self.info_sections[name] = label
    
    def update_section(self, name: str, text: str):
        """Update an info section."""
        if name in self.info_sections:
            self.info_sections[name].config(text=text)
    
    def remove_section(self, name: str):
        """Remove an info section."""
        if name in self.info_sections:
            self.info_sections[name].destroy()
            del self.info_sections[name]


class SearchableCombobox(ttkb.Combobox):
    """Enhanced combobox with search functionality."""
    
    def __init__(self, parent, values=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.all_values = values or []
        self['values'] = self.all_values
        
        # Bind events for search functionality
        self.bind('<KeyRelease>', self._on_keyrelease)
        self.bind('<Button-1>', self._on_click)
    
    def _on_keyrelease(self, event):
        """Handle key release for search functionality."""
        current_text = self.get().lower()
        
        if current_text:
            # Filter values based on current text
            filtered_values = [
                value for value in self.all_values 
                if current_text in value.lower()
            ]
            self['values'] = filtered_values
        else:
            self['values'] = self.all_values
    
    def _on_click(self, event):
        """Handle click to show all values."""
        self['values'] = self.all_values
    
    def set_values(self, values):
        """Update the list of values."""
        self.all_values = values
        self['values'] = values


def create_labeled_frame(parent: tk.Widget, text: str, **kwargs) -> tuple[ttkb.LabelFrame, ttkb.Frame]:
    """Create a labeled frame with an inner content frame."""
    label_frame = ttkb.LabelFrame(parent, text=text, **kwargs)
    content_frame = ttkb.Frame(label_frame, padding=10)
    content_frame.pack(fill="both", expand=True)
    return label_frame, content_frame


def create_button_row(parent: tk.Widget, buttons: list[dict], **kwargs) -> ttkb.Frame:
    """Create a row of buttons with consistent spacing."""
    button_frame = ttkb.Frame(parent)
    
    for i, btn_config in enumerate(buttons):
        btn = ttkb.Button(
            button_frame,
            text=btn_config.get('text', 'Button'),
            command=btn_config.get('command'),
            style=btn_config.get('style', 'TButton')
        )
        
        # Add padding except for the first button
        padx = (10, 0) if i > 0 else 0
        btn.pack(side="left", padx=padx)
        
        # Add tooltip if provided
        if 'tooltip' in btn_config:
            Tooltip(btn, btn_config['tooltip'])
    
    return button_frame
