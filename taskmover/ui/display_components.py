"""
TaskMover UI Framework - Display Components
"""
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional, List, Union, Dict
from .base_component import BaseComponent, ComponentState
import threading
import time


class Label(BaseComponent):
    """
    Text display component with rich text support.
    """
    
    def __init__(self, parent: tk.Widget,
                 text: str = "",
                 font_size: Optional[int] = None,
                 font_weight: str = "normal",
                 color: Optional[str] = None,
                 wrap_length: Optional[int] = None,
                 icon: Optional[str] = None,
                 truncate: bool = False,
                 max_length: Optional[int] = None,
                 **kwargs):
        """
        Initialize the label.
        
        Args:
            parent: Parent widget
            text: Text to display
            font_size: Font size override
            font_weight: Font weight (normal, bold)
            color: Text color
            wrap_length: Text wrapping length
            icon: Icon name/path to display
            truncate: Whether to truncate long text
            max_length: Maximum text length before truncation
            **kwargs: Additional widget options
        """
        self.text = text
        self.font_size = font_size
        self.font_weight = font_weight
        self.color = color
        self.wrap_length = wrap_length
        self.icon = icon
        self.truncate = truncate
        self.max_length = max_length
        self._original_text = text
        
        super().__init__(parent, **kwargs)
        
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the label widget."""
        container = ttk.Frame(self.parent)
        
        # Configure text
        display_text = self._get_display_text()
        
        # Create label widget
        label_kwargs = {
            'text': display_text,
            'anchor': kwargs.get('anchor', 'w'),
            'justify': kwargs.get('justify', 'left')
        }
        
        # Apply styling
        if self.wrap_length:
            label_kwargs['wraplength'] = self.wrap_length
        
        # Font configuration
        font_config = []
        if self.font_size:
            font_config.extend(['Arial', self.font_size])
        else:
            font_config.extend(['Arial', 10])
            
        if self.font_weight == 'bold':
            font_config.append('bold')
            
        label_kwargs['font'] = tuple(font_config)
        
        if self.color:
            label_kwargs['foreground'] = self.color
        
        self.label = tk.Label(container, **label_kwargs)
        
        # Icon support (placeholder for future icon system)
        if self.icon:
            # TODO: Implement icon display
            pass
        
        self.label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        return container
    
    def _get_display_text(self) -> str:
        """Get the text to display with truncation if needed."""
        text = self.text
        
        if self.truncate and self.max_length and len(text) > self.max_length:
            text = text[:self.max_length - 3] + "..."
        
        return text
    
    def set_text(self, text: str):
        """Update the label text."""
        self.text = text
        self._original_text = text
        
        if hasattr(self, 'label'):
            display_text = self._get_display_text()
            self.label.configure(text=display_text)
    
    def get_text(self) -> str:
        """Get the original text."""
        return self._original_text
    
    def set_color(self, color: str):
        """Set the text color."""
        self.color = color
        if hasattr(self, 'label'):
            self.label.configure(foreground=color)
    
    def set_font_weight(self, weight: str):
        """Set the font weight."""
        self.font_weight = weight
        if hasattr(self, 'label'):
            current_font = self.label.cget('font')
            # Update font with new weight
            font_config = ['Arial', self.font_size or 10]
            if weight == 'bold':
                font_config.append('bold')
            self.label.configure(font=tuple(font_config))


class Badge(BaseComponent):
    """
    Status indicator badge component.
    """
    
    def __init__(self, parent: tk.Widget,
                 text: str = "",
                 badge_type: str = "default",  # default, primary, success, warning, error, info
                 size: str = "medium",  # small, medium, large
                 position: str = "inline",  # inline, corner-top-right, corner-top-left
                 count: Optional[int] = None,
                 max_count: int = 99,
                 **kwargs):
        """
        Initialize the badge.
        
        Args:
            parent: Parent widget
            text: Badge text
            badge_type: Badge color type
            size: Badge size
            position: Badge position
            count: Numeric count (overrides text)
            max_count: Maximum count before showing "99+"
            **kwargs: Additional widget options
        """
        self.badge_text = text
        self.badge_type = badge_type
        self.size = size
        self.position = position
        self.count = count
        self.max_count = max_count
        
        super().__init__(parent, **kwargs)
        
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the badge widget."""
        container = ttk.Frame(self.parent)
        
        # Determine display text
        display_text = self._get_display_text()
        
        # Color scheme based on type
        color_schemes = {
            'default': {'bg': '#6c757d', 'fg': 'white'},
            'primary': {'bg': '#007bff', 'fg': 'white'},
            'success': {'bg': '#28a745', 'fg': 'white'},
            'warning': {'bg': '#ffc107', 'fg': 'black'},
            'error': {'bg': '#dc3545', 'fg': 'white'},
            'info': {'bg': '#17a2b8', 'fg': 'white'}
        }
        
        colors = color_schemes.get(self.badge_type, color_schemes['default'])
        
        # Size configuration
        size_configs = {
            'small': {'font_size': 8, 'padx': 4, 'pady': 2},
            'medium': {'font_size': 10, 'padx': 6, 'pady': 3},
            'large': {'font_size': 12, 'padx': 8, 'pady': 4}
        }
        
        size_config = size_configs.get(self.size, size_configs['medium'])
        
        # Create badge label
        self.badge_label = tk.Label(container,
                                   text=display_text,
                                   background=colors['bg'],
                                   foreground=colors['fg'],
                                   font=('Arial', size_config['font_size'], 'bold'),
                                   relief='flat',
                                   borderwidth=0)
        
        # Position the badge
        if self.position == "inline":
            self.badge_label.pack(side=tk.LEFT, padx=size_config['padx'], pady=size_config['pady'])
        else:
            # Corner positioning would require different layout logic
            self.badge_label.pack(side=tk.LEFT, padx=size_config['padx'], pady=size_config['pady'])
        
        return container
    
    def _get_display_text(self) -> str:
        """Get the display text for the badge."""
        if self.count is not None:
            if self.count > self.max_count:
                return f"{self.max_count}+"
            return str(self.count)
        return self.badge_text
    
    def set_count(self, count: int):
        """Update the badge count."""
        self.count = count
        if hasattr(self, 'badge_label'):
            self.badge_label.configure(text=self._get_display_text())
    
    def set_text(self, text: str):
        """Update the badge text."""
        self.badge_text = text
        self.count = None  # Clear count when setting text
        if hasattr(self, 'badge_label'):
            self.badge_label.configure(text=self._get_display_text())
    
    def set_type(self, badge_type: str):
        """Update the badge type/color."""
        self.badge_type = badge_type
        if hasattr(self, 'badge_label'):
            color_schemes = {
                'default': {'bg': '#6c757d', 'fg': 'white'},
                'primary': {'bg': '#007bff', 'fg': 'white'},
                'success': {'bg': '#28a745', 'fg': 'white'},
                'warning': {'bg': '#ffc107', 'fg': 'black'},
                'error': {'bg': '#dc3545', 'fg': 'white'},
                'info': {'bg': '#17a2b8', 'fg': 'white'}
            }
            colors = color_schemes.get(badge_type, color_schemes['default'])
            self.badge_label.configure(background=colors['bg'], foreground=colors['fg'])


