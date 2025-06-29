"""
Dialog Components
================

Modern dialog components for TaskMover application including
confirmation dialogs, progress dialogs, and notification components.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, Any, Callable, List
import threading
import time
from .base_component import BaseComponent, ModernButton
from .theme_manager import get_theme_manager


class ModernDialog(BaseComponent):
    """Base class for modern dialogs with consistent styling."""
    
    def __init__(self, parent: tk.Widget, title: str = "Dialog", **kwargs):
        self.parent = parent
        self.title = title
        self.result = None
        self.dialog_window: Optional[tk.Toplevel] = None
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create dialog window."""
        self.dialog_window = tk.Toplevel(self.parent)
        self.dialog_window.title(self.title)
        if hasattr(self.parent, 'winfo_toplevel'):
            self.dialog_window.transient(self.parent.winfo_toplevel())
        self.dialog_window.grab_set()
        
        # Configure dialog styling
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        self.dialog_window.configure(bg=tokens.colors["background"])
        self.dialog_window.resizable(False, False)
        
        # Center on parent
        self._center_dialog()
        
        # Create dialog content
        self._create_dialog_content()
        
        # Handle close event
        self.dialog_window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _center_dialog(self):
        """Center dialog on parent window."""
        self.dialog_window.update_idletasks()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog_window.winfo_reqwidth()
        dialog_height = self.dialog_window.winfo_reqheight()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog_window.geometry(f"+{x}+{y}")
    
    def _create_dialog_content(self):
        """Override in subclasses to create dialog content."""
        pass
    
    def _on_close(self):
        """Handle dialog close."""
        self.result = None
        self.dialog_window.destroy()
    
    def show(self) -> Any:
        """Show dialog and return result."""
        self.parent.wait_window(self.dialog_window)
        return self.result


class ConfirmationDialog(ModernDialog):
    """Modern confirmation dialog."""
    
    def __init__(self, parent: tk.Widget, title: str = "Confirm Action", 
                 message: str = "Are you sure?", icon: str = "⚠️", **kwargs):
        self.message = message
        self.icon = icon
        super().__init__(parent, title, **kwargs)
    
    def _create_dialog_content(self):
        """Create confirmation dialog content."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Main frame
        main_frame = tk.Frame(self.dialog_window, bg=tokens.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=tokens.spacing["xl"], pady=tokens.spacing["xl"])
        
        # Icon and message frame
        content_frame = tk.Frame(main_frame, bg=tokens.colors["background"])
        content_frame.pack(fill="x", pady=(0, tokens.spacing["xl"]))
        
        # Icon
        icon_label = tk.Label(
            content_frame,
            text=self.icon,
            font=(tokens.fonts["family"], 32, tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["warning"]
        )
        icon_label.pack(side="left", padx=(0, tokens.spacing["lg"]))
        
        # Message
        message_label = tk.Label(
            content_frame,
            text=self.message,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            wraplength=300,
            justify="left"
        )
        message_label.pack(side="left", fill="x", expand=True)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=tokens.colors["background"])
        button_frame.pack(fill="x")
        
        # Buttons
        cancel_btn = ModernButton(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            variant="secondary",
            width=100
        )
        cancel_btn.pack(side="right", padx=(tokens.spacing["sm"], 0))
        
        confirm_btn = ModernButton(
            button_frame,
            text="Confirm",
            command=self._on_confirm,
            variant="primary",
            width=100
        )
        confirm_btn.pack(side="right")
        
        # Bind Enter and Escape keys
        self.dialog_window.bind('<Return>', lambda e: self._on_confirm())
        self.dialog_window.bind('<Escape>', lambda e: self._on_cancel())
        
        # Focus confirm button
        confirm_btn.focus_set()
    
    def _on_confirm(self):
        """Handle confirm action."""
        self.result = True
        self.dialog_window.destroy()
    
    def _on_cancel(self):
        """Handle cancel action."""
        self.result = False
        self.dialog_window.destroy()


class ProgressDialog(ModernDialog):
    """Modern progress dialog for long-running operations."""
    
    def __init__(self, parent: tk.Widget, title: str = "Processing", 
                 message: str = "Please wait...", cancelable: bool = True, **kwargs):
        self.message = message
        self.cancelable = cancelable
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value=message)
        self.cancelled = False
        
        super().__init__(parent, title, **kwargs)
    
    def _create_dialog_content(self):
        """Create progress dialog content."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Main frame
        main_frame = tk.Frame(self.dialog_window, bg=tokens.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=tokens.spacing["xl"], pady=tokens.spacing["xl"])
        
        # Status message
        status_label = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            wraplength=400
        )
        status_label.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            style="Modern.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        # Progress percentage
        self.percentage_label = tk.Label(
            main_frame,
            text="0%",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text_secondary"]
        )
        self.percentage_label.pack(pady=(0, tokens.spacing["lg"]))
        
        # Cancel button (if cancelable)
        if self.cancelable:
            cancel_btn = ModernButton(
                main_frame,
                text="Cancel",
                command=self._on_cancel,
                variant="secondary",
                width=100
            )
            cancel_btn.pack()
        
        # Update progress display
        self._update_progress_display()
    
    def _update_progress_display(self):
        """Update progress percentage display."""
        if self.dialog_window and self.dialog_window.winfo_exists():
            progress = self.progress_var.get()
            self.percentage_label.config(text=f"{progress:.0f}%")
            self.dialog_window.after(100, self._update_progress_display)
    
    def update_progress(self, progress: float, status: Optional[str] = None):
        """Update progress and status."""
        if self.dialog_window and self.dialog_window.winfo_exists():
            self.progress_var.set(min(100, max(0, progress)))
            if status:
                self.status_var.set(status)
            self.dialog_window.update_idletasks()
    
    def _on_cancel(self):
        """Handle cancel action."""
        self.cancelled = True
        self.result = False
        self.dialog_window.destroy()
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self.cancelled


