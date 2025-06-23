"""
Layout Demo Example

Demonstrates various layout options using TaskMover UI components.
"""

import tkinter as tk

from ui.display_components import CustomLabel
from ui.layout_components import Accordion, Card, Panel, TabContainer


class LayoutDemoExample:
    def __init__(self, parent):
        self.parent = parent
        self.create_layout_demo()

    def create_layout_demo(self):
        # Main tab container
        tab_container = TabContainer(self.parent)
        tab_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Panel demo tab
        self.create_panel_demo(tab_container)

        # Accordion demo tab
        self.create_accordion_demo(tab_container)

        # Card layout demo tab
        self.create_card_demo(tab_container)

    def create_panel_demo(self, parent):
        frame = tk.Frame(parent)
        parent.add(frame, text="Panels")

        # Nested panels
        outer_panel = Panel(frame, title="Outer Panel")
        outer_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        inner_panel1 = Panel(outer_panel, title="Inner Panel 1")
        inner_panel1.pack(fill=tk.X, padx=10, pady=5)

        CustomLabel(inner_panel1, text="Content in first inner panel").pack(pady=10)

        inner_panel2 = Panel(outer_panel, title="Inner Panel 2")
        inner_panel2.pack(fill=tk.X, padx=10, pady=5)

        CustomLabel(inner_panel2, text="Content in second inner panel").pack(pady=10)

    def create_accordion_demo(self, parent):
        frame = tk.Frame(parent)
        parent.add(frame, text="Accordion")

        accordion = Accordion(frame)
        accordion.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add accordion sections
        sections = [
            ("Section 1", "This is the content of the first section."),
            ("Section 2", "This is the content of the second section."),
            ("Section 3", "This is the content of the third section."),
        ]

        for title, content in sections:
            section_frame = tk.Frame(accordion)
            CustomLabel(section_frame, text=content).pack(pady=20)
            accordion.add_section(title, section_frame)

    def create_card_demo(self, parent):
        frame = tk.Frame(parent)
        parent.add(frame, text="Cards")

        # Create a grid of cards
        for i in range(6):
            row = i // 3
            col = i % 3

            card = Card(frame, title=f"Card {i+1}")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            CustomLabel(card, text=f"Content for card {i+1}").pack(pady=20)

        # Configure grid weights
        for i in range(3):
            frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            frame.grid_rowconfigure(i, weight=1)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Layout Demo Example")
    root.geometry("900x700")

    example = LayoutDemoExample(root)
    root.mainloop()
