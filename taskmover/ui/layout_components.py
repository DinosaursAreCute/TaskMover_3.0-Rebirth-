"""
TaskMover UI Framework - Layout Components
"""
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional, List, Union, Dict
from .base_component import BaseComponent, ComponentState


class MainWindow(BaseComponent):
    """
    Application main window container with state management.
    """
    
    def __init__(self, parent: Optional[tk.Widget] = None,
                 title: str = "TaskMover",
                 size: tuple = (1200, 800),
                 min_size: tuple = (800, 600),
                 position: Optional[tuple] = None,
                 resizable: bool = True,
                 **kwargs):
        """
        Initialize the main window.
        
        Args:
            parent: Parent widget (None for root window)
            title: Window title
            size: Initial window size (width, height)
            min_size: Minimum window size
            position: Initial position (x, y)
            resizable: Whether window is resizable
            **kwargs: Additional widget options
        """
        self.title = title
        self.size = size
        self.min_size = min_size
        self.position = position
        self.resizable = resizable
        self._window_state = "normal"  # normal, minimized, maximized
        self._menu_bar = None
        self._status_bar = None
        self._shortcuts = {}
        
        # Create root window if no parent provided
        if parent is None:
            parent = tk.Tk()
            
        super().__init__(parent, **kwargs)
        
        self._setup_window()
        self._setup_shortcuts()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the main window structure."""
        # If parent is the root window, configure it directly
        if isinstance(self.parent, tk.Tk):
            window = self.parent
        else:
            window = tk.Toplevel(self.parent)
        
        # Configure window
        window.title(self.title)
        window.geometry(f"{self.size[0]}x{self.size[1]}")
        window.minsize(self.min_size[0], self.min_size[1])
        window.resizable(self.resizable, self.resizable)
        
        if self.position:
            window.geometry(f"{self.size[0]}x{self.size[1]}+{self.position[0]}+{self.position[1]}")
        
        # Main container frame
        self.main_container = ttk.Frame(window)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        return window
    
    def _setup_window(self):
        """Setup window event handlers and state management."""
        self.widget.protocol("WM_DELETE_WINDOW", self._on_close)
        self.widget.bind("<Configure>", self._on_configure)
        
        # LOGIC INTEGRATION POINT: Window state persistence
        # self._load_window_state()
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Default shortcuts
        self.add_shortcut("Ctrl+q", self._on_close)
        self.add_shortcut("F11", self._toggle_fullscreen)
        self.add_shortcut("Alt+F4", self._on_close)
        
        # LOGIC INTEGRATION POINT: Application-specific shortcuts
        # self._setup_app_shortcuts()
    
    def _on_close(self):
        """Handle window close event."""
        # LOGIC INTEGRATION POINT: Save application state before closing
        # self._save_application_state()
        
        self.trigger_event('window_closing')
        self.widget.quit()
    
    def _on_configure(self, event):
        """Handle window configuration changes."""
        if event.widget == self.widget:
            # Track window state changes
            current_state = self.widget.state()
            if current_state != self._window_state:
                self._window_state = current_state
                self.trigger_event('window_state_changed', current_state)
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        current = self.widget.attributes('-fullscreen')
        self.widget.attributes('-fullscreen', not current)
    
    def add_shortcut(self, key_sequence: str, callback: Callable):
        """Add a keyboard shortcut."""
        self._shortcuts[key_sequence] = callback
        self.widget.bind_all(f"<{key_sequence}>", lambda e: callback())
    
    def remove_shortcut(self, key_sequence: str):
        """Remove a keyboard shortcut."""
        if key_sequence in self._shortcuts:
            self.widget.unbind_all(f"<{key_sequence}>")
            del self._shortcuts[key_sequence]
    
    def set_menu_bar(self, menu_bar):
        """Set the window menu bar."""
        self._menu_bar = menu_bar
        self.widget.config(menu=menu_bar)
    
    def set_status_bar(self, status_bar):
        """Set the window status bar."""
        if self._status_bar:
            self._status_bar.destroy()
        
        self._status_bar = status_bar
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def get_window_state(self) -> dict:
        """Get current window state for persistence."""
        geometry = self.widget.geometry()
        return {
            'geometry': geometry,
            'state': self._window_state,
            'position': (self.widget.winfo_x(), self.widget.winfo_y()),
            'size': (self.widget.winfo_width(), self.widget.winfo_height())
        }
    
    def restore_window_state(self, state: dict):
        """Restore window state from saved data."""
        if 'geometry' in state:
            self.widget.geometry(state['geometry'])
        if 'state' in state:
            self.widget.state(state['state'])


class Sidebar(BaseComponent):
    """
    Collapsible sidebar container for navigation.
    """
    
    def __init__(self, parent: tk.Widget,
                 width: int = 250,
                 min_width: int = 50,
                 collapsible: bool = True,
                 position: str = "left",  # left, right
                 auto_collapse: bool = False,
                 **kwargs):
        """
        Initialize the sidebar.
        
        Args:
            parent: Parent widget
            width: Sidebar width
            min_width: Minimum width when collapsed
            collapsible: Whether sidebar can be collapsed
            position: Sidebar position
            auto_collapse: Auto-collapse on small screens
            **kwargs: Additional widget options
        """
        self.width = width
        self.min_width = min_width
        self.collapsible = collapsible
        self.position = position
        self.auto_collapse = auto_collapse
        self._collapsed = False
        self._sections = []
        
        super().__init__(parent, **kwargs)
        
        if self.auto_collapse:
            self._setup_auto_collapse()
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the sidebar structure."""
        # Main sidebar container
        container = ttk.Frame(self.parent)
        
        # Header section
        self.header = ttk.Frame(container, height=40)
        self.header.pack(side=tk.TOP, fill=tk.X)
        self.header.pack_propagate(False)
        
        # Collapse/expand button
        if self.collapsible:
            self.toggle_btn = ttk.Button(self.header, 
                                       text="◀" if self.position == "left" else "▶",
                                       width=3,
                                       command=self._toggle_collapse)
            
            if self.position == "left":
                self.toggle_btn.pack(side=tk.RIGHT, pady=5, padx=5)
            else:
                self.toggle_btn.pack(side=tk.LEFT, pady=5, padx=5)
        
        # Content area
        self.content = ttk.Frame(container)
        self.content.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Resize handle
        self.resize_handle = ttk.Frame(container, width=3, cursor="sb_h_double_arrow")
        
        if self.position == "left":
            self.resize_handle.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            self.resize_handle.pack(side=tk.LEFT, fill=tk.Y)
        
        self._setup_resize()
        
        return container
    
    def _setup_resize(self):
        """Setup resize handle functionality."""
        self.resize_handle.bind("<Button-1>", self._start_resize)
        self.resize_handle.bind("<B1-Motion>", self._do_resize)
        self.resize_handle.bind("<ButtonRelease-1>", self._end_resize)
        
        self._resizing = False
        self._resize_start_x = 0
    
    def _start_resize(self, event):
        """Start resize operation."""
        self._resizing = True
        self._resize_start_x = event.x_root
        self._initial_width = self.widget.winfo_width()
    
    def _do_resize(self, event):
        """Handle resize drag."""
        if not self._resizing:
            return
        
        delta = event.x_root - self._resize_start_x
        
        if self.position == "right":
            delta = -delta
        
        new_width = max(self.min_width, self._initial_width + delta)
        self.width = new_width
        
        # Update width
        self.widget.configure(width=new_width)
    
    def _end_resize(self, event):
        """End resize operation."""
        self._resizing = False
    
    def _toggle_collapse(self):
        """Toggle sidebar collapse state."""
        if self._collapsed:
            self.expand()
        else:
            self.collapse()
    
    def collapse(self):
        """Collapse the sidebar."""
        if not self.collapsible or self._collapsed:
            return
        
        self._collapsed = True
        self._stored_width = self.width
        
        # Update UI
        self.widget.configure(width=self.min_width)
        
        if hasattr(self, 'toggle_btn'):
            self.toggle_btn.configure(text="▶" if self.position == "left" else "◀")
        
        # Hide content sections
        for section in self._sections:
            if hasattr(section, 'content_frame'):
                section['content_frame'].pack_forget()
        
        self.trigger_event('sidebar_collapsed')
    
    def expand(self):
        """Expand the sidebar."""
        if not self._collapsed:
            return
        
        self._collapsed = False
        
        # Restore width
        restore_width = getattr(self, '_stored_width', self.width)
        self.widget.configure(width=restore_width)
        
        if hasattr(self, 'toggle_btn'):
            self.toggle_btn.configure(text="◀" if self.position == "left" else "▶")
        
        # Show content sections
        for section in self._sections:
            if hasattr(section, 'content_frame'):
                section['content_frame'].pack(side=tk.TOP, fill=tk.X, before=section.get('next_section'))
        
        self.trigger_event('sidebar_expanded')
    
    def add_section(self, title: str, content_widget: tk.Widget = None) -> dict:
        """Add a section to the sidebar."""
        section_frame = ttk.LabelFrame(self.content, text=title, padding=5)
        section_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        if content_widget:
            content_widget.pack(in_=section_frame, fill=tk.BOTH, expand=True)
        
        section = {
            'title': title,
            'frame': section_frame,
            'content_frame': content_widget
        }
        
        self._sections.append(section)
        return section
    
    def remove_section(self, title: str):
        """Remove a section from the sidebar."""
        section = next((s for s in self._sections if s['title'] == title), None)
        if section:
            section['frame'].destroy()
            self._sections.remove(section)
    
    def _setup_auto_collapse(self):
        """Setup auto-collapse functionality."""
        def check_window_size():
            if hasattr(self.parent, 'winfo_width'):
                window_width = self.parent.winfo_width()
                if window_width < 800 and not self._collapsed:
                    self.collapse()
                elif window_width >= 800 and self._collapsed:
                    self.expand()
            
            # Schedule next check
            self.widget.after(1000, check_window_size)
        
        # Start checking
        self.widget.after(1000, check_window_size)


