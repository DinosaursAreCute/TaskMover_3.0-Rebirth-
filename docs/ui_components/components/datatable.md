# DataTable

## Description
Data table with sortable columns, filtering, and selection.

## Module
`ui.data_display_components`

## Constructor Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parent` | <class 'tkinter.Widget'> | Required | Parameter description |
| `columns` | typing.List[typing.Dict] | None | Parameter description |
| `data` | typing.List[typing.Dict] | None | Parameter description |
| `sortable` | <class 'bool'> | True | Parameter description |
| `filterable` | <class 'bool'> | True | Parameter description |
| `selectable` | <class 'bool'> | True | Parameter description |
| `multi_select` | <class 'bool'> | False | Parameter description |
| `resizable_columns` | <class 'bool'> | True | Parameter description |
| `virtual_scrolling` | <class 'bool'> | False | Parameter description |
| `kwargs` | Any | Required | Parameter description |

## Methods
### add_keyboard_shortcut(self, key_combination: str, handler: Callable)
Add a keyboard shortcut for this component.

### add_row(self, row_data: Dict)
Add a new row to the table.

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

### get_selected_rows(self) -> List[Dict]
Get the selected row data.

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

### remove_row(self, row_index: int)
Remove a row from the table.

### set_column_filter(self, column_id: str, filter_value: Any)
Set a filter for a specific column.

### set_data(self, data: List[Dict])
Update table data.

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
from ui.data_display_components import DataTable

# Basic usage
component = DataTable(parent)
component.pack()

# With configuration
component.configure(
    # Add relevant configuration options
)
```

## See Also
- [Component Gallery](../gallery.md)
- [Style Guide](../style-guide/README.md)
- [Examples](../examples/datatable.py)
