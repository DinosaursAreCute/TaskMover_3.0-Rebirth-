"""
TaskMover UI Framework - Theme Management System
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
from enum import Enum
import json
import os
from pathlib import Path


class ThemeMode(Enum):
    """Available theme modes"""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class ThemeManager:
    """
    Centralized theme management for consistent styling across the application.
    Supports light/dark themes and custom styling.
    """
    
    def __init__(self):
        """Initialize the theme manager."""
        self.current_mode = ThemeMode.LIGHT
        self._themes: Dict[str, Dict] = {}
        self._component_styles: Dict[str, Dict] = {}
        
        # Color palettes
        self._color_palettes = {
            ThemeMode.LIGHT: {
                'primary': '#2563eb',      # Blue-600
                'primary_hover': '#1d4ed8', # Blue-700
                'secondary': '#64748b',     # Slate-500
                'accent': '#10b981',        # Emerald-500
                'neutral_50': '#f8fafc',    # Slate-50
                'neutral_100': '#f1f5f9',   # Slate-100
                'neutral_200': '#e2e8f0',   # Slate-200
                'neutral_300': '#cbd5e1',   # Slate-300
                'neutral_400': '#94a3b8',   # Slate-400
                'neutral_500': '#64748b',   # Slate-500
                'neutral_600': '#475569',   # Slate-600
                'neutral_700': '#334155',   # Slate-700
                'neutral_800': '#1e293b',   # Slate-800
                'neutral_900': '#0f172a',   # Slate-900
                'background': '#ffffff',
                'surface': '#f8fafc',
                'text_primary': '#0f172a',
                'text_secondary': '#475569',
                'text_muted': '#94a3b8',
                'border': '#e2e8f0',
                'error': '#dc2626',
                'warning': '#d97706',
                'success': '#059669',
                'info': '#0284c7'
            },
            ThemeMode.DARK: {
                'primary': '#3b82f6',      # Blue-500
                'primary_hover': '#2563eb', # Blue-600
                'secondary': '#64748b',     # Slate-500
                'accent': '#10b981',        # Emerald-500
                'neutral_50': '#0f172a',    # Slate-900 (inverted)
                'neutral_100': '#1e293b',   # Slate-800
                'neutral_200': '#334155',   # Slate-700
                'neutral_300': '#475569',   # Slate-600
                'neutral_400': '#64748b',   # Slate-500
                'neutral_500': '#94a3b8',   # Slate-400
                'neutral_600': '#cbd5e1',   # Slate-300
                'neutral_700': '#e2e8f0',   # Slate-200
                'neutral_800': '#f1f5f9',   # Slate-100
                'neutral_900': '#f8fafc',   # Slate-50
                'background': '#0f172a',
                'surface': '#1e293b',
                'text_primary': '#f8fafc',
                'text_secondary': '#cbd5e1',
                'text_muted': '#64748b',
                'border': '#334155',
                'error': '#ef4444',
                'warning': '#f59e0b',
                'success': '#22c55e',
                'info': '#3b82f6'
            }
        }
        
        # Typography system
        self._typography = {
            'heading_large': {'family': 'Segoe UI', 'size': 24, 'weight': 'bold'},
            'heading_medium': {'family': 'Segoe UI', 'size': 20, 'weight': 'bold'},
            'heading_small': {'family': 'Segoe UI', 'size': 16, 'weight': 'bold'},
            'body_large': {'family': 'Segoe UI', 'size': 14, 'weight': 'normal'},
            'body_medium': {'family': 'Segoe UI', 'size': 12, 'weight': 'normal'},
            'body_small': {'family': 'Segoe UI', 'size': 10, 'weight': 'normal'},
            'caption': {'family': 'Segoe UI', 'size': 9, 'weight': 'normal'},
            'button': {'family': 'Segoe UI', 'size': 12, 'weight': 'normal'},
            'code': {'family': 'Consolas', 'size': 11, 'weight': 'normal'}
        }
        
        # Spacing system (in pixels)
        self._spacing = {
            'xs': 2,
            'sm': 4,
            'md': 8,
            'lg': 16,
            'xl': 24,
            'xxl': 32,
            'xxxl': 48
        }
        
        # Shadow and elevation system
        self._shadows = {
            'none': '',
            'sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
            'md': '0 4px 6px rgba(0, 0, 0, 0.1)',
            'lg': '0 10px 15px rgba(0, 0, 0, 0.1)',
            'xl': '0 20px 25px rgba(0, 0, 0, 0.1)'
        }
        
        # Animation timing and easing
        self._animations = {
            'duration_fast': 150,
            'duration_normal': 300,
            'duration_slow': 500,
            'easing_ease': 'ease',
            'easing_ease_in': 'ease-in',
            'easing_ease_out': 'ease-out',
            'easing_ease_in_out': 'ease-in-out'
        }
        
        # Initialize default component styles
        self._initialize_component_styles()
    
    def _initialize_component_styles(self):
        """Initialize default styles for all components."""
        # Base component styles
        self._component_styles = {
            'BaseComponent': {
                'normal': {
                    'background': 'background',
                    'foreground': 'text_primary',
                    'borderwidth': 0,
                    'relief': 'flat'
                },
                'hover': {
                    'background': 'neutral_100'
                },
                'focused': {
                    'background': 'neutral_100',
                    'highlightthickness': 2,
                    'highlightcolor': 'primary'
                },
                'disabled': {
                    'background': 'neutral_200',
                    'foreground': 'text_muted'
                },
                'error': {
                    'background': 'background',
                    'foreground': 'error',
                    'highlightthickness': 2,
                    'highlightcolor': 'error'
                }
            },
            'Button': {
                'normal': {
                    'background': 'primary',
                    'foreground': 'white',
                    'borderwidth': 0,
                    'relief': 'flat',
                    'font': self._get_font('button'),
                    'padx': self._spacing['lg'],
                    'pady': self._spacing['md'],
                    'cursor': 'hand2'
                },
                'hover': {
                    'background': 'primary_hover'
                },
                'focused': {
                    'highlightthickness': 2,
                    'highlightcolor': 'primary'
                },
                'disabled': {
                    'background': 'neutral_300',
                    'foreground': 'text_muted',
                    'cursor': 'arrow'
                }
            },
            'SecondaryButton': {
                'normal': {
                    'background': 'neutral_100',
                    'foreground': 'text_primary',
                    'borderwidth': 1,
                    'relief': 'solid',
                    'highlightthickness': 0,
                    'font': self._get_font('button'),
                    'padx': self._spacing['lg'],
                    'pady': self._spacing['md'],
                    'cursor': 'hand2'
                },
                'hover': {
                    'background': 'neutral_200'
                }
            },
            'TextInput': {
                'normal': {
                    'background': 'background',
                    'foreground': 'text_primary',
                    'borderwidth': 2,
                    'relief': 'solid',
                    'highlightthickness': 0,
                    'insertbackground': 'text_primary',
                    'font': self._get_font('body_medium'),
                    'padx': self._spacing['md'],
                    'pady': self._spacing['md']
                },
                'focused': {
                    'highlightthickness': 2,
                    'highlightcolor': 'primary'
                },
                'error': {
                    'highlightthickness': 2,
                    'highlightcolor': 'error'
                }
            },
            'Label': {
                'normal': {
                    'background': 'background',
                    'foreground': 'text_primary',
                    'borderwidth': 0,
                    'font': self._get_font('body_medium')
                }
            },
            'Frame': {
                'normal': {
                    'background': 'background',
                    'borderwidth': 0,
                    'relief': 'flat'
                }
            },
            'Card': {
                'normal': {
                    'background': 'surface',
                    'borderwidth': 1,
                    'relief': 'solid',
                    'padx': self._spacing['lg'],
                    'pady': self._spacing['lg']
                },
                'hover': {
                    'background': 'neutral_50'
                }
            }
        }
    
    def set_theme_mode(self, mode: ThemeMode):
        """Set the current theme mode."""
        if mode != self.current_mode:
            self.current_mode = mode
            # Theme change will be applied when components request styles
    
    def get_theme_mode(self) -> ThemeMode:
        """Get the current theme mode."""
        return self.current_mode
    
    def get_color(self, color_name: str) -> str:
        """Get a color value from the current theme palette."""
        palette = self._color_palettes.get(self.current_mode, self._color_palettes[ThemeMode.LIGHT])
        return palette.get(color_name, color_name)
    
    def get_typography(self, style_name: str) -> Dict[str, Any]:
        """Get typography settings for a given style."""
        return self._typography.get(style_name, self._typography['body_medium']).copy()
    
    def get_spacing(self, size: str) -> int:
        """Get spacing value for a given size."""
        return self._spacing.get(size, self._spacing['md'])
    
    def _get_font(self, style_name: str) -> tuple:
        """Get font tuple for tkinter from typography style."""
        typography = self.get_typography(style_name)
        return (typography['family'], typography['size'], typography['weight'])
    
    def get_component_style(self, component_name: str, state: str = 'normal') -> Dict[str, Any]:
        """
        Get the complete style dictionary for a component in a given state.
        
        Args:
            component_name: Name of the component class
            state: Component state (normal, hover, focused, disabled, error)
        
        Returns:
            Dictionary of style properties with resolved color values
        """
        # Get component style template
        component_styles = self._component_styles.get(component_name, {})
        base_style = component_styles.get('normal', {}).copy()
        state_style = component_styles.get(state, {}).copy()
        
        # Merge base and state styles
        final_style = {**base_style, **state_style}
        
        # Resolve color references
        resolved_style = {}
        for key, value in final_style.items():
            if isinstance(value, str) and value in self._color_palettes[self.current_mode]:
                resolved_style[key] = self.get_color(value)
            else:
                resolved_style[key] = value
        
        return resolved_style
    
    def register_component_style(self, component_name: str, styles: Dict[str, Dict[str, Any]]):
        """Register custom styles for a component."""
        self._component_styles[component_name] = styles
    
    def update_component_style(self, component_name: str, state: str, style_updates: Dict[str, Any]):
        """Update specific style properties for a component state."""
        if component_name not in self._component_styles:
            self._component_styles[component_name] = {}
        
        if state not in self._component_styles[component_name]:
            self._component_styles[component_name][state] = {}
        
        self._component_styles[component_name][state].update(style_updates)
    
    def load_theme_from_file(self, file_path: str):
        """Load theme configuration from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                theme_data = json.load(f)
            
            if 'color_palettes' in theme_data:
                for mode_name, palette in theme_data['color_palettes'].items():
                    try:
                        mode = ThemeMode(mode_name)
                        self._color_palettes[mode] = palette
                    except ValueError:
                        print(f"Unknown theme mode: {mode_name}")
            
            if 'typography' in theme_data:
                self._typography.update(theme_data['typography'])
            
            if 'component_styles' in theme_data:
                self._component_styles.update(theme_data['component_styles'])
            
            # Reinitialize with new data
            self._initialize_component_styles()
            
        except Exception as e:
            print(f"Error loading theme from {file_path}: {e}")
    
    def save_theme_to_file(self, file_path: str):
        """Save current theme configuration to a JSON file."""
        try:
            theme_data = {
                'color_palettes': {mode.value: palette for mode, palette in self._color_palettes.items()},
                'typography': self._typography,
                'spacing': self._spacing,
                'component_styles': self._component_styles
            }
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(theme_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving theme to {file_path}: {e}")
    
    def create_style_sheet(self) -> str:
        """Create a CSS-like style sheet for documentation purposes."""
        css_content = []
        css_content.append(f"/* TaskMover Theme - {self.current_mode.value.title()} Mode */\n")
        
        # Color variables
        css_content.append(":root {")
        palette = self._color_palettes[self.current_mode]
        for color_name, color_value in palette.items():
            css_content.append(f"  --{color_name.replace('_', '-')}: {color_value};")
        css_content.append("}\n")
        
        # Typography
        css_content.append("/* Typography */")
        for style_name, typography in self._typography.items():
            css_content.append(f".text-{style_name.replace('_', '-')} {{")
            css_content.append(f"  font-family: '{typography['family']}';")
            css_content.append(f"  font-size: {typography['size']}px;")
            css_content.append(f"  font-weight: {typography['weight']};")
            css_content.append("}")
        
        return "\n".join(css_content)
