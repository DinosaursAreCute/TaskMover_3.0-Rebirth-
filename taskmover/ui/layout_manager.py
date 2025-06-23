"""
TaskMover UI Framework - Layout Management System
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from .base_component import BaseComponent, FrameComponent


class LayoutDirection(Enum):
    """Layout direction options"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class LayoutAlign(Enum):
    """Layout alignment options"""
    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"


class LayoutJustify(Enum):
    """Layout justify options"""
    START = "start"
    CENTER = "center"
    END = "end"
    SPACE_BETWEEN = "space_between"
    SPACE_AROUND = "space_around"
    SPACE_EVENLY = "space_evenly"


class ResponsiveGridManager:
    """
    Advanced grid layout manager with responsive capabilities.
    Provides flexible column layouts that adapt to different screen sizes.
    """
    
    def __init__(self, container: tk.Widget):
        """
        Initialize the grid manager.
        
        Args:
            container: The container widget to manage
        """
        self.container = container
        self.children: List[Dict[str, Any]] = []
        self.breakpoints = {
            'xs': 0,      # Extra small devices
            'sm': 576,    # Small devices
            'md': 768,    # Medium devices  
            'lg': 992,    # Large devices
            'xl': 1200,   # Extra large devices
            'xxl': 1400   # Extra extra large devices
        }
        self.current_breakpoint = 'lg'
        
        # Grid configuration
        self.columns = 12  # Bootstrap-style 12-column grid
        self.gap = 8       # Gap between grid items
        
        # Bind to window resize events
        self.container.bind('<Configure>', self._on_resize)
    
    def add_item(self, widget: tk.Widget, 
                 col_xs: int = 12, col_sm: int = None, col_md: int = None,
                 col_lg: int = None, col_xl: int = None, col_xxl: int = None,
                 order: int = 0, **grid_options):
        """
        Add an item to the responsive grid.
        
        Args:
            widget: Widget to add
            col_xs: Columns for extra small screens (default: 12)
            col_sm: Columns for small screens (inherits from xs if None)
            col_md: Columns for medium screens (inherits from sm if None)
            col_lg: Columns for large screens (inherits from md if None)
            col_xl: Columns for extra large screens (inherits from lg if None)
            col_xxl: Columns for extra extra large screens (inherits from xl if None)
            order: Display order (0 = natural order)
            **grid_options: Additional grid options
        """
        # Set up column inheritance
        columns = {
            'xs': col_xs,
            'sm': col_sm or col_xs,
            'md': col_md or col_sm or col_xs,
            'lg': col_lg or col_md or col_sm or col_xs,
            'xl': col_xl or col_lg or col_md or col_sm or col_xs,
            'xxl': col_xxl or col_xl or col_lg or col_md or col_sm or col_xs
        }
        
        item = {
            'widget': widget,
            'columns': columns,
            'order': order,
            'grid_options': grid_options,
            'current_row': 0,
            'current_col': 0
        }
        
        self.children.append(item)
        self._relayout()
    
    def remove_item(self, widget: tk.Widget):
        """Remove an item from the grid."""
        self.children = [item for item in self.children if item['widget'] != widget]
        widget.grid_forget()
        self._relayout()
    
    def set_gap(self, gap: int):
        """Set the gap between grid items."""
        self.gap = gap
        self._relayout()
    
    def _on_resize(self, event=None):
        """Handle container resize events."""
        if event and event.widget == self.container:
            width = event.width
            new_breakpoint = self._get_breakpoint_for_width(width)
            
            if new_breakpoint != self.current_breakpoint:
                self.current_breakpoint = new_breakpoint
                self._relayout()
    
    def _get_breakpoint_for_width(self, width: int) -> str:
        """Determine the appropriate breakpoint for a given width."""
        for bp_name in reversed(list(self.breakpoints.keys())):
            if width >= self.breakpoints[bp_name]:
                return bp_name
        return 'xs'
    
    def _relayout(self):
        """Recalculate and apply the grid layout."""
        if not self.children:
            return
        
        # Sort children by order
        sorted_children = sorted(self.children, key=lambda x: x['order'])
        
        # Calculate layout
        current_row = 0
        current_col = 0
        
        for item in sorted_children:
            widget = item['widget']
            cols_needed = item['columns'][self.current_breakpoint]
            
            # Check if we need to wrap to next row
            if current_col + cols_needed > self.columns:
                current_row += 1
                current_col = 0
            
            # Calculate column span
            col_span = max(1, cols_needed)
            
            # Apply grid layout
            grid_options = {
                'row': current_row,
                'column': current_col,
                'columnspan': col_span,
                'sticky': 'ew',
                'padx': self.gap // 2,
                'pady': self.gap // 2,
                **item['grid_options']
            }
            
            widget.grid(**grid_options)
            
            # Update position
            item['current_row'] = current_row
            item['current_col'] = current_col
            
            current_col += col_span
        
        # Configure column weights for responsiveness
        for i in range(self.columns):
            self.container.grid_columnconfigure(i, weight=1)


