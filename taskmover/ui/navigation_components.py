"""
Navigation Components
====================

Modern sidebar navigation, toolbar, and breadcrumb components with
hierarchical structure, visual indicators, and keyboard navigation.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

from .base_component import BaseComponent, ComponentState
from .theme_manager import get_theme_manager

logger = logging.getLogger(__name__)


@dataclass
class NavigationItem:
    """Navigation item with hierarchical support."""
    id: str
    label: str
    icon: str = ""
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    badge_count: int = 0
    enabled: bool = True
    callback: Optional[Callable] = None
    
    def __post_init__(self):
        if not self.children:
            self.children = []


class NavigationState(Enum):
    """Navigation states."""
    EXPANDED = "expanded"
    COLLAPSED = "collapsed"
    HIDDEN = "hidden"


class ModernSidebar(BaseComponent):
    """
    Modern sidebar navigation with hierarchical menu structure,
    visual state indicators, and collapsible sections.
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        width: int = 250,
        min_width: int = 50,
        **kwargs
    ):
        self.width = width
        self.min_width = min_width
        self.state = NavigationState.EXPANDED
        self.items: Dict[str, NavigationItem] = {}
        self.selected_item: Optional[str] = None
        self._item_widgets: Dict[str, tk.Widget] = {}
        
        super().__init__(parent, **kwargs)
        
        # Configure initial size
        self.configure(width=width)
        self.pack_propagate(False)
    
    def _create_component(self):
        """Create sidebar UI."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure sidebar styling
        self.configure(
            bg=tokens.colors["surface"],
            relief="solid",
            bd=1,
            highlightbackground=tokens.colors["border"],
            highlightthickness=1
        )
        
        # Header section
        self.header_frame = tk.Frame(
            self,
            bg=tokens.colors["surface"],
            height=60
        )
        self.header_frame.pack(fill="x", padx=tokens.spacing["sm"], pady=tokens.spacing["sm"])
        self.header_frame.pack_propagate(False)
        
        # App title
        self.title_label = tk.Label(
            self.header_frame,
            text="TaskMover",
            font=(tokens.fonts["family"], int(int(tokens.fonts["size_heading_1"])), "bold"),
            bg=tokens.colors["surface"],
            fg=tokens.colors["text"],
            anchor="w"
        )
        self.title_label.pack(fill="x", pady=(tokens.spacing["sm"], 0))
        
        # Navigation content
        self.nav_frame = tk.Frame(self, bg=tokens.colors["surface"])
        self.nav_frame.pack(fill="both", expand=True, padx=tokens.spacing["sm"])
        
        # Create scrollable content
        self.canvas = tk.Canvas(
            self.nav_frame,
            bg=tokens.colors["surface"],
            highlightthickness=0,
            bd=0
        )
        self.scrollbar = ttk.Scrollbar(
            self.nav_frame,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg=tokens.colors["surface"])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Collapse/expand button
        self.collapse_frame = tk.Frame(self, bg=tokens.colors["surface"], height=40)
        self.collapse_frame.pack(fill="x", side="bottom")
        self.collapse_frame.pack_propagate(False)
        
        self.collapse_button = tk.Button(
            self.collapse_frame,
            text="◀ Collapse",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), "normal"),
            bg=tokens.colors["surface"],
            fg=tokens.colors["text_secondary"],
            bd=0,
            relief="flat",
            command=self.toggle_collapse,
            cursor="hand2"
        )
        self.collapse_button.pack(fill="x", padx=tokens.spacing["sm"], pady=tokens.spacing["xs"])
        
        # Initialize with default navigation items
        self._setup_default_navigation()
    
    def _setup_default_navigation(self):
        """Setup default navigation structure."""
        # Add main navigation items
        self.add_item(NavigationItem("dashboard", "Dashboard", "🏠"))
        
        # Patterns section
        patterns_item = NavigationItem("patterns", "Patterns", "📋")
        self.add_item(patterns_item)
        self.add_item(NavigationItem("patterns_library", "Library", "•", "patterns"))
        self.add_item(NavigationItem("patterns_groups", "Groups", "•", "patterns"))
        self.add_item(NavigationItem("patterns_new", "New", "+", "patterns"))
        
        # Rules section
        rules_item = NavigationItem("rules", "Rules", "📏", badge_count=12)
        self.add_item(rules_item)
        self.add_item(NavigationItem("rules_active", "Active", "•", "rules"))
        self.add_item(NavigationItem("rules_disabled", "Disabled", "•", "rules"))
        self.add_item(NavigationItem("rules_new", "New", "+", "rules"))
        
        # Rulesets section
        rulesets_item = NavigationItem("rulesets", "Rulesets", "📦")
        self.add_item(rulesets_item)
        self.add_item(NavigationItem("rulesets_recent", "Recent", "•", "rulesets"))
        self.add_item(NavigationItem("rulesets_templates", "Templates", "•", "rulesets"))
        self.add_item(NavigationItem("rulesets_new", "New", "+", "rulesets"))
        
        # Execute
        self.add_item(NavigationItem("execute", "Execute", "⚡"))
        
        # Activity section separator
        self._add_separator("Activity")
        
        # History and stats
        self.add_item(NavigationItem("history", "History", "📈"))
        self.add_item(NavigationItem("statistics", "Statistics", "📊"))
        self.add_item(NavigationItem("logs", "Logs", "📜"))
        
        # System section separator
        self._add_separator("System")
        
        # Settings and help
        self.add_item(NavigationItem("settings", "Settings", "⚙️"))
        self.add_item(NavigationItem("help", "Help", "❓"))
        
        # Render all items
        self._render_navigation()
    
    def add_item(self, item: NavigationItem):
        """Add navigation item."""
        self.items[item.id] = item
        
        # Add to parent's children list
        if item.parent_id and item.parent_id in self.items:
            if item.id not in self.items[item.parent_id].children:
                self.items[item.parent_id].children.append(item.id)
    
    def _add_separator(self, title: str):
        """Add section separator."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        separator_frame = tk.Frame(
            self.scrollable_frame,
            bg=tokens.colors["surface"],
            height=30
        )
        separator_frame.pack(fill="x", pady=(tokens.spacing["md"], tokens.spacing["xs"]))
        separator_frame.pack_propagate(False)
        
        # Separator line and text
        line_frame = tk.Frame(separator_frame, bg=tokens.colors["surface"])
        line_frame.pack(fill="x", pady=tokens.spacing["sm"])
        
        # Left line
        left_line = tk.Frame(line_frame, bg=tokens.colors["border"], height=1)
        left_line.pack(side="left", fill="x", expand=True)
        
        # Title
        title_label = tk.Label(
            line_frame,
            text=f" {title} ",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), "normal"),
            bg=tokens.colors["surface"],
            fg=tokens.colors["text_secondary"]
        )
        title_label.pack(side="left")
        
        # Right line
        right_line = tk.Frame(line_frame, bg=tokens.colors["border"], height=1)
        right_line.pack(side="left", fill="x", expand=True)
    
    def _render_navigation(self):
        """Render all navigation items."""
        # Clear existing widgets
        for widget in self._item_widgets.values():
            widget.destroy()
        self._item_widgets.clear()
        
        # Render root items first
        for item_id, item in self.items.items():
            if item.parent_id is None:
                self._render_item(item, level=0)
                # Render children
                for child_id in item.children:
                    if child_id in self.items:
                        self._render_item(self.items[child_id], level=1)
    
    def _render_item(self, item: NavigationItem, level: int = 0):
        """Render a single navigation item."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Calculate indentation
        indent = tokens.spacing["md"] + (level * tokens.spacing["lg"])
        
        # Item frame
        item_frame = tk.Frame(
            self.scrollable_frame,
            bg=tokens.colors["surface"],
            height=36
        )
        item_frame.pack(fill="x", pady=1)
        item_frame.pack_propagate(False)
        
        # Item button
        item_button = tk.Button(
            item_frame,
            text=f"{item.icon} {item.label}",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), "normal"),
            bg=tokens.colors["surface"],
            fg=tokens.colors["text"],
            bd=0,
            relief="flat",
            anchor="w",
            padx=indent,
            command=lambda: self._on_item_click(item.id),
            cursor="hand2" if item.enabled else "arrow"
        )
        item_button.pack(fill="both", expand=True)
        
        # Configure item styling
        if item.id == self.selected_item:
            item_button.configure(bg=tokens.colors["primary"], fg="white")
        elif not item.enabled:
            item_button.configure(fg=tokens.colors["text_disabled"])
        
        # Hover effects
        def on_enter(e):
            if item.enabled and item.id != self.selected_item:
                item_button.configure(bg=tokens.colors["hover"])
        
        def on_leave(e):
            if item.enabled and item.id != self.selected_item:
                item_button.configure(bg=tokens.colors["surface"])
        
        item_button.bind("<Enter>", on_enter)
        item_button.bind("<Leave>", on_leave)
        
        # Badge for counts
        if item.badge_count > 0:
            badge_label = tk.Label(
                item_frame,
                text=str(item.badge_count),
                font=(tokens.fonts["family"], int(int(tokens.fonts["size_caption"])), "bold"),
                bg=tokens.colors["primary"],
                fg="white",
                width=3,
                height=1
            )
            badge_label.place(relx=0.85, rely=0.5, anchor="center")
        
        self._item_widgets[item.id] = item_frame
    
    def _on_item_click(self, item_id: str):
        """Handle navigation item click."""
        if item_id in self.items:
            item = self.items[item_id]
            
            if item.enabled:
                # Update selection
                old_selection = self.selected_item
                self.selected_item = item_id
                
                # Re-render to update styling
                self._render_navigation()
                
                # Trigger callback
                if item.callback:
                    item.callback(item_id)
                
                # Trigger component callback
                self._trigger_callback('item_selected', {
                    'item_id': item_id,
                    'old_selection': old_selection,
                    'item': item
                })
                
                logger.debug(f"Navigation item selected: {item_id}")
    
    def select_item(self, item_id: str):
        """Programmatically select navigation item."""
        self._on_item_click(item_id)
    
    def set_item_badge(self, item_id: str, count: int):
        """Set badge count for navigation item."""
        if item_id in self.items:
            self.items[item_id].badge_count = count
            self._render_navigation()
    
    def set_item_enabled(self, item_id: str, enabled: bool):
        """Enable or disable navigation item."""
        if item_id in self.items:
            self.items[item_id].enabled = enabled
            self._render_navigation()
    
    def toggle_collapse(self):
        """Toggle sidebar collapse state."""
        if self.state == NavigationState.EXPANDED:
            self.collapse()
        else:
            self.expand()
    
    def collapse(self):
        """Collapse sidebar to icon-only mode."""
        self.state = NavigationState.COLLAPSED
        self.configure(width=self.min_width)
        
        # Hide text elements
        self.title_label.configure(text="TM")
        self.collapse_button.configure(text="▶")
        
        # Update navigation items to show only icons
        self._render_collapsed_navigation()
        
        self._trigger_callback('collapsed')
        logger.debug("Sidebar collapsed")
    
    def expand(self):
        """Expand sidebar to full mode."""
        self.state = NavigationState.EXPANDED
        self.configure(width=self.width)
        
        # Show text elements
        self.title_label.configure(text="TaskMover")
        self.collapse_button.configure(text="◀ Collapse")
        
        # Render full navigation
        self._render_navigation()
        
        self._trigger_callback('expanded')
        logger.debug("Sidebar expanded")
    
    def _render_collapsed_navigation(self):
        """Render navigation in collapsed (icon-only) mode."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Clear existing widgets
        for widget in self._item_widgets.values():
            widget.destroy()
        self._item_widgets.clear()
        
        # Render only root items with icons
        for item_id, item in self.items.items():
            if item.parent_id is None and item.icon:
                item_frame = tk.Frame(
                    self.scrollable_frame,
                    bg=tokens.colors["surface"],
                    height=40,
                    width=40
                )
                item_frame.pack(pady=2)
                item_frame.pack_propagate(False)
                
                # Icon button
                icon_button = tk.Button(
                    item_frame,
                    text=item.icon,
                    font=(tokens.fonts["family"], 16, "normal"),
                    bg=tokens.colors["surface"],
                    fg=tokens.colors["text"],
                    bd=0,
                    relief="flat",
                    command=lambda id=item.id: self._on_item_click(id),
                    cursor="hand2" if item.enabled else "arrow"
                )
                icon_button.pack(fill="both", expand=True)
                
                # Selection styling
                if item.id == self.selected_item:
                    icon_button.configure(bg=tokens.colors["primary"], fg="white")
                
                # Hover effects
                def make_hover_handler(btn, item_id):
                    def on_enter(e):
                        if item.enabled and item_id != self.selected_item:
                            btn.configure(bg=tokens.colors["hover"])
                    def on_leave(e):
                        if item.enabled and item_id != self.selected_item:
                            btn.configure(bg=tokens.colors["surface"])
                    return on_enter, on_leave
                
                enter_handler, leave_handler = make_hover_handler(icon_button, item.id)
                icon_button.bind("<Enter>", enter_handler)
                icon_button.bind("<Leave>", leave_handler)
                
                self._item_widgets[item.id] = item_frame


