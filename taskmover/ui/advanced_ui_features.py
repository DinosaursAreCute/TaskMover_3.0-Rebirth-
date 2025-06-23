"""
TaskMover UI Framework - Advanced UI Features
Context Menus, Multi-Selection, and Keyboard Navigation
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Any, Optional, Callable, Union
from .base_component import BaseComponent, ComponentState


class ContextMenu(BaseComponent):
    """
    Universal context menu framework for all UI components.
    """
    
    def __init__(self, parent: tk.Widget, **kwargs):
        """
        Initialize the context menu.
        
        Args:
            parent: Parent widget
            **kwargs: Additional widget options
        """
        self._menu_items = []
        self._active_context = None
        
        super().__init__(parent, **kwargs)
        
        self._setup_menu()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the context menu widget."""
        # Context menus are created on-demand, not at initialization
        menu = tk.Menu(self.parent, tearoff=0)
        return menu
    
    def _setup_menu(self):
        """Set up the context menu."""
        self._menu_widget = self._widget
    
    def add_item(self, label: str, command: Callable, 
                 icon: Optional[str] = None,
                 shortcut: Optional[str] = None,
                 enabled: bool = True,
                 separator_before: bool = False,
                 separator_after: bool = False):
        """
        Add an item to the context menu.
        
        Args:
            label: Display text for the menu item
            command: Function to call when item is clicked
            icon: Optional icon name
            shortcut: Optional keyboard shortcut text
            enabled: Whether the item is enabled
            separator_before: Add separator before this item
            separator_after: Add separator after this item
        """
        item = {
            'type': 'command',
            'label': label,
            'command': command,
            'icon': icon,
            'shortcut': shortcut,
            'enabled': enabled,
            'separator_before': separator_before,
            'separator_after': separator_after
        }
        self._menu_items.append(item)
    
    def add_submenu(self, label: str, submenu_items: List[Dict],
                    icon: Optional[str] = None,
                    enabled: bool = True):
        """
        Add a submenu to the context menu.
        
        Args:
            label: Display text for the submenu
            submenu_items: List of submenu item dictionaries
            icon: Optional icon name
            enabled: Whether the submenu is enabled
        """
        item = {
            'type': 'submenu',
            'label': label,
            'submenu_items': submenu_items,
            'icon': icon,
            'enabled': enabled
        }
        self._menu_items.append(item)
    
    def add_separator(self):
        """Add a separator to the menu."""
        item = {'type': 'separator'}
        self._menu_items.append(item)
    
    def add_checkable_item(self, label: str, variable: tk.BooleanVar,
                          command: Optional[Callable] = None,
                          icon: Optional[str] = None,
                          enabled: bool = True):
        """
        Add a checkable item to the menu.
        
        Args:
            label: Display text for the item
            variable: BooleanVar to track check state
            command: Optional command to call when toggled
            icon: Optional icon name
            enabled: Whether the item is enabled
        """
        item = {
            'type': 'checkbutton',
            'label': label,
            'variable': variable,
            'command': command,
            'icon': icon,
            'enabled': enabled
        }
        self._menu_items.append(item)
    
    def show(self, x: int, y: int, context: Optional[Any] = None):
        """
        Show the context menu at specified coordinates.
        
        Args:
            x: X coordinate (screen coordinates)
            y: Y coordinate (screen coordinates)
            context: Optional context object for menu actions
        """
        self._active_context = context
        self._build_menu()
        
        try:
            if isinstance(self._menu_widget, tk.Menu):
                self._menu_widget.post(x, y)
        except tk.TclError:
            # Handle case where menu can't be displayed
            pass
    
    def _build_menu(self):
        """Build the menu from current items."""
        # Clear existing menu
        menu = self._menu_widget
        if isinstance(menu, tk.Menu):
            menu.delete(0, tk.END)
        
        for item in self._menu_items:
            if item.get('separator_before') and isinstance(menu, tk.Menu):
                menu.add_separator()
            
            if item['type'] == 'command':
                self._add_command_item(item)
            elif item['type'] == 'submenu':
                self._add_submenu_item(item)
            elif item['type'] == 'separator' and isinstance(menu, tk.Menu):
                menu.add_separator()
            elif item['type'] == 'checkbutton':
                self._add_checkbutton_item(item)
            
            if item.get('separator_after') and isinstance(menu, tk.Menu):
                menu.add_separator()
    
    def _add_command_item(self, item: Dict):
        """Add a command item to the menu."""
        menu = self._menu_widget
        if not isinstance(menu, tk.Menu):
            return
            
        label = item['label']
        if item.get('shortcut'):
            label += f"\t{item['shortcut']}"
        
        state = tk.NORMAL if item.get('enabled', True) else tk.DISABLED
        
        menu.add_command(
            label=label,
            command=lambda: self._execute_command(item['command']),
            state=state
        )
    
    def _add_submenu_item(self, item: Dict):
        """Add a submenu item to the menu."""
        menu = self._menu_widget
        if not isinstance(menu, tk.Menu):
            return
            
        submenu = tk.Menu(menu, tearoff=0)
        
        for subitem in item.get('submenu_items', []):
            if subitem.get('type') == 'separator':
                submenu.add_separator()
            else:
                submenu.add_command(
                    label=subitem.get('label', ''),
                    command=lambda cmd=subitem.get('command'): self._execute_command(cmd),
                    state=tk.NORMAL if subitem.get('enabled', True) else tk.DISABLED
                )
        
        state = tk.NORMAL if item.get('enabled', True) else tk.DISABLED
        menu.add_cascade(label=item['label'], menu=submenu, state=state)
    
    def _add_checkbutton_item(self, item: Dict):
        """Add a checkbutton item to the menu."""
        menu = self._menu_widget
        if not isinstance(menu, tk.Menu):
            return
            
        state = tk.NORMAL if item.get('enabled', True) else tk.DISABLED
        
        menu.add_checkbutton(
            label=item['label'],
            variable=item['variable'],
            command=lambda: self._execute_command(item.get('command')),
            state=state
        )
    
    def _execute_command(self, command: Optional[Callable]):
        """Execute a menu command with context."""
        if command:
            if self._active_context is not None:
                # Try to pass context if command accepts it
                try:
                    command(self._active_context)
                except TypeError:
                    # Command doesn't accept context parameter
                    command()
            else:
                command()
    
    def clear_items(self):
        """Clear all menu items."""
        self._menu_items.clear()
    
    def get_active_context(self) -> Any:
        """Get the current active context."""
        return self._active_context


