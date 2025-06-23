"""
Data Display Example

Demonstrates how to display data using TaskMover UI components.
"""

import tkinter as tk

from ui.data_display_components import DataTable, ListView
from ui.layout_components import Panel, Splitter


class DataDisplayExample:
    def __init__(self, parent):
        self.parent = parent
        self.create_display()

    def create_display(self):
        # Create splitter for side-by-side display
        splitter = Splitter(self.parent, orient="horizontal")
        splitter.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel with list view
        left_panel = Panel(splitter, title="File List")
        self.create_list_view(left_panel)

        # Right panel with data table
        right_panel = Panel(splitter, title="File Details")
        self.create_data_table(right_panel)

        splitter.add(left_panel)
        splitter.add(right_panel)

    def create_list_view(self, parent):
        files = [
            "document1.pdf",
            "image1.jpg",
            "spreadsheet1.xlsx",
            "presentation1.pptx",
            "archive1.zip",
        ]

        list_view = ListView(parent, items=files)
        list_view.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_data_table(self, parent):
        data = [
            {"Name": "document1.pdf", "Size": "2.3 MB", "Modified": "2024-01-15"},
            {"Name": "image1.jpg", "Size": "1.8 MB", "Modified": "2024-01-14"},
            {"Name": "spreadsheet1.xlsx", "Size": "456 KB", "Modified": "2024-01-13"},
            {"Name": "presentation1.pptx", "Size": "5.2 MB", "Modified": "2024-01-12"},
            {"Name": "archive1.zip", "Size": "12.1 MB", "Modified": "2024-01-11"},
        ]

        table = DataTable(parent, data=data)
        table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Data Display Example")
    root.geometry("800x600")

    example = DataDisplayExample(root)
    root.mainloop()
