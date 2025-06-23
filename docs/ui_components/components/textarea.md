# TextArea

## Description
Multi-line text input component with scrolling and optional features.

## Module
`ui.input_components`

## Constructor Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parent` | <class 'tkinter.Widget'> | Required | Parameter description |
| `height` | <class 'int'> | 10 | Parameter description |
| `width` | <class 'int'> | 40 | Parameter description |
| `wrap` | <class 'str'> | word | Parameter description |
| `show_line_numbers` | <class 'bool'> | False | Parameter description |
| `syntax_highlighting` | <class 'bool'> | False | Parameter description |
| `kwargs` | Any | Required | Parameter description |

## Methods
### add_keyboard_shortcut(self, key_combination: str, handler: Callable)
Add a keyboard shortcut for this component.

### add_validator(self, validator: Callable[[Any], tuple[bool, str]])
Add a validation function that returns (is_valid, error_message).

### animate_property(self, property_name: str, target_value: Any, duration: float = 0.3)
Animate a property change. Placeholder for future implementation.

### apply_style(self, style_dict: Dict[str, Any])
Apply a style dictionary to the component.

### bind_event(self, event_name: str, handler: Callable)
Bind an event handler to a custom event.

### clear(self)
Clear the text content.

### destroy(self)
Destroy the component and clean up resources.

### get_selection(self) -> str
Get the selected text.

### get_value(self) -> str
Get the current text content.

### get_widget(self) -> tkinter.Widget
Get the underlying tkinter widget.

### grid(self, **kwargs)
Grid the component.

### insert_text(self, text: str, position: str = 'insert')
Insert text at the specified position.

### pack(self, **kwargs)
Pack the component.

### place(self, **kwargs)
Place the component.

### set_enabled(self, enabled: bool)
Enable or disable the component.

### set_readonly(self, readonly: bool)
Set the text area to readonly mode.

### set_screen_reader_text(self, text: str)
Set text for screen readers.

### set_state(self, state: ui.base_component.ComponentState)
Set the component state and update styling.

### set_tab_order(self, order: int)
Set the tab order for keyboard navigation.

### set_theme_manager(self, theme_manager)
Set the theme manager for this component.

### set_value(self, value: str)
Set the text content.

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
from ui.input_components import TextArea

# Basic usage
component = TextArea(parent)
component.pack()

# With configuration
component.configure(
    # Add relevant configuration options
)
```

## See Also
- [Component Gallery](../gallery.md)
- [Style Guide](../style-guide/README.md)
- [Examples](../examples/textarea.py)
