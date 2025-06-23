# TaskMover UI Components Documentation

## Overview

This documentation provides comprehensive information about all TaskMover UI components,
including usage examples, API reference, and best practices.

## Component Categories

### Input Components
Components for user input and interaction:

### Input Components
- **CustomEntry**: Component definition
- **CustomButton**: Component definition
- **CustomCheckbox**: Component definition
- **CustomRadioButton**: Component definition
- **CustomCombobox**: Component definition
- **FileSelector**: Component definition
- **DateTimePicker**: Component definition
- **ColorPicker**: Component definition
- **SliderInput**: Component definition
- **SearchBox**: Component definition

### Display Components
- **CustomLabel**: Component definition
- **IconLabel**: Component definition
- **StatusIndicator**: System status display component
- **ProgressBar**: Progress indication component
- **Badge**: Status indicator badge component
- **Tooltip**: Hover information tooltip component

### Layout Components
- **Panel**: Resizable panel component with docking and state persistence
- **Splitter**: Component definition
- **TabContainer**: Tab container with closeable and reorderable tabs
- **Accordion**: Component definition
- **Card**: Component definition
- **GroupBox**: Component definition

### Navigation Components
- **MenuBar**: Component definition
- **ContextMenu**: Component definition
- **Toolbar**: Toolbar component with tool groups and overflow handling
- **Breadcrumb**: Breadcrumb navigation component
- **Sidebar**: Collapsible sidebar container for navigation
- **StatusBar**: Component definition

### Data Display Components
- **DataTable**: Data table with sortable columns, filtering, and selection
- **ListView**: List view component with item selection and virtual scrolling
- **TreeView**: Tree view component with expand/collapse and lazy loading
- **PropertyGrid**: Property grid component for editing object properties
- **Chart**: Component definition

### Specialized Components
- **FileList**: Component definition
- **PreviewPane**: Component definition
- **LogViewer**: Component definition
- **ConsoleOutput**: Component definition
- **ImageViewer**: Component definition

### Dialogs Components
- **MessageDialog**: Message dialog with icon and configurable buttons
- **ConfirmationDialog**: Confirmation dialog with Yes/No or OK/Cancel buttons
- **InputDialog**: Input dialog for collecting user input
- **FileDialog**: Component definition
- **SettingsDialog**: Settings dialog with categorized options
- **AboutDialog**: Component definition
- **ProgressDialog**: Progress dialog for long-running operations
- **ErrorDialog**: Component definition

### Pattern Management Components
- **PatternEditor**: Component definition
- **PatternList**: Component definition
- **PatternTester**: Pattern testing interface for validating patterns against sample files
- **PatternBuilder**: Visual pattern builder for creating file organization patterns

### Rule Management Components
- **RuleEditor**: Rule editor for creating and modifying file organization rules
- **RuleList**: Rule list management interface with drag-and-drop reordering
- **ConditionBuilder**: Component definition
- **ActionSelector**: Component definition

### Ruleset Management Components
- **RulesetEditor**: Editor for creating and modifying rulesets
- **RulesetList**: Component definition
- **RulesetImportExport**: Component definition
- **RulesetValidation**: Component definition

### File Organization Components
- **FileOrganizer**: Component definition
- **SourceSelector**: Component definition
- **DestinationBuilder**: Component definition
- **OperationPreview**: Component definition
- **ExecutionMonitor**: Real-time monitoring of organization execution

## Quick Start

```python
from ui.input_components import CustomEntry, CustomButton
from ui.layout_components import Panel
from ui.theme_manager import ThemeManager

# Create a simple form
panel = Panel(parent)
entry = CustomEntry(panel, placeholder="Enter text...")
button = CustomButton(panel, text="Submit")

# Apply theme
theme_manager = ThemeManager()
theme_manager.apply_theme(panel, "modern")
```

## Architecture

The UI system is built on the following principles:

1. **Component-Based**: Each UI element is a reusable component
2. **Theme-Driven**: Consistent styling through theme system
3. **Event-Driven**: Components communicate through events
4. **Accessible**: Built-in accessibility features
5. **Responsive**: Adapts to different screen sizes

## Documentation Structure

- `components/` - Individual component documentation
- `examples/` - Usage examples and code samples
- `style-guide/` - Visual style guide and design patterns
- `api/` - Complete API reference

For detailed information about specific components, see the individual component documentation files.