class Tooltip(BaseComponent):
    """
    Hover information tooltip component.
    """
    
    def __init__(self, parent: tk.Widget,
                 text: str = "",
                 delay: int = 500,  # milliseconds
                 position: str = "auto",  # auto, top, bottom, left, right
                 rich_content: bool = False,
                 **kwargs):
        """
        Initialize the tooltip.
        
        Args:
            parent: Parent widget
            text: Tooltip text
            delay: Delay before showing tooltip (ms)
            position: Tooltip position relative to parent
            rich_content: Whether to support rich text content
            **kwargs: Additional widget options
        """
        self.tooltip_text = text
        self.delay = delay
        self.position = position
        self.rich_content = rich_content
        self._tooltip_window = None
        self._show_timer = None
        self._target_widget = None
        
        super().__init__(parent, **kwargs)
        
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the tooltip (invisible until triggered)."""
        # Tooltip doesn't have a visible widget initially
        container = ttk.Frame(self.parent)
        return container
    
    def attach_to(self, widget: tk.Widget):
        """Attach tooltip to a target widget."""
        self._target_widget = widget
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        widget.bind("<Motion>", self._on_motion)
    
    def _on_enter(self, event):
        """Handle mouse enter event."""
        if self._show_timer:
            self._target_widget.after_cancel(self._show_timer)
        
        self._show_timer = self._target_widget.after(self.delay, self._show_tooltip)
    
    def _on_leave(self, event):
        """Handle mouse leave event."""
        if self._show_timer:
            self._target_widget.after_cancel(self._show_timer)
            self._show_timer = None
        
        self._hide_tooltip()
    
    def _on_motion(self, event):
        """Handle mouse motion (for repositioning)."""
        # Store mouse position for tooltip positioning
        self._mouse_x = event.x_root
        self._mouse_y = event.y_root
    
    def _show_tooltip(self):
        """Show the tooltip window."""
        if self._tooltip_window or not self.tooltip_text:
            return
        
        # Create tooltip window
        self._tooltip_window = tw = tk.Toplevel(self._target_widget)
        tw.wm_overrideredirect(True)
        tw.wm_attributes("-topmost", True)
        
        # Create tooltip content
        if self.rich_content:
            # TODO: Implement rich text support
            label = tk.Label(tw, text=self.tooltip_text, 
                           background="#ffffe0", 
                           foreground="black",
                           relief="solid", 
                           borderwidth=1,
                           font=("Arial", 9))
        else:
            label = tk.Label(tw, text=self.tooltip_text, 
                           background="#ffffe0", 
                           foreground="black",
                           relief="solid", 
                           borderwidth=1,
                           font=("Arial", 9))
        
        label.pack()
        
        # Position tooltip
        self._position_tooltip()
    
    def _position_tooltip(self):
        """Position the tooltip relative to the cursor/widget."""
        if not self._tooltip_window:
            return
        
        # Get tooltip size
        self._tooltip_window.update_idletasks()
        tw_width = self._tooltip_window.winfo_reqwidth()
        tw_height = self._tooltip_window.winfo_reqheight()
        
        # Calculate position
        x = getattr(self, '_mouse_x', 0) + 10
        y = getattr(self, '_mouse_y', 0) + 10
        
        # Adjust for screen boundaries
        screen_width = self._tooltip_window.winfo_screenwidth()
        screen_height = self._tooltip_window.winfo_screenheight()
        
        if x + tw_width > screen_width:
            x = x - tw_width - 20
        if y + tw_height > screen_height:
            y = y - tw_height - 20
        
        self._tooltip_window.wm_geometry(f"+{x}+{y}")
    
    def _hide_tooltip(self):
        """Hide the tooltip window."""
        if self._tooltip_window:
            self._tooltip_window.destroy()
            self._tooltip_window = None
    
    def set_text(self, text: str):
        """Update tooltip text."""
        self.tooltip_text = text
    
    def set_delay(self, delay: int):
        """Update tooltip delay."""
        self.delay = delay


class ProgressBar(BaseComponent):
    """
    Progress indication component.
    """
    
    def __init__(self, parent: tk.Widget,
                 mode: str = "determinate",  # determinate, indeterminate
                 value: float = 0.0,
                 maximum: float = 100.0,
                 show_text: bool = True,
                 text_format: str = "{percent}%",  # {percent}, {value}/{max}, custom
                 color_scheme: str = "default",  # default, success, warning, error
                 **kwargs):
        """
        Initialize the progress bar.
        
        Args:
            parent: Parent widget
            mode: Progress mode
            value: Current progress value
            maximum: Maximum progress value
            show_text: Whether to show progress text
            text_format: Format for progress text
            color_scheme: Color scheme for the progress bar
            **kwargs: Additional widget options
        """
        self.mode = mode
        self._value = value
        self.maximum = maximum
        self.show_text = show_text
        self.text_format = text_format
        self.color_scheme = color_scheme
        
        super().__init__(parent, **kwargs)
        
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the progress bar widget."""
        container = ttk.Frame(self.parent)
        
        # Create progress bar
        style_name = f"Custom.{self.color_scheme}.Horizontal.TProgressbar"
        
        self.progress = ttk.Progressbar(container,
                                       mode=self.mode,
                                       maximum=self.maximum,
                                       value=self._value,
                                       style=style_name)
        
        self.progress.pack(side=tk.TOP, fill=tk.X, expand=True, pady=(0, 5))
        
        # Text overlay
        if self.show_text:
            self.text_label = tk.Label(container, text=self._get_progress_text())
            self.text_label.pack(side=tk.BOTTOM)
        
        # Apply color scheme
        self._setup_style()
        
        return container
    
    def _setup_style(self):
        """Setup custom styling for the progress bar."""
        style = ttk.Style()
        
        color_schemes = {
            'default': {'bg': '#007bff', 'fg': '#e9ecef'},
            'success': {'bg': '#28a745', 'fg': '#e9ecef'},
            'warning': {'bg': '#ffc107', 'fg': '#e9ecef'},
            'error': {'bg': '#dc3545', 'fg': '#e9ecef'}
        }
        
        colors = color_schemes.get(self.color_scheme, color_schemes['default'])
        style_name = f"Custom.{self.color_scheme}.Horizontal.TProgressbar"
        
        try:
            style.theme_use('clam')
            style.configure(style_name,
                          background=colors['bg'],
                          troughcolor=colors['fg'],
                          borderwidth=1,
                          lightcolor=colors['bg'],
                          darkcolor=colors['bg'])
        except:
            # Fallback if styling fails
            pass
    
    def _get_progress_text(self) -> str:
        """Get the progress text based on format."""
        if self.mode == "indeterminate":
            return "Processing..."
        
        percent = (self._value / self.maximum) * 100 if self.maximum > 0 else 0
        
        if self.text_format == "{percent}%":
            return f"{percent:.1f}%"
        elif self.text_format == "{value}/{max}":
            return f"{self._value:.1f}/{self.maximum:.1f}"
        else:
            # Custom format
            return self.text_format.format(
                percent=percent,
                value=self._value,
                max=self.maximum
            )
    
    def set_value(self, value: float):
        """Update progress value."""
        self._value = max(0, min(self.maximum, value))
        
        if hasattr(self, 'progress'):
            self.progress['value'] = self._value
        
        if hasattr(self, 'text_label') and self.show_text:
            self.text_label.configure(text=self._get_progress_text())
    
    def get_value(self) -> float:
        """Get current progress value."""
        return self._value
    
    def set_maximum(self, maximum: float):
        """Update maximum value."""
        self.maximum = maximum
        if hasattr(self, 'progress'):
            self.progress['maximum'] = maximum
        
        if hasattr(self, 'text_label') and self.show_text:
            self.text_label.configure(text=self._get_progress_text())
    
    def start_indeterminate(self):
        """Start indeterminate progress animation."""
        if hasattr(self, 'progress'):
            self.progress.start(10)  # 10ms intervals
    
    def stop_indeterminate(self):
        """Stop indeterminate progress animation."""
        if hasattr(self, 'progress'):
            self.progress.stop()
    
    def set_color_scheme(self, scheme: str):
        """Update color scheme."""
        self.color_scheme = scheme
        self._setup_style()