class NotificationManager:
    """Manager for showing toast-style notifications."""
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.notifications: List[tk.Toplevel] = []
        self.notification_count = 0
    
    def show_notification(self, message: str, notification_type: str = "info", 
                         duration: int = 3000, title: Optional[str] = None):
        """Show a toast notification."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Create notification window
        notification = tk.Toplevel(self.parent)
        notification.withdraw()  # Hide initially
        notification.overrideredirect(True)  # Remove window decorations
        notification.attributes('-topmost', True)  # Keep on top
        
        # Configure notification styling
        bg_color = self._get_notification_color(notification_type)
        notification.configure(bg=bg_color)
        
        # Main frame with padding
        main_frame = tk.Frame(notification, bg=bg_color)
        main_frame.pack(fill="both", expand=True, padx=tokens.spacing["md"], pady=tokens.spacing["md"])
        
        # Icon and message
        content_frame = tk.Frame(main_frame, bg=bg_color)
        content_frame.pack(fill="x")
        
        # Icon
        icon = self._get_notification_icon(notification_type)
        icon_label = tk.Label(
            content_frame,
            text=icon,
            font=(tokens.fonts["family"], 16, tokens.fonts["weight_normal"]),
            bg=bg_color,
            fg="white"
        )
        icon_label.pack(side="left", padx=(0, tokens.spacing["sm"]))
        
        # Text content
        text_frame = tk.Frame(content_frame, bg=bg_color)
        text_frame.pack(side="left", fill="x", expand=True)
        
        title_label = None
        if title:
            title_label = tk.Label(
                text_frame,
                text=title,
                font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
                bg=bg_color,
                fg="white",
                anchor="w"
            )
            title_label.pack(fill="x")
        
        message_label = tk.Label(
            text_frame,
            text=message,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg=bg_color,
            fg="white",
            anchor="w",
            wraplength=300
        )
        message_label.pack(fill="x")
        
        # Position notification
        self._position_notification(notification)
        
        # Show notification
        notification.deiconify()
        self.notifications.append(notification)
        
        # Schedule auto-hide
        notification.after(duration, lambda: self._hide_notification(notification))
        
        # Click to dismiss
        def dismiss_notification(event=None):
            self._hide_notification(notification)
        
        notification.bind('<Button-1>', dismiss_notification)
        widgets_to_bind = [main_frame, content_frame, icon_label, text_frame, message_label]
        if title_label:
            widgets_to_bind.append(title_label)
        
        for widget in widgets_to_bind:
            widget.bind('<Button-1>', dismiss_notification)
    
    def _get_notification_color(self, notification_type: str) -> str:
        """Get color for notification type."""
        colors = {
            "info": "#3498db",
            "success": "#27ae60",
            "warning": "#f39c12",
            "error": "#e74c3c"
        }
        return colors.get(notification_type, colors["info"])
    
    def _get_notification_icon(self, notification_type: str) -> str:
        """Get icon for notification type."""
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        return icons.get(notification_type, icons["info"])
    
    def _position_notification(self, notification: tk.Toplevel):
        """Position notification in top-right corner."""
        notification.update_idletasks()
        
        # Get screen dimensions
        screen_width = notification.winfo_screenwidth()
        screen_height = notification.winfo_screenheight()
        
        # Get notification dimensions
        width = notification.winfo_reqwidth()
        height = notification.winfo_reqheight()
        
        # Position in top-right corner with offset for multiple notifications
        x = screen_width - width - 20
        y = 20 + (len(self.notifications) * (height + 10))
        
        notification.geometry(f"+{x}+{y}")
    
    def _hide_notification(self, notification: tk.Toplevel):
        """Hide and destroy notification."""
        if notification in self.notifications:
            self.notifications.remove(notification)
        
        try:
            notification.destroy()
        except tk.TclError:
            pass  # Window already destroyed
        
        # Reposition remaining notifications
        self._reposition_notifications()
    
    def _reposition_notifications(self):
        """Reposition remaining notifications."""
        for i, notification in enumerate(self.notifications):
            try:
                notification.update_idletasks()
                screen_width = notification.winfo_screenwidth()
                width = notification.winfo_reqwidth()
                height = notification.winfo_reqheight()
                
                x = screen_width - width - 20
                y = 20 + (i * (height + 10))
                
                notification.geometry(f"+{x}+{y}")
            except tk.TclError:
                continue  # Window destroyed
    
    def clear_all(self):
        """Clear all notifications."""
        for notification in self.notifications[:]:
            self._hide_notification(notification)


class ConflictResolutionDialog(ModernDialog):
    """Dialog for resolving file conflicts during organization."""
    
    def __init__(self, parent: tk.Widget, source_file: str, target_file: str, 
                 conflict_type: str = "duplicate", **kwargs):
        self.source_file = source_file
        self.target_file = target_file
        self.conflict_type = conflict_type
        self.resolution = None
        
        super().__init__(parent, f"File Conflict - {conflict_type.title()}", **kwargs)
    
    def _create_dialog_content(self):
        """Create conflict resolution dialog content."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Main frame
        main_frame = tk.Frame(self.dialog_window, bg=tokens.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=tokens.spacing["xl"], pady=tokens.spacing["xl"])
        
        # Title
        title_label = tk.Label(
            main_frame,
            text=f"File Conflict Detected: {self.conflict_type.title()}",
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_2"]), tokens.fonts["weight_bold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        title_label.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        # File details frame
        details_frame = tk.LabelFrame(
            main_frame,
            text="File Details",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        details_frame.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        # Source file info
        tk.Label(
            details_frame,
            text="Source:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", padx=tokens.spacing["md"], pady=(tokens.spacing["sm"], 0))
        
        tk.Label(
            details_frame,
            text=self.source_file,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text_secondary"],
            wraplength=400
        ).pack(anchor="w", padx=tokens.spacing["lg"], pady=(0, tokens.spacing["sm"]))
        
        # Target file info
        tk.Label(
            details_frame,
            text="Target:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", padx=tokens.spacing["md"])
        
        tk.Label(
            details_frame,
            text=self.target_file,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text_secondary"],
            wraplength=400
        ).pack(anchor="w", padx=tokens.spacing["lg"], pady=(0, tokens.spacing["md"]))
        
        # Resolution options
        options_frame = tk.LabelFrame(
            main_frame,
            text="Resolution Options",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        options_frame.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        # Resolution buttons
        button_configs = [
            ("Skip", "skip", "Skip this file and continue"),
            ("Replace", "replace", "Replace the target file"),
            ("Rename", "rename", "Rename the source file automatically"),
            ("Manual", "manual", "Choose a new name manually")
        ]
        
        for text, action, description in button_configs:
            btn_frame = tk.Frame(options_frame, bg=tokens.colors["background"])
            btn_frame.pack(fill="x", padx=tokens.spacing["md"], pady=tokens.spacing["xs"])
            
            btn = ModernButton(
                btn_frame,
                text=text,
                command=lambda a=action: self._select_resolution(a),
                variant="secondary",
                width=80
            )
            btn.pack(side="left")
            
            desc_label = tk.Label(
                btn_frame,
                text=description,
                font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
                bg=tokens.colors["background"],
                fg=tokens.colors["text_secondary"]
            )
            desc_label.pack(side="left", padx=(tokens.spacing["md"], 0))
        
        # Cancel button
        cancel_btn = ModernButton(
            main_frame,
            text="Cancel Operation",
            command=self._on_cancel,
            variant="danger",
            width=120
        )
        cancel_btn.pack(pady=(tokens.spacing["lg"], 0))
    
    def _select_resolution(self, action: str):
        """Select resolution action."""
        self.resolution = action
        self.result = action
        self.dialog_window.destroy()
    
    def _on_cancel(self):
        """Handle cancel action."""
        self.resolution = "cancel"
        self.result = "cancel"
        self.dialog_window.destroy()
