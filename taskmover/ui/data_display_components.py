"""
TaskMover UI Framework - Data Display Components
"""
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional, List, Union, Dict
from .base_component import BaseComponent, ComponentState


class DataTable(BaseComponent):
    """
    Data table with sortable columns, filtering, and selection.
    """
    
    def __init__(self, parent: tk.Widget,
                 columns: List[Dict] = None,
                 data: List[Dict] = None,
                 sortable: bool = True,
                 filterable: bool = True,
                 selectable: bool = True,
                 multi_select: bool = False,
                 resizable_columns: bool = True,
                 virtual_scrolling: bool = False,
                 **kwargs):
        """
        Initialize the data table.
        
        Args:
            parent: Parent widget
            columns: Column definitions
            data: Table data
            sortable: Whether columns are sortable
            filterable: Whether table supports filtering
            selectable: Whether rows are selectable
            multi_select: Whether multiple rows can be selected
            resizable_columns: Whether columns can be resized
            virtual_scrolling: Whether to use virtual scrolling for large datasets
            **kwargs: Additional widget options
        """
        self.columns = columns or []
        self.data = data or []
        self.sortable = sortable
        self.filterable = filterable
        self.selectable = selectable
        self.multi_select = multi_select
        self.resizable_columns = resizable_columns
        self.virtual_scrolling = virtual_scrolling
        
        self._selected_rows = set()
        self._sort_column = None
        self._sort_direction = 'asc'
        self._filtered_data = self.data.copy()
        self._column_filters = {}
        
        super().__init__(parent, **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the data table structure."""
        container = ttk.Frame(self.parent)
        
        # Filter bar (if enabled)
        if self.filterable:
            self.filter_frame = ttk.Frame(container)
            self.filter_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            
            # Quick filter entry
            tk.Label(self.filter_frame, text="Filter:").pack(side=tk.LEFT)
            self.filter_var = tk.StringVar()
            self.filter_var.trace("w", self._on_filter_changed)
            self.filter_entry = ttk.Entry(self.filter_frame, textvariable=self.filter_var)
            self.filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Table container
        table_frame = ttk.Frame(container)
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Create treeview for table
        tree_columns = [col['id'] for col in self.columns] if self.columns else ['#0']
        
        self.tree = ttk.Treeview(table_frame, columns=tree_columns, show='headings' if self.columns else 'tree')
        
        # Configure columns
        for col in self.columns:
            col_id = col['id']
            self.tree.heading(col_id, text=col['title'], 
                            command=lambda c=col_id: self._on_column_clicked(c) if self.sortable else None)
            self.tree.column(col_id, width=col.get('width', 100), 
                           minwidth=col.get('min_width', 50),
                           anchor=col.get('align', 'w'))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        if self.selectable:
            self.tree.bind('<<TreeviewSelect>>', self._on_selection_changed)
        
        self.tree.bind('<Button-3>', self._on_right_click)  # Context menu
        self.tree.bind('<Double-1>', self._on_double_click)
        
        # Load initial data
        self._populate_table()
        
        return container
    
    def _populate_table(self):
        """Populate the table with data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add filtered data
        for i, row in enumerate(self._filtered_data):
            values = [row.get(col['id'], '') for col in self.columns]
            item_id = self.tree.insert('', tk.END, values=values, tags=(str(i),))
            
            # Store row data reference
            self.tree.set(item_id, '#data', row)
    
    def _on_column_clicked(self, column_id: str):
        """Handle column header click for sorting."""
        if self._sort_column == column_id:
            # Toggle sort direction
            self._sort_direction = 'desc' if self._sort_direction == 'asc' else 'asc'
        else:
            self._sort_column = column_id
            self._sort_direction = 'asc'
        
        self._sort_data()
        self._populate_table()
        
        # Update column header to show sort indicator
        for col in self.columns:
            if col['id'] == column_id:
                indicator = ' ↑' if self._sort_direction == 'asc' else ' ↓'
                self.tree.heading(column_id, text=col['title'] + indicator)
            else:
                self.tree.heading(col['id'], text=col['title'])
    
    def _sort_data(self):
        """Sort the filtered data."""
        if not self._sort_column:
            return
        
        reverse = self._sort_direction == 'desc'
        
        try:
            self._filtered_data.sort(
                key=lambda x: x.get(self._sort_column, ''),
                reverse=reverse
            )
        except TypeError:
            # Handle mixed types by converting to string
            self._filtered_data.sort(
                key=lambda x: str(x.get(self._sort_column, '')),
                reverse=reverse
            )
    
    def _on_filter_changed(self, *args):
        """Handle filter text changes."""
        filter_text = self.filter_var.get().lower()
        
        if not filter_text:
            self._filtered_data = self.data.copy()
        else:
            self._filtered_data = []
            for row in self.data:
                # Search in all string values
                for value in row.values():
                    if filter_text in str(value).lower():
                        self._filtered_data.append(row)
                        break
        
        self._sort_data()
        self._populate_table()
    
    def _on_selection_changed(self, event):
        """Handle row selection changes."""
        selected_items = self.tree.selection()
        
        if not self.multi_select and len(selected_items) > 1:
            # Keep only the last selected item
            for item in selected_items[:-1]:
                self.tree.selection_remove(item)
            selected_items = selected_items[-1:]
        
        # Update selected rows
        self._selected_rows.clear()
        for item in selected_items:
            row_data = self.tree.set(item, '#data')
            if row_data:
                self._selected_rows.add(id(row_data))
        
        self.trigger_event('selection_changed', list(selected_items))
    
    def _on_right_click(self, event):
        """Handle right-click for context menu."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            row_data = self.tree.set(item, '#data')
            self.trigger_event('context_menu', {'item': item, 'data': row_data, 'x': event.x_root, 'y': event.y_root})
    
    def _on_double_click(self, event):
        """Handle double-click on row."""
        item = self.tree.identify_row(event.y)
        if item:
            row_data = self.tree.set(item, '#data')
            self.trigger_event('row_double_click', {'item': item, 'data': row_data})
    
    def set_data(self, data: List[Dict]):
        """Update table data."""
        self.data = data
        self._filtered_data = data.copy()
        self._sort_data()
        self._populate_table()
    
    def add_row(self, row_data: Dict):
        """Add a new row to the table."""
        self.data.append(row_data)
        self._on_filter_changed()  # Reapply filter
    
    def remove_row(self, row_index: int):
        """Remove a row from the table."""
        if 0 <= row_index < len(self.data):
            self.data.pop(row_index)
            self._on_filter_changed()  # Reapply filter
    
    def get_selected_rows(self) -> List[Dict]:
        """Get the selected row data."""
        selected_data = []
        for item in self.tree.selection():
            row_data = self.tree.set(item, '#data')
            if row_data:
                selected_data.append(row_data)
        return selected_data
    
    def set_column_filter(self, column_id: str, filter_value: Any):
        """Set a filter for a specific column."""
        self._column_filters[column_id] = filter_value
        self._apply_column_filters()
    
    def _apply_column_filters(self):
        """Apply column-specific filters."""
        if not self._column_filters:
            self._filtered_data = self.data.copy()
        else:
            self._filtered_data = []
            for row in self.data:
                match = True
                for col_id, filter_val in self._column_filters.items():
                    if filter_val and str(filter_val).lower() not in str(row.get(col_id, '')).lower():
                        match = False
                        break
                if match:
                    self._filtered_data.append(row)
        
        self._sort_data()
        self._populate_table()


class ListView(BaseComponent):
    """
    List view component with item selection and virtual scrolling.
    """
    
    def __init__(self, parent: tk.Widget,
                 items: List[Any] = None,
                 item_renderer: Optional[Callable] = None,
                 selectable: bool = True,
                 multi_select: bool = False,
                 searchable: bool = True,
                 virtual_scrolling: bool = False,
                 **kwargs):
        """
        Initialize the list view.
        
        Args:
            parent: Parent widget
            items: List items
            item_renderer: Custom item rendering function
            selectable: Whether items are selectable
            multi_select: Whether multiple items can be selected
            searchable: Whether list supports search
            virtual_scrolling: Whether to use virtual scrolling
            **kwargs: Additional widget options
        """
        self.items = items or []
        self.item_renderer = item_renderer
        self.selectable = selectable
        self.multi_select = multi_select
        self.searchable = searchable
        self.virtual_scrolling = virtual_scrolling
        
        self._selected_items = set()
        self._filtered_items = self.items.copy()
        self._item_widgets = {}
        
        super().__init__(parent, **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the list view structure."""
        container = ttk.Frame(self.parent)
        
        # Search bar (if enabled)
        if self.searchable:
            search_frame = ttk.Frame(container)
            search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            
            tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
            self.search_var = tk.StringVar()
            self.search_var.trace("w", self._on_search_changed)
            self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
            self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # List container with scrollbar
        list_frame = ttk.Frame(container)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(list_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Build list items
        self._build_list()
        
        return container
    
    def _build_list(self):
        """Build the list item widgets."""
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self._item_widgets.clear()
        
        # Create item widgets
        for i, item in enumerate(self._filtered_items):
            item_widget = self._create_item_widget(item, i)
            self._item_widgets[i] = item_widget
    
    def _create_item_widget(self, item: Any, index: int) -> tk.Widget:
        """Create a single list item widget."""
        item_frame = ttk.Frame(self.scrollable_frame)
        item_frame.pack(side=tk.TOP, fill=tk.X, padx=2, pady=1)
        
        # Use custom renderer if provided
        if self.item_renderer:
            content = self.item_renderer(item, index)
            if isinstance(content, tk.Widget):
                content.pack(in_=item_frame, fill=tk.BOTH, expand=True)
            else:
                label = tk.Label(item_frame, text=str(content))
                label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        else:
            # Default rendering
            label = tk.Label(item_frame, text=str(item), anchor='w')
            label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Selection handling
        if self.selectable:
            item_frame.bind("<Button-1>", lambda e, idx=index: self._on_item_clicked(idx))
            item_frame.bind("<Double-Button-1>", lambda e, idx=index: self._on_item_double_clicked(idx))
            
            # Context menu
            item_frame.bind("<Button-3>", lambda e, idx=index: self._on_item_right_clicked(idx, e))
        
        # Visual selection state
        if index in self._selected_items:
            item_frame.configure(relief='solid', borderwidth=1)
        
        return item_frame
    
    def _on_search_changed(self, *args):
        """Handle search text changes."""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            self._filtered_items = self.items.copy()
        else:
            self._filtered_items = [
                item for item in self.items
                if search_text in str(item).lower()
            ]
        
        self._build_list()
    
    def _on_item_clicked(self, index: int):
        """Handle item click."""
        if not self.multi_select:
            self._selected_items.clear()
        
        if index in self._selected_items:
            self._selected_items.remove(index)
        else:
            self._selected_items.add(index)
        
        self._update_selection_visual()
        self.trigger_event('selection_changed', list(self._selected_items))
    
    def _on_item_double_clicked(self, index: int):
        """Handle item double-click."""
        item = self._filtered_items[index] if index < len(self._filtered_items) else None
        self.trigger_event('item_double_click', {'index': index, 'item': item})
    
    def _on_item_right_clicked(self, index: int, event):
        """Handle item right-click."""
        item = self._filtered_items[index] if index < len(self._filtered_items) else None
        self.trigger_event('context_menu', {
            'index': index, 
            'item': item, 
            'x': event.x_root, 
            'y': event.y_root
        })
    
    def _update_selection_visual(self):
        """Update visual selection state."""
        for i, widget in self._item_widgets.items():
            if i in self._selected_items:
                widget.configure(relief='solid', borderwidth=1)
            else:
                widget.configure(relief='flat', borderwidth=0)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def set_items(self, items: List[Any]):
        """Update list items."""
        self.items = items
        self._filtered_items = items.copy()
        self._selected_items.clear()
        self._build_list()
    
    def add_item(self, item: Any):
        """Add a new item to the list."""
        self.items.append(item)
        self._on_search_changed()  # Reapply search filter
    
    def remove_item(self, index: int):
        """Remove an item from the list."""
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self._selected_items.discard(index)
            self._on_search_changed()  # Reapply search filter
    
    def get_selected_items(self) -> List[Any]:
        """Get the selected items."""
        return [self._filtered_items[i] for i in self._selected_items if i < len(self._filtered_items)]
    
    def set_selected_indices(self, indices: List[int]):
        """Set the selected item indices."""
        self._selected_items = set(indices)
        self._update_selection_visual()


class GridView(BaseComponent):
    """
    Grid view component with responsive columns and item templates.
    """
    
    def __init__(self, parent: tk.Widget,
                 items: List[Any] = None,
                 item_template: Optional[Callable] = None,
                 columns: int = 3,
                 item_size: tuple = (150, 100),
                 responsive: bool = True,
                 selectable: bool = True,
                 **kwargs):
        """
        Initialize the grid view.
        
        Args:
            parent: Parent widget
            items: Grid items
            item_template: Item template function
            columns: Number of columns
            item_size: Item size (width, height)
            responsive: Whether grid is responsive
            selectable: Whether items are selectable
            **kwargs: Additional widget options
        """
        self.items = items or []
        self.item_template = item_template
        self.columns = columns
        self.item_size = item_size
        self.responsive = responsive
        self.selectable = selectable
        
        self._selected_items = set()
        self._item_widgets = {}
        
        super().__init__(parent, **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the grid view structure."""
        container = ttk.Frame(self.parent)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel and resize
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        if self.responsive:
            container.bind("<Configure>", self._on_resize)
        
        # Build grid
        self._build_grid()
        
        return container
    
    def _build_grid(self):
        """Build the grid layout."""
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self._item_widgets.clear()
        
        # Calculate columns if responsive
        if self.responsive:
            canvas_width = self.canvas.winfo_width()
            if canvas_width > 1:
                self.columns = max(1, canvas_width // self.item_size[0])
        
        # Create grid items
        for i, item in enumerate(self.items):
            row = i // self.columns
            col = i % self.columns
            
            item_widget = self._create_grid_item(item, i)
            item_widget.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
            
            self._item_widgets[i] = item_widget
        
        # Configure grid weights for responsive behavior
        for i in range(self.columns):
            self.scrollable_frame.grid_columnconfigure(i, weight=1)
    
    def _create_grid_item(self, item: Any, index: int) -> tk.Widget:
        """Create a single grid item widget."""
        item_frame = ttk.Frame(self.scrollable_frame, width=self.item_size[0], height=self.item_size[1])
        item_frame.grid_propagate(False)
        
        # Use custom template if provided
        if self.item_template:
            content = self.item_template(item, index)
            if isinstance(content, tk.Widget):
                content.pack(in_=item_frame, fill=tk.BOTH, expand=True)
            else:
                label = tk.Label(item_frame, text=str(content), wraplength=self.item_size[0]-10)
                label.pack(fill=tk.BOTH, expand=True)
        else:
            # Default template
            label = tk.Label(item_frame, text=str(item), wraplength=self.item_size[0]-10,
                           justify=tk.CENTER)
            label.pack(fill=tk.BOTH, expand=True)
        
        # Selection handling
        if self.selectable:
            item_frame.bind("<Button-1>", lambda e, idx=index: self._on_item_clicked(idx))
            item_frame.bind("<Double-Button-1>", lambda e, idx=index: self._on_item_double_clicked(idx))
            item_frame.bind("<Button-3>", lambda e, idx=index: self._on_item_right_clicked(idx, e))
        
        # Visual selection state
        if index in self._selected_items:
            item_frame.configure(relief='solid', borderwidth=2)
        
        return item_frame
    
    def _on_item_clicked(self, index: int):
        """Handle item click."""
        if index in self._selected_items:
            self._selected_items.remove(index)
        else:
            self._selected_items.add(index)
        
        self._update_selection_visual()
        self.trigger_event('selection_changed', list(self._selected_items))
    
    def _on_item_double_clicked(self, index: int):
        """Handle item double-click."""
        item = self.items[index] if index < len(self.items) else None
        self.trigger_event('item_double_click', {'index': index, 'item': item})
    
    def _on_item_right_clicked(self, index: int, event):
        """Handle item right-click."""
        item = self.items[index] if index < len(self.items) else None
        self.trigger_event('context_menu', {
            'index': index, 
            'item': item, 
            'x': event.x_root, 
            'y': event.y_root
        })
    
    def _update_selection_visual(self):
        """Update visual selection state."""
        for i, widget in self._item_widgets.items():
            if i in self._selected_items:
                widget.configure(relief='solid', borderwidth=2)
            else:
                widget.configure(relief='flat', borderwidth=0)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_resize(self, event):
        """Handle container resize for responsive layout."""
        if event.widget == self.canvas.master:
            self._build_grid()
    
    def set_items(self, items: List[Any]):
        """Update grid items."""
        self.items = items
        self._selected_items.clear()
        self._build_grid()
    
    def set_columns(self, columns: int):
        """Set the number of columns."""
        self.columns = columns
        self._build_grid()
    
    def get_selected_items(self) -> List[Any]:
        """Get the selected items."""
        return [self.items[i] for i in self._selected_items if i < len(self.items)]


class TreeView(BaseComponent):
    """
    Tree view component with expand/collapse and lazy loading.
    """
    
    def __init__(self, parent: tk.Widget,
                 tree_data: Dict = None,
                 lazy_loading: bool = False,
                 node_renderer: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize the tree view.
        
        Args:
            parent: Parent widget
            tree_data: Tree structure data
            lazy_loading: Whether to use lazy loading
            node_renderer: Custom node rendering function
            **kwargs: Additional widget options
        """
        self.tree_data = tree_data or {}
        self.lazy_loading = lazy_loading
        self.node_renderer = node_renderer
        self._expanded_nodes = set()
        self._selected_node = None
        
        super().__init__(parent, **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the tree view structure."""
        container = ttk.Frame(self.parent)
        
        # Create treeview widget
        self.tree = ttk.Treeview(container)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind('<<TreeviewOpen>>', self._on_node_expanded)
        self.tree.bind('<<TreeviewClose>>', self._on_node_collapsed)
        self.tree.bind('<<TreeviewSelect>>', self._on_selection_changed)
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._on_right_click)
        
        # Build initial tree
        self._build_tree()
        
        return container
    
    def _build_tree(self):
        """Build the tree structure."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Build from tree data
        if self.tree_data:
            self._build_tree_recursive(self.tree_data, '')
    
    def _build_tree_recursive(self, node_data: Dict, parent_id: str):
        """Recursively build tree nodes."""
        for key, value in node_data.items():
            if isinstance(value, dict):
                # Branch node
                node_id = self.tree.insert(parent_id, tk.END, text=key, open=False)
                
                if 'children' in value:
                    self._build_tree_recursive(value['children'], node_id)
                elif self.lazy_loading:
                    # Add dummy child for lazy loading
                    self.tree.insert(node_id, tk.END, text='Loading...')
            else:
                # Leaf node
                self.tree.insert(parent_id, tk.END, text=f"{key}: {value}")
    
    def _on_node_expanded(self, event):
        """Handle node expansion."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self._expanded_nodes.add(item)
            
            # Handle lazy loading
            if self.lazy_loading:
                children = self.tree.get_children(item)
                if len(children) == 1 and self.tree.item(children[0])['text'] == 'Loading...':
                    # Remove dummy child and load real children
                    self.tree.delete(children[0])
                    self.trigger_event('lazy_load', {'node': item})
    
    def _on_node_collapsed(self, event):
        """Handle node collapse."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self._expanded_nodes.discard(item)
    
    def _on_selection_changed(self, event):
        """Handle selection changes."""
        selected = self.tree.selection()
        if selected:
            self._selected_node = selected[0]
            node_text = self.tree.item(selected[0])['text']
            self.trigger_event('selection_changed', {'node': selected[0], 'text': node_text})
    
    def _on_double_click(self, event):
        """Handle double-click on node."""
        if self._selected_node:
            node_text = self.tree.item(self._selected_node)['text']
            self.trigger_event('node_double_click', {'node': self._selected_node, 'text': node_text})
    
    def _on_right_click(self, event):
        """Handle right-click for context menu."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            node_text = self.tree.item(item)['text']
            self.trigger_event('context_menu', {
                'node': item, 
                'text': node_text, 
                'x': event.x_root, 
                'y': event.y_root
            })
    
    def add_node(self, parent_id: str, text: str, **kwargs) -> str:
        """Add a new node to the tree."""
        return self.tree.insert(parent_id, tk.END, text=text, **kwargs)
    
    def remove_node(self, node_id: str):
        """Remove a node from the tree."""
        self.tree.delete(node_id)
    
    def expand_node(self, node_id: str):
        """Expand a specific node."""
        self.tree.item(node_id, open=True)
        self._expanded_nodes.add(node_id)
    
    def collapse_node(self, node_id: str):
        """Collapse a specific node."""
        self.tree.item(node_id, open=False)
        self._expanded_nodes.discard(node_id)
    
    def get_selected_node(self) -> Optional[str]:
        """Get the selected node ID."""
        return self._selected_node
    
    def set_tree_data(self, tree_data: Dict):
        """Update the tree data."""
        self.tree_data = tree_data
        self._build_tree()
