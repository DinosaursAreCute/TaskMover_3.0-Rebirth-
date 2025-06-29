"""
Base Component System
====================

Foundation classes for all TaskMover UI components with modern design principles,
accessibility features, and consistent behavior patterns.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable, Union, List, Literal
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ComponentState(Enum):
    """Standard component states for consistent UI behavior."""
    DEFAULT = "default"
    HOVER = "hover"
    ACTIVE = "active"
    FOCUS = "focus"
    DISABLED = "disabled"
    LOADING = "loading"


class ComponentSize(Enum):
    """Standard component sizes following design system."""
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"


@dataclass
class ComponentTheme:
    """Theme configuration for components."""
    primary: str = "#2563eb"
    secondary: str = "#64748b"
    success: str = "#16a34a"
    warning: str = "#d97706"
    error: str = "#dc2626"
    background: str = "#ffffff"
    surface: str = "#f8fafc"
    border: str = "#e2e8f0"
    text: str = "#1e293b"
    text_secondary: str = "#64748b"
    
    # Spacing system
    spacing_xs: int = 4
    spacing_sm: int = 8
    spacing_md: int = 16
    spacing_lg: int = 24
    spacing_xl: int = 32
    spacing_2xl: int = 48
    
    # Typography
    font_family: str = "Segoe UI"
    font_size_caption: int = 12
    font_size_body: int = 14
    font_size_body_large: int = 16
    font_size_heading_2: int = 20
    font_size_heading_1: int = 24
    font_size_display: int = 32


class BaseComponent(ABC, tk.Frame):
    """
    Base class for all UI components providing consistent behavior,
    accessibility features, and modern design patterns.
    """
    
    def __init__(
        self,
        parent: Union[tk.Widget, tk.Tk, tk.Toplevel],
        theme: Optional[ComponentTheme] = None,
        size: ComponentSize = ComponentSize.MD,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.theme = theme or ComponentTheme()
        self.size = size
        self.state = ComponentState.DEFAULT
        self._callbacks: Dict[str, List[Callable]] = {}
        self._keyboard_bindings: Dict[str, Callable] = {}
        
        # Configure base styling
        self._setup_base_styling()
        self._setup_accessibility()
        self._create_component()
        
        logger.debug(f"Created {self.__class__.__name__} component")
    
    def _setup_base_styling(self):
        """Configure base styling and theme."""
        self.configure(
            bg=self.theme.surface,
            relief='flat',
            bd=0
        )
    
    def _setup_accessibility(self):
        """Setup accessibility features including keyboard navigation."""
        # Standard keyboard bindings
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<FocusOut>', self._on_focus_out)
        self.bind('<Enter>', self._on_mouse_enter)
        self.bind('<Leave>', self._on_mouse_leave)
        
        # Make component focusable
        self.focus_set()
    
    @abstractmethod
    def _create_component(self):
        """Create the component's UI elements. Must be implemented by subclasses."""
        pass
    
    def _on_focus_in(self, event):
        """Handle focus gained."""
        self.set_state(ComponentState.FOCUS)
        self._trigger_callback('focus_in', event)
    
    def _on_focus_out(self, event):
        """Handle focus lost."""
        self.set_state(ComponentState.DEFAULT)
        self._trigger_callback('focus_out', event)
    
    def _on_mouse_enter(self, event):
        """Handle mouse enter."""
        if self.state != ComponentState.DISABLED:
            self.set_state(ComponentState.HOVER)
            self._trigger_callback('mouse_enter', event)
    
    def _on_mouse_leave(self, event):
        """Handle mouse leave."""
        if self.state != ComponentState.DISABLED:
            self.set_state(ComponentState.DEFAULT)
            self._trigger_callback('mouse_leave', event)
    
    def set_state(self, state: ComponentState):
        """Set component state with visual feedback."""
        old_state = self.state
        self.state = state
        self._update_visual_state()
        self._trigger_callback('state_changed', {'old': old_state, 'new': state})
    
    def _update_visual_state(self):
        """Update component appearance based on current state."""
        state_colors = {
            ComponentState.DEFAULT: self.theme.surface,
            ComponentState.HOVER: "#f1f5f9",  # Slightly darker
            ComponentState.ACTIVE: "#e2e8f0",  # Darker
            ComponentState.FOCUS: self.theme.surface,
            ComponentState.DISABLED: "#f8fafc",
            ComponentState.LOADING: self.theme.surface,
        }
        
        self.configure(bg=state_colors.get(self.state, self.theme.surface))
        
        # Add focus ring for accessibility
        if self.state == ComponentState.FOCUS:
            self.configure(highlightbackground=self.theme.primary, highlightthickness=2)
        else:
            self.configure(highlightthickness=0)
    
    def add_callback(self, event_name: str, callback: Callable):
        """Add event callback."""
        if event_name not in self._callbacks:
            self._callbacks[event_name] = []
        self._callbacks[event_name].append(callback)
    
    def _trigger_callback(self, event_name: str, data: Any = None):
        """Trigger callbacks for an event."""
        for callback in self._callbacks.get(event_name, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in callback for {event_name}: {e}")
    
    def add_keyboard_binding(self, key_sequence: str, callback: Callable):
        """Add keyboard shortcut."""
        self.bind(key_sequence, callback)
        self._keyboard_bindings[key_sequence] = callback
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the component."""
        if enabled:
            self.set_state(ComponentState.DEFAULT)
        else:
            self.set_state(ComponentState.DISABLED)
    
    def show_loading(self, loading: bool = True):
        """Show or hide loading state."""
        if loading:
            self.set_state(ComponentState.LOADING)
        else:
            self.set_state(ComponentState.DEFAULT)


class ModernButton(BaseComponent):
    """Modern button component with consistent styling and behavior."""
    
    def __init__(
        self,
        parent: tk.Widget,
        text: str = "",
        icon: str = "",
        command: Optional[Callable] = None,
        variant: str = "primary",  # Changed from button_type to variant
        width: Optional[int] = None,
        state: Literal["normal", "disabled"] = "normal",
        **kwargs
    ):
        # Filter out custom parameters that shouldn't go to tkinter
        custom_params = {
            'text', 'icon', 'command', 'variant', 'width', 'state'
        }
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in custom_params}
        
        self.text = text
        self.icon = icon
        self.command = command
        self.variant = variant
        self.button_width = width
        self.button_state = state
        
        super().__init__(parent, **filtered_kwargs)
    
    def _create_component(self):
        """Create button UI."""
        from .theme_manager import get_theme_manager
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Create button
        button_text = f"{self.icon} {self.text}".strip() if self.icon else self.text
        
        valid_states: Dict[str, Literal["normal", "disabled"]] = {"normal": "normal", "disabled": "disabled", "active": "normal"}
        button_state = valid_states.get(self.button_state, "normal")
        
        self.button = tk.Button(
            self,
            text=button_text,
            command=self._on_click,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            state=button_state,
            cursor="hand2" if self.button_state == "normal" else "arrow",
            relief="flat",
            bd=0,
            padx=tokens.spacing["md"],
            pady=tokens.spacing["sm"]
        )
        
        if self.button_width:
            self.button.configure(width=self.button_width)
        
        self.button.pack(fill="both", expand=True)
        
        # Configure button styling based on variant
        self._setup_button_styling()
    
    def _setup_button_styling(self):
        """Setup button styling based on variant."""
        from .theme_manager import get_theme_manager
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Color schemes for different variants
        if self.variant == "primary":
            bg_color = tokens.colors["primary"]
            fg_color = "white"
            hover_color = tokens.colors["primary_dark"]
        elif self.variant == "secondary":
            bg_color = tokens.colors["surface"]
            fg_color = tokens.colors["text"]
            hover_color = tokens.colors["hover"]
        elif self.variant == "danger":
            bg_color = tokens.colors["error"]
            fg_color = "white"
            hover_color = "#c0392b"  # Darker red
        else:
            bg_color = tokens.colors["surface"]
            fg_color = tokens.colors["text"]
            hover_color = tokens.colors["hover"]
        
        # Apply base styling
        self.button.configure(
            bg=bg_color,
            fg=fg_color,
            activebackground=hover_color,
            activeforeground=fg_color
        )
        
        # Hover effects
        def on_enter(event):
            if self.button_state == "normal":
                self.button.configure(bg=hover_color)
        
        def on_leave(event):
            if self.button_state == "normal":
                self.button.configure(bg=bg_color)
        
        self.button.bind("<Enter>", on_enter)
        self.button.bind("<Leave>", on_leave)
    
    def _on_click(self):
        """Handle button click."""
        if self.state != ComponentState.DISABLED and self.command:
            self.set_state(ComponentState.ACTIVE)
            self.after(100, lambda: self.set_state(ComponentState.DEFAULT))
            self.command()


class ModernCard(BaseComponent):
    """Modern card component for displaying grouped content."""
    
    def __init__(
        self,
        parent: tk.Widget,
        title: str = "",
        subtitle: str = "",
        **kwargs
    ):
        self.title = title
        self.subtitle = subtitle
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create card UI."""
        # Configure card appearance
        self.configure(
            bg="white",
            relief="solid",
            bd=1,
            highlightbackground=self.theme.border,
            highlightthickness=1
        )
        
        # Header section
        if self.title or self.subtitle:
            header_frame = tk.Frame(self, bg="white")
            header_frame.pack(fill="x", padx=self.theme.spacing_md, pady=(self.theme.spacing_md, 0))
            
            if self.title:
                title_label = tk.Label(
                    header_frame,
                    text=self.title,
                    font=(self.theme.font_family, self.theme.font_size_heading_2, "bold"),
                    bg="white",
                    fg=self.theme.text,
                    anchor="w"
                )
                title_label.pack(fill="x")
            
            if self.subtitle:
                subtitle_label = tk.Label(
                    header_frame,
                    text=self.subtitle,
                    font=(self.theme.font_family, self.theme.font_size_body, "normal"),
                    bg="white",
                    fg=self.theme.text_secondary,
                    anchor="w"
                )
                subtitle_label.pack(fill="x")
        
        # Content area
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(fill="both", expand=True, padx=self.theme.spacing_md, pady=self.theme.spacing_md)
    
    def add_content(self, widget: tk.Widget):
        """Add content to the card."""
        widget.pack(in_=self.content_frame, fill="x", pady=(0, self.theme.spacing_sm))


class StatusBar(BaseComponent):
    """Status bar component for displaying application status."""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.status_items: Dict[str, tk.Label] = {}
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create status bar UI."""
        self.configure(
            bg=self.theme.surface,
            relief="sunken",
            bd=1,
            height=30
        )
        
        # Create status sections
        self.left_frame = tk.Frame(self, bg=self.theme.surface)
        self.left_frame.pack(side="left", fill="x", expand=True, padx=self.theme.spacing_sm)
        
        self.right_frame = tk.Frame(self, bg=self.theme.surface)
        self.right_frame.pack(side="right", padx=self.theme.spacing_sm)
    
    def set_status(self, key: str, text: str, side: str = "left"):
        """Set status text for a specific key."""
        parent_frame = self.left_frame if side == "left" else self.right_frame
        
        if key not in self.status_items:
            label = tk.Label(
                parent_frame,
                font=(self.theme.font_family, self.theme.font_size_caption, "normal"),
                bg=self.theme.surface,
                fg=self.theme.text_secondary
            )
            label.pack(side="left" if side == "left" else "right", padx=self.theme.spacing_sm)
            self.status_items[key] = label
        
        self.status_items[key].configure(text=text)


# Export main classes
__all__ = [
    "BaseComponent",
    "ComponentState", 
    "ComponentSize",
    "ComponentTheme",
    "ModernButton",
    "ModernCard",
    "StatusBar",
]