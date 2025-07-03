"""
Advanced Features Example

Demonstrates advanced UI features like drag & drop, multi-selection, etc.
"""

import tkinter as tk

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

try:
    from taskmover.ui.base_component import ModernButton as TaskMoverButton
    COMPONENTS_AVAILABLE = True
except ImportError:
    print("Warning: Custom components not available, using placeholders")
    COMPONENTS_AVAILABLE = False

from tkinter import messagebox


# Placeholder classes for demonstration
class DragDropManager:
    """Placeholder for drag & drop functionality."""
    def make_draggable(self, widget):
        print(f"Making {widget} draggable")
    
    def make_drop_target(self, widget, callback):
        print(f"Making {widget} a drop target")


class MultiSelectionManager:
    """Placeholder for multi-selection functionality."""
    def enable_multi_selection(self, widget):
        print(f"Enabling multi-selection for {widget}")


class CustomButton(tk.Button):
    """Custom button placeholder."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)


class AdvancedFeaturesExample:
    def __init__(self, parent):
        self.parent = parent
        self.create_advanced_demo()

    def create_advanced_demo(self):
        # Main panel
        # Create main container
        main_panel = tk.Frame(self.parent)
        main_panel.pack(fill="both", expand=True, padx=20, pady=20)
        main_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Drag & Drop demo
        self.create_drag_drop_demo(main_panel)

        # Multi-selection demo
        self.create_multi_selection_demo(main_panel)

        # Keyboard navigation demo
        self.create_keyboard_nav_demo(main_panel)

    def create_drag_drop_demo(self, parent):
        # Drag & Drop section
        dd_frame = tk.LabelFrame(parent, text="Drag & Drop Demo", padx=10, pady=10)
        dd_frame.pack(fill=tk.X, pady=10)

        # Source area
        source_frame = tk.Frame(dd_frame, bg="lightblue", height=100)
        source_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        source_frame.pack_propagate(False)

        tk.Label(source_frame, text="Drag from here", bg="lightblue").pack(expand=True)

        # Target area
        target_frame = tk.Frame(dd_frame, bg="lightgreen", height=100)
        target_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        target_frame.pack_propagate(False)

        tk.Label(target_frame, text="Drop here", bg="lightgreen").pack(expand=True)

        # Initialize drag & drop
        dd_manager = DragDropManager()
        dd_manager.make_draggable(source_frame)
        dd_manager.make_drop_target(target_frame, self.on_drop)

    def create_multi_selection_demo(self, parent):
        # Multi-selection section
        ms_frame = tk.LabelFrame(parent, text="Multi-Selection Demo", padx=10, pady=10)
        ms_frame.pack(fill=tk.X, pady=10)

        # List with multi-selection
        listbox = tk.Listbox(ms_frame, selectmode=tk.EXTENDED, height=6)
        listbox.pack(fill=tk.X, pady=5)

        for i in range(10):
            listbox.insert(tk.END, f"Selectable Item {i+1}")

        # Selection manager
        ms_manager = MultiSelectionManager()
        ms_manager.enable_multi_selection(listbox)

        # Button to get selected items
        get_selection_btn = CustomButton(
            ms_frame,
            text="Get Selected Items",
            command=lambda: self.show_selection(listbox),
        )
        get_selection_btn.pack(pady=5)

    def create_keyboard_nav_demo(self, parent):
        # Keyboard navigation section
        kb_frame = tk.LabelFrame(
            parent, text="Keyboard Navigation Demo", padx=10, pady=10
        )
        kb_frame.pack(fill=tk.X, pady=10)

        # Info label
        info_label = tk.Label(
            kb_frame,
            text="Use Tab/Shift+Tab to navigate, Enter/Space to activate",
            fg="blue",
        )
        info_label.pack(pady=5)

        # Navigable buttons
        button_frame = tk.Frame(kb_frame)
        button_frame.pack(pady=5)

        for i in range(3):
            btn = CustomButton(
                button_frame,
                text=f"Button {i+1}",
                command=lambda x=i: print(f"Button {x+1} activated"),
            )
            btn.grid(row=0, column=i, padx=5)

            # Add keyboard bindings
            btn.bind(
                "<Return>", lambda e, x=i: print(f"Button {x+1} activated via Enter")
            )
            btn.bind(
                "<space>", lambda e, x=i: print(f"Button {x+1} activated via Space")
            )

    def on_drop(self, event):
        print("Item dropped!")
        messagebox.showinfo("Drop Event", "Item was successfully dropped!")

    def show_selection(self, listbox):
        selected = [listbox.get(i) for i in listbox.curselection()]
        if selected:
            items = ", ".join(selected)
            messagebox.showinfo("Selected Items", f"Selected: {items}")
        else:
            messagebox.showinfo("Selected Items", "No items selected")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Advanced Features Example")
    root.geometry("600x700")

    example = AdvancedFeaturesExample(root)
    root.mainloop()
