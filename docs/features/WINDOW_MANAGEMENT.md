# Window Management System

## Overview

TaskMover's enhanced window management system provides intelligent, responsive window positioning and sizing that adapts to different screen configurations and user preferences.

## Key Features

### 🎯 **Proportional Window Sizing**
Windows automatically size themselves based on screen dimensions rather than using fixed pixel values.

**Benefits:**
- Consistent experience across different screen sizes
- Better usability on high-DPI displays
- Adaptive to ultra-wide and mobile displays
- Maintains readability on any screen

### 📐 **Intelligent Positioning**
Windows center themselves automatically on screen or relative to their parent windows.

**Positioning Types:**
- **Screen-centered** - Main application window centers on primary display
- **Parent-relative** - Dialog windows center on their parent window
- **Multi-monitor aware** - Handles multiple display configurations

### 🔧 **Responsive Design**
The system adapts to various screen configurations and user scenarios.

**Adaptive Features:**
- Minimum size constraints prevent unusably small windows
- Maximum size limits prevent overwhelming large windows
- Edge detection keeps windows fully visible
- Multi-monitor support for complex setups

## Implementation Details

### Core Functions

#### `center_window(window, proportional=True, width_ratio=0.6, height_ratio=0.7)`
Centers a window on the screen with optional proportional sizing.

**Parameters:**
- `window` - The tkinter window to position
- `proportional` - Whether to use proportional sizing (default: True)
- `width_ratio` - Proportion of screen width to use (default: 0.6 = 60%)
- `height_ratio` - Proportion of screen height to use (default: 0.7 = 70%)

**Example:**
```python
# Create main window at 60% screen width, 70% screen height
center_window(main_window, proportional=True, width_ratio=0.6, height_ratio=0.7)

# Create window with fixed size
center_window(dialog, width=400, height=300)
```

#### `center_window_on_parent(child, parent, proportional=True, width_ratio=0.4, height_ratio=0.5)`
Centers a child window relative to its parent window.

**Parameters:**
- `child` - The child window to position
- `parent` - The parent window to center on
- `proportional` - Whether to use proportional sizing relative to parent
- `width_ratio` - Proportion of parent width (default: 0.4 = 40%)
- `height_ratio` - Proportion of parent height (default: 0.5 = 50%)

**Example:**
```python
# Create dialog at 40% of parent width, 50% of parent height
center_window_on_parent(settings_dialog, main_window, 
                       proportional=True, width_ratio=0.4, height_ratio=0.5)
```

### Size Calculation Algorithm

#### Proportional Sizing Logic
```python
def calculate_proportional_size(screen_width, screen_height, width_ratio, height_ratio):
    # Calculate proportional dimensions
    width = int(screen_width * width_ratio)
    height = int(screen_height * height_ratio)
    
    # Apply minimum constraints
    width = max(width, 400)   # Minimum 400px width
    height = max(height, 300) # Minimum 300px height
    
    # Apply maximum constraints  
    width = min(width, int(screen_width * 0.9))   # Max 90% of screen
    height = min(height, int(screen_height * 0.9)) # Max 90% of screen
    
    return width, height
```

#### Positioning Algorithm
```python
def calculate_center_position(container_width, container_height, window_width, window_height):
    x = (container_width - window_width) // 2
    y = (container_height - window_height) // 2
    
    # Ensure window stays within bounds
    x = max(0, min(x, container_width - window_width))
    y = max(0, min(y, container_height - window_height))
    
    return x, y
```

## Default Window Configurations

### Main Application Window
- **Size:** 60% screen width × 70% screen height
- **Position:** Screen center
- **Minimum:** 800×600 pixels
- **Behavior:** Remembers last size and position

### Settings Dialog
- **Size:** 40% parent width × 50% parent height
- **Position:** Centered on parent
- **Minimum:** 500×400 pixels
- **Behavior:** Modal, always on top

### About Dialog
- **Size:** 40% parent width × 50% parent height
- **Position:** Centered on parent
- **Minimum:** 400×300 pixels
- **Behavior:** Modal, fixed content

### Progress Dialog
- **Size:** Fixed 450×200 pixels
- **Position:** Centered on parent
- **Behavior:** Modal, progress tracking

## Multi-Monitor Support

### Primary Display Detection
The system automatically detects the primary display and uses it for initial window positioning.

### Cross-Monitor Behavior
- Windows initially appear on the same monitor as their parent
- Full-screen operations respect monitor boundaries
- Window dragging across monitors is fully supported

### Edge Case Handling
- **Off-screen windows** - Automatically repositioned to visible area
- **Display disconnection** - Windows move to remaining displays
- **Resolution changes** - Windows resize proportionally

## Accessibility Features

### High-DPI Support
- Proportional sizing scales naturally with DPI
- Minimum sizes ensure readability
- Text and controls remain appropriately sized

### Low Vision Support
- Large window option available (increase width/height ratios)
- High contrast theme compatibility
- Keyboard navigation fully supported

### Motor Accessibility
- Large click targets on window controls
- Generous margins and spacing
- Predictable window behavior

## Configuration Options

### User Customization
Users can customize window behavior through settings:

```python
# Example settings configuration
window_settings = {
    "main_window": {
        "width_ratio": 0.8,    # 80% of screen width
        "height_ratio": 0.9,   # 90% of screen height
        "remember_size": True,  # Remember last size
        "remember_position": True
    },
    "dialogs": {
        "width_ratio": 0.5,    # 50% of parent width
        "height_ratio": 0.6,   # 60% of parent height
        "always_center": True
    }
}
```

### Developer Options
Developers can override default behavior:

```python
# Force specific window size
center_window(window, proportional=False, width=800, height=600)

# Use custom ratios
center_window(window, proportional=True, width_ratio=0.8, height_ratio=0.8)

# Position relative to specific coordinates
window.geometry("800x600+100+100")
```

## Testing and Validation

### Automated Testing
- Unit tests for size calculation functions
- Integration tests for window positioning
- Cross-platform compatibility tests

### Manual Testing Scenarios
- **Multiple monitor setups** - Verify correct positioning
- **High-DPI displays** - Ensure proper scaling
- **Window resizing** - Test responsive behavior
- **Display configuration changes** - Verify adaptation

### Visual Testing
The `test_proportional_windows.py` script provides interactive testing:

```bash
cd taskmover_redesign/tests
python test_proportional_windows.py
```

## Troubleshooting

### Common Issues

**Windows appear too small:**
- Check minimum size constraints
- Verify screen resolution detection
- Adjust width/height ratios in settings

**Windows appear off-screen:**
- Reset window positions in settings
- Check multi-monitor configuration
- Verify display connection status

**Inconsistent sizing:**
- Clear cached window positions
- Restart application to reload settings
- Check for display DPI changes

### Debug Information
Enable developer mode for detailed window management logging:

```python
# In settings
{
    "developer_mode": True,
    "logging_level": "DEBUG"
}
```

This will log all window operations to help diagnose issues.

## Future Enhancements

### Planned Features
- **Window state persistence** - Remember window states across sessions
- **Custom window layouts** - User-defined window arrangements
- **Snapping behavior** - Windows snap to screen edges and each other
- **Virtual desktop support** - Integration with OS virtual desktops

### Advanced Options
- **Animation system** - Smooth window transitions
- **Gesture support** - Touch and trackpad gestures for window management
- **Voice control** - Accessibility through voice commands
- **Remote display support** - Optimized behavior for remote desktop scenarios

---

The window management system provides a solid foundation for a professional, user-friendly interface that adapts to modern display environments while maintaining accessibility and usability.
