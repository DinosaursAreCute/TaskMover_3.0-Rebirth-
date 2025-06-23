# SizeConditionDialog

## Description
Dialog for creating file size conditions.

## Module
`ui.rule_management_components`

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
from ui.rule_management_components import SizeConditionDialog

# Basic usage
component = SizeConditionDialog(parent)
component.pack()

# With configuration
component.configure(
    # Add relevant configuration options
)
```

## See Also
- [Component Gallery](../gallery.md)
- [Style Guide](../style-guide/README.md)
- [Examples](../examples/sizeconditiondialog.py)
