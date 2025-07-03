"""
Layout Demo Example

Demonstrates layout components and containers.
"""

import tkinter as tk
from tkinter import ttk

# Placeholder components
CustomLabel = tk.Label

class TabContainer(ttk.Notebook):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

class Accordion(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

class Card(tk.Frame):
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, relief=tk.RAISED, bd=1, **kwargs)
        if title:
            label = tk.Label(self, text=title, font=("Arial", 10, "bold"))
            label.pack(pady=5)

class Panel(tk.Frame):
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, **kwargs)
        if title:
            label = tk.Label(self, text=title, font=("Arial", 12, "bold"))
            label.pack(pady=5)


class LayoutDemoExample:
    def __init__(self, parent):
        self.parent = parent
        self.create_layout_demo()

    def create_layout_demo(self):
        # Main container
        main_frame = tk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab container demo
        tab_demo = TabContainer(main_frame)
        tab_demo.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Cards
        card_frame = tk.Frame(tab_demo)
        tab_demo.add(card_frame, text="Cards")
        
        for i in range(3):
            card = Card(card_frame, title=f"Card {i+1}")
            card.pack(fill=tk.X, padx=5, pady=5)
            
            content = CustomLabel(card, text=f"This is content for card {i+1}")
            content.pack(padx=10, pady=10)

        # Tab 2: Panels
        panel_frame = tk.Frame(tab_demo)
        tab_demo.add(panel_frame, text="Panels")
        
        panel = Panel(panel_frame, title="Settings Panel")
        panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        content = CustomLabel(panel, text="Panel content goes here")
        content.pack(padx=10, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Layout Demo")
    root.geometry("600x400")
    
    app = LayoutDemoExample(root)
    root.mainloop()
