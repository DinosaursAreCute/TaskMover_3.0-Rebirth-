"""
Basic Form Example

Demonstrates how to create a simple form using TaskMover UI components.
"""

import tkinter as tk

from ui.display_components import CustomLabel
from ui.input_components import CustomButton, CustomCheckbox, CustomEntry
from ui.layout_components import Panel


class BasicFormExample:
    def __init__(self, parent):
        self.parent = parent
        self.create_form()

    def create_form(self):
        # Main panel
        form_panel = Panel(self.parent, title="User Registration")
        form_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Name field
        name_label = CustomLabel(form_panel, text="Full Name:")
        name_label.pack(anchor="w", pady=(10, 2))

        self.name_entry = CustomEntry(form_panel, placeholder="Enter your full name")
        self.name_entry.pack(fill=tk.X, pady=(0, 10))

        # Email field
        email_label = CustomLabel(form_panel, text="Email:")
        email_label.pack(anchor="w", pady=(0, 2))

        self.email_entry = CustomEntry(form_panel, placeholder="Enter your email")
        self.email_entry.pack(fill=tk.X, pady=(0, 10))

        # Newsletter checkbox
        self.newsletter_check = CustomCheckbox(
            form_panel, text="Subscribe to newsletter"
        )
        self.newsletter_check.pack(anchor="w", pady=10)

        # Submit button
        submit_btn = CustomButton(form_panel, text="Register", command=self.submit_form)
        submit_btn.pack(pady=20)

    def submit_form(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        newsletter = self.newsletter_check.get()

        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Newsletter: {newsletter}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Basic Form Example")
    root.geometry("400x300")

    example = BasicFormExample(root)
    root.mainloop()
