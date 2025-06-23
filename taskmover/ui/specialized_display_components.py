"""
TaskMover UI Framework - Specialized Display Components
"""
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional, List, Union, Dict
from .base_component import BaseComponent, ComponentState
import os
import mimetypes


class FilePreview(BaseComponent):
    """
    File preview component with support for various file types.
    """
    
    def __init__(self, parent: tk.Widget,
                 file_path: Optional[str] = None,
                 show_metadata: bool = True,
                 max_text_size: int = 1024 * 1024,  # 1MB
                 **kwargs):
        """
        Initialize the file preview.
        
        Args:
            parent: Parent widget
            file_path: Path to file to preview
            show_metadata: Whether to show file metadata
            max_text_size: Maximum text file size to preview
            **kwargs: Additional widget options
        """
        self.file_path = file_path
        self.show_metadata = show_metadata
        self.max_text_size = max_text_size
        self._current_content = None
        
        super().__init__(parent, **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the file preview structure."""
        container = ttk.Frame(self.parent)
        
        # Header with file info
        if self.show_metadata:
            self.header_frame = ttk.Frame(container)
            self.header_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            
            self.file_name_label = tk.Label(self.header_frame, text="No file selected",
                                          font=('Arial', 10, 'bold'))
            self.file_name_label.pack(side=tk.TOP, anchor='w')
            
            self.file_info_label = tk.Label(self.header_frame, text="",
                                          font=('Arial', 8), foreground='gray')
            self.file_info_label.pack(side=tk.TOP, anchor='w')
        
        # Preview area
        self.preview_frame = ttk.Frame(container)
        self.preview_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Default content
        self.default_label = tk.Label(self.preview_frame, 
                                    text="Select a file to preview",
                                    foreground='gray')
        self.default_label.pack(expand=True)
        
        # Load initial file if provided
        if self.file_path:
            self.set_file(self.file_path)
        
        return container
    
    def set_file(self, file_path: str):
        """Set the file to preview."""
        self.file_path = file_path
        
        if not os.path.exists(file_path):
            self._show_error("File not found")
            return
        
        try:
            # Update metadata
            if self.show_metadata:
                self._update_metadata()
            
            # Clear previous content
            self._clear_preview()
            
            # Determine file type and show appropriate preview
            file_type = self._get_file_type(file_path)
            
            if file_type == 'text':
                self._show_text_preview()
            elif file_type == 'image':
                self._show_image_preview()
            elif file_type == 'directory':
                self._show_directory_preview()
            else:
                self._show_binary_info()
                
        except Exception as e:
            self._show_error(f"Error loading file: {str(e)}")
    
    def _update_metadata(self):
        """Update file metadata display."""
        if not self.file_path or not os.path.exists(self.file_path):
            return
        
        file_name = os.path.basename(self.file_path)
        stat = os.stat(self.file_path)
        
        # File name
        self.file_name_label.configure(text=file_name)
        
        # File info
        if os.path.isdir(self.file_path):
            try:
                item_count = len(os.listdir(self.file_path))
                info_text = f"Directory • {item_count} items"
            except PermissionError:
                info_text = "Directory • Access denied"
        else:
            file_size = self._format_file_size(stat.st_size)
            mime_type, _ = mimetypes.guess_type(self.file_path)
            mime_info = mime_type if mime_type else "Unknown type"
            info_text = f"{file_size} • {mime_info}"
        
        self.file_info_label.configure(text=info_text)
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine the file type for preview."""
        if os.path.isdir(file_path):
            return 'directory'
        
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if mime_type:
            if mime_type.startswith('text/'):
                return 'text'
            elif mime_type.startswith('image/'):
                return 'image'
        
        # Check by extension
        ext = os.path.splitext(file_path)[1].lower()
        text_extensions = {'.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.md', '.yml', '.yaml', '.ini', '.cfg', '.log'}
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.ico'}
        
        if ext in text_extensions:
            return 'text'
        elif ext in image_extensions:
            return 'image'
        
        return 'binary'
    
    def _clear_preview(self):
        """Clear the preview area."""
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
    
    def _show_text_preview(self):
        """Show text file preview."""
        try:
            file_size = os.path.getsize(self.file_path)
            
            if file_size > self.max_text_size:
                self._show_message(f"File too large to preview ({self._format_file_size(file_size)})")
                return
            
            # Read file content
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(self.file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            # Create text widget with scrollbar
            text_frame = ttk.Frame(self.preview_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 9))
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            
            text_widget.configure(yscrollcommand=scrollbar.set)
            text_widget.insert(1.0, content)
            text_widget.configure(state='disabled')  # Read-only
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Basic syntax highlighting for common file types
            self._apply_syntax_highlighting(text_widget)
            
        except Exception as e:
            self._show_error(f"Error reading text file: {str(e)}")
    
    def _apply_syntax_highlighting(self, text_widget: tk.Text):
        """Apply basic syntax highlighting."""
        ext = os.path.splitext(self.file_path)[1].lower()
        
        # Configure text styles
        text_widget.tag_configure("keyword", foreground="blue")
        text_widget.tag_configure("string", foreground="green")
        text_widget.tag_configure("comment", foreground="gray")
        
        # Very basic highlighting for Python files
        if ext == '.py':
            content = text_widget.get(1.0, tk.END)
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                line_start = f"{i+1}.0"
                
                # Highlight comments
                if '#' in line:
                    comment_start = line.find('#')
                    start_pos = f"{i+1}.{comment_start}"
                    end_pos = f"{i+1}.{len(line)}"
                    text_widget.tag_add("comment", start_pos, end_pos)
                
                # Highlight keywords (very basic)
                keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'import', 'from', 'return']
                for keyword in keywords:
                    start_idx = 0
                    while True:
                        start_idx = line.find(keyword, start_idx)
                        if start_idx == -1:
                            break
                        
                        # Check if it's a whole word
                        if (start_idx == 0 or not line[start_idx-1].isalnum()) and \
                           (start_idx + len(keyword) >= len(line) or not line[start_idx + len(keyword)].isalnum()):
                            start_pos = f"{i+1}.{start_idx}"
                            end_pos = f"{i+1}.{start_idx + len(keyword)}"
                            text_widget.tag_add("keyword", start_pos, end_pos)
                        
                        start_idx += len(keyword)
    
    def _show_image_preview(self):
        """Show image file preview."""
        try:
            # For now, just show a placeholder
            # In a real implementation, you would use PIL/Pillow to load and display the image
            self._show_message(f"Image preview: {os.path.basename(self.file_path)}\n(Image preview requires PIL/Pillow library)")
            
            # TODO: Implement actual image preview with PIL
            # from PIL import Image, ImageTk
            # image = Image.open(self.file_path)
            # # Resize if too large
            # photo = ImageTk.PhotoImage(image)
            # label = tk.Label(self.preview_frame, image=photo)
            # label.image = photo  # Keep a reference
            # label.pack(expand=True)
            
        except Exception as e:
            self._show_error(f"Error loading image: {str(e)}")
    
    def _show_directory_preview(self):
        """Show directory contents preview."""
        try:
            items = os.listdir(self.file_path)
            items.sort()
            
            # Create listbox for directory contents
            list_frame = ttk.Frame(self.preview_frame)
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            listbox = tk.Listbox(list_frame)
            scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
            
            listbox.configure(yscrollcommand=scrollbar.set)
            
            # Add items
            for item in items:
                item_path = os.path.join(self.file_path, item)
                if os.path.isdir(item_path):
                    listbox.insert(tk.END, f"📁 {item}")
                else:
                    listbox.insert(tk.END, f"📄 {item}")
            
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
        except PermissionError:
            self._show_error("Access denied")
        except Exception as e:
            self._show_error(f"Error reading directory: {str(e)}")
    
    def _show_binary_info(self):
        """Show information about binary files."""
        try:
            file_size = os.path.getsize(self.file_path)
            ext = os.path.splitext(self.file_path)[1].lower()
            
            info_text = f"Binary file\nSize: {self._format_file_size(file_size)}\nExtension: {ext or 'None'}\n\nThis file type cannot be previewed."
            
            self._show_message(info_text)
            
        except Exception as e:
            self._show_error(f"Error reading file info: {str(e)}")
    
    def _show_message(self, message: str):
        """Show a message in the preview area."""
        label = tk.Label(self.preview_frame, text=message, 
                        justify=tk.CENTER, foreground='gray')
        label.pack(expand=True)
    
    def _show_error(self, error_message: str):
        """Show an error message in the preview area."""
        label = tk.Label(self.preview_frame, text=error_message, 
                        justify=tk.CENTER, foreground='red')
        label.pack(expand=True)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def clear(self):
        """Clear the preview."""
        self.file_path = None
        self._clear_preview()
        
        if self.show_metadata:
            self.file_name_label.configure(text="No file selected")
            self.file_info_label.configure(text="")
        
        self.default_label = tk.Label(self.preview_frame, 
                                    text="Select a file to preview",
                                    foreground='gray')
        self.default_label.pack(expand=True)


