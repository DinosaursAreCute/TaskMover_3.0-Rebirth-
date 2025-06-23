# Dropdown

## Description
Selection dropdown component with search and multi-select capabilities.

## Module
`ui.additional_input_components`

## Constructor Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parent` | <class 'tkinter.Widget'> | Required | Parameter description |
| `options` | typing.List[typing.Union[str, typing.Dict[str, typing.Any]]] | None | Parameter description |
| `placeholder` | <class 'str'> | Select an option | Parameter description |
| `searchable` | <class 'bool'> | True | Parameter description |
| `multi_select` | <class 'bool'> | False | Parameter description |
| `custom_render` | typing.Optional[typing.Callable] | None | Parameter description |
| `kwargs` | Any | Required | Parameter description |

## Methods
### add_keyboard_shortcut(self, key_combination: str, handler: Callable)
Add a keyboard shortcut for this component.

### add_option(self, option: Union[str, Dict[str, Any]])
Add a new option to the dropdown.

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

### get_value(self) -> Union[Any, List[Any]]
Get the selected value(s).

### get_widget(self) -> tkinter.Widget
Get the underlying tkinter widget.

### grid(self, **kwargs)
Grid the component.

### pack(self, **kwargs)
Pack the component.

### place(self, **kwargs)
Place the component.

### remove_option(self, value: Any)
Remove an option by value.

### set_enabled(self, enabled: bool)
Enable or disable the component.

### set_options(self, options: List[Union[str, Dict[str, Any]]])
Set the options list.

### set_screen_reader_text(self, text: str)
Set text for screen readers.

### set_state(self, state: ui.base_component.ComponentState)
Set the component state and update styling.

### set_tab_order(self, order: int)
Set the tab order for keyboard navigation.

### set_theme_manager(self, theme_manager)
Set the theme manager for this component.

### set_value(self, value: Union[Any, List[Any]])
Set the selected value(s).

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
from ui.additional_input_components import Dropdown

# Basic usage
component = Dropdown(parent)
component.pack()

# With configuration
component.configure(
    # Add relevant configuration options
)
```

## See Also
- [Component Gallery](../gallery.md)
- [Style Guide](../style-guide/README.md)
- [Examples](../examples/dropdown.py)
