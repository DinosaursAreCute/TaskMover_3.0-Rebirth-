"""
Input Components
===============

Modern input components including smart pattern input, checkboxes,
dropdowns, and form validation with accessibility features.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable, Any, Union
import re
import logging

from .base_component import BaseComponent, ComponentState
from .theme_manager import get_theme_manager

logger = logging.getLogger(__name__)


class SmartPatternInput(BaseComponent):
    """
    Smart pattern input with auto-completion, validation, and suggestions.
    Implements the enhanced pattern input from the UI specification.
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        placeholder: str = "Enter pattern...",
        **kwargs
    ):
        self.placeholder = placeholder
        self.current_value = ""
        self.suggestions = []
        self.validation_result = {"valid": False, "message": "", "matches": 0}
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create smart pattern input UI."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Main input frame
        self.input_frame = tk.Frame(self, bg=tokens.colors["background"])
        self.input_frame.pack(fill="x", padx=tokens.spacing["md"], pady=tokens.spacing["sm"])
        
        # Input field with search icon
        input_container = tk.Frame(self.input_frame, bg="white", relief="solid", bd=1)
        input_container.pack(fill="x")
        
        self.entry = tk.Entry(
            input_container,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            bg="white",
            fg=tokens.colors["text"],
            bd=0,
            relief="flat"
        )
        self.entry.pack(side="left", fill="both", expand=True, padx=tokens.spacing["sm"], pady=tokens.spacing["xs"])
        
        # Search icon
        search_icon = tk.Label(
            input_container,
            text="🔍",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            bg="white",
            fg=tokens.colors["text_secondary"]
        )
        search_icon.pack(side="right", padx=tokens.spacing["xs"])
        
        # Validation status
        self.status_frame = tk.Frame(self.input_frame, bg=tokens.colors["background"])
        self.status_frame.pack(fill="x", pady=(tokens.spacing["xs"], 0))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["success"],
            anchor="w"
        )
        self.status_label.pack(fill="x")
        
        # Suggestions panel
        self.suggestions_frame = tk.Frame(self, bg=tokens.colors["background"])
        self.suggestions_frame.pack(fill="x", padx=tokens.spacing["md"])
        
        # Quick groups
        groups_label = tk.Label(
            self.suggestions_frame,
            text="💡 Suggestions:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text_secondary"],
            anchor="w"
        )
        groups_label.pack(fill="x", pady=(tokens.spacing["sm"], tokens.spacing["xs"]))
        
        # Quick group buttons
        self.groups_container = tk.Frame(self.suggestions_frame, bg=tokens.colors["background"])
        self.groups_container.pack(fill="x")
        
        # Setup default suggestions
        self._setup_default_suggestions()
        
        # Options checkboxes
        self.options_frame = tk.Frame(self, bg=tokens.colors["background"])
        self.options_frame.pack(fill="x", padx=tokens.spacing["md"], pady=(tokens.spacing["md"], 0))
        
        options_label = tk.Label(
            self.options_frame,
            text="Options:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            anchor="w"
        )
        options_label.pack(fill="x")
        
        # Checkbox options
        checkbox_frame = tk.Frame(self.options_frame, bg=tokens.colors["background"])
        checkbox_frame.pack(fill="x", pady=tokens.spacing["xs"])
        
        # Case Sensitive
        self.case_sensitive_var = tk.BooleanVar()
        self.case_sensitive_cb = tk.Checkbutton(
            checkbox_frame,
            text="Case Sensitive",
            variable=self.case_sensitive_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            activebackground=tokens.colors["background"],
            selectcolor="white",
            command=self._on_option_changed
        )
        self.case_sensitive_cb.pack(side="left", padx=(0, tokens.spacing["lg"]))
        
        # Include Hidden Files
        self.hidden_files_var = tk.BooleanVar()
        self.hidden_files_cb = tk.Checkbutton(
            checkbox_frame,
            text="Include Hidden Files",
            variable=self.hidden_files_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            activebackground=tokens.colors["background"],
            selectcolor="white",
            command=self._on_option_changed
        )
        self.hidden_files_cb.pack(side="left", padx=(0, tokens.spacing["lg"]))
        
        # Recursive
        self.recursive_var = tk.BooleanVar(value=True)
        self.recursive_cb = tk.Checkbutton(
            checkbox_frame,
            text="Recursive",
            variable=self.recursive_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            activebackground=tokens.colors["background"],
            selectcolor="white",
            command=self._on_option_changed
        )
        self.recursive_cb.pack(side="left")
        
        # Bind events
        self.entry.bind("<KeyRelease>", self._on_text_changed)
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        
        # Initial placeholder
        self._show_placeholder()
    
    def _setup_default_suggestions(self):
        """Setup default pattern suggestions."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        suggestions = [
            ("@documents", "Office files"),
            ("size > 10MB", "Large files"),
            ("modified > today-7", "Recent files"),
            ("@media", "Images & videos"),
            ("@code", "Source code"),
            ("@archives", "Compressed files"),
        ]
        
        for suggestion, tooltip in suggestions:
            btn = tk.Button(
                self.groups_container,
                text=suggestion,
                font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
                bg=tokens.colors["surface"],
                fg=tokens.colors["text"],
                relief="solid",
                bd=1,
                padx=tokens.spacing["sm"],
                pady=tokens.spacing["xs"],
                cursor="hand2",
                command=lambda s=suggestion: self._insert_suggestion(s)
            )
            btn.pack(side="left", padx=(0, tokens.spacing["xs"]))
            
            # Hover effects
            def make_hover_handler(button):
                def on_enter(e):
                    button.configure(bg=tokens.colors["hover"])
                def on_leave(e):
                    button.configure(bg=tokens.colors["surface"])
                return on_enter, on_leave
            
            enter_handler, leave_handler = make_hover_handler(btn)
            btn.bind("<Enter>", enter_handler)
            btn.bind("<Leave>", leave_handler)
    
    def _show_placeholder(self):
        """Show placeholder text."""
        if not self.current_value:
            self.entry.configure(fg=get_theme_manager().get_current_tokens().colors["text_disabled"])
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.placeholder)
    
    def _hide_placeholder(self):
        """Hide placeholder text."""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=get_theme_manager().get_current_tokens().colors["text"])
    
    def _on_focus_in(self, event):
        """Handle focus in."""
        self._hide_placeholder()
        super()._on_focus_in(event)
    
    def _on_focus_out(self, event):
        """Handle focus out."""
        if not self.entry.get():
            self._show_placeholder()
        super()._on_focus_out(event)
    
    def _on_text_changed(self, event):
        """Handle text changes with validation."""
        current_text = self.entry.get()
        
        # Don't validate placeholder text
        if current_text == self.placeholder:
            return
        
        self.current_value = current_text
        
        # Validate pattern
        self._validate_pattern(current_text)
        
        # Trigger callback
        self._trigger_callback('text_changed', {
            'text': current_text,
            'validation': self.validation_result
        })
    
    def _validate_pattern(self, pattern: str):
        """Validate pattern syntax and estimate matches."""
        if not pattern.strip():
            self.validation_result = {"valid": False, "message": "", "matches": 0}
            self.status_label.configure(text="", fg=get_theme_manager().get_current_tokens().colors["text_secondary"])
            return
        
        try:
            # Basic pattern validation
            valid = True
            message = "✓ Valid pattern"
            matches = self._estimate_matches(pattern)
            
            # Check for basic syntax errors
            if pattern.count("(") != pattern.count(")"):
                valid = False
                message = "✗ Unmatched parentheses"
            elif "AND AND" in pattern or "OR OR" in pattern:
                valid = False
                message = "✗ Invalid operator sequence"
            
            self.validation_result = {
                "valid": valid,
                "message": message,
                "matches": matches,
                "performance": "Fast" if matches < 1000 else "Moderate"
            }
            
            # Update status display
            if valid:
                status_text = f"{message} • 🎯 {matches} files match • Estimated performance: {self.validation_result['performance']}"
                color = get_theme_manager().get_current_tokens().colors["success"]
            else:
                status_text = message
                color = get_theme_manager().get_current_tokens().colors["error"]
            
            self.status_label.configure(text=status_text, fg=color)
            
        except Exception as e:
            self.validation_result = {"valid": False, "message": f"✗ Validation error: {str(e)}", "matches": 0}
            self.status_label.configure(
                text=self.validation_result["message"],
                fg=get_theme_manager().get_current_tokens().colors["error"]
            )
    
    def _estimate_matches(self, pattern: str) -> int:
        """Estimate number of files that would match pattern."""
        # This is a simplified estimation - in real implementation,
        # this would query the actual file system or cache
        import random
        return random.randint(1, 100)  # Placeholder implementation
    
    def _insert_suggestion(self, suggestion: str):
        """Insert suggestion into input."""
        current_text = self.entry.get()
        
        # Clear placeholder
        if current_text == self.placeholder:
            current_text = ""
        
        # Add suggestion with appropriate separator
        if current_text and not current_text.endswith(" "):
            if not current_text.endswith(" AND ") and not current_text.endswith(" OR "):
                current_text += " AND "
        
        new_text = current_text + suggestion
        
        self.entry.delete(0, tk.END)
        self.entry.insert(0, new_text)
        self.entry.configure(fg=get_theme_manager().get_current_tokens().colors["text"])
        
        # Validate new text
        self._validate_pattern(new_text)
        self.current_value = new_text
        
        # Trigger callback
        self._trigger_callback('suggestion_inserted', {'suggestion': suggestion, 'new_text': new_text})
    
    def _on_option_changed(self):
        """Handle option checkbox changes."""
        options = {
            'case_sensitive': self.case_sensitive_var.get(),
            'include_hidden': self.hidden_files_var.get(),
            'recursive': self.recursive_var.get()
        }
        
        # Re-validate with new options
        self._validate_pattern(self.current_value)
        
        # Trigger callback
        self._trigger_callback('options_changed', options)
    
    def get_pattern(self) -> str:
        """Get current pattern value."""
        text = self.entry.get()
        return text if text != self.placeholder else ""
    
    def set_pattern(self, pattern: str):
        """Set pattern value."""
        self.entry.delete(0, tk.END)
        if pattern:
            self.entry.insert(0, pattern)
            self.entry.configure(fg=get_theme_manager().get_current_tokens().colors["text"])
        elif self.placeholder:
            self._show_placeholder()
        
        # Validate the new pattern
        self._validate_pattern(pattern)
    
    def get_options(self) -> Dict[str, bool]:
        """Get current options."""
        return {
            "case_sensitive": self.case_sensitive_var.get(),
            "include_hidden": self.hidden_files_var.get(),
            "recursive": self.recursive_var.get()
        }
    
    def set_options(self, options: Dict[str, bool]):
        """Set options."""
        if "case_sensitive" in options:
            self.case_sensitive_var.set(options["case_sensitive"])
        if "include_hidden" in options:
            self.hidden_files_var.set(options["include_hidden"])
        if "recursive" in options:
            self.recursive_var.set(options["recursive"])
        
        self._on_option_changed()

    def get_value(self) -> str:
        """Get current pattern value (alias for get_pattern)."""
        return self.get_pattern()
    
    def set_value(self, value: str):
        """Set pattern value (alias for set_pattern)."""
        self.set_pattern(value)

    # ...existing code...


class ModernEntry(BaseComponent):
    """Modern text entry with validation and styling."""
    
    def __init__(
        self,
        parent: tk.Widget,
        placeholder: str = "",
        validation_func: Optional[Callable] = None,
        textvariable: Optional[tk.StringVar] = None,
        **kwargs
    ):
        # Filter out custom parameters that shouldn't go to tkinter Frame
        custom_params = {
            'placeholder', 'validation_func', 'textvariable'
        }
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in custom_params}
        
        self.placeholder = placeholder
        self.validation_func = validation_func
        self.textvariable = textvariable
        self.is_valid = True
        
        super().__init__(parent, **filtered_kwargs)
    
    def _create_component(self):
        """Create entry UI."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Entry container
        self.entry_container = tk.Frame(self, bg="white", relief="solid", bd=1)
        self.entry_container.pack(fill="x", padx=tokens.spacing["sm"], pady=tokens.spacing["xs"])
        
        # Entry field
        entry_kwargs = {
            'font': (tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            'bg': "white",
            'fg': tokens.colors["text"],
            'bd': 0,
            'relief': "flat"
        }
        
        # Add textvariable if provided
        if self.textvariable:
            entry_kwargs['textvariable'] = self.textvariable
        
        self.entry = tk.Entry(self.entry_container, **entry_kwargs)
        self.entry.pack(fill="both", expand=True, padx=tokens.spacing["sm"], pady=tokens.spacing["xs"])
        
        # Validation message
        self.validation_label = tk.Label(
            self,
            text="",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg=self.theme.background,
            fg=tokens.colors["error"],
            anchor="w"
        )
        self.validation_label.pack(fill="x", padx=tokens.spacing["sm"])
        
        # Bind events
        self.entry.bind("<KeyRelease>", self._on_text_changed)
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        
        # Show placeholder if needed
        if self.placeholder:
            self._show_placeholder()
    
    def _show_placeholder(self):
        """Show placeholder text."""
        if not self.entry.get():
            self.entry.configure(fg=get_theme_manager().get_current_tokens().colors["text_disabled"])
            self.entry.insert(0, self.placeholder)
    
    def _hide_placeholder(self):
        """Hide placeholder text."""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=get_theme_manager().get_current_tokens().colors["text"])
    
    def _on_focus_in(self, event):
        """Handle focus in."""
        self._hide_placeholder()
        
        # Update border color
        self.entry_container.configure(highlightbackground=get_theme_manager().get_current_tokens().colors["primary"])
        
        super()._on_focus_in(event)
    
    def _on_focus_out(self, event):
        """Handle focus out."""
        if not self.entry.get():
            self._show_placeholder()
        
        # Reset border color
        self.entry_container.configure(highlightbackground=get_theme_manager().get_current_tokens().colors["border"])
        
        super()._on_focus_out(event)
    
    def _on_text_changed(self, event):
        """Handle text changes."""
        text = self.entry.get()
        
        # Don't validate placeholder
        if text == self.placeholder:
            return
        
        # Validate if function provided
        if self.validation_func:
            try:
                self.is_valid = self.validation_func(text)
                if self.is_valid:
                    self.validation_label.configure(text="")
                    self.entry_container.configure(relief="solid", bd=1)
                else:
                    self.validation_label.configure(text="Invalid input")
                    self.entry_container.configure(relief="solid", bd=2)
            except Exception as e:
                self.is_valid = False
                self.validation_label.configure(text=str(e))
        
        # Trigger callback
        self._trigger_callback('text_changed', {'text': text, 'valid': self.is_valid})
    
    def get_value(self) -> str:
        """Get entry value."""
        text = self.entry.get()
        return text if text != self.placeholder else ""
    
    def set_value(self, value: str):
        """Set entry value."""
        self.entry.delete(0, tk.END)
        if value:
            self.entry.insert(0, value)
            self.entry.configure(fg=get_theme_manager().get_current_tokens().colors["text"])
        elif self.placeholder:
            self._show_placeholder()


