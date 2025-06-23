"""
TaskMover UI Framework - Common Input Components
"""
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional, List, Union
import re
from .base_component import BaseComponent, ComponentState


class TextInput(BaseComponent):
    """
    Single-line text input component with validation and formatting support.
    """
    
    def __init__(self, parent: tk.Widget,
                 placeholder: str = "",
                 max_length: Optional[int] = None,
                 input_type: str = "text",  # text, email, password, number
                 mask: Optional[str] = None,
                 show_clear_button: bool = False,
                 **kwargs):
        """
        Initialize the text input.
        
        Args:
            parent: Parent widget
            placeholder: Placeholder text
            max_length: Maximum character length
            input_type: Type of input (text, email, password, number)
            mask: Input mask pattern
            show_clear_button: Whether to show clear button
            **kwargs: Additional widget options
        """
        self.placeholder = placeholder
        self.max_length = max_length
        self.input_type = input_type
        self.mask = mask
        self.show_clear_button = show_clear_button
        self._placeholder_active = False
        self._last_valid_value = ""
        
        super().__init__(parent, **kwargs)
        
        self._setup_validation()
        self._setup_placeholder()
        if show_clear_button:
            self._setup_clear_button()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the Entry widget."""
        entry_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['placeholder', 'max_length', 'input_type', 'mask', 'show_clear_button']}
        
        if self.input_type == "password":
            entry_kwargs['show'] = '*'
        
        return tk.Entry(self.parent, **entry_kwargs)
    
    def _setup_default_bindings(self):
        """Setup default event bindings."""
        super()._setup_default_bindings()
        
        self._widget.bind('<KeyRelease>', self._on_key_release)
        self._widget.bind('<FocusIn>', self._on_focus_in_input)
        self._widget.bind('<FocusOut>', self._on_focus_out_input)
        
        # Validation on change
        vcmd = (self._widget.register(self._validate_input), '%P', '%S')
        self._widget.configure(validate='key', validatecommand=vcmd)
    
    def _setup_validation(self):
        """Setup input type-specific validation."""
        if self.input_type == "email":
            self.add_validator(self._validate_email)
        elif self.input_type == "number":
            self.add_validator(self._validate_number)
    
    def _setup_placeholder(self):
        """Setup placeholder text functionality."""
        if self.placeholder:
            self._show_placeholder()
    
    def _setup_clear_button(self):
        """Setup clear button functionality."""
        # This would be implemented as an overlay button
        # For now, we'll use a keyboard shortcut
        self._widget.bind('<Control-l>', lambda e: self.clear())
    
    def _validate_input(self, new_value: str, char: str) -> bool:
        """Validate input during typing."""
        # Check max length
        if self.max_length and len(new_value) > self.max_length:
            return False
        
        # Apply input mask
        if self.mask:
            if not self._matches_mask(new_value):
                return False
        
        # Type-specific validation during typing
        if self.input_type == "number":
            if new_value and not re.match(r'^-?\d*\.?\d*$', new_value):
                return False
        
        return True
    
    def _matches_mask(self, value: str) -> bool:
        """Check if value matches the input mask."""
        # Simple mask implementation (can be extended)
        # 9 = digit, A = letter, * = any character
        if not self.mask:
            return True
        
        if len(value) > len(self.mask):
            return False
        
        for i, char in enumerate(value):
            if i >= len(self.mask):
                return False
            
            mask_char = self.mask[i]
            if mask_char == '9' and not char.isdigit():
                return False
            elif mask_char == 'A' and not char.isalpha():
                return False
            elif mask_char not in ['9', 'A', '*'] and char != mask_char:
                return False
        
        return True
    
    def _validate_email(self, value: str) -> tuple[bool, str]:
        """Validate email format."""
        if not value:
            return True, ""
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, value):
            return True, ""
        else:
            return False, "Please enter a valid email address"
    
    def _validate_number(self, value: str) -> tuple[bool, str]:
        """Validate number format."""
        if not value:
            return True, ""
        
        try:
            float(value)
            return True, ""
        except ValueError:
            return False, "Please enter a valid number"
    
    def _on_key_release(self, event=None):
        """Handle key release events."""
        self.trigger_event('value_changed', self.get_value())
        
        # Update placeholder state
        if self.placeholder:
            if self.get_value() and self._placeholder_active:
                self._hide_placeholder()
            elif not self.get_value() and not self._placeholder_active:
                self._show_placeholder()
    
    def _on_focus_in_input(self, event=None):
        """Handle focus in for input."""
        super()._on_focus_in(event)
        if self.placeholder and self._placeholder_active:
            self._hide_placeholder()
    
    def _on_focus_out_input(self, event=None):
        """Handle focus out for input."""
        super()._on_focus_out(event)
        if self.placeholder and not self.get_value():
            self._show_placeholder()
        
        # Run validation
        self.validate()
    
    def _show_placeholder(self):
        """Show placeholder text."""
        if not self._placeholder_active and not self.get_value():
            self._placeholder_active = True
            self._widget.configure(foreground='gray')
            self._widget.insert(0, self.placeholder)
    
    def _hide_placeholder(self):
        """Hide placeholder text."""
        if self._placeholder_active:
            self._placeholder_active = False
            self._widget.delete(0, tk.END)
            if self.theme_manager:
                style = self.theme_manager.get_component_style('TextInput', self.state.value)
                if 'foreground' in style:
                    self._widget.configure(foreground=style['foreground'])
    
    def get_value(self) -> str:
        """Get the current input value."""
        value = self._widget.get()
        return "" if self._placeholder_active else value
    
    def set_value(self, value: str):
        """Set the input value."""
        if self._placeholder_active:
            self._hide_placeholder()
        
        self._widget.delete(0, tk.END)
        if value:
            self._widget.insert(0, value)
        elif self.placeholder:
            self._show_placeholder()
    
    def clear(self):
        """Clear the input value."""
        self.set_value("")
    
    def select_all(self):
        """Select all text in the input."""
        if not self._placeholder_active:
            self._widget.select_range(0, tk.END)
    
    def set_placeholder(self, placeholder: str):
        """Update the placeholder text."""
        old_placeholder_active = self._placeholder_active
        if old_placeholder_active:
            self._hide_placeholder()
        
        self.placeholder = placeholder
        
        if old_placeholder_active or not self.get_value():
            self._show_placeholder()


class TextArea(BaseComponent):
    """
    Multi-line text input component with scrolling and optional features.
    """
    
    def __init__(self, parent: tk.Widget,
                 height: int = 10,
                 width: int = 40,
                 wrap: str = tk.WORD,
                 show_line_numbers: bool = False,
                 syntax_highlighting: bool = False,
                 **kwargs):
        """
        Initialize the text area.
        
        Args:
            parent: Parent widget
            height: Height in lines
            width: Width in characters
            wrap: Text wrapping mode
            show_line_numbers: Whether to show line numbers
            syntax_highlighting: Whether to enable syntax highlighting
            **kwargs: Additional widget options
        """
        self.height = height
        self.width = width
        self.wrap = wrap
        self.show_line_numbers = show_line_numbers
        self.syntax_highlighting = syntax_highlighting
        
        super().__init__(parent, **kwargs)
        
        if show_line_numbers:
            self._setup_line_numbers()
        
        if syntax_highlighting:
            self._setup_syntax_highlighting()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the Text widget with scrollbar."""
        # Create a frame to hold text and scrollbar
        frame = ttk.Frame(self.parent)
        
        # Create text widget
        text_kwargs = {k: v for k, v in kwargs.items() 
                      if k not in ['height', 'width', 'wrap', 'show_line_numbers', 'syntax_highlighting']}
        
        self.text_widget = tk.Text(frame, 
                                  height=self.height,
                                  width=self.width,
                                  wrap=self.wrap,
                                  **text_kwargs)
        
        # Create scrollbar
        self.scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)
        
        # Layout
        self.text_widget.grid(row=0, column=0, sticky='nsew')
        self.scrollbar.grid(row=0, column=1, sticky='ns')
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        return frame
    
    def _setup_default_bindings(self):
        """Setup default event bindings."""
        # Bind events to the text widget instead of the frame
        if hasattr(self, 'text_widget'):
            self.text_widget.bind('<KeyRelease>', self._on_key_release)
            self.text_widget.bind('<FocusIn>', self._on_focus_in)
            self.text_widget.bind('<FocusOut>', self._on_focus_out)
            self.text_widget.bind('<Button-1>', self._on_click)
    
    def _setup_line_numbers(self):
        """Setup line number display."""
        # This would create a separate text widget for line numbers
        # Implementation placeholder
        pass
    
    def _setup_syntax_highlighting(self):
        """Setup syntax highlighting."""
        # This would implement syntax highlighting using text tags
        # Implementation placeholder
        pass
    
    def _on_key_release(self, event=None):
        """Handle key release events."""
        self.trigger_event('value_changed', self.get_value())
    
    def get_value(self) -> str:
        """Get the current text content."""
        if hasattr(self, 'text_widget'):
            return self.text_widget.get('1.0', tk.END).rstrip('\n')
        return ""
    
    def set_value(self, value: str):
        """Set the text content."""
        if hasattr(self, 'text_widget'):
            self.text_widget.delete('1.0', tk.END)
            self.text_widget.insert('1.0', value)
    
    def clear(self):
        """Clear the text content."""
        self.set_value("")
    
    def insert_text(self, text: str, position: str = tk.INSERT):
        """Insert text at the specified position."""
        if hasattr(self, 'text_widget'):
            self.text_widget.insert(position, text)
    
    def get_selection(self) -> str:
        """Get the selected text."""
        if hasattr(self, 'text_widget'):
            try:
                return self.text_widget.selection_get()
            except tk.TclError:
                return ""
        return ""
    
    def set_readonly(self, readonly: bool):
        """Set the text area to readonly mode."""
        if hasattr(self, 'text_widget'):
            state = tk.DISABLED if readonly else tk.NORMAL
            self.text_widget.configure(state=state)