class ModernToolbar(BaseComponent):
    """Modern toolbar with icon buttons, groups, and overflow menu."""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.buttons: Dict[str, tk.Button] = {}
        self.button_groups: List[List[str]] = []
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create toolbar UI."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure toolbar styling
        self.configure(
            bg=tokens.colors["surface"],
            height=50,
            relief="flat",
            bd=0
        )
        self.pack_propagate(False)
        
        # Left button group
        self.left_frame = tk.Frame(self, bg=tokens.colors["surface"])
        self.left_frame.pack(side="left", fill="y", padx=tokens.spacing["sm"])
        
        # Center search area
        self.center_frame = tk.Frame(self, bg=tokens.colors["surface"])
        self.center_frame.pack(side="left", fill="both", expand=True, padx=tokens.spacing["lg"])
        
        # Right button group
        self.right_frame = tk.Frame(self, bg=tokens.colors["surface"])
        self.right_frame.pack(side="right", fill="y", padx=tokens.spacing["sm"])
        
        # Setup default toolbar
        self._setup_default_toolbar()
    
    def _setup_default_toolbar(self):
        """Setup default toolbar buttons."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Left buttons
        left_buttons = [
            ("home", "🏠", "Home"),
            ("file", "📁", "File"),
            ("settings", "⚙️", "Settings"),
            ("new", "📝", "New"),
            ("stats", "📊", "Stats"),
        ]
        
        for btn_id, icon, tooltip in left_buttons:
            self.add_button(btn_id, icon, tooltip, "left")
        
        # Add separator
        self._add_separator(self.left_frame)
        
        # Action buttons
        action_buttons = [
            ("undo", "↶", "Undo"),
            ("redo", "↷", "Redo"),
        ]
        
        for btn_id, icon, tooltip in action_buttons:
            self.add_button(btn_id, icon, tooltip, "left")
        
        # Search in center
        search_frame = tk.Frame(self.center_frame, bg=tokens.colors["surface"])
        search_frame.pack(fill="x", pady=tokens.spacing["sm"])
        
        search_label = tk.Label(
            search_frame,
            text="Search:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), "normal"),
            bg=tokens.colors["surface"],
            fg=tokens.colors["text"]
        )
        search_label.pack(side="left", padx=(0, tokens.spacing["sm"]))
        
        self.search_entry = tk.Entry(
            search_frame,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), "normal"),
            bg="white",
            fg=tokens.colors["text"],
            relief="solid",
            bd=1,
            width=30
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        
        search_button = tk.Button(
            search_frame,
            text="🔍",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), "normal"),
            bg=tokens.colors["surface"],
            fg=tokens.colors["text"],
            bd=0,
            relief="flat",
            cursor="hand2"
        )
        search_button.pack(side="left", padx=(tokens.spacing["xs"], 0))
        
        # Right buttons
        right_buttons = [
            ("help", "❓", "Help"),
            ("profile", "👤", "Profile"),
        ]
        
        for btn_id, icon, tooltip in right_buttons:
            self.add_button(btn_id, icon, tooltip, "right")
    
    def add_button(self, button_id: str, icon: str, tooltip: str, position: str = "left"):
        """Add button to toolbar."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        parent_frame = self.left_frame if position == "left" else self.right_frame
        
        button = tk.Button(
            parent_frame,
            text=icon,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body_large"]), "normal"),
            bg=tokens.colors["surface"],
            fg=tokens.colors["text"],
            bd=0,
            relief="flat",
            width=3,
            height=2,
            cursor="hand2",
            command=lambda: self._on_button_click(button_id)
        )
        button.pack(side="left", padx=1, pady=tokens.spacing["xs"])
        
        # Hover effects
        def on_enter(e):
            button.configure(bg=tokens.colors["hover"])
        
        def on_leave(e):
            button.configure(bg=tokens.colors["surface"])
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        # Tooltip (simple implementation)
        def show_tooltip(e):
            # Create tooltip window
            tooltip_window = tk.Toplevel()
            tooltip_window.withdraw()
            tooltip_window.overrideredirect(True)
            
            tooltip_label = tk.Label(
                tooltip_window,
                text=tooltip,
                font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), "normal"),
                bg="#ffffe0",
                fg="black",
                relief="solid",
                bd=1,
                padx=4,
                pady=2
            )
            tooltip_label.pack()
            
            # Position tooltip
            x = button.winfo_rootx() + 20
            y = button.winfo_rooty() + 30
            tooltip_window.geometry(f"+{x}+{y}")
            tooltip_window.deiconify()
            
            # Auto-hide after 2 seconds
            tooltip_window.after(2000, tooltip_window.destroy)
        
        button.bind("<Button-3>", show_tooltip)  # Right-click for tooltip
        
        self.buttons[button_id] = button
    
    def _add_separator(self, parent_frame):
        """Add vertical separator."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        separator = tk.Frame(
            parent_frame,
            bg=tokens.colors["border"],
            width=1,
            height=30
        )
        separator.pack(side="left", padx=tokens.spacing["sm"], pady=tokens.spacing["sm"])
    
    def _on_button_click(self, button_id: str):
        """Handle toolbar button click."""
        self._trigger_callback('button_clicked', {'button_id': button_id})
        logger.debug(f"Toolbar button clicked: {button_id}")
    
    def set_button_enabled(self, button_id: str, enabled: bool):
        """Enable or disable toolbar button."""
        if button_id in self.buttons:
            button = self.buttons[button_id]
            if enabled:
                button.configure(state="normal", cursor="hand2")
            else:
                button.configure(state="disabled", cursor="arrow")
    
    def get_search_text(self) -> str:
        """Get current search text."""
        return self.search_entry.get()
    
    def set_search_text(self, text: str):
        """Set search text."""
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, text)


# Export main classes
__all__ = [
    "ModernSidebar",
    "ModernToolbar",
    "NavigationItem",
    "NavigationState",
]