class PropertyGrid(BaseComponent):
    """
    Property grid component for editing object properties.
    """
    
    def __init__(self, parent: tk.Widget,
                 properties: Dict[str, Any] = None,
                 categories: Dict[str, List[str]] = None,
                 property_types: Dict[str, str] = None,
                 readonly_properties: List[str] = None,
                 **kwargs):
        """
        Initialize the property grid.
        
        Args:
            parent: Parent widget
            properties: Property values dictionary
            categories: Property categories
            property_types: Property type definitions
            readonly_properties: List of readonly property names
            **kwargs: Additional widget options
        """
        self.properties = properties or {}
        self.categories = categories or {}
        self.property_types = property_types or {}
        self.readonly_properties = readonly_properties or []
        
        self._property_widgets = {}
        self._category_frames = {}
        self._expanded_categories = set()
        
        super().__init__(parent, **kwargs)
    
    def _create_widget(self, **kwargs) -> tk.Widget:
        """Create the property grid structure."""
        container = ttk.Frame(self.parent)
        
        # Search bar
        search_frame = ttk.Frame(container)
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_changed)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Property grid with scrollbar
        grid_frame = ttk.Frame(container)
        grid_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(grid_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.canvas.yview)
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
        
        # Build property grid
        self._build_property_grid()
        
        return container
    
    def _build_property_grid(self):
        """Build the property grid widgets."""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self._property_widgets.clear()
        self._category_frames.clear()
        
        # Group properties by category
        categorized_props = {}
        uncategorized_props = {}
        
        for prop_name, prop_value in self.properties.items():
            category = self._get_property_category(prop_name)
            if category:
                if category not in categorized_props:
                    categorized_props[category] = {}
                categorized_props[category][prop_name] = prop_value
            else:
                uncategorized_props[prop_name] = prop_value
        
        # Create category sections
        for category, props in categorized_props.items():
            self._create_category_section(category, props)
        
        # Create uncategorized properties
        if uncategorized_props:
            self._create_category_section("General", uncategorized_props)
    
    def _create_category_section(self, category: str, properties: Dict[str, Any]):
        """Create a category section with properties."""
        # Category header
        category_frame = ttk.LabelFrame(self.scrollable_frame, text=category, padding=5)
        category_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        self._category_frames[category] = category_frame
        
        # Properties in this category
        for prop_name, prop_value in properties.items():
            self._create_property_widget(category_frame, prop_name, prop_value)
    
    def _create_property_widget(self, parent: tk.Widget, prop_name: str, prop_value: Any):
        """Create a widget for a single property."""
        prop_frame = ttk.Frame(parent)
        prop_frame.pack(side=tk.TOP, fill=tk.X, pady=1)
        
        # Property label
        label = tk.Label(prop_frame, text=prop_name, width=20, anchor='w')
        label.pack(side=tk.LEFT)
        
        # Property editor based on type
        prop_type = self.property_types.get(prop_name, self._infer_property_type(prop_value))
        readonly = prop_name in self.readonly_properties
        
        editor_widget = self._create_property_editor(prop_frame, prop_name, prop_value, prop_type, readonly)
        editor_widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        self._property_widgets[prop_name] = {
            'frame': prop_frame,
            'label': label,
            'editor': editor_widget,
            'type': prop_type
        }
    
    def _create_property_editor(self, parent: tk.Widget, prop_name: str, prop_value: Any, 
                              prop_type: str, readonly: bool) -> tk.Widget:
        """Create the appropriate editor widget for a property."""
        if readonly:
            # Read-only label
            widget = tk.Label(parent, text=str(prop_value), relief='sunken', anchor='w')
            return widget
        
        if prop_type == 'bool':
            # Checkbox for boolean
            var = tk.BooleanVar(value=bool(prop_value))
            widget = ttk.Checkbutton(parent, variable=var, 
                                   command=lambda: self._on_property_changed(prop_name, var.get()))
            widget._var = var  # Keep reference
            return widget
        
        elif prop_type == 'int':
            # Spinbox for integers
            var = tk.IntVar(value=int(prop_value) if prop_value is not None else 0)
            widget = ttk.Spinbox(parent, from_=-999999, to=999999, textvariable=var)
            widget.bind('<FocusOut>', lambda e: self._on_property_changed(prop_name, var.get()))
            widget._var = var
            return widget
        
        elif prop_type == 'float':
            # Entry for floats
            var = tk.DoubleVar(value=float(prop_value) if prop_value is not None else 0.0)
            widget = ttk.Entry(parent, textvariable=var)
            widget.bind('<FocusOut>', lambda e: self._on_property_changed(prop_name, var.get()))
            widget._var = var
            return widget
        
        elif prop_type == 'choice':
            # Combobox for choices
            # This would need to be configured with available choices
            widget = ttk.Combobox(parent, values=['Option 1', 'Option 2', 'Option 3'])
            widget.set(str(prop_value))
            widget.bind('<<ComboboxSelected>>', lambda e: self._on_property_changed(prop_name, widget.get()))
            return widget
        
        elif prop_type == 'color':
            # Color picker (simplified)
            widget = ttk.Button(parent, text=str(prop_value),
                              command=lambda: self._choose_color(prop_name))
            return widget
        
        elif prop_type == 'file':
            # File picker
            frame = ttk.Frame(parent)
            entry = ttk.Entry(frame, text=str(prop_value))
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            button = ttk.Button(frame, text="...", width=3,
                              command=lambda: self._choose_file(prop_name, entry))
            button.pack(side=tk.RIGHT)
            return frame
        
        else:
            # Default: text entry
            var = tk.StringVar(value=str(prop_value))
            widget = ttk.Entry(parent, textvariable=var)
            widget.bind('<FocusOut>', lambda e: self._on_property_changed(prop_name, var.get()))
            widget._var = var
            return widget
    
    def _infer_property_type(self, value: Any) -> str:
        """Infer property type from value."""
        if isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        else:
            return 'string'
    
    def _get_property_category(self, prop_name: str) -> Optional[str]:
        """Get the category for a property."""
        for category, props in self.categories.items():
            if prop_name in props:
                return category
        return None
    
    def _on_property_changed(self, prop_name: str, new_value: Any):
        """Handle property value changes."""
        self.properties[prop_name] = new_value
        self.trigger_event('property_changed', {'property': prop_name, 'value': new_value})
    
    def _on_search_changed(self, *args):
        """Handle search filter changes."""
        search_text = self.search_var.get().lower()
        
        # Show/hide properties based on search
        for prop_name, widget_info in self._property_widgets.items():
            if not search_text or search_text in prop_name.lower():
                widget_info['frame'].pack(side=tk.TOP, fill=tk.X, pady=1)
            else:
                widget_info['frame'].pack_forget()
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _choose_color(self, prop_name: str):
        """Open color chooser dialog."""
        from tkinter import colorchooser
        color = colorchooser.askcolor(title=f"Choose color for {prop_name}")
        if color[1]:  # If a color was selected
            self._on_property_changed(prop_name, color[1])
    
    def _choose_file(self, prop_name: str, entry_widget: ttk.Entry):
        """Open file chooser dialog."""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(title=f"Choose file for {prop_name}")
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
            self._on_property_changed(prop_name, filename)
    
    def set_properties(self, properties: Dict[str, Any]):
        """Update all properties."""
        self.properties = properties
        self._build_property_grid()
    
    def get_property(self, prop_name: str) -> Any:
        """Get a property value."""
        return self.properties.get(prop_name)
    
    def set_property(self, prop_name: str, value: Any):
        """Set a property value."""
        self.properties[prop_name] = value
        
        # Update widget if it exists
        if prop_name in self._property_widgets:
            widget_info = self._property_widgets[prop_name]
            editor = widget_info['editor']
            
            if hasattr(editor, '_var'):
                editor._var.set(value)
            elif hasattr(editor, 'set'):
                editor.set(str(value))
    
    def add_property(self, prop_name: str, value: Any, category: str = None, prop_type: str = None):
        """Add a new property."""
        self.properties[prop_name] = value
        
        if category:
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(prop_name)
        
        if prop_type:
            self.property_types[prop_name] = prop_type
        
        self._build_property_grid()
    
    def remove_property(self, prop_name: str):
        """Remove a property."""
        if prop_name in self.properties:
            del self.properties[prop_name]
        
        # Remove from categories
        for category, props in self.categories.items():
            if prop_name in props:
                props.remove(prop_name)
                break
        
        if prop_name in self.property_types:
            del self.property_types[prop_name]
        
        self._build_property_grid()