class PatternContextMenu(ContextMenu):
    """
    Context menu specifically for pattern management.
    """
    
    def __init__(self, parent: tk.Widget,
                 on_edit: Optional[Callable] = None,
                 on_duplicate: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None,
                 on_test: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize pattern context menu.
        
        Args:
            parent: Parent widget
            on_edit: Callback for edit action
            on_duplicate: Callback for duplicate action
            on_delete: Callback for delete action
            on_test: Callback for test action
            **kwargs: Additional options
        """
        super().__init__(parent, **kwargs)
        
        # Add pattern-specific menu items
        self.add_item("Edit Pattern", on_edit or self._placeholder_action, 
                     icon="edit", shortcut="Ctrl+E")
        self.add_item("Duplicate Pattern", on_duplicate or self._placeholder_action,
                     icon="copy", shortcut="Ctrl+D")
        self.add_separator()
        self.add_item("Test Pattern", on_test or self._placeholder_action,
                     icon="test", shortcut="F5")
        self.add_separator()
        self.add_item("Delete Pattern", on_delete or self._placeholder_action,
                     icon="delete", shortcut="Delete")
    
    def _placeholder_action(self, context=None):
        """Placeholder action for testing."""
        print(f"Pattern action executed with context: {context}")


class RuleContextMenu(ContextMenu):
    """
    Context menu specifically for rule management.
    """
    
    def __init__(self, parent: tk.Widget,
                 on_edit: Optional[Callable] = None,
                 on_duplicate: Optional[Callable] = None,
                 on_toggle_enabled: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None,
                 on_test: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize rule context menu.
        
        Args:
            parent: Parent widget
            on_edit: Callback for edit action
            on_duplicate: Callback for duplicate action
            on_toggle_enabled: Callback for enable/disable toggle
            on_delete: Callback for delete action
            on_test: Callback for test action
            **kwargs: Additional options
        """
        super().__init__(parent, **kwargs)
        
        # Add rule-specific menu items
        self.add_item("Edit Rule", on_edit or self._placeholder_action,
                     icon="edit", shortcut="Ctrl+E")
        self.add_item("Duplicate Rule", on_duplicate or self._placeholder_action,
                     icon="copy", shortcut="Ctrl+D")
        self.add_separator()
        
        # Enabled/disabled toggle
        self.enabled_var = tk.BooleanVar(value=True)
        self.add_checkable_item("Enabled", self.enabled_var,
                               command=on_toggle_enabled or self._placeholder_action)
        
        self.add_separator()
        self.add_item("Test Rule", on_test or self._placeholder_action,
                     icon="test", shortcut="F5")
        self.add_separator()
        self.add_item("Delete Rule", on_delete or self._placeholder_action,
                     icon="delete", shortcut="Delete")
    
    def _placeholder_action(self, context=None):
        """Placeholder action for testing."""
        print(f"Rule action executed with context: {context}")
    
    def set_rule_enabled(self, enabled: bool):
        """Set the enabled state of the rule."""
        self.enabled_var.set(enabled)


class RulesetContextMenu(ContextMenu):
    """
    Context menu specifically for ruleset management.
    """
    
    def __init__(self, parent: tk.Widget,
                 on_edit: Optional[Callable] = None,
                 on_duplicate: Optional[Callable] = None,
                 on_execute: Optional[Callable] = None,
                 on_export: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize ruleset context menu.
        
        Args:
            parent: Parent widget
            on_edit: Callback for edit action
            on_duplicate: Callback for duplicate action
            on_execute: Callback for execute action
            on_export: Callback for export action
            on_delete: Callback for delete action
            **kwargs: Additional options
        """
        super().__init__(parent, **kwargs)
        
        # Add ruleset-specific menu items
        self.add_item("Edit Ruleset", on_edit or self._placeholder_action,
                     icon="edit", shortcut="Ctrl+E")
        self.add_item("Duplicate Ruleset", on_duplicate or self._placeholder_action,
                     icon="copy", shortcut="Ctrl+D")
        self.add_separator()
        self.add_item("Execute Ruleset", on_execute or self._placeholder_action,
                     icon="run", shortcut="F5")
        self.add_separator()
        self.add_item("Export Ruleset", on_export or self._placeholder_action,
                     icon="export", shortcut="Ctrl+S")
        self.add_separator()
        self.add_item("Delete Ruleset", on_delete or self._placeholder_action,
                     icon="delete", shortcut="Delete")
    
    def _placeholder_action(self, context=None):
        """Placeholder action for testing."""
        print(f"Ruleset action executed with context: {context}")


class FileContextMenu(ContextMenu):
    """
    Context menu specifically for file operations.
    """
    
    def __init__(self, parent: tk.Widget,
                 on_preview: Optional[Callable] = None,
                 on_organize: Optional[Callable] = None,
                 on_exclude: Optional[Callable] = None,
                 on_properties: Optional[Callable] = None,
                 **kwargs):
        """
        Initialize file context menu.
        
        Args:
            parent: Parent widget
            on_preview: Callback for preview action
            on_organize: Callback for organize action
            on_exclude: Callback for exclude action
            on_properties: Callback for properties action
            **kwargs: Additional options
        """
        super().__init__(parent, **kwargs)
        
        # Add file-specific menu items
        self.add_item("Preview File", on_preview or self._placeholder_action,
                     icon="preview", shortcut="Space")
        self.add_separator()
        self.add_item("Organize Now", on_organize or self._placeholder_action,
                     icon="organize", shortcut="Ctrl+O")
        self.add_item("Exclude from Organization", on_exclude or self._placeholder_action,
                     icon="exclude")
        self.add_separator()
        self.add_item("Properties", on_properties or self._placeholder_action,
                     icon="properties", shortcut="Alt+Enter")
    
    def _placeholder_action(self, context=None):
        """Placeholder action for testing."""
        print(f"File action executed with context: {context}")


class SelectionManager(BaseComponent):
    """
    Manages multi-selection state across UI components.
    """
    
    def __init__(self, parent: tk.Widget, **kwargs):
        """
        Initialize the selection manager.
        
        Args:
            parent: Parent widget
            **kwargs: Additional widget options
        """
        self._selected_items = set()
        self._selection_callbacks = []
        self._selection_mode = 'multiple'  # 'single', 'multiple', 'extended'
        
        super().__init__(parent, **kwargs)
        
        self._setup_selection_ui()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the selection UI widget."""
        # Selection toolbar
        toolbar = ttk.Frame(self.parent)
        return toolbar
    
    def _setup_selection_ui(self):
        """Set up the selection UI."""
        # Selection count label
        self.count_label = ttk.Label(self._widget, text="0 items selected")
        self.count_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Select all button
        self.select_all_btn = ttk.Button(self._widget, text="Select All",
                                        command=self.select_all)
        self.select_all_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Select none button
        self.select_none_btn = ttk.Button(self._widget, text="Select None",
                                         command=self.select_none)
        self.select_none_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Invert selection button
        self.invert_btn = ttk.Button(self._widget, text="Invert Selection",
                                    command=lambda: self.invert_selection([]))
        self.invert_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Selection actions
        self.actions_frame = ttk.Frame(self._widget)
        self.actions_frame.pack(side=tk.RIGHT)
        
        # Initially hidden
        self._widget.pack_forget()
    
    def add_item(self, item_id: str, item_data: Any = None):
        """
        Add an item to the selection.
        
        Args:
            item_id: Unique identifier for the item
            item_data: Optional data associated with the item
        """
        if self._selection_mode == 'single':
            self._selected_items.clear()
        
        self._selected_items.add(item_id)
        self._update_ui()
        self._notify_callbacks()
    
    def remove_item(self, item_id: str):
        """
        Remove an item from the selection.
        
        Args:
            item_id: Unique identifier for the item
        """
        self._selected_items.discard(item_id)
        self._update_ui()
        self._notify_callbacks()
    
    def toggle_item(self, item_id: str, item_data: Any = None):
        """
        Toggle an item's selection state.
        
        Args:
            item_id: Unique identifier for the item
            item_data: Optional data associated with the item
        """
        if item_id in self._selected_items:
            self.remove_item(item_id)
        else:
            self.add_item(item_id, item_data)
    
    def select_all(self, available_items: Optional[List[str]] = None):
        """
        Select all items.
        
        Args:
            available_items: List of all available item IDs
        """
        if available_items:
            self._selected_items.update(available_items)
            self._update_ui()
            self._notify_callbacks()
    
    def select_none(self):
        """Clear all selections."""
        self._selected_items.clear()
        self._update_ui()
        self._notify_callbacks()
    
    def invert_selection(self, available_items: List[str]):
        """
        Invert the current selection.
        
        Args:
            available_items: List of all available item IDs
        """
        current_selection = self._selected_items.copy()
        self._selected_items.clear()
        
        for item_id in available_items:
            if item_id not in current_selection:
                self._selected_items.add(item_id)
        
        self._update_ui()
        self._notify_callbacks()
    
    def get_selected_items(self) -> set:
        """Get the set of selected item IDs."""
        return self._selected_items.copy()
    
    def get_selection_count(self) -> int:
        """Get the number of selected items."""
        return len(self._selected_items)
    
    def is_selected(self, item_id: str) -> bool:
        """Check if an item is selected."""
        return item_id in self._selected_items
    
    def set_selection_mode(self, mode: str):
        """
        Set the selection mode.
        
        Args:
            mode: Selection mode ('single', 'multiple', 'extended')
        """
        self._selection_mode = mode
        if mode == 'single' and len(self._selected_items) > 1:
            # Keep only the first selected item
            first_item = next(iter(self._selected_items))
            self._selected_items = {first_item}
            self._update_ui()
            self._notify_callbacks()
    
    def add_selection_callback(self, callback: Callable):
        """
        Add a callback to be called when selection changes.
        
        Args:
            callback: Function to call with selection set
        """
        self._selection_callbacks.append(callback)
    
    def _update_ui(self):
        """Update the selection UI."""
        count = len(self._selected_items)
        
        if count == 0:
            self.count_label.config(text="No items selected")
            self._widget.pack_forget()
        else:
            if count == 1:
                self.count_label.config(text="1 item selected")
            else:
                self.count_label.config(text=f"{count} items selected")
            
            # Show selection toolbar
            self._widget.pack(fill=tk.X, pady=(5, 0))
    
    def _notify_callbacks(self):
        """Notify all selection callbacks."""
        for callback in self._selection_callbacks:
            try:
                callback(self._selected_items.copy())
            except Exception as e:
                print(f"Error in selection callback: {e}")


class BatchOperationUI(BaseComponent):
    """
    UI for performing batch operations on selected items.
    """
    
    def __init__(self, parent: tk.Widget,
                 selection_manager: SelectionManager,
                 **kwargs):
        """
        Initialize the batch operation UI.
        
        Args:
            parent: Parent widget
            selection_manager: SelectionManager instance
            **kwargs: Additional widget options
        """
        self.selection_manager = selection_manager
        self._available_operations = []
        
        super().__init__(parent, **kwargs)
        
        self._setup_batch_ui()
        
        # Connect to selection manager
        self.selection_manager.add_selection_callback(self._on_selection_change)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the batch operation UI widget."""
        # Batch operation toolbar
        toolbar = ttk.Frame(self.parent)
        return toolbar
    
    def _setup_batch_ui(self):
        """Set up the batch operation UI."""
        # Operation selector
        ttk.Label(self._widget, text="Batch Operation:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.operation_var = tk.StringVar()
        self.operation_combo = ttk.Combobox(self._widget, textvariable=self.operation_var,
                                           state="readonly", width=20)
        self.operation_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Execute button
        self.execute_btn = ttk.Button(self._widget, text="Execute",
                                     command=self._execute_batch_operation,
                                     state=tk.DISABLED)
        self.execute_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress indicator (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self._widget, variable=self.progress_var,
                                           mode='determinate', length=200)
        self.progress_bar.pack(side=tk.LEFT, padx=(10, 0))
        self.progress_bar.pack_forget()
        
        # Initially hidden
        self._widget.pack_forget()
    
    def add_operation(self, name: str, operation_func: Callable,
                     description: Optional[str] = None,
                     requires_confirmation: bool = True):
        """
        Add a batch operation.
        
        Args:
            name: Display name for the operation
            operation_func: Function to execute the operation
            description: Optional description
            requires_confirmation: Whether to show confirmation dialog
        """
        operation = {
            'name': name,
            'function': operation_func,
            'description': description,
            'requires_confirmation': requires_confirmation
        }
        self._available_operations.append(operation)
        
        # Update combobox
        operation_names = [op['name'] for op in self._available_operations]
        self.operation_combo['values'] = operation_names
    
    def _on_selection_change(self, selected_items: set):
        """Handle selection changes."""
        if selected_items:
            # Show batch operation UI
            self._widget.pack(fill=tk.X, pady=(5, 0))
            self.execute_btn.config(state=tk.NORMAL)
        else:
            # Hide batch operation UI
            self._widget.pack_forget()
    
    def _execute_batch_operation(self):
        """Execute the selected batch operation."""
        operation_name = self.operation_var.get()
        if not operation_name:
            return
        
        # Find the operation
        operation = None
        for op in self._available_operations:
            if op['name'] == operation_name:
                operation = op
                break
        
        if not operation:
            return
        
        selected_items = self.selection_manager.get_selected_items()
        if not selected_items:
            return
        
        # Show confirmation if required
        if operation['requires_confirmation']:
            from tkinter import messagebox
            result = messagebox.askyesno(
                "Confirm Batch Operation",
                f"Execute '{operation_name}' on {len(selected_items)} selected items?\n\n"
                f"{operation.get('description', '')}"
            )
            if not result:
                return
        
        # Execute operation
        self._show_progress()
        
        try:
            # *Logic placeholder*: Execute batch operation
            operation['function'](selected_items)
            
            # Simulation of progress
            self._simulate_progress()
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Batch Operation Error", f"Error executing operation: {e}")
        finally:
            self._hide_progress()
    
    def _show_progress(self):
        """Show the progress indicator."""
        self.progress_bar.pack(side=tk.LEFT, padx=(10, 0))
        self.execute_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
    
    def _hide_progress(self):
        """Hide the progress indicator."""
        self.progress_bar.pack_forget()
        self.execute_btn.config(state=tk.NORMAL)
    
    def _simulate_progress(self):
        """Simulate progress for demonstration."""
        # *Logic placeholder*: Replace with actual progress tracking
        for i in range(101):
            self.progress_var.set(i)
            self._widget.update()
            import time
            time.sleep(0.01)  # Small delay for visualization


class KeyboardNavigationManager:
    """
    Manages keyboard navigation and shortcuts across the application.
    """
    
    def __init__(self, root_widget: tk.Widget):
        """
        Initialize the keyboard navigation manager.
        
        Args:
            root_widget: Root application widget
        """
        self.root_widget = root_widget
        self._shortcuts = {}
        self._focus_order = []
        self._current_focus_index = 0
        
        self._setup_navigation()
    
    def _setup_navigation(self):
        """Set up keyboard navigation."""
        # Bind global navigation keys
        self.root_widget.bind_all('<Tab>', self._handle_tab)
        self.root_widget.bind_all('<Shift-Tab>', self._handle_shift_tab)
        self.root_widget.bind_all('<F1>', self._show_help)
        
        # Bind common shortcuts
        self.add_shortcut('Ctrl+n', self._new_action, "New")
        self.add_shortcut('Ctrl+o', self._open_action, "Open")
        self.add_shortcut('Ctrl+s', self._save_action, "Save")
        self.add_shortcut('Ctrl+z', self._undo_action, "Undo")
        self.add_shortcut('Ctrl+y', self._redo_action, "Redo")
        self.add_shortcut('F5', self._refresh_action, "Refresh")
        self.add_shortcut('Escape', self._cancel_action, "Cancel/Close")
    
    def add_shortcut(self, key_combo: str, command: Callable, 
                    description: Optional[str] = None):
        """
        Add a keyboard shortcut.
        
        Args:
            key_combo: Key combination (e.g., 'Ctrl+s', 'F5')
            command: Function to execute
            description: Optional description for help
        """
        self._shortcuts[key_combo] = {
            'command': command,
            'description': description
        }
        
        # Bind the shortcut
        self.root_widget.bind_all(f'<{key_combo}>', lambda e: command())
    
    def remove_shortcut(self, key_combo: str):
        """
        Remove a keyboard shortcut.
        
        Args:
            key_combo: Key combination to remove
        """
        if key_combo in self._shortcuts:
            del self._shortcuts[key_combo]
            self.root_widget.unbind_all(f'<{key_combo}>')
    
    def add_to_focus_order(self, widget: tk.Widget):
        """
        Add a widget to the focus order.
        
        Args:
            widget: Widget to add to focus order
        """
        self._focus_order.append(widget)
    
    def set_focus_order(self, widgets: List[tk.Widget]):
        """
        Set the complete focus order.
        
        Args:
            widgets: List of widgets in focus order
        """
        self._focus_order = widgets.copy()
    
    def _handle_tab(self, event):
        """Handle Tab key navigation."""
        if self._focus_order:
            self._current_focus_index = (self._current_focus_index + 1) % len(self._focus_order)
            widget = self._focus_order[self._current_focus_index]
            try:
                widget.focus_set()
            except tk.TclError:
                # Widget might be destroyed, skip it
                pass
    
    def _handle_shift_tab(self, event):
        """Handle Shift+Tab key navigation."""
        if self._focus_order:
            self._current_focus_index = (self._current_focus_index - 1) % len(self._focus_order)
            widget = self._focus_order[self._current_focus_index]
            try:
                widget.focus_set()
            except tk.TclError:
                # Widget might be destroyed, skip it
                pass
    
    def _show_help(self, event=None):
        """Show keyboard shortcuts help."""
        help_text = "Keyboard Shortcuts:\n\n"
        for key_combo, shortcut_info in self._shortcuts.items():
            description = shortcut_info.get('description', 'No description')
            help_text += f"{key_combo}: {description}\n"
        
        # *Logic placeholder*: Show help dialog
        from tkinter import messagebox
        messagebox.showinfo("Keyboard Shortcuts", help_text)
    
    def _new_action(self):
        """Placeholder for new action."""
        print("New action triggered")
    
    def _open_action(self):
        """Placeholder for open action."""
        print("Open action triggered")
    
    def _save_action(self):
        """Placeholder for save action."""
        print("Save action triggered")
    
    def _undo_action(self):
        """Placeholder for undo action."""
        print("Undo action triggered")
    
    def _redo_action(self):
        """Placeholder for redo action."""
        print("Redo action triggered")
    
    def _refresh_action(self):
        """Placeholder for refresh action."""
        print("Refresh action triggered")
    
    def _cancel_action(self):
        """Placeholder for cancel action."""
        print("Cancel action triggered")
    
    def get_shortcuts(self) -> Dict[str, Dict]:
        """Get all registered shortcuts."""
        return self._shortcuts.copy()


def setup_context_menu_for_widget(widget: tk.Widget, 
                                  context_menu: ContextMenu,
                                  get_context_func: Optional[Callable] = None):
    """
    Set up context menu for a widget.
    
    Args:
        widget: Widget to add context menu to
        context_menu: ContextMenu instance
        get_context_func: Optional function to get context data
    """
    def show_context_menu(event):
        try:
            context = None
            if get_context_func:
                context = get_context_func(event)
            
            context_menu.show(event.x_root, event.y_root, context)
        except Exception as e:
            print(f"Error showing context menu: {e}")
    
    # Bind right-click
    widget.bind("<Button-3>", show_context_menu)
    
    # For Mac compatibility
    widget.bind("<Button-2>", show_context_menu)
    widget.bind("<Control-Button-1>", show_context_menu)


class DragAndDropManager:
    """
    Manages drag and drop operations across UI components.
    """
    
    def __init__(self, root_widget: tk.Widget):
        """
        Initialize the drag and drop manager.
        
        Args:
            root_widget: Root application widget
        """
        self.root_widget = root_widget
        self._drag_sources = {}
        self._drop_targets = {}
        self._current_drag = None
        self._drag_preview = None
        
        self._setup_drag_drop()
    
    def _setup_drag_drop(self):
        """Set up drag and drop system."""
        # Create drag preview window (initially hidden)
        self._preview_window = tk.Toplevel(self.root_widget)
        self._preview_window.withdraw()
        self._preview_window.overrideredirect(True)
        self._preview_window.configure(bg='gray90')
        
        self._preview_label = tk.Label(self._preview_window, 
                                      text="Dragging...",
                                      bg='gray90', 
                                      relief=tk.RAISED,
                                      borderwidth=1)
        self._preview_label.pack(padx=2, pady=2)
    
    def register_drag_source(self, widget: tk.Widget, 
                           data_provider: Callable,
                           drag_type: str = 'default'):
        """
        Register a widget as a drag source.
        
        Args:
            widget: Widget that can be dragged from
            data_provider: Function that returns drag data
            drag_type: Type of drag operation
        """
        self._drag_sources[widget] = {
            'data_provider': data_provider,
            'drag_type': drag_type
        }
        
        # Bind drag events
        widget.bind('<Button-1>', lambda e: self._start_drag(e, widget))
        widget.bind('<B1-Motion>', self._on_drag_motion)
        widget.bind('<ButtonRelease-1>', self._end_drag)
    
    def register_drop_target(self, widget: tk.Widget,
                           drop_handler: Callable,
                           accepted_types: Optional[List[str]] = None):
        """
        Register a widget as a drop target.
        
        Args:
            widget: Widget that can receive drops
            drop_handler: Function to handle drop data
            accepted_types: List of accepted drag types
        """
        if accepted_types is None:
            accepted_types = ['default']
        
        self._drop_targets[widget] = {
            'drop_handler': drop_handler,
            'accepted_types': accepted_types
        }
        
        # Bind drop events
        widget.bind('<Enter>', lambda e: self._on_drag_enter(e, widget))
        widget.bind('<Leave>', lambda e: self._on_drag_leave(e, widget))
    
    def _start_drag(self, event, source_widget: tk.Widget):
        """Start a drag operation."""
        if source_widget not in self._drag_sources:
            return
        
        source_info = self._drag_sources[source_widget]
        
        # Get drag data
        try:
            drag_data = source_info['data_provider']()
            if not drag_data:
                return
        except Exception as e:
            print(f"Error getting drag data: {e}")
            return
        
        self._current_drag = {
            'source': source_widget,
            'data': drag_data,
            'type': source_info['drag_type'],
            'start_x': event.x_root,
            'start_y': event.y_root
        }
        
        # Show drag preview
        self._show_drag_preview(drag_data, event.x_root, event.y_root)
    
    def _on_drag_motion(self, event):
        """Handle drag motion."""
        if not self._current_drag:
            return
        
        # Update preview position
        if self._preview_window:
            self._preview_window.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        
        # Check for potential drop targets
        self._update_drop_feedback(event.x_root, event.y_root)
    
    def _end_drag(self, event):
        """End the drag operation."""
        if not self._current_drag:
            return
        
        # Find drop target at current position
        drop_target = self._find_drop_target_at_position(event.x_root, event.y_root)
        
        if drop_target:
            # Perform drop
            target_info = self._drop_targets[drop_target]
            
            # Check if type is accepted
            if self._current_drag['type'] in target_info['accepted_types']:
                try:
                    target_info['drop_handler'](self._current_drag['data'])
                except Exception as e:
                    print(f"Error handling drop: {e}")
        
        # Clean up
        self._hide_drag_preview()
        self._current_drag = None
    
    def _show_drag_preview(self, data: Any, x: int, y: int):
        """Show the drag preview."""
        # Update preview text
        preview_text = str(data)
        if len(preview_text) > 30:
            preview_text = preview_text[:27] + "..."
        
        self._preview_label.config(text=preview_text)
        
        # Position and show window
        self._preview_window.geometry(f"+{x + 10}+{y + 10}")
        self._preview_window.deiconify()
        self._preview_window.lift()
    
    def _hide_drag_preview(self):
        """Hide the drag preview."""
        if self._preview_window:
            self._preview_window.withdraw()
    
    def _find_drop_target_at_position(self, x: int, y: int) -> Optional[tk.Widget]:
        """Find drop target widget at screen position."""
        # Convert screen coordinates to widget-relative coordinates
        for widget in self._drop_targets:
            try:
                widget_x = widget.winfo_rootx()
                widget_y = widget.winfo_rooty()
                widget_width = widget.winfo_width()
                widget_height = widget.winfo_height()
                
                if (widget_x <= x <= widget_x + widget_width and
                    widget_y <= y <= widget_y + widget_height):
                    return widget
            except tk.TclError:
                # Widget might be destroyed
                continue
        
        return None
    
    def _on_drag_enter(self, event, target_widget: tk.Widget):
        """Handle drag entering a drop target."""
        if not self._current_drag:
            return
        
        target_info = self._drop_targets[target_widget]
        
        # Check if this target accepts the current drag type
        if self._current_drag['type'] in target_info['accepted_types']:
            # Highlight drop target
            self._highlight_drop_target(target_widget, True)
    
    def _on_drag_leave(self, event, target_widget: tk.Widget):
        """Handle drag leaving a drop target."""
        if not self._current_drag:
            return
        
        # Remove highlight
        self._highlight_drop_target(target_widget, False)
    
    def _highlight_drop_target(self, widget: tk.Widget, highlight: bool):
        """Highlight or unhighlight a drop target."""
        # *Logic placeholder*: Implement visual drop feedback
        # This could use border changes, cursor changes, or overlay indicators
        # For now, we'll use a simple print for demonstration
        if highlight:
            print(f"Drop target highlighted: {widget}")
        else:
            print(f"Drop target unhighlighted: {widget}")
        
        # Alternative implementation could use:
        # - Relief changes (raised/sunken)
        # - Cursor changes 
        # - Temporary overlay widgets
        # - Border modifications where supported
    
    def _update_drop_feedback(self, x: int, y: int):
        """Update visual feedback for current drag position."""
        # *Logic placeholder*: Add more sophisticated drop feedback
        pass


class DragDropIntegration:
    """
    Integration of drag and drop with TaskMover components.
    """
    
    def __init__(self, drag_manager: DragAndDropManager):
        """
        Initialize drag and drop integration.
        
        Args:
            drag_manager: DragAndDropManager instance
        """
        self.drag_manager = drag_manager
    
    def setup_pattern_drag_drop(self, pattern_list_widget: tk.Widget,
                               rule_editor_widget: tk.Widget):
        """
        Set up drag and drop between pattern list and rule editor.
        
        Args:
            pattern_list_widget: Widget containing patterns
            rule_editor_widget: Rule editor widget
        """
        # Register pattern list as drag source
        def get_selected_pattern():
            # *Logic placeholder*: Get selected pattern data
            return {"type": "pattern", "id": "sample_pattern", "name": "Sample Pattern"}
        
        self.drag_manager.register_drag_source(
            pattern_list_widget, 
            get_selected_pattern,
            'pattern'
        )
        
        # Register rule editor as drop target
        def handle_pattern_drop(data):
            # *Logic placeholder*: Handle pattern drop in rule editor
            print(f"Pattern dropped in rule editor: {data}")
        
        self.drag_manager.register_drop_target(
            rule_editor_widget,
            handle_pattern_drop,
            ['pattern']
        )
    
    def setup_rule_drag_drop(self, rule_list_widget: tk.Widget,
                           ruleset_editor_widget: tk.Widget):
        """
        Set up drag and drop between rule list and ruleset editor.
        
        Args:
            rule_list_widget: Widget containing rules
            ruleset_editor_widget: Ruleset editor widget
        """
        # Register rule list as drag source
        def get_selected_rule():
            # *Logic placeholder*: Get selected rule data
            return {"type": "rule", "id": "sample_rule", "name": "Sample Rule"}
        
        self.drag_manager.register_drag_source(
            rule_list_widget,
            get_selected_rule,
            'rule'
        )
        
        # Register ruleset editor as drop target
        def handle_rule_drop(data):
            # *Logic placeholder*: Handle rule drop in ruleset editor
            print(f"Rule dropped in ruleset editor: {data}")
        
        self.drag_manager.register_drop_target(
            ruleset_editor_widget,
            handle_rule_drop,
            ['rule']
        )
    
    def setup_file_drag_drop(self, file_explorer_widget: tk.Widget,
                           organization_widget: tk.Widget):
        """
        Set up drag and drop for file operations.
        
        Args:
            file_explorer_widget: File explorer widget
            organization_widget: Organization preview widget
        """
        # Register file explorer as drag source
        def get_selected_files():
            # *Logic placeholder*: Get selected files
            return {"type": "files", "paths": ["/path/to/file1.txt", "/path/to/file2.txt"]}
        
        self.drag_manager.register_drag_source(
            file_explorer_widget,
            get_selected_files,
            'files'
        )
        
        # Register organization widget as drop target
        def handle_file_drop(data):
            # *Logic placeholder*: Handle file drop for organization
            print(f"Files dropped for organization: {data}")
        
        self.drag_manager.register_drop_target(
            organization_widget,
            handle_file_drop,
            ['files']
        )
    
    def setup_priority_reordering(self, priority_list_widget: tk.Widget):
        """
        Set up drag and drop for priority reordering.
        
        Args:
            priority_list_widget: Priority list widget
        """
        # Register as both source and target for reordering
        def get_priority_item():
            # *Logic placeholder*: Get item being reordered
            return {"type": "priority_item", "id": "item_1", "priority": 5}
        
        def handle_priority_drop(data):
            # *Logic placeholder*: Handle priority reordering
            print(f"Priority item reordered: {data}")
        
        self.drag_manager.register_drag_source(
            priority_list_widget,
            get_priority_item,
            'priority_item'
        )
        
        self.drag_manager.register_drop_target(
            priority_list_widget,
            handle_priority_drop,
            ['priority_item']
        )