class TabContainer(BaseComponent):
    """
    Tab container with closeable and reorderable tabs.
    """
    
    def __init__(self, parent: tk.Widget,
                 closeable_tabs: bool = True,
                 reorderable: bool = True,
                 show_add_button: bool = True,
                 max_tabs: Optional[int] = None,
                 **kwargs):
        """
        Initialize the tab container.
        
        Args:
            parent: Parent widget
            closeable_tabs: Whether tabs can be closed
            reorderable: Whether tabs can be reordered
            show_add_button: Whether to show "add new tab" button
            max_tabs: Maximum number of tabs allowed
            **kwargs: Additional widget options
        """
        self.closeable_tabs = closeable_tabs
        self.reorderable = reorderable
        self.show_add_button = show_add_button
        self.max_tabs = max_tabs
        self._tabs = []
        self._active_tab = None
        
        super().__init__(parent, **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the tab container structure."""
        container = ttk.Frame(self.parent)
        
        # Tab header area
        self.tab_header = ttk.Frame(container, height=35)
        self.tab_header.pack(side=tk.TOP, fill=tk.X)
        self.tab_header.pack_propagate(False)
        
        # Tab content area
        self.tab_content = ttk.Frame(container)
        self.tab_content.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Add new tab button
        if self.show_add_button:
            self.add_tab_btn = ttk.Button(self.tab_header, text="+", width=3,
                                        command=self._on_add_tab_clicked)
            self.add_tab_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        return container
    
    def add_tab(self, title: str, content: tk.Widget = None, tab_id: str = None) -> str:
        """Add a new tab."""
        if self.max_tabs and len(self._tabs) >= self.max_tabs:
            return None
        
        if tab_id is None:
            tab_id = f"tab_{len(self._tabs)}"
        
        # Create tab button
        tab_frame = ttk.Frame(self.tab_header)
        
        tab_button = ttk.Button(tab_frame, text=title,
                              command=lambda: self.activate_tab(tab_id))
        tab_button.pack(side=tk.LEFT)
        
        # Close button
        if self.closeable_tabs:
            close_btn = ttk.Button(tab_frame, text="×", width=2,
                                 command=lambda: self.close_tab(tab_id))
            close_btn.pack(side=tk.RIGHT)
        
        tab_frame.pack(side=tk.LEFT, padx=1, pady=2)
        
        # Create content frame
        if content is None:
            content = ttk.Frame(self.tab_content)
        
        # Tab data
        tab = {
            'id': tab_id,
            'title': title,
            'button': tab_button,
            'frame': tab_frame,
            'content': content,
            'closeable': self.closeable_tabs
        }
        
        self._tabs.append(tab)
        
        # Activate if first tab
        if len(self._tabs) == 1:
            self.activate_tab(tab_id)
        
        self.trigger_event('tab_added', tab)
        return tab_id
    
    def close_tab(self, tab_id: str):
        """Close a tab."""
        tab = self._get_tab_by_id(tab_id)
        if not tab or not tab.get('closeable', True):
            return
        
        # Trigger close event (can be cancelled)
        if not self.trigger_event('tab_closing', tab):
            return
        
        # Remove from list
        self._tabs.remove(tab)
        
        # Destroy UI elements
        tab['frame'].destroy()
        tab['content'].destroy()
        
        # If this was the active tab, activate another
        if self._active_tab == tab_id:
            if self._tabs:
                self.activate_tab(self._tabs[0]['id'])
            else:
                self._active_tab = None
        
        self.trigger_event('tab_closed', tab)
    
    def activate_tab(self, tab_id: str):
        """Activate a specific tab."""
        tab = self._get_tab_by_id(tab_id)
        if not tab:
            return
        
        # Deactivate current tab
        if self._active_tab:
            current_tab = self._get_tab_by_id(self._active_tab)
            if current_tab:
                current_tab['content'].pack_forget()
                current_tab['button'].state(['!pressed'])
        
        # Activate new tab
        self._active_tab = tab_id
        tab['content'].pack(in_=self.tab_content, fill=tk.BOTH, expand=True)
        tab['button'].state(['pressed'])
        
        self.trigger_event('tab_activated', tab)
    
    def get_active_tab_id(self) -> Optional[str]:
        """Get the active tab ID."""
        return self._active_tab
    
    def get_tab_content(self, tab_id: str) -> Optional[tk.Widget]:
        """Get the content widget for a tab."""
        tab = self._get_tab_by_id(tab_id)
        return tab['content'] if tab else None
    
    def set_tab_title(self, tab_id: str, title: str):
        """Update tab title."""
        tab = self._get_tab_by_id(tab_id)
        if tab:
            tab['title'] = title
            tab['button'].configure(text=title)
    
    def _get_tab_by_id(self, tab_id: str) -> Optional[dict]:
        """Get tab data by ID."""
        return next((tab for tab in self._tabs if tab['id'] == tab_id), None)
    
    def _on_add_tab_clicked(self):
        """Handle add tab button click."""
        # LOGIC INTEGRATION POINT: Create new tab content
        self.trigger_event('add_tab_requested')


class Panel(BaseComponent):
    """
    Resizable panel component with docking and state persistence.
    """
    
    def __init__(self, parent: tk.Widget,
                 title: str = "Panel",
                 resizable: bool = True,
                 collapsible: bool = True,
                 dockable: bool = False,
                 min_size: tuple = (200, 150),
                 **kwargs):
        """
        Initialize the panel.
        
        Args:
            parent: Parent widget
            title: Panel title
            resizable: Whether panel can be resized
            collapsible: Whether panel can be collapsed
            dockable: Whether panel supports docking
            min_size: Minimum panel size
            **kwargs: Additional widget options
        """
        self.title = title
        self.resizable = resizable
        self.collapsible = collapsible
        self.dockable = dockable
        self.min_size = min_size
        self._collapsed = False
        self._maximized = False
        self._stored_size = None
        
        super().__init__(parent, **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the panel structure."""
        container = ttk.Frame(self.parent, relief="raised", borderwidth=1)
        
        # Header
        self.header = ttk.Frame(container, height=30)
        self.header.pack(side=tk.TOP, fill=tk.X)
        self.header.pack_propagate(False)
        
        # Title label
        self.title_label = tk.Label(self.header, text=self.title, 
                                  font=('Arial', 9, 'bold'))
        self.title_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(self.header)
        button_frame.pack(side=tk.RIGHT, padx=2)
        
        if self.collapsible:
            self.collapse_btn = ttk.Button(button_frame, text="−", width=2,
                                         command=self._toggle_collapse)
            self.collapse_btn.pack(side=tk.RIGHT, padx=1)
        
        self.maximize_btn = ttk.Button(button_frame, text="□", width=2,
                                     command=self._toggle_maximize)
        self.maximize_btn.pack(side=tk.RIGHT, padx=1)
        
        # Content area
        self.content = ttk.Frame(container)
        self.content.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Resize handles (if resizable)
        if self.resizable:
            self._create_resize_handles(container)
        
        return container
    
    def _create_resize_handles(self, container):
        """Create resize handles for the panel."""
        # Bottom-right corner handle
        self.resize_handle = tk.Frame(container, width=10, height=10,
                                    cursor="bottom_right_corner",
                                    bg='gray')
        self.resize_handle.place(relx=1.0, rely=1.0, anchor='se')
        
        # Bind resize events
        self.resize_handle.bind("<Button-1>", self._start_resize)
        self.resize_handle.bind("<B1-Motion>", self._do_resize)
        self.resize_handle.bind("<ButtonRelease-1>", self._end_resize)
        
        self._resizing = False
    
    def _start_resize(self, event):
        """Start resize operation."""
        self._resizing = True
        self._resize_start_x = event.x_root
        self._resize_start_y = event.y_root
        self._initial_width = self.widget.winfo_width()
        self._initial_height = self.widget.winfo_height()
    
    def _do_resize(self, event):
        """Handle resize drag."""
        if not self._resizing:
            return
        
        delta_x = event.x_root - self._resize_start_x
        delta_y = event.y_root - self._resize_start_y
        
        new_width = max(self.min_size[0], self._initial_width + delta_x)
        new_height = max(self.min_size[1], self._initial_height + delta_y)
        
        self.widget.configure(width=new_width, height=new_height)
    
    def _end_resize(self, event):
        """End resize operation."""
        self._resizing = False
        self.trigger_event('panel_resized')
    
    def _toggle_collapse(self):
        """Toggle panel collapse state."""
        if self._collapsed:
            self.expand()
        else:
            self.collapse()
    
    def collapse(self):
        """Collapse the panel."""
        if self._collapsed:
            return
        
        self._collapsed = True
        self._stored_size = (self.widget.winfo_width(), self.widget.winfo_height())
        
        # Hide content
        self.content.pack_forget()
        
        # Update collapse button
        if hasattr(self, 'collapse_btn'):
            self.collapse_btn.configure(text="+")
        
        self.trigger_event('panel_collapsed')
    
    def expand(self):
        """Expand the panel."""
        if not self._collapsed:
            return
        
        self._collapsed = False
        
        # Show content
        self.content.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Restore size if stored
        if self._stored_size:
            self.widget.configure(width=self._stored_size[0], height=self._stored_size[1])
        
        # Update collapse button
        if hasattr(self, 'collapse_btn'):
            self.collapse_btn.configure(text="−")
        
        self.trigger_event('panel_expanded')
    
    def _toggle_maximize(self):
        """Toggle panel maximize state."""
        if self._maximized:
            self.restore()
        else:
            self.maximize()
    
    def maximize(self):
        """Maximize the panel."""
        if self._maximized:
            return
        
        self._maximized = True
        self._stored_size = (self.widget.winfo_width(), self.widget.winfo_height())
        
        # Fill parent container
        self.widget.pack(fill=tk.BOTH, expand=True)
        
        # Update maximize button
        self.maximize_btn.configure(text="◱")
        
        self.trigger_event('panel_maximized')
    
    def restore(self):
        """Restore panel from maximized state."""
        if not self._maximized:
            return
        
        self._maximized = False
        
        # Restore original packing
        # This would need to be implemented based on the original layout
        
        # Update maximize button
        self.maximize_btn.configure(text="□")
        
        self.trigger_event('panel_restored')
    
    def set_content(self, content_widget: tk.Widget):
        """Set the panel content."""
        # Clear existing content
        for child in self.content.winfo_children():
            child.destroy()
        
        # Add new content
        content_widget.pack(in_=self.content, fill=tk.BOTH, expand=True)
    
    def get_content_frame(self) -> tk.Widget:
        """Get the content frame for adding widgets."""
        return self.content
