"""
Theme Manager System
===================

Comprehensive theme management for TaskMover UI with light/dark mode support,
design tokens, and consistent styling across all components.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from dataclasses import dataclass, asdict, field
import json
import logging

logger = logging.getLogger(__name__)


class ThemeMode(Enum):
    """Available theme modes."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


@dataclass
class DesignTokens:
    """Design system tokens for consistent styling."""
    
    # Color palette
    colors: Dict[str, str] = field(default_factory=dict)
    
    # Typography
    fonts: Dict[str, str] = field(default_factory=dict)
    
    # Spacing
    spacing: Dict[str, int] = field(default_factory=dict)
    
    # Shadows
    shadows: Dict[str, str] = field(default_factory=dict)
    
    # Border radius
    radius: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.colors:
            self.colors = {
                # Primary colors
                "primary": "#2563eb",
                "primary_dark": "#1d4ed8", 
                "primary_darker": "#1e40af",
                "primary_light": "#3b82f6",
                
                # Semantic colors
                "secondary": "#64748b",
                "success": "#16a34a",
                "warning": "#d97706",
                "error": "#dc2626",
                "info": "#0ea5e9",
                
                # Neutral colors (light theme)
                "background": "#ffffff",
                "surface": "#f8fafc",
                "surface_variant": "#f1f5f9",
                "border": "#e2e8f0",
                "border_variant": "#cbd5e1",
                "text": "#1e293b",
                "text_secondary": "#64748b",
                "text_disabled": "#94a3b8",
                
                # Interactive states
                "hover": "#f1f5f9",
                "active": "#e2e8f0",
                "focus": "#dbeafe",
                "disabled": "#f8fafc",
            }
        
        if not self.fonts:
            self.fonts = {
                "family": "Segoe UI",
                "family_mono": "Consolas",
                "size_caption": "9",
                "size_body": "11", 
                "size_body_large": "13",
                "size_heading_2": "16",
                "size_heading_1": "20",
                "size_display": "24",
                "weight_normal": "normal",
                "weight_semibold": "bold",
                "weight_bold": "bold",
            }
        
        if not self.spacing:
            self.spacing = {
                "xs": 4,
                "sm": 8, 
                "md": 16,
                "lg": 24,
                "xl": 32,
                "2xl": 48,
            }
        
        if not self.shadows:
            self.shadows = {
                "sm": "1 1 3 rgba(0,0,0,0.1)",
                "md": "2 2 6 rgba(0,0,0,0.15)",
                "lg": "4 4 12 rgba(0,0,0,0.2)",
            }
        
        if not self.radius:
            self.radius = {
                "sm": 4,
                "md": 6,
                "lg": 8,
                "xl": 12,
            }


@dataclass
class DarkTokens(DesignTokens):
    """Dark theme design tokens."""
    
    def __post_init__(self):
        super().__post_init__()
        # Override colors for dark theme
        self.colors.update({
            # Primary colors (adjusted for dark)
            "primary": "#3b82f6",
            "primary_dark": "#2563eb",
            "primary_darker": "#1d4ed8", 
            "primary_light": "#60a5fa",
            
            # Semantic colors (adjusted for dark)
            "secondary": "#94a3b8",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "info": "#06b6d4",
            
            # Neutral colors (dark theme)
            "background": "#0f172a",
            "surface": "#1e293b",
            "surface_variant": "#334155",
            "border": "#334155",
            "border_variant": "#475569",
            "text": "#f8fafc",
            "text_secondary": "#cbd5e1", 
            "text_disabled": "#64748b",
            
            # Interactive states (dark)
            "hover": "#334155",
            "active": "#475569",
            "focus": "#1e40af",
            "disabled": "#1e293b",
        })


