# ProgressDialog

## Description
Progress dialog for long-running operations.

## Module
`ui.dialog_components`

## Constructor Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parent` | <class 'tkinter.Widget'> | Required | Parameter description |
| `title` | <class 'str'> | Progress | Parameter description |
| `operation_name` | <class 'str'> | Operation in progress... | Parameter description |
| `cancellable` | <class 'bool'> | True | Parameter description |
| `show_details` | <class 'bool'> | False | Parameter description |
| `kwargs` | Any | Required | Parameter description |

## Methods
### add_detail(self, detail: str)
Add a detail message.

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

### complete(self, success: bool = True, message: Optional[str] = None)
Mark operation as complete.

### destroy(self)
Destroy the component and clean up resources.

### get_value(self) -> Any
Get the current value of the component. Override in subclasses.

### get_widget(self) -> tkinter.Widget
Get the underlying tkinter widget.

### grid(self, **kwargs)
Grid the component.

### hide(self)
Hide dialog.

### is_cancelled(self) -> bool
Check if operation was cancelled.

### pack(self, **kwargs)
Pack the component.

### place(self, **kwargs)
Place the component.

### set_enabled(self, enabled: bool)
Enable or disable the component.

### set_progress(self, value: int, maximum: Optional[int] = None, status: Optional[str] = None)
Update progress.

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

### show(self)
Show dialog non-modally.

### show_modal(self) -> Any
Show dialog modally and return result.

### trigger_event(self, event_name: str, *args, **kwargs)
Trigger a custom event.

### validate(self) -> bool
Run all validators and return True if all pass.


## Properties
No properties documented.

## Usage Example

```python
from ui.dialog_components import ProgressDialog

# Basic usage
component = ProgressDialog(parent)
component.pack()

# With configuration
component.configure(
    # Add relevant configuration options
)
```

## See Also
- [Component Gallery](../gallery.md)
- [Style Guide](../style-guide/README.md)
- [Examples](../examples/progressdialog.py)
