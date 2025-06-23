"""
TaskMover UI Framework - Navigation Components
"""
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional, List, Union, Dict
from .base_component import BaseComponent, ComponentState


class NavigationMenu(BaseComponent):
    """
    Hierarchical navigation menu with search and keyboard navigation.
    """
    
    def __init__(self, parent: tk.Widget,
                 items: List[Dict] = None,
                 show_icons: bool = True,
                 searchable: bool = True,
                 expandable: bool = True,
                 **kwargs):
        """
        Initialize the navigation menu.
        
        Args:
            parent: Parent widget
            items: Menu items structure
            show_icons: Whether to show item icons
            searchable: Whether to enable search
            expandable: Whether to support expandable submenus
            **kwargs: Additional widget options
        """
        self.items = items or []
        self.show_icons = show_icons
        self.searchable = searchable
        self.expandable = expandable
        self._selected_item = None
        self._expanded_items = set()
        self._filtered_items = self.items.copy()
        
        super().__init__(parent, **kwargs)
        
        if self.searchable:
            self._setup_search()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the navigation menu structure."""
        container = ttk.Frame(self.parent)
        
        # Search bar (if enabled)
        if self.searchable:
            self.search_frame = ttk.Frame(container)
            self.search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            
            self.search_var = tk.StringVar()
            self.search_var.trace("w", self._on_search_changed)
            
            self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var,
                                        font=('Arial', 9))
            self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Search placeholder
            self.search_entry.insert(0, "Search menu...")
            self.search_entry.bind("<FocusIn>", self._clear_search_placeholder)
            self.search_entry.bind("<FocusOut>", self._restore_search_placeholder)
        
        # Menu items container
        self.menu_frame = ttk.Frame(container)
        self.menu_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Create scrollable area
        self.canvas = tk.Canvas(self.menu_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.menu_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Build menu items
        self._build_menu_items()
        
        return container
    
    def _setup_search(self):
        """Setup search functionality."""
        pass  # Already handled in _create_widget
    
    def _on_search_changed(self, *args):
        """Handle search text changes."""
        search_text = self.search_var.get().lower()
        
        if search_text == "search menu...":
            search_text = ""
        
        if search_text:
            self._filtered_items = self._filter_items(self.items, search_text)
        else:
            self._filtered_items = self.items.copy()
        
        self._rebuild_menu()
    
    def _filter_items(self, items: List[Dict], search_text: str) -> List[Dict]:
        """Filter menu items based on search text."""
        filtered = []
        
        for item in items:
            # Check if item matches
            if search_text in item.get('label', '').lower():
                filtered.append(item)
            elif 'children' in item:
                # Check children
                filtered_children = self._filter_items(item['children'], search_text)
                if filtered_children:
                    item_copy = item.copy()
                    item_copy['children'] = filtered_children
                    filtered.append(item_copy)
        
        return filtered
    
    def _clear_search_placeholder(self, event):
        """Clear search placeholder text."""
        if self.search_entry.get() == "Search menu...":
            self.search_entry.delete(0, tk.END)
    
    def _restore_search_placeholder(self, event):
        """Restore search placeholder if empty."""
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search menu...")
    
    def _build_menu_items(self):
        """Build the menu item widgets."""
        self._clear_menu()
        self._create_menu_items(self._filtered_items, self.scrollable_frame, level=0)
    
    def _rebuild_menu(self):
        """Rebuild the menu items."""
        self._build_menu_items()
    
    def _clear_menu(self):
        """Clear all menu item widgets."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
    
    def _create_menu_items(self, items: List[Dict], parent: tk.Widget, level: int = 0):
        """Create menu item widgets recursively."""
        for item in items:
            item_frame = self._create_menu_item(item, parent, level)
            
            # Create submenu if expandable and has children
            if self.expandable and 'children' in item:
                item_id = item.get('id', item.get('label', ''))
                if item_id in self._expanded_items:
                    self._create_menu_items(item['children'], parent, level + 1)
    
    def _create_menu_item(self, item: Dict, parent: tk.Widget, level: int) -> tk.Widget:
        """Create a single menu item widget."""
        item_frame = ttk.Frame(parent)
        item_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Indentation for hierarchy
        indent = level * 20
        
        # Main button frame
        button_frame = ttk.Frame(item_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=(indent, 0))
        
        # Expand/collapse button for items with children
        if self.expandable and 'children' in item:
            item_id = item.get('id', item.get('label', ''))
            is_expanded = item_id in self._expanded_items
            
            expand_btn = ttk.Button(button_frame, text="▼" if is_expanded else "▶", width=2,
                                  command=lambda i=item: self._toggle_item_expansion(i))
            expand_btn.pack(side=tk.LEFT)
        
        # Icon (if enabled and provided)
        if self.show_icons and 'icon' in item:
            # TODO: Implement icon display
            icon_label = tk.Label(button_frame, text="●", width=2)
            icon_label.pack(side=tk.LEFT)
        
        # Item label button
        label_text = item.get('label', 'Menu Item')
        badge_text = item.get('badge', '')
        if badge_text:
            label_text += f" ({badge_text})"
        
        item_button = ttk.Button(button_frame, text=label_text,
                               command=lambda i=item: self._on_item_selected(i))
        item_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Highlight if selected
        item_id = item.get('id', item.get('label', ''))
        if self._selected_item == item_id:
            item_button.state(['pressed'])
        
        return item_frame
    
    def _toggle_item_expansion(self, item: Dict):
        """Toggle expansion state of a menu item."""
        item_id = item.get('id', item.get('label', ''))
        
        if item_id in self._expanded_items:
            self._expanded_items.remove(item_id)
        else:
            self._expanded_items.add(item_id)
        
        self._rebuild_menu()
        self.trigger_event('item_expanded', item)
    
    def _on_item_selected(self, item: Dict):
        """Handle menu item selection."""
        item_id = item.get('id', item.get('label', ''))
        self._selected_item = item_id
        
        # Update visual selection state
        self._rebuild_menu()
        
        # Trigger selection event
        self.trigger_event('item_selected', item)
        
        # LOGIC INTEGRATION POINT: Handle navigation action
        # self._handle_navigation(item)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def add_item(self, item: Dict, parent_id: Optional[str] = None):
        """Add a new menu item."""
        if parent_id:
            parent_item = self._find_item_by_id(self.items, parent_id)
            if parent_item:
                if 'children' not in parent_item:
                    parent_item['children'] = []
                parent_item['children'].append(item)
        else:
            self.items.append(item)
        
        self._rebuild_menu()
    
    def remove_item(self, item_id: str):
        """Remove a menu item."""
        self._remove_item_recursive(self.items, item_id)
        self._rebuild_menu()
    
    def _remove_item_recursive(self, items: List[Dict], item_id: str) -> bool:
        """Recursively remove item from menu structure."""
        for i, item in enumerate(items):
            if item.get('id') == item_id:
                items.pop(i)
                return True
            elif 'children' in item:
                if self._remove_item_recursive(item['children'], item_id):
                    return True
        return False
    
    def _find_item_by_id(self, items: List[Dict], item_id: str) -> Optional[Dict]:
        """Find menu item by ID."""
        for item in items:
            if item.get('id') == item_id:
                return item
            elif 'children' in item:
                found = self._find_item_by_id(item['children'], item_id)
                if found:
                    return found
        return None
    
    def set_selected_item(self, item_id: str):
        """Set the selected menu item."""
        self._selected_item = item_id
        self._rebuild_menu()
    
    def get_selected_item(self) -> Optional[Dict]:
        """Get the currently selected menu item."""
        if self._selected_item:
            return self._find_item_by_id(self.items, self._selected_item)
        return None


