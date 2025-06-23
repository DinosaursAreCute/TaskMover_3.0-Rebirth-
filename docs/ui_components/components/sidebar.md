# Sidebar

## Description
Collapsible sidebar container for navigation.

## Module
`ui.layout_components`

## Constructor Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parent` | <class 'tkinter.Widget'> | Required | Parameter description |
| `width` | <class 'int'> | 250 | Parameter description |
| `min_width` | <class 'int'> | 50 | Parameter description |
| `collapsible` | <class 'bool'> | True | Parameter description |
| `position` | <class 'str'> | left | Parameter description |
| `auto_collapse` | <class 'bool'> | False | Parameter description |
| `kwargs` | Any | Required | Parameter description |

## Methods
### add_keyboard_shortcut(self, key_combination: str, handler: Callable)
Add a keyboard shortcut for this component.

### add_section(self, title: str, content_widget: tkinter.Widget = None) -> dict
Add a section to the sidebar.

### add_validator(self, validator: Callable[[Any], tuple[bool, str]])
Add a validation function that returns (is_valid, error_message).

### animate_property(self, property_name: str, target_value: Any, duration: float = 0.3)
Animate a property change. Placeholder for future implementation.

### apply_style(self, style_dict: Dict[str, Any])
Apply a style dictionary to the component.

### bind_event(self, event_name: str, handler: Callable)
Bind an event handler to a custom event.

### collapse(self)
Collapse the sidebar.

### destroy(self)
Destroy the component and clean up resources.

### expand(self)
Expand the sidebar.

### get_value(self) -> Any
Get the current value of the component. Override in subclasses.

### get_widget(self) -> tkinter.Widget
Get the underlying tkinter widget.

### grid(self, **kwargs)
Grid the component.

### pack(self, **kwargs)
Pack the component.

### place(self, **kwargs)
Place the component.

### remove_section(self, title: str)
Remove a section from the sidebar.

### set_enabled(self, enabled: bool)
Enable or disable the component.

### set_screen_reader_text(self, text: str)
Set text for screen readers.

### set_state(self, state: ui.base_component.ComponentState)
Set the component state and update styling.

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
from ui.layout_components import Sidebar

# Basic usage
component = Sidebar(parent)
component.pack()

# With configuration
component.configure(
    # Add relevant configuration options
)
```

## See Also
- [Component Gallery](../gallery.md)
- [Style Guide](../style-guide/README.md)
- [Examples](../examples/sidebar.py)