class ThemeManager:
    """
    Centralized theme management system providing consistent styling,
    theme switching, and design token management.
    """
    
    def __init__(self):
        self.current_mode = ThemeMode.LIGHT
        self.light_tokens = DesignTokens()
        self.dark_tokens = DarkTokens()
        self._observers: List[Callable] = []
        self._ttk_style: Optional[ttk.Style] = None
        
        logger.info("ThemeManager initialized")
    
    def initialize_ttk_styles(self, root: tk.Tk):
        """Initialize TTK styles with current theme."""
        self._ttk_style = ttk.Style(root)
        self._setup_base_styles()
        self._apply_theme_styles()
        
        logger.info(f"TTK styles initialized for {self.current_mode.value} theme")
    
    def _setup_base_styles(self):
        """Setup base TTK styles."""
        if not self._ttk_style:
            return
            
        tokens = self.get_current_tokens()
        
        # Configure base styles
        self._ttk_style.theme_use('clam')  # Use clam as base theme
        
        # Button styles
        self._configure_button_styles(tokens)
        
        # Frame styles
        self._configure_frame_styles(tokens)
        
        # Entry styles
        self._configure_entry_styles(tokens)
        
        # Treeview styles
        self._configure_treeview_styles(tokens)
        
        # Notebook styles
        self._configure_notebook_styles(tokens)
    
    def _configure_button_styles(self, tokens: DesignTokens):
        """Configure button styles."""
        # Primary button
        self._ttk_style.configure(
            "Primary.TButton",
            background=tokens.colors["primary"],
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=(tokens.fonts["family"], tokens.fonts["size_body"], tokens.fonts["weight_normal"]),
            padding=(tokens.spacing["md"], tokens.spacing["sm"]),
        )
        
        self._ttk_style.map(
            "Primary.TButton",
            background=[
                ("active", tokens.colors["primary_dark"]),
                ("pressed", tokens.colors["primary_darker"]),
                ("disabled", tokens.colors["disabled"]),
            ],
            foreground=[("disabled", tokens.colors["text_disabled"])],
        )
        
        # Secondary button
        self._ttk_style.configure(
            "Secondary.TButton",
            background=tokens.colors["surface"],
            foreground=tokens.colors["text"],
            borderwidth=1,
            bordercolor=tokens.colors["border"],
            focuscolor="none",
            font=(tokens.fonts["family"], tokens.fonts["size_body"], tokens.fonts["weight_normal"]),
            padding=(tokens.spacing["md"], tokens.spacing["sm"]),
        )
        
        self._ttk_style.map(
            "Secondary.TButton",
            background=[
                ("active", tokens.colors["hover"]),
                ("pressed", tokens.colors["active"]),
                ("disabled", tokens.colors["disabled"]),
            ],
            bordercolor=[("focus", tokens.colors["primary"])],
        )
        
        # Icon button (small)
        self._ttk_style.configure(
            "Icon.TButton",
            background=tokens.colors["surface"],
            foreground=tokens.colors["text"],
            borderwidth=0,
            focuscolor="none",
            font=(tokens.fonts["family"], tokens.fonts["size_body"], tokens.fonts["weight_normal"]),
            padding=(tokens.spacing["sm"], tokens.spacing["sm"]),
        )
        
        # Toolbar button
        self._ttk_style.configure(
            "Toolbar.TButton",
            background=tokens.colors["surface"],
            foreground=tokens.colors["text"],
            borderwidth=0,
            focuscolor="none",
            font=(tokens.fonts["family"], tokens.fonts["size_caption"], tokens.fonts["weight_normal"]),
            padding=(tokens.spacing["sm"], tokens.spacing["xs"]),
        )
    
    def _configure_frame_styles(self, tokens: DesignTokens):
        """Configure frame styles."""
        # Card frame
        self._ttk_style.configure(
            "Card.TFrame",
            background=tokens.colors["background"],
            borderwidth=1,
            relief="solid",
            bordercolor=tokens.colors["border"],
        )
        
        # Sidebar frame
        self._ttk_style.configure(
            "Sidebar.TFrame",
            background=tokens.colors["surface"],
            borderwidth=1,
            relief="solid", 
            bordercolor=tokens.colors["border"],
        )
        
        # Toolbar frame
        self._ttk_style.configure(
            "Toolbar.TFrame",
            background=tokens.colors["surface"],
            borderwidth=0,
            relief="flat",
        )
    
    def _configure_entry_styles(self, tokens: DesignTokens):
        """Configure entry/input styles."""
        self._ttk_style.configure(
            "Modern.TEntry",
            borderwidth=1,
            relief="solid",
            bordercolor=tokens.colors["border"],
            focuscolor=tokens.colors["primary"],
            font=(tokens.fonts["family"], tokens.fonts["size_body"], tokens.fonts["weight_normal"]),
            padding=(tokens.spacing["sm"], tokens.spacing["xs"]),
        )
        
        self._ttk_style.map(
            "Modern.TEntry",
            bordercolor=[("focus", tokens.colors["primary"])],
            background=[
                ("readonly", tokens.colors["surface_variant"]),
                ("disabled", tokens.colors["disabled"]),
            ],
        )
    
    def _configure_treeview_styles(self, tokens: DesignTokens):
        """Configure treeview/table styles."""
        self._ttk_style.configure(
            "Modern.Treeview",
            background=tokens.colors["background"],
            foreground=tokens.colors["text"],
            borderwidth=1,
            relief="solid",
            bordercolor=tokens.colors["border"],
            font=(tokens.fonts["family"], tokens.fonts["size_body"], tokens.fonts["weight_normal"]),
            rowheight=28,
        )
        
        self._ttk_style.configure(
            "Modern.Treeview.Heading",
            background=tokens.colors["surface"],
            foreground=tokens.colors["text"],
            borderwidth=1,
            relief="solid",
            bordercolor=tokens.colors["border"],
            font=(tokens.fonts["family"], tokens.fonts["size_body"], tokens.fonts["weight_semibold"]),
            padding=(tokens.spacing["sm"], tokens.spacing["xs"]),
        )
        
        self._ttk_style.map(
            "Modern.Treeview",
            background=[("selected", tokens.colors["primary"])],
            foreground=[("selected", "white")],
        )
    
    def _configure_notebook_styles(self, tokens: DesignTokens):
        """Configure notebook/tab styles."""
        self._ttk_style.configure(
            "Modern.TNotebook",
            background=tokens.colors["surface"],
            borderwidth=0,
        )
        
        self._ttk_style.configure(
            "Modern.TNotebook.Tab",
            background=tokens.colors["surface"],
            foreground=tokens.colors["text"],
            borderwidth=1,
            bordercolor=tokens.colors["border"],
            font=(tokens.fonts["family"], tokens.fonts["size_body"], tokens.fonts["weight_normal"]),
            padding=(tokens.spacing["md"], tokens.spacing["sm"]),
        )
        
        self._ttk_style.map(
            "Modern.TNotebook.Tab",
            background=[
                ("selected", tokens.colors["background"]),
                ("active", tokens.colors["hover"]),
            ],
            bordercolor=[("selected", tokens.colors["primary"])],
        )
    
    def _apply_theme_styles(self):
        """Apply current theme to all configured styles."""
        tokens = self.get_current_tokens()
        
        # Re-configure all styles with current theme tokens
        self._configure_button_styles(tokens)
        self._configure_frame_styles(tokens)
        self._configure_entry_styles(tokens)
        self._configure_treeview_styles(tokens)
        self._configure_notebook_styles(tokens)
    
    def get_current_tokens(self) -> DesignTokens:
        """Get design tokens for current theme mode."""
        if self.current_mode == ThemeMode.DARK:
            return self.dark_tokens
        else:
            return self.light_tokens
    
    def set_theme_mode(self, mode: ThemeMode):
        """Switch to specified theme mode."""
        if mode != self.current_mode:
            old_mode = self.current_mode
            self.current_mode = mode
            
            # Reapply styles if TTK is initialized
            if self._ttk_style:
                self._apply_theme_styles()
            
            # Notify observers
            self._notify_theme_changed(old_mode, mode)
            
            logger.info(f"Theme switched from {old_mode.value} to {mode.value}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_mode = ThemeMode.DARK if self.current_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
        self.set_theme_mode(new_mode)
    
    def add_theme_observer(self, callback: Callable):
        """Add observer for theme changes."""
        self._observers.append(callback)
    
    def remove_theme_observer(self, callback: Callable):
        """Remove theme change observer."""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_theme_changed(self, old_mode: ThemeMode, new_mode: ThemeMode):
        """Notify all observers of theme change."""
        for observer in self._observers:
            try:
                observer(old_mode, new_mode)
            except Exception as e:
                logger.error(f"Error notifying theme observer: {e}")
    
    def get_color(self, color_name: str) -> str:
        """Get color value from current theme."""
        tokens = self.get_current_tokens()
        return tokens.colors.get(color_name, "#000000")
    
    def get_font(self, font_name: str) -> str:
        """Get font value from current theme."""
        tokens = self.get_current_tokens()
        return tokens.fonts.get(font_name, "Arial")
    
    def get_spacing(self, spacing_name: str) -> int:
        """Get spacing value from current theme."""
        tokens = self.get_current_tokens()
        return tokens.spacing.get(spacing_name, 8)
    
    def export_theme(self, filepath: str):
        """Export current theme configuration to file."""
        tokens = self.get_current_tokens()
        theme_data = {
            "mode": self.current_mode.value,
            "tokens": asdict(tokens)
        }
        
        with open(filepath, 'w') as f:
            json.dump(theme_data, f, indent=2)
        
        logger.info(f"Theme exported to {filepath}")
    
    def import_theme(self, filepath: str):
        """Import theme configuration from file."""
        try:
            with open(filepath, 'r') as f:
                theme_data = json.load(f)
            
            # Apply imported tokens
            if theme_data.get("mode") == "dark":
                self.dark_tokens = DarkTokens(**theme_data["tokens"])
                self.set_theme_mode(ThemeMode.DARK)
            else:
                self.light_tokens = DesignTokens(**theme_data["tokens"])
                self.set_theme_mode(ThemeMode.LIGHT)
            
            logger.info(f"Theme imported from {filepath}")
            
        except Exception as e:
            logger.error(f"Error importing theme: {e}")
            raise


# Global theme manager instance
theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    return theme_manager


# Export main classes
__all__ = [
    "ThemeManager",
    "ThemeMode", 
    "DesignTokens",
    "DarkTokens",
    "theme_manager",
    "get_theme_manager",
]