class Breadcrumb(BaseComponent):
    """Breadcrumb navigation component."""
    
    def __init__(self, parent: tk.Widget,
                 path: List[Dict] = None,
                 separator: str = " > ",
                 max_items: int = 5,
                 show_home: bool = True,
                 **kwargs):
        """
        Initialize the breadcrumb.
        
        Args:
            parent: Parent widget
            path: Breadcrumb path items
            separator: Separator between items
            max_items: Maximum items before overflow
            show_home: Whether to show home button
            **kwargs: Additional widget options
        """
        self.path = path or []
        self.separator = separator
        self.max_items = max_items
        self.show_home = show_home
        
        super().__init__(parent, **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the breadcrumb structure."""
        container = ttk.Frame(self.parent)
        
        # Scrollable frame for breadcrumbs
        self.canvas = tk.Canvas(container, height=30, highlightthickness=0)
        self.breadcrumb_frame = ttk.Frame(self.canvas)
        
        self.canvas.create_window((0, 0), window=self.breadcrumb_frame, anchor="nw")
        self.canvas.pack(side=tk.TOP, fill=tk.X)
        
        # Bind scrolling
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.breadcrumb_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self._build_breadcrumbs()
        
        return container
    
    def _build_breadcrumbs(self):
        """Build the breadcrumb widgets."""
        # Clear existing breadcrumbs
        for widget in self.breadcrumb_frame.winfo_children():
            widget.destroy()
        
        # Home button
        if self.show_home:
            home_btn = ttk.Button(self.breadcrumb_frame, text="🏠", width=3,
                                command=lambda: self._on_breadcrumb_clicked(None))
            home_btn.pack(side=tk.LEFT, padx=2)
            
            if self.path:
                separator_label = tk.Label(self.breadcrumb_frame, text=self.separator)
                separator_label.pack(side=tk.LEFT)
        
        # Handle overflow
        display_path = self.path
        if len(self.path) > self.max_items:
            # Show ellipsis and last few items
            display_path = [
                {'label': '...', 'id': 'overflow', 'clickable': False}
            ] + self.path[-(self.max_items-1):]
        
        # Build breadcrumb items
        for i, item in enumerate(display_path):
            # Breadcrumb button or label
            if item.get('clickable', True) and item.get('id') != 'overflow':
                breadcrumb_btn = ttk.Button(self.breadcrumb_frame, 
                                          text=item['label'],
                                          command=lambda it=item: self._on_breadcrumb_clicked(it))
                breadcrumb_btn.pack(side=tk.LEFT)
            else:
                breadcrumb_label = tk.Label(self.breadcrumb_frame, 
                                          text=item['label'],
                                          foreground='gray')
                breadcrumb_label.pack(side=tk.LEFT)
            
            # Separator (except for last item)
            if i < len(display_path) - 1:
                separator_label = tk.Label(self.breadcrumb_frame, text=self.separator)
                separator_label.pack(side=tk.LEFT)
    
    def _on_breadcrumb_clicked(self, item: Optional[Dict]):
        """Handle breadcrumb click."""
        if item is None:
            # Home clicked
            self.trigger_event('home_clicked')
        else:
            self.trigger_event('breadcrumb_clicked', item)
        
        # LOGIC INTEGRATION POINT: Handle navigation
        # self._navigate_to_item(item)
    
    def _on_mousewheel(self, event):
        """Handle horizontal scrolling."""
        self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")
    
    def set_path(self, path: List[Dict]):
        """Update the breadcrumb path."""
        self.path = path
        self._build_breadcrumbs()
    
    def add_item(self, item: Dict):
        """Add item to the end of the breadcrumb."""
        self.path.append(item)
        self._build_breadcrumbs()
    
    def pop_to_item(self, item_id: str):
        """Remove all items after the specified item."""
        for i, item in enumerate(self.path):
            if item.get('id') == item_id:
                self.path = self.path[:i+1]
                break
        
        self._build_breadcrumbs()
    
    def clear(self):
        """Clear all breadcrumb items."""
        self.path.clear()
        self._build_breadcrumbs()


class Toolbar(BaseComponent):
    """Toolbar component with tool groups and overflow handling."""
    
    def __init__(self, parent: tk.Widget,
                 tools: List[Dict] = None,
                 orientation: str = "horizontal",  # horizontal, vertical
                 show_labels: bool = True,
                 show_tooltips: bool = True,
                 customizable: bool = True,
                 **kwargs):
        """
        Initialize the toolbar.
        
        Args:
            parent: Parent widget
            tools: Tool definitions
            orientation: Toolbar orientation
            show_labels: Whether to show tool labels
            show_tooltips: Whether to show tooltips
            customizable: Whether toolbar can be customized
            **kwargs: Additional widget options
        """
        self.tools = tools or []
        self.orientation = orientation
        self.show_labels = show_labels
        self.show_tooltips = show_tooltips
        self.customizable = customizable
        self._tool_widgets = {}
        
        super().__init__(parent, **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the toolbar structure."""
        container = ttk.Frame(self.parent)
        
        # Main toolbar frame
        if self.orientation == "horizontal":
            self.toolbar_frame = ttk.Frame(container)
            self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        else:
            self.toolbar_frame = ttk.Frame(container)
            self.toolbar_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Overflow menu button (initially hidden)
        self.overflow_btn = ttk.Menubutton(self.toolbar_frame, text="≡")
        self.overflow_menu = tk.Menu(self.overflow_btn, tearoff=0)
        self.overflow_btn.configure(menu=self.overflow_menu)
        
        # Build toolbar tools
        self._build_toolbar()
        
        # Bind resize event to handle overflow
        container.bind("<Configure>", self._check_overflow)
        
        return container
    
    def _build_toolbar(self):
        """Build the toolbar widgets."""
        # Clear existing widgets
        for widget in self.toolbar_frame.winfo_children():
            if widget != self.overflow_btn:
                widget.destroy()
        
        self._tool_widgets.clear()
        
        # Group tools by group
        groups = {}
        for tool in self.tools:
            group = tool.get('group', 'default')
            if group not in groups:
                groups[group] = []
            groups[group].append(tool)
        
        # Create tool groups
        first_group = True
        for group_name, group_tools in groups.items():
            # Add separator between groups
            if not first_group:
                self._add_separator()
            
            # Create tools in group
            for tool in group_tools:
                self._create_tool_widget(tool)
            
            first_group = False
    
    def _create_tool_widget(self, tool: Dict):
        """Create a single tool widget."""
        tool_id = tool.get('id', tool.get('label', ''))
        
        # Tool button frame
        tool_frame = ttk.Frame(self.toolbar_frame)
        
        if self.orientation == "horizontal":
            tool_frame.pack(side=tk.LEFT, padx=1)
        else:
            tool_frame.pack(side=tk.TOP, pady=1)
        
        # Tool button
        button_kwargs = {
            'command': lambda t=tool: self._on_tool_clicked(t)
        }
        
        if 'icon' in tool:
            # TODO: Implement icon display
            button_kwargs['text'] = tool.get('icon', '●')
        elif self.show_labels:
            button_kwargs['text'] = tool.get('label', 'Tool')
        else:
            button_kwargs['text'] = tool.get('label', 'Tool')[:1]  # First letter
        
        tool_btn = ttk.Button(tool_frame, **button_kwargs)
        
        if self.orientation == "horizontal":
            tool_btn.pack(side=tk.TOP)
        else:
            tool_btn.pack(side=tk.LEFT)
        
        # Label (if enabled and separate from button)
        if self.show_labels and 'icon' in tool:
            label = tk.Label(tool_frame, text=tool.get('label', ''), 
                           font=('Arial', 8))
            if self.orientation == "horizontal":
                label.pack(side=tk.BOTTOM)
            else:
                label.pack(side=tk.RIGHT)
        
        # Tooltip (if enabled)
        if self.show_tooltips and 'tooltip' in tool:
            # TODO: Integrate with Tooltip component
            pass
        
        # Store widget reference
        self._tool_widgets[tool_id] = {
            'frame': tool_frame,
            'button': tool_btn,
            'tool': tool
        }
    
    def _add_separator(self):
        """Add a separator between tool groups."""
        if self.orientation == "horizontal":
            sep = ttk.Separator(self.toolbar_frame, orient=tk.VERTICAL)
            sep.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        else:
            sep = ttk.Separator(self.toolbar_frame, orient=tk.HORIZONTAL)
            sep.pack(side=tk.TOP, fill=tk.X, pady=5)
    
    def _on_tool_clicked(self, tool: Dict):
        """Handle tool button click."""
        self.trigger_event('tool_clicked', tool)
        
        # LOGIC INTEGRATION POINT: Execute tool action
        # self._execute_tool_action(tool)
    
    def _check_overflow(self, event):
        """Check if tools overflow and show overflow menu."""
        # This would implement overflow detection and management
        # For now, just a placeholder
        pass
    
    def add_tool(self, tool: Dict, group: str = "default"):
        """Add a new tool to the toolbar."""
        tool['group'] = group
        self.tools.append(tool)
        self._build_toolbar()
    
    def remove_tool(self, tool_id: str):
        """Remove a tool from the toolbar."""
        self.tools = [t for t in self.tools if t.get('id') != tool_id]
        self._build_toolbar()
    
    def set_tool_enabled(self, tool_id: str, enabled: bool):
        """Enable or disable a tool."""
        if tool_id in self._tool_widgets:
            state = 'normal' if enabled else 'disabled'
            self._tool_widgets[tool_id]['button'].configure(state=state)
    
    def set_tool_pressed(self, tool_id: str, pressed: bool):
        """Set tool pressed state (for toggle tools)."""
        if tool_id in self._tool_widgets:
            if pressed:
                self._tool_widgets[tool_id]['button'].state(['pressed'])
            else:
                self._tool_widgets[tool_id]['button'].state(['!pressed'])
