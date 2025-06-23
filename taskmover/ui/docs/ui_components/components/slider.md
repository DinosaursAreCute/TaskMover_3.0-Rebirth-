# Slider

## Description
Numeric range input slider component.

## Module
`ui.additional_input_components`

## Constructor Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parent` | <class 'tkinter.Widget'> | Required | Parameter description |
| `min_value` | <class 'float'> | 0 | Parameter description |
| `max_value` | <class 'float'> | 100 | Parameter description |
| `initial_value` | <class 'float'> | None | Parameter description |
| `step` | <class 'float'> | 1 | Parameter description |
| `orientation` | <class 'str'> | horizontal | Parameter description |
| `show_value` | <class 'bool'> | True | Parameter description |
| `show_ticks` | <class 'bool'> | False | Parameter description |
| `tick_interval` | typing.Optional[float] | None | Parameter description |
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

### destroy(self)
Destroy the component and clean up resources.

### get_value(self) -> float
Get the current slider value.

### get_widget(self) -> tkinter.Widget
Get the underlying tkinter widget.

### grid(self, **kwargs)
Grid the component.

### pack(self, **kwargs)
Pack the component.

### place(self, **kwargs)
Place the component.

### set_enabled(self, enabled: bool)
Enable or disable the component.

### set_range(self, min_value: float, max_value: float)
Set the slider range.

### set_screen_reader_text(self, text: str)
Set text for screen readers.

### set_state(self, state: ui.base_component.ComponentState)
Set the component state and update styling.

### set_step(self, step: float)
Set the slider step increment.

### set_tab_order(self, order: int)
Set the tab order for keyboard navigation.

### set_theme_manager(self, theme_manager)
Set the theme manager for this component.

### set_value(self, value: float)
Set the slider value.

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
from ui.additional_input_components import Slider

# Basic usage
component = Slider(parent)
component.pack()

# With configuration
component.configure(
    # Add relevant configuration options
)
```

## See Also
- [Component Gallery](../gallery.md)
- [Style Guide](../style-guide/README.md)
- [Examples](../examples/slider.py)