class ModernCombobox(BaseComponent):
    """Modern combobox with search and styling."""
    
    def __init__(
        self,
        parent: tk.Widget,
        values: Optional[List[str]] = None,
        textvariable: Optional[tk.StringVar] = None,
        state: str = "readonly",
        width: Optional[int] = None,
        **kwargs
    ):
        # Filter out custom parameters that shouldn't go to tkinter Frame
        custom_params = {
            'values', 'textvariable', 'state', 'width'
        }
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in custom_params}
        
        self.values = values or []
        self.textvariable = textvariable
        self.combobox_state = state
        self.combobox_width = width
        self.selected_value = ""
        
        super().__init__(parent, **filtered_kwargs)
    
    def _create_component(self):
        """Create combobox UI."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Combobox
        combobox_kwargs = {
            'values': self.values,
            'font': (tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            'state': self.combobox_state
        }
        
        # Add optional parameters
        if self.textvariable:
            combobox_kwargs['textvariable'] = self.textvariable
        if self.combobox_width:
            combobox_kwargs['width'] = self.combobox_width
            
        self.combobox = ttk.Combobox(self, **combobox_kwargs)
        self.combobox.pack(fill="x", padx=tokens.spacing["sm"], pady=tokens.spacing["xs"])
        
        # Bind events
        self.combobox.bind("<<ComboboxSelected>>", self._on_selection_changed)
    
    def _on_selection_changed(self, event):
        """Handle selection change."""
        self.selected_value = self.combobox.get()
        self._trigger_callback('selection_changed', {'value': self.selected_value})
    
    def get_value(self) -> str:
        """Get selected value."""
        return self.combobox.get()
    
    def set_value(self, value: str):
        """Set selected value."""
        if value in self.values:
            self.combobox.set(value)
            self.selected_value = value
    
    def set_values(self, values: List[str]):
        """Update available values."""
        self.values = values
        self.combobox.configure(values=values)


# Export main classes
__all__ = [
    "SmartPatternInput",
    "ModernEntry", 
    "ModernCombobox",
]