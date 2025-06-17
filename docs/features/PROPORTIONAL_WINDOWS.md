# Proportional Window Sizing Implementation

## Overview
This document describes the implementation of proportional window sizing for TaskMover, ensuring that all windows open centered on the screen and are proportionally sized to the display dimensions.

## Changes Made

### 1. Enhanced Core Utilities (`taskmover_redesign/core/utils.py`)

**New Functions Added:**

- `get_screen_dimensions(window)`: Gets screen width and height
- `calculate_proportional_size(screen_width, screen_height, width_ratio, height_ratio)`: Calculates proportional window dimensions with min/max constraints
- `center_window_on_parent(child, parent, ...)`: Centers a child window on its parent window with optional proportional sizing

**Enhanced Functions:**

- `center_window()`: Now supports proportional sizing with `proportional=True`, `width_ratio`, and `height_ratio` parameters

**Features:**
- Automatic minimum size enforcement (400x300 minimum)
- Maximum size constraints (90% of screen max)
- Screen edge detection and prevention of off-screen windows
- Support for both fixed and proportional sizing modes

### 2. Updated Main Application (`taskmover_redesign/app.py`)

**Changes:**
- Main window now uses proportional sizing (60% width, 70% height)
- About dialog uses proportional sizing (40% width, 50% height)
- Imported `center_window_on_parent` for child window management

```python
# Main window with proportional sizing
center_window(self.root, proportional=True, width_ratio=0.6, height_ratio=0.7)

# About dialog with proportional sizing
center_window_on_parent(about_dialog, self.root, proportional=True, width_ratio=0.4, height_ratio=0.5)
```

### 3. Enhanced Dialog System (`taskmover_redesign/ui/components.py`)

**SimpleDialog Class Updates:**
- Added support for proportional sizing in constructor
- New parameters: `proportional=False`, `width_ratio=0.4`, `height_ratio=0.5`
- Automatic proportional sizing when enabled
- Fallback to fixed sizing when disabled

**ProgressDialog Updates:**
- Uses new `center_window_on_parent()` function for better centering
- Maintains consistent 450x200 size but centers properly on parent

### 4. Settings Dialog Enhancement

**Both `settings_components.py` and `settings_components_new.py`:**
- Settings dialogs now use proportional sizing (40% width, 50% height)
- Better responsive design for different screen sizes

### 5. Core Module Exports (`taskmover_redesign/core/__init__.py`)

**Added Exports:**
- `center_window_on_parent` function now available for import
- Updated `__all__` list to include new function

## Usage Examples

### Main Application Window
```python
# 60% of screen width, 70% of screen height, centered
center_window(self.root, proportional=True, width_ratio=0.6, height_ratio=0.7)
```

### Dialog Windows
```python
# 40% of parent width, 50% of parent height, centered on parent
center_window_on_parent(dialog, parent, proportional=True, width_ratio=0.4, height_ratio=0.5)
```

### SimpleDialog Class
```python
# Use proportional sizing in dialog constructor
super().__init__(parent, "Settings", proportional=True, width_ratio=0.4, height_ratio=0.5)
```

## Size Ratios Used

| Window Type | Width Ratio | Height Ratio | Description |
|-------------|-------------|--------------|-------------|
| Main Window | 0.6 (60%) | 0.7 (70%) | Primary application window |
| Settings Dialog | 0.4 (40%) | 0.5 (50%) | Configuration dialogs |
| About Dialog | 0.4 (40%) | 0.5 (50%) | Information dialogs |
| Progress Dialog | Fixed 450px | Fixed 200px | Status dialogs |

## Benefits

1. **Responsive Design**: Windows automatically adapt to different screen sizes
2. **Consistent UX**: All windows follow the same centering and sizing principles
3. **Better Usability**: Windows are never too small or too large for the screen
4. **Multi-Monitor Support**: Windows center correctly on the active monitor
5. **Backwards Compatibility**: Fixed sizing still available when needed

## Error Handling

- Minimum size constraints prevent windows from being too small
- Maximum size constraints prevent windows from exceeding screen bounds
- Screen edge detection prevents windows from appearing off-screen
- Fallback to fixed sizing if proportional calculation fails

## Testing

Use the included test script `test_proportional_windows.py` to verify:
- Main window proportional sizing
- Dialog proportional sizing relative to parent
- Proper centering on screen and parent windows
- Minimum/maximum size constraints

## Future Enhancements

1. **User Preferences**: Allow users to customize default window size ratios
2. **Window State Memory**: Remember and restore window sizes between sessions
3. **Multi-Monitor Awareness**: Better handling of multi-monitor setups
4. **Dynamic Ratios**: Adjust ratios based on content requirements
