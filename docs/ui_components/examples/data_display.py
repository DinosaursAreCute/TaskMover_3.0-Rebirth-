"""
Data Display Example

Demonstrates data display components like tables and lists.
"""

import tkinter as tk
from tkinter import ttk

# Placeholder components
class DataTable(ttk.Treeview):
    def __init__(self, parent, columns=None, **kwargs):
        super().__init__(parent, **kwargs)
        if columns:
            self['columns'] = columns
            self['show'] = 'headings'
            for col in columns:
                self.heading(col, text=col)

class ListView(tk.Listbox):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

class Panel(tk.Frame):
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, **kwargs)
        if title:
            label = tk.Label(self, text=title, font=("Arial", 12, "bold"))
            label.pack(pady=5)

class Splitter(ttk.PanedWindow):
    def __init__(self, parent, orient=tk.HORIZONTAL, **kwargs):
        super().__init__(parent, orient=orient, **kwargs)


class DataDisplayExample:
    def __init__(self, parent):
        self.parent = parent
        self.create_data_display()

    def create_data_display(self):
        # Main splitter
        splitter = Splitter(self.parent, orient=tk.HORIZONTAL)
        splitter.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel with list
        left_panel = Panel(splitter, title="Items")
        splitter.add(left_panel)

        list_view = ListView(left_panel, height=10)
        list_view.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add some sample data
        for i in range(10):
            list_view.insert(tk.END, f"Item {i+1}")

        # Right panel with table
        right_panel = Panel(splitter, title="Details")
        splitter.add(right_panel)

        # Data table
        columns = ('Name', 'Type', 'Size')
        table = DataTable(right_panel, columns=columns)
        table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add sample data
        sample_data = [
            ('file1.txt', 'Text', '2 KB'),
            ('image.jpg', 'Image', '150 KB'),
            ('document.pdf', 'PDF', '500 KB'),
            ('music.mp3', 'Audio', '3 MB'),
            ('video.mp4', 'Video', '50 MB')
        ]
        
        for item in sample_data:
            table.insert('', tk.END, values=item)

        # Scrollbars
        table_scroll = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=table.yview)
        table.configure(yscrollcommand=table_scroll.set)
        table_scroll.pack(side=tk.RIGHT, fill=tk.Y)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Data Display Example")
    root.geometry("800x400")
    
    app = DataDisplayExample(root)
    root.mainloop()