class StatusIndicator(BaseComponent):
    """
    System status display component.
    """
    
    def __init__(self, parent: tk.Widget,
                 status: str = "unknown",  # success, warning, error, info, unknown
                 text: str = "",
                 show_icon: bool = True,
                 blink: bool = False,
                 size: str = "medium",  # small, medium, large
                 **kwargs):
        """
        Initialize the status indicator.
        
        Args:
            parent: Parent widget
            status: Current status
            text: Status text
            show_icon: Whether to show status icon
            blink: Whether to blink for attention
            size: Indicator size
            **kwargs: Additional widget options
        """
        self.status = status
        self.status_text = text
        self.show_icon = show_icon
        self.blink = blink
        self.size = size
        self._blink_state = True
        self._blink_job = None
        
        super().__init__(parent, **kwargs)
        
        if self.blink:
            self._start_blinking()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the status indicator widget."""
        container = ttk.Frame(self.parent)
        
        # Status configuration
        status_configs = {
            'success': {'color': '#28a745', 'symbol': '●', 'text_color': '#155724'},
            'warning': {'color': '#ffc107', 'symbol': '▲', 'text_color': '#856404'},
            'error': {'color': '#dc3545', 'symbol': '●', 'text_color': '#721c24'},
            'info': {'color': '#17a2b8', 'symbol': '●', 'text_color': '#0c5460'},
            'unknown': {'color': '#6c757d', 'symbol': '?', 'text_color': '#495057'}
        }
        
        config = status_configs.get(self.status, status_configs['unknown'])
        
        # Size configuration
        size_configs = {
            'small': {'font_size': 8, 'icon_size': 10},
            'medium': {'font_size': 10, 'icon_size': 12},
            'large': {'font_size': 12, 'icon_size': 14}
        }
        
        size_config = size_configs.get(self.size, size_configs['medium'])
        
        # Icon indicator
        if self.show_icon:
            self.icon_label = tk.Label(container,
                                     text=config['symbol'],
                                     foreground=config['color'],
                                     font=('Arial', size_config['icon_size'], 'bold'))
            self.icon_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status text
        if self.status_text:
            self.text_label = tk.Label(container,
                                     text=self.status_text,
                                     foreground=config['text_color'],
                                     font=('Arial', size_config['font_size']))
            self.text_label.pack(side=tk.LEFT)
        
        return container
    
    def _start_blinking(self):
        """Start blinking animation."""
        if not self.blink:
            return
        
        self._blink_state = not self._blink_state
        
        if hasattr(self, 'icon_label'):
            if self._blink_state:
                self.icon_label.configure(foreground=self._get_status_color())
            else:
                self.icon_label.configure(foreground='lightgray')
        
        # Schedule next blink
        self._blink_job = self.widget.after(500, self._start_blinking)
    
    def _get_status_color(self) -> str:
        """Get color for current status."""
        colors = {
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'info': '#17a2b8',
            'unknown': '#6c757d'
        }
        return colors.get(self.status, colors['unknown'])
    
    def set_status(self, status: str, text: str = None):
        """Update the status."""
        old_status = self.status
        self.status = status
        
        if text is not None:
            self.status_text = text
        
        # Update visual elements
        if hasattr(self, 'icon_label'):
            status_configs = {
                'success': {'color': '#28a745', 'symbol': '●'},
                'warning': {'color': '#ffc107', 'symbol': '▲'},
                'error': {'color': '#dc3545', 'symbol': '●'},
                'info': {'color': '#17a2b8', 'symbol': '●'},
                'unknown': {'color': '#6c757d', 'symbol': '?'}
            }
            config = status_configs.get(status, status_configs['unknown'])
            self.icon_label.configure(text=config['symbol'], foreground=config['color'])
        
        if hasattr(self, 'text_label') and text is not None:
            text_colors = {
                'success': '#155724',
                'warning': '#856404',
                'error': '#721c24',
                'info': '#0c5460',
                'unknown': '#495057'
            }
            text_color = text_colors.get(status, text_colors['unknown'])
            self.text_label.configure(text=text, foreground=text_color)
        
        # Trigger status change event
        self.trigger_event('status_changed', {'old_status': old_status, 'new_status': status})
    
    def set_blinking(self, blink: bool):
        """Enable or disable blinking."""
        self.blink = blink
        
        if self._blink_job:
            self.widget.after_cancel(self._blink_job)
            self._blink_job = None
        
        if blink:
            self._start_blinking()
        else:
            # Reset to normal color
            if hasattr(self, 'icon_label'):
                self.icon_label.configure(foreground=self._get_status_color())
    
    def set_text(self, text: str):
        """Update status text."""
        self.status_text = text
        if hasattr(self, 'text_label'):
            self.text_label.configure(text=text)
