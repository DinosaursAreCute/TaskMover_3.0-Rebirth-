"""
TaskMover UI Framework - Base Component System
"""
import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
import uuid


class ComponentState(Enum):
    """Component visual states"""
    NORMAL = "normal"
    HOVER = "hover"
    FOCUSED = "focused"
    DISABLED = "disabled"
    ERROR = "error"


class BaseComponent(ABC):
    """
    Abstract base class for all UI components in TaskMover.
    Provides common functionality for styling, events, validation, and accessibility.
    """
    
    def __init__(self, parent: tk.Widget, **kwargs):
        """
        Initialize the base component.
        
        Args:
            parent: Parent tkinter widget
            **kwargs: Component-specific configuration
        """
        self.parent = parent
        self.component_id = str(uuid.uuid4())
        self.state = ComponentState.NORMAL
        self.enabled = True
        self.visible = True
        
        # Event system
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Styling
        self.styles: Dict[str, Any] = {}
        self.theme_manager = None  # Will be injected
        
        # Validation
        self.validators: List[Callable] = []
        self.validation_errors: List[str] = []
        
        # Accessibility
        self.tab_order: Optional[int] = None
        self.screen_reader_text: Optional[str] = None
        self.keyboard_shortcuts: Dict[str, Callable] = {}
        
        # Animation support
        self.animations: Dict[str, Any] = {}
        
        # Initialize the widget
        self._widget = self._create_widget(**kwargs)
        self._setup_default_bindings()
    
    @abstractmethod
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the underlying tkinter widget. Must be implemented by subclasses."""
        pass
    
    def _setup_default_bindings(self):
        """Setup default event bindings for the component."""
        if hasattr(self._widget, 'bind'):
            self._widget.bind('<Enter>', self._on_enter)
            self._widget.bind('<Leave>', self._on_leave)
            self._widget.bind('<FocusIn>', self._on_focus_in)
            self._widget.bind('<FocusOut>', self._on_focus_out)
            self._widget.bind('<Button-1>', self._on_click)
    
    # Event System
    def bind_event(self, event_name: str, handler: Callable):
        """Bind an event handler to a custom event."""
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)
    
    def trigger_event(self, event_name: str, *args, **kwargs):
        """Trigger a custom event."""
        if event_name in self._event_handlers:
            for handler in self._event_handlers[event_name]:
                try:
                    handler(self, *args, **kwargs)
                except Exception as e:
                    print(f"Error in event handler {event_name}: {e}")
    
    def _on_enter(self, event=None):
        """Handle mouse enter event."""
        if self.enabled and self.state != ComponentState.DISABLED:
            self.set_state(ComponentState.HOVER)
            self.trigger_event('hover', True)
    
    def _on_leave(self, event=None):
        """Handle mouse leave event."""
        if self.enabled and self.state == ComponentState.HOVER:
            self.set_state(ComponentState.NORMAL)
            self.trigger_event('hover', False)
    
    def _on_focus_in(self, event=None):
        """Handle focus in event."""
        if self.enabled:
            self.set_state(ComponentState.FOCUSED)
            self.trigger_event('focus', True)
    
    def _on_focus_out(self, event=None):
        """Handle focus out event."""
        if self.enabled and self.state == ComponentState.FOCUSED:
            self.set_state(ComponentState.NORMAL)
            self.trigger_event('focus', False)
    
    def _on_click(self, event=None):
        """Handle click event."""
        if self.enabled:
            self.trigger_event('click', event)
    
    # State Management
    def set_state(self, state: ComponentState):
        """Set the component state and update styling."""
        if self.state != state:
            old_state = self.state
            self.state = state
            self._update_styling()
            self.trigger_event('state_changed', old_state, state)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the component."""
        if self.enabled != enabled:
            self.enabled = enabled
            if enabled:
                self.set_state(ComponentState.NORMAL)
            else:
                self.set_state(ComponentState.DISABLED)
            self._update_widget_state()
    
    def set_visible(self, visible: bool):
        """Show or hide the component."""
        if self.visible != visible:
            self.visible = visible
            if visible:
                self._widget.grid()
            else:
                self._widget.grid_remove()
            self.trigger_event('visibility_changed', visible)
    
    # Styling System
    def apply_style(self, style_dict: Dict[str, Any]):
        """Apply a style dictionary to the component."""
        self.styles.update(style_dict)
        self._update_styling()
    
    def set_theme_manager(self, theme_manager):
        """Set the theme manager for this component."""
        self.theme_manager = theme_manager
        self._update_styling()
    
    def _update_styling(self):
        """Update the widget styling based on current state and theme."""
        if self.theme_manager:
            style = self.theme_manager.get_component_style(
                self.__class__.__name__, 
                self.state
            )
            style.update(self.styles)
            self._apply_widget_style(style)
    
    def _apply_widget_style(self, style: Dict[str, Any]):
        """Apply style to the underlying widget. Override in subclasses."""
        try:
            if hasattr(self._widget, 'configure'):
                # Filter out only valid tkinter options
                valid_options = self._get_valid_widget_options()
                widget_style = {k: v for k, v in style.items() if k in valid_options}
                if widget_style:
                    self._widget.configure(**widget_style)
        except tk.TclError as e:
            print(f"Error applying style to {self.__class__.__name__}: {e}")
    
    def _get_valid_widget_options(self) -> set:
        """Get valid configuration options for the widget."""
        try:
            return set(self._widget.configure().keys())
        except:
            return set()
    
    def _update_widget_state(self):
        """Update widget-specific state. Override in subclasses."""
        try:
            if hasattr(self._widget, 'configure'):
                state = 'disabled' if not self.enabled else 'normal'
                self._widget.configure(state=state)
        except:
            pass
    
    # Validation System
    def add_validator(self, validator: Callable[[Any], tuple[bool, str]]):
        """Add a validation function that returns (is_valid, error_message)."""
        self.validators.append(validator)
    
    def validate(self) -> bool:
        """Run all validators and return True if all pass."""
        self.validation_errors.clear()
        
        for validator in self.validators:
            try:
                is_valid, error_message = validator(self.get_value())
                if not is_valid:
                    self.validation_errors.append(error_message)
            except Exception as e:
                self.validation_errors.append(f"Validation error: {e}")
        
        has_errors = len(self.validation_errors) > 0
        if has_errors:
            self.set_state(ComponentState.ERROR)
        elif self.state == ComponentState.ERROR:
            self.set_state(ComponentState.NORMAL)
        
        self.trigger_event('validation_changed', not has_errors, self.validation_errors)
        return not has_errors
    
    def get_value(self) -> Any:
        """Get the current value of the component. Override in subclasses."""
        return None
    
    def set_value(self, value: Any):
        """Set the value of the component. Override in subclasses."""
        pass
    
    # Accessibility
    def set_tab_order(self, order: int):
        """Set the tab order for keyboard navigation."""
        self.tab_order = order
    
    def set_screen_reader_text(self, text: str):
        """Set text for screen readers."""
        self.screen_reader_text = text
        # TODO: Implement actual screen reader support
    
    def add_keyboard_shortcut(self, key_combination: str, handler: Callable):
        """Add a keyboard shortcut for this component."""
        self.keyboard_shortcuts[key_combination] = handler
        # TODO: Implement global shortcut system
    
    # Animation Support (placeholder for future implementation)
    def animate_property(self, property_name: str, target_value: Any, duration: float = 0.3):
        """Animate a property change. Placeholder for future implementation."""
        # LOGIC INTEGRATION POINT: Connect to animation system
        pass
    
    # Widget Access
    def get_widget(self) -> tk.Widget:
        """Get the underlying tkinter widget."""
        return self._widget
    
    def grid(self, **kwargs):
        """Grid the component."""
        return self._widget.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the component."""
        return self._widget.pack(**kwargs)
    
    def place(self, **kwargs):
        """Place the component."""
        return self._widget.place(**kwargs)
    
    def destroy(self):
        """Destroy the component and clean up resources."""
        if hasattr(self, '_widget') and self._widget:
            self._widget.destroy()
        self._event_handlers.clear()
        self.validators.clear()
        self.validation_errors.clear()


class FrameComponent(BaseComponent):
    """Base frame component that can contain other components."""
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create a Frame widget."""
        return ttk.Frame(self.parent, **kwargs)
    
    def add_child(self, child_component: BaseComponent, **grid_options):
        """Add a child component to this frame."""
        child_component.grid(**grid_options)
        if self.theme_manager:
            child_component.set_theme_manager(self.theme_manager)