class Button(BaseComponent):
    """
    Clickable button component with various styles and states.
    """
    
    def __init__(self, parent: tk.Widget,
                 text: str = "",
                 command: Optional[Callable] = None,
                 icon: Optional[str] = None,
                 style: str = "primary",  # primary, secondary, outline, ghost
                 size: str = "medium",    # small, medium, large
                 loading: bool = False,
                 **kwargs):
        """
        Initialize the button.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Command to execute on click
            icon: Icon name/path
            style: Button style variant
            size: Button size
            loading: Whether button is in loading state
            **kwargs: Additional widget options
        """
        self.text = text
        self.command = command
        self.icon = icon
        self.button_style = style
        self.size = size
        self.loading = loading
        
        super().__init__(parent, **kwargs)
        
        if command:
            self.bind_event('click', lambda *args: command())
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the Button widget."""
        button_kwargs = {k: v for k, v in kwargs.items() 
                        if k not in ['text', 'command', 'icon', 'style', 'size', 'loading']}
        
        return tk.Button(self.parent, 
                        text=self.text,
                        command=self._on_button_click,
                        **button_kwargs)
    
    def _on_button_click(self):
        """Handle button click."""
        if not self.loading and self.enabled:
            self.trigger_event('click')
    
    def set_text(self, text: str):
        """Set the button text."""
        self.text = text
        self._widget.configure(text=text)
    
    def set_loading(self, loading: bool):
        """Set the loading state."""
        if loading != self.loading:
            self.loading = loading
            if loading:
                self._widget.configure(text="Loading...", state='disabled')
            else:
                self._widget.configure(text=self.text, state='normal' if self.enabled else 'disabled')
    
    def set_command(self, command: Callable):
        """Set the button command."""
        self.command = command
    
    def click(self):
        """Programmatically click the button."""
        if not self.loading and self.enabled:
            self._on_button_click()


class IconButton(Button):
    """
    Icon-only button component.
    """
    
    def __init__(self, parent: tk.Widget,
                 icon: str,
                 command: Optional[Callable] = None,
                 tooltip: Optional[str] = None,
                 size: str = "medium",
                 shape: str = "square",  # square, circle
                 **kwargs):
        """
        Initialize the icon button.
        
        Args:
            parent: Parent widget
            icon: Icon name/character
            command: Command to execute on click
            tooltip: Tooltip text
            size: Button size
            shape: Button shape
            **kwargs: Additional widget options
        """
        self.shape = shape
        self.tooltip = tooltip
        
        super().__init__(parent, text=icon, command=command, size=size, **kwargs)
        
        if tooltip:
            self._setup_tooltip()
    
    def _setup_tooltip(self):
        """Setup tooltip functionality."""
        # LOGIC INTEGRATION POINT: Connect to tooltip system
        pass


class Checkbox(BaseComponent):
    """
    Boolean input checkbox component.
    """
    
    def __init__(self, parent: tk.Widget,
                 text: str = "",
                 checked: bool = False,
                 indeterminate: bool = False,
                 **kwargs):
        """
        Initialize the checkbox.
        
        Args:
            parent: Parent widget
            text: Checkbox label text
            checked: Initial checked state
            indeterminate: Whether to show indeterminate state
            **kwargs: Additional widget options
        """
        self.text = text
        self._checked = checked
        self._indeterminate = indeterminate
        self._var = tk.BooleanVar(value=checked)
        
        super().__init__(parent, **kwargs)
        
        self._var.trace('w', self._on_value_changed)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the Checkbutton widget."""
        checkbox_kwargs = {k: v for k, v in kwargs.items() 
                          if k not in ['text', 'checked', 'indeterminate']}
        
        return tk.Checkbutton(self.parent,
                             text=self.text,
                             variable=self._var,
                             **checkbox_kwargs)
    
    def _on_value_changed(self, *args):
        """Handle value change."""
        self._checked = self._var.get()
        self._indeterminate = False
        self.trigger_event('value_changed', self._checked)
    
    def get_value(self) -> bool:
        """Get the checkbox state."""
        return self._checked
    
    def set_value(self, value: bool):
        """Set the checkbox state."""
        self._checked = value
        self._indeterminate = False
        self._var.set(value)
    
    def set_indeterminate(self, indeterminate: bool):
        """Set indeterminate state."""
        self._indeterminate = indeterminate
        if indeterminate:
            # Implementation placeholder for indeterminate state
            pass
    
    def toggle(self):
        """Toggle the checkbox state."""
        self.set_value(not self._checked)