class FlexLayout(FrameComponent):
    """
    Flexible layout container similar to CSS Flexbox.
    Provides advanced layout capabilities with direction, alignment, and justification.
    """
    
    def __init__(self, parent: tk.Widget, 
                 direction: LayoutDirection = LayoutDirection.HORIZONTAL,
                 align: LayoutAlign = LayoutAlign.START,
                 justify: LayoutJustify = LayoutJustify.START,
                 gap: int = 8,
                 wrap: bool = False,
                 **kwargs):
        """
        Initialize the flex layout.
        
        Args:
            parent: Parent widget
            direction: Layout direction (horizontal/vertical)
            align: Cross-axis alignment
            justify: Main-axis justification
            gap: Gap between items
            wrap: Whether items should wrap
            **kwargs: Additional frame options
        """
        super().__init__(parent, **kwargs)
        
        self.direction = direction
        self.align = align
        self.justify = justify
        self.gap = gap
        self.wrap = wrap
        
        self.children: List[Dict[str, Any]] = []
        
        # Bind to size changes
        self._widget.bind('<Configure>', self._on_configure)
    
    def add_child(self, child: tk.Widget, 
                  flex_grow: float = 0,
                  flex_shrink: float = 1,
                  flex_basis: Optional[int] = None,
                  align_self: Optional[LayoutAlign] = None,
                  order: int = 0,
                  **grid_options):
        """
        Add a child to the flex layout.
        
        Args:
            child: Child widget to add
            flex_grow: How much the child should grow (0 = don't grow)
            flex_shrink: How much the child should shrink (1 = normal shrinking)
            flex_basis: Initial size of the child
            align_self: Override alignment for this child
            order: Display order
            **grid_options: Additional grid options
        """
        child_info = {
            'widget': child,
            'flex_grow': flex_grow,
            'flex_shrink': flex_shrink,
            'flex_basis': flex_basis,
            'align_self': align_self,
            'order': order,
            'grid_options': grid_options
        }
        
        self.children.append(child_info)
        child.grid(in_=self._widget)
        self._relayout()
    
    def remove_child(self, child: tk.Widget):
        """Remove a child from the flex layout."""
        self.children = [item for item in self.children if item['widget'] != child]
        child.grid_forget()
        self._relayout()
    
    def set_direction(self, direction: LayoutDirection):
        """Change the layout direction."""
        if direction != self.direction:
            self.direction = direction
            self._relayout()
    
    def set_justify(self, justify: LayoutJustify):
        """Change the justification."""
        if justify != self.justify:
            self.justify = justify
            self._relayout()
    
    def set_align(self, align: LayoutAlign):
        """Change the alignment."""
        if align != self.align:
            self.align = align
            self._relayout()
    
    def _on_configure(self, event=None):
        """Handle configuration changes."""
        if event and event.widget == self._widget:
            self._relayout()
    
    def _relayout(self):
        """Recalculate and apply the flex layout."""
        if not self.children:
            return
        
        # Sort by order
        sorted_children = sorted(self.children, key=lambda x: x['order'])
        
        if self.direction == LayoutDirection.HORIZONTAL:
            self._layout_horizontal(sorted_children)
        else:
            self._layout_vertical(sorted_children)
    
    def _layout_horizontal(self, children: List[Dict[str, Any]]):
        """Layout children horizontally."""
        container_width = self._widget.winfo_width()
        if container_width <= 1:  # Widget not yet sized
            self._widget.after(10, self._relayout)
            return
        
        # Calculate available space
        total_gap = self.gap * (len(children) - 1) if len(children) > 1 else 0
        available_width = container_width - total_gap
        
        # Calculate basis sizes
        total_basis = 0
        flex_items = []
        
        for child_info in children:
            basis = child_info['flex_basis']
            if basis is None:
                # Use widget's requested width
                child_info['widget'].update_idletasks()
                basis = child_info['widget'].winfo_reqwidth()
            
            child_info['calculated_basis'] = basis
            total_basis += basis
            
            if child_info['flex_grow'] > 0:
                flex_items.append(child_info)
        
        # Distribute extra space
        extra_space = available_width - total_basis
        if extra_space > 0 and flex_items:
            total_grow = sum(item['flex_grow'] for item in flex_items)
            if total_grow > 0:
                for item in flex_items:
                    grow_share = item['flex_grow'] / total_grow
                    item['calculated_basis'] += extra_space * grow_share
        
        # Position children
        current_x = 0
        
        # Handle justification
        if self.justify == LayoutJustify.CENTER:
            total_width = sum(item['calculated_basis'] for item in children) + total_gap
            current_x = (available_width - total_width + total_gap) // 2
        elif self.justify == LayoutJustify.END:
            total_width = sum(item['calculated_basis'] for item in children) + total_gap
            current_x = available_width - total_width + total_gap
        
        for i, child_info in enumerate(children):
            widget = child_info['widget']
            width = int(child_info['calculated_basis'])
            
            # Handle space distribution for justify
            if self.justify == LayoutJustify.SPACE_BETWEEN and len(children) > 1:
                if i == 0:
                    current_x = 0
                else:
                    current_x += self.gap + available_width // (len(children) - 1)
            elif self.justify == LayoutJustify.SPACE_AROUND:
                space = available_width // len(children) if children else 0
                current_x = space // 2 + i * space
            elif self.justify == LayoutJustify.SPACE_EVENLY:
                space = available_width // (len(children) + 1) if children else 0
                current_x = space * (i + 1)
            
            # Handle alignment
            sticky = self._get_sticky_for_align(child_info.get('align_self', self.align))
            
            grid_options = {
                'row': 0,
                'column': i,
                'sticky': sticky,
                'padx': (0, self.gap) if i < len(children) - 1 else 0,
                **child_info['grid_options']
            }
            
            widget.grid(**grid_options)
            
            if i < len(children) - 1:
                current_x += width + self.gap
        
        # Configure column weights
        for i in range(len(children)):
            weight = children[i]['flex_grow'] if children[i]['flex_grow'] > 0 else 0
            self._widget.grid_columnconfigure(i, weight=weight, minsize=0)
    
    def _layout_vertical(self, children: List[Dict[str, Any]]):
        """Layout children vertically."""
        # Similar to horizontal but for vertical direction
        for i, child_info in enumerate(children):
            widget = child_info['widget']
            sticky = self._get_sticky_for_align(child_info.get('align_self', self.align))
            
            grid_options = {
                'row': i,
                'column': 0,
                'sticky': sticky,
                'pady': (0, self.gap) if i < len(children) - 1 else 0,
                **child_info['grid_options']
            }
            
            widget.grid(**grid_options)
            
            # Configure row weight
            weight = child_info['flex_grow'] if child_info['flex_grow'] > 0 else 0
            self._widget.grid_rowconfigure(i, weight=weight)
        
        # Configure column to fill width
        self._widget.grid_columnconfigure(0, weight=1)
    
    def _get_sticky_for_align(self, align: LayoutAlign) -> str:
        """Convert alignment to tkinter sticky value."""
        if self.direction == LayoutDirection.HORIZONTAL:
            return {
                LayoutAlign.START: 'w',
                LayoutAlign.CENTER: '',
                LayoutAlign.END: 'e',
                LayoutAlign.STRETCH: 'ew'
            }.get(align, '')
        else:
            return {
                LayoutAlign.START: 'n',
                LayoutAlign.CENTER: '',
                LayoutAlign.END: 's',
                LayoutAlign.STRETCH: 'ns'
            }.get(align, '')


class StackLayout(FrameComponent):
    """
    Stack layout for overlaying components.
    Useful for creating layered interfaces.
    """
    
    def __init__(self, parent: tk.Widget, **kwargs):
        """Initialize the stack layout."""
        super().__init__(parent, **kwargs)
        self.children: List[tk.Widget] = []
    
    def add_child(self, child: tk.Widget, z_index: int = 0):
        """Add a child to the stack with a specific z-index."""
        self.children.append(child)
        child.place(in_=self._widget, x=0, y=0, relwidth=1, relheight=1)
        
        # Simulate z-index by raising/lowering
        if z_index > 0:
            for _ in range(z_index):
                child.lift()
        elif z_index < 0:
            for _ in range(abs(z_index)):
                child.lower()
    
    def remove_child(self, child: tk.Widget):
        """Remove a child from the stack."""
        if child in self.children:
            self.children.remove(child)
            child.place_forget()
    
    def bring_to_front(self, child: tk.Widget):
        """Bring a child to the front of the stack."""
        if child in self.children:
            child.lift()
    
    def send_to_back(self, child: tk.Widget):
        """Send a child to the back of the stack."""
        if child in self.children:
            child.lower()
