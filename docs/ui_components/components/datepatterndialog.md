# DatePatternDialog

## Description
Dialog for creating date criteria.

## Module
`ui.pattern_management_components`

## Constructor Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parent` | Any | Required | Parameter description |

## Methods
### show_modal(self)
Show dialog and return result.


## Properties
No properties documented.

## Usage Example

```python
from ui.pattern_management_components import DatePatternDialog

# Basic usage
component = DatePatternDialog(parent)
component.pack()

# With configuration
component.configure(
    # Add relevant configuration options
)
```

## See Also
- [Component Gallery](../gallery.md)
- [Style Guide](../style-guide/README.md)
- [Examples](../examples/datepatterndialog.py)