class RadioButton(BaseComponent):
    """
    Single-choice radio button component.
    """
    
    def __init__(self, parent: tk.Widget,
                 text: str = "",
                 value: Any = None,
                 variable: Optional[tk.Variable] = None,
                 **kwargs):
        """
        Initialize the radio button.
        
        Args:
            parent: Parent widget
            text: Radio button label text
            value: Value when selected
            variable: Shared variable for radio group
            **kwargs: Additional widget options
        """
        self.text = text
        self.value = value
        self._variable = variable or tk.StringVar()
        
        super().__init__(parent, **kwargs)
        
        self._variable.trace('w', self._on_value_changed)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the Radiobutton widget."""
        radio_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['text', 'value', 'variable']}
        
        return tk.Radiobutton(self.parent,
                             text=self.text,
                             value=self.value,
                             variable=self._variable,
                             **radio_kwargs)
    
    def _on_value_changed(self, *args):
        """Handle value change."""
        self.trigger_event('value_changed', self._variable.get())
    
    def get_value(self) -> Any:
        """Get the current value."""
        return self._variable.get()
    
    def set_value(self, value: Any):
        """Set the radio button value."""
        self._variable.set(value)
    
    def is_selected(self) -> bool:
        """Check if this radio button is selected."""
        return self._variable.get() == self.value
    
    def select(self):
        """Select this radio button."""
        self._variable.set(self.value)
