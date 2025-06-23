"""
TaskMover UI Framework - Additional Input Components
"""
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional, List, Union, Dict
from .base_component import BaseComponent, ComponentState


class Dropdown(BaseComponent):
    """
    Selection dropdown component with search and multi-select capabilities.
    """
    
    def __init__(self, parent: tk.Widget,
                 options: List[Union[str, Dict[str, Any]]] = None,
                 placeholder: str = "Select an option",
                 searchable: bool = True,
                 multi_select: bool = False,
                 custom_render: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the dropdown.
        
        Args:
            parent: Parent widget
            options: List of options (strings or dicts with 'value' and 'label')
            placeholder: Placeholder text
            searchable: Whether to enable search functionality
            multi_select: Whether to allow multiple selections
            custom_render: Custom rendering function for options
            **kwargs: Additional widget options
        """
        self.options = options or []
        self.placeholder = placeholder
        self.searchable = searchable
        self.multi_select = multi_select
        self.custom_render = custom_render
        self._selected_values = []
        self._filtered_options = self.options.copy()
        self._is_open = False
        
        super().__init__(parent, **kwargs)
        
        self._setup_search()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the dropdown widget structure."""
        # Main container
        container = ttk.Frame(self.parent)
        
        # Display area (shows selected value(s))
        self.display_frame = ttk.Frame(container)
        self.display_frame.pack(fill=tk.X, padx=2, pady=2)
        
        if self.searchable:
            # Use Entry for searchable dropdown
            self.display_widget = tk.Entry(self.display_frame)
            self.display_widget.bind('<KeyRelease>', self._on_search)
        else:
            # Use Label for non-searchable dropdown
            self.display_widget = tk.Label(self.display_frame, text=self.placeholder)
        
        self.display_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Dropdown arrow button
        self.arrow_button = tk.Button(self.display_frame, 
                                     text="▼", 
                                     width=2,
                                     command=self._toggle_dropdown)
        self.arrow_button.pack(side=tk.RIGHT)
        
        # Options listbox (initially hidden)
        self.options_frame = ttk.Frame(container)
        self.options_listbox = tk.Listbox(self.options_frame, 
                                         selectmode=tk.MULTIPLE if self.multi_select else tk.SINGLE,
                                         height=min(10, len(self.options) if self.options else 5))
        
        # Scrollbar for options
        self.options_scrollbar = ttk.Scrollbar(self.options_frame, 
                                              orient=tk.VERTICAL,
                                              command=self.options_listbox.yview)
        self.options_listbox.configure(yscrollcommand=self.options_scrollbar.set)
        
        self.options_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.options_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection events
        self.options_listbox.bind('<<ListboxSelect>>', self._on_selection_change)
        self.options_listbox.bind('<Double-Button-1>', self._on_double_click)
        
        # Populate options
        self._populate_options()
        
        return container
    
    def _setup_default_bindings(self):
        """Setup default event bindings."""
        super()._setup_default_bindings()
        
        # Close dropdown when clicking outside
        self._widget.bind('<FocusOut>', self._on_focus_out_dropdown)
        
        # Keyboard navigation
        if hasattr(self, 'display_widget'):
            self.display_widget.bind('<Down>', lambda e: self._navigate_options(1))
            self.display_widget.bind('<Up>', lambda e: self._navigate_options(-1))
            self.display_widget.bind('<Return>', lambda e: self._select_highlighted())
            self.display_widget.bind('<Escape>', lambda e: self._close_dropdown())
    
    def _setup_search(self):
        """Setup search functionality."""
        if self.searchable and hasattr(self, 'display_widget'):
            self.display_widget.bind('<KeyRelease>', self._on_search)
    
    def _populate_options(self):
        """Populate the options listbox."""
        if hasattr(self, 'options_listbox'):
            self.options_listbox.delete(0, tk.END)
            
            for option in self._filtered_options:
                display_text = self._get_option_display_text(option)
                self.options_listbox.insert(tk.END, display_text)
    
    def _get_option_display_text(self, option: Union[str, Dict[str, Any]]) -> str:
        """Get the display text for an option."""
        if isinstance(option, dict):
            return option.get('label', str(option.get('value', '')))
        return str(option)
    
    def _get_option_value(self, option: Union[str, Dict[str, Any]]) -> Any:
        """Get the value for an option."""
        if isinstance(option, dict):
            return option.get('value', option.get('label'))
        return option
    
    def _toggle_dropdown(self):
        """Toggle the dropdown open/closed state."""
        if self._is_open:
            self._close_dropdown()
        else:
            self._open_dropdown()
    
    def _open_dropdown(self):
        """Open the dropdown options."""
        if not self._is_open:
            self._is_open = True
            self.options_frame.pack(fill=tk.BOTH, expand=True)
            self.arrow_button.configure(text="▲")
            
            # Focus the listbox for keyboard navigation
            self.options_listbox.focus_set()
            
            self.trigger_event('dropdown_opened')
    
    def _close_dropdown(self):
        """Close the dropdown options."""
        if self._is_open:
            self._is_open = False
            self.options_frame.pack_forget()
            self.arrow_button.configure(text="▼")
            
            self.trigger_event('dropdown_closed')
    
    def _on_search(self, event=None):
        """Handle search input."""
        if not self.searchable:
            return
        
        search_term = self.display_widget.get().lower()
        
        # Filter options based on search term
        self._filtered_options = []
        for option in self.options:
            display_text = self._get_option_display_text(option).lower()
            if search_term in display_text:
                self._filtered_options.append(option)
        
        # Repopulate the listbox
        self._populate_options()
        
        # Open dropdown if not already open
        if search_term and not self._is_open:
            self._open_dropdown()
    
    def _on_selection_change(self, event=None):
        """Handle selection change in the listbox."""
        if not hasattr(self, 'options_listbox'):
            return
        
        selected_indices = self.options_listbox.curselection()
        
        if self.multi_select:
            # Multiple selection
            self._selected_values = []
            for index in selected_indices:
                if 0 <= index < len(self._filtered_options):
                    option = self._filtered_options[index]
                    self._selected_values.append(self._get_option_value(option))
        else:
            # Single selection
            if selected_indices:
                index = selected_indices[0]
                if 0 <= index < len(self._filtered_options):
                    option = self._filtered_options[index]
                    self._selected_values = [self._get_option_value(option)]
                    
                    # Close dropdown for single select
                    self._close_dropdown()
            else:
                self._selected_values = []
        
        self._update_display()
        self.trigger_event('value_changed', self.get_value())
    
    def _on_double_click(self, event=None):
        """Handle double-click on option."""
        if not self.multi_select:
            self._close_dropdown()
    
    def _on_focus_out_dropdown(self, event=None):
        """Handle focus out event."""
        # Close dropdown when focus is lost
        self._widget.after(100, self._check_focus_and_close)
    
    def _check_focus_and_close(self):
        """Check if focus is still within dropdown and close if not."""
        focused_widget = self._widget.focus_get()
        if focused_widget not in [self.display_widget, self.options_listbox, self.arrow_button]:
            self._close_dropdown()
    
    def _navigate_options(self, direction: int):
        """Navigate options with keyboard."""
        if not self._is_open:
            self._open_dropdown()
            return
        
        current_selection = self.options_listbox.curselection()
        if current_selection:
            current_index = current_selection[0]
        else:
            current_index = -1 if direction > 0 else len(self._filtered_options)
        
        new_index = current_index + direction
        new_index = max(0, min(new_index, len(self._filtered_options) - 1))
        
        self.options_listbox.selection_clear(0, tk.END)
        self.options_listbox.selection_set(new_index)
        self.options_listbox.see(new_index)
    
    def _select_highlighted(self):
        """Select the currently highlighted option."""
        current_selection = self.options_listbox.curselection()
        if current_selection:
            self._on_selection_change()
    
    def _update_display(self):
        """Update the display widget with selected values."""
        if not hasattr(self, 'display_widget'):
            return
        
        if not self._selected_values:
            display_text = self.placeholder
        elif self.multi_select:
            # Show count for multiple selections
            display_text = f"{len(self._selected_values)} selected"
        else:
            # Show single selection
            value = self._selected_values[0]
            # Find the option to get display text
            for option in self.options:
                if self._get_option_value(option) == value:
                    display_text = self._get_option_display_text(option)
                    break
            else:
                display_text = str(value)
        
        if isinstance(self.display_widget, tk.Entry):
            current_text = self.display_widget.get()
            if current_text != display_text:
                self.display_widget.delete(0, tk.END)
                self.display_widget.insert(0, display_text)
        else:
            self.display_widget.configure(text=display_text)
    
    def get_value(self) -> Union[Any, List[Any]]:
        """Get the selected value(s)."""
        if self.multi_select:
            return self._selected_values.copy()
        else:
            return self._selected_values[0] if self._selected_values else None
    
    def set_value(self, value: Union[Any, List[Any]]):
        """Set the selected value(s)."""
        if self.multi_select:
            if not isinstance(value, list):
                value = [value] if value is not None else []
            self._selected_values = value.copy()
        else:
            self._selected_values = [value] if value is not None else []
        
        self._update_display()
        self._update_listbox_selection()
    
    def _update_listbox_selection(self):
        """Update the listbox selection to match selected values."""
        if not hasattr(self, 'options_listbox'):
            return
        
        self.options_listbox.selection_clear(0, tk.END)
        
        for i, option in enumerate(self._filtered_options):
            option_value = self._get_option_value(option)
            if option_value in self._selected_values:
                self.options_listbox.selection_set(i)
    
    def add_option(self, option: Union[str, Dict[str, Any]]):
        """Add a new option to the dropdown."""
        self.options.append(option)
        self._filtered_options = self.options.copy()
        self._populate_options()
    
    def remove_option(self, value: Any):
        """Remove an option by value."""
        self.options = [opt for opt in self.options if self._get_option_value(opt) != value]
        self._filtered_options = self.options.copy()
        self._populate_options()
        
        # Remove from selected values if present
        if value in self._selected_values:
            self._selected_values.remove(value)
            self._update_display()
    
    def set_options(self, options: List[Union[str, Dict[str, Any]]]):
        """Set the options list."""
        self.options = options.copy()
        self._filtered_options = self.options.copy()
        self._selected_values = []
        self._populate_options()
        self._update_display()


class Slider(BaseComponent):
    """
    Numeric range input slider component.
    """
    
    def __init__(self, parent: tk.Widget,
                 min_value: float = 0,
                 max_value: float = 100,
                 initial_value: float = None,
                 step: float = 1,
                 orientation: str = "horizontal",
                 show_value: bool = True,
                 show_ticks: bool = False,
                 tick_interval: Optional[float] = None,
                 **kwargs):
        """
        Initialize the slider.
        
        Args:
            parent: Parent widget
            min_value: Minimum value
            max_value: Maximum value
            initial_value: Initial value (defaults to min_value)
            step: Step increment
            orientation: Slider orientation (horizontal/vertical)
            show_value: Whether to show current value
            show_ticks: Whether to show tick marks
            tick_interval: Interval between ticks
            **kwargs: Additional widget options
        """
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.orientation = orientation
        self.show_value = show_value
        self.show_ticks = show_ticks
        self.tick_interval = tick_interval
        
        if initial_value is None:
            initial_value = min_value
        self._value = initial_value
        
        super().__init__(parent, **kwargs)
        
        if show_ticks:
            self._setup_ticks()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the slider widget structure."""
        container = ttk.Frame(self.parent)
        
        # Create the scale widget
        scale_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['min_value', 'max_value', 'initial_value', 'step', 
                                   'orientation', 'show_value', 'show_ticks', 'tick_interval']}
        
        self.scale = tk.Scale(container,
                             from_=self.min_value,
                             to=self.max_value,
                             resolution=self.step,
                             orient=tk.HORIZONTAL if self.orientation == "horizontal" else tk.VERTICAL,
                             command=self._on_value_change,
                             **scale_kwargs)
        
        self.scale.set(self._value)
        
        if self.orientation == "horizontal":
            self.scale.pack(side=tk.TOP, fill=tk.X, expand=True)
            
            if self.show_value:
                self.value_label = tk.Label(container, text=str(self._value))
                self.value_label.pack(side=tk.BOTTOM)
        else:
            self.scale.pack(side=tk.LEFT, fill=tk.Y, expand=True)
            
            if self.show_value:
                self.value_label = tk.Label(container, text=str(self._value))
                self.value_label.pack(side=tk.RIGHT)
        
        return container
    
    def _setup_ticks(self):
        """Setup tick marks for the slider."""
        # Implementation placeholder for tick marks
        # This would create additional labels/marks along the slider
        pass
    
    def _on_value_change(self, value):
        """Handle value change."""
        try:
            self._value = float(value)
            if hasattr(self, 'value_label') and self.show_value:
                self.value_label.configure(text=str(self._value))
            
            self.trigger_event('value_changed', self._value)
        except ValueError:
            pass
    
    def get_value(self) -> float:
        """Get the current slider value."""
        return self._value
    
    def set_value(self, value: float):
        """Set the slider value."""
        value = max(self.min_value, min(self.max_value, value))
        self._value = value
        
        if hasattr(self, 'scale'):
            self.scale.set(value)
        
        if hasattr(self, 'value_label') and self.show_value:
            self.value_label.configure(text=str(value))
    
    def set_range(self, min_value: float, max_value: float):
        """Set the slider range."""
        self.min_value = min_value
        self.max_value = max_value
        
        if hasattr(self, 'scale'):
            self.scale.configure(from_=min_value, to=max_value)
            # Ensure current value is within new range
            self.set_value(self._value)
    
    def set_step(self, step: float):
        """Set the slider step increment."""
        self.step = step
        if hasattr(self, 'scale'):
            self.scale.configure(resolution=step)
