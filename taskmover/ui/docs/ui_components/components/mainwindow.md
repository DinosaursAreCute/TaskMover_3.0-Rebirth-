# MainWindow

## Description
Application main window container with state management.

## Module
`ui.layout_components`

## Constructor Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parent` | typing.Optional[tkinter.Widget] | None | Parameter description |
| `title` | <class 'str'> | TaskMover | Parameter description |
| `size` | <class 'tuple'> | (1200, 800) | Parameter description |
| `min_size` | <class 'tuple'> | (800, 600) | Parameter description |
| `position` | typing.Optional[tuple] | None | Parameter description |
| `resizable` | <class 'bool'> | True | Parameter description |
| `kwargs` | Any | Required | Parameter description |

## Methods
### add_keyboard_shortcut(self, key_combination: str, handler: Callable)
Add a keyboard shortcut for this component.

### add_shortcut(self, key_sequence: str, callback: Callable)
Add a keyboard shortcut.

### add_validator(self, validator: Callable[[Any], tuple[bool, str]])
Add a validation function that returns (is_valid, error_message).

### animate_property(self, property_name: str, target_value: Any, duration: float = 0.3)
Animate a property change. Placeholder for future implementation.

### apply_style(self, style_dict: Dict[str, Any])
Apply a style dictionary to the component.

### bind_event(self, event_name: str, handler: Callable)
Bind an event handler to a custom event.

### destroy(self)
Destroy the component and clean up resources.

### get_value(self) -> Any
Get the current value of the component. Override in subclasses.

### get_widget(self) -> tkinter.Widget
Get the underlying tkinter widget.

### get_window_state(self) -> dict
Get current window state for persistence.

### grid(self, **kwargs)
Grid the component.

### pack(self, **kwargs)
Pack the component.

### place(self, **kwargs)
Place the component.

### remove_shortcut(self, key_sequence: str)
Remove a keyboard shortcut.

### restore_window_state(self, state: dict)
Restore window state from saved data.

### set_enabled(self, enabled: bool)
Enable or disable the component.

### set_menu_bar(self, menu_bar)
Set the window menu bar.

### set_screen_reader_text(self, text: str)
Set text for screen readers.

### set_state(self, state: ui.base_component.ComponentState)
Set the component state and update styling.

### set_status_bar(self, status_bar)
Set the window status bar.

### set_tab_order(self, order: int)
Set the tab order for keyboard navigation.

### set_theme_manager(self, theme_manager)
Set the theme manager for this component.

### set_value(self, value: Any)
Set the value of the component. Override in subclasses.

### set_visible(self, visible: bool)
Show or hide the component.

### trigger_event(self, event_name: str, *args, **kwargs)
Trigger a custom event.

### validate(self) -> bool
Run all validators and return True if all pass.


## Properties
No properties documented.

## Usage Example

```python
from ui.layout_components import MainWindow

# Basic usage
component = MainWindow(parent)
component.pack()

# With configuration
component.configure(
    # Add relevant configuration options
)
```

## See Also
- [Component Gallery](../gallery.md)
- [Style Guide](../style-guide/README.md)
- [Examples](../examples/mainwindow.py)
