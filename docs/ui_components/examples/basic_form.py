"""
Basic Form Example

Demonstrates basic form components and layout.
"""

import tkinter as tk

# Try to import custom components, fall back to standard tkinter
try:
    from taskmover.ui.display_components import CustomLabel  # type: ignore
except ImportError:
    CustomLabel = tk.Label

CustomButton = tk.Button

# Custom Entry with placeholder support
class CustomEntry(tk.Entry):
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, **kwargs)
        if placeholder:
            self.insert(0, placeholder)
            self.config(fg='gray')
            self.bind('<FocusIn>', self._clear_placeholder)
            
    def _clear_placeholder(self, event):
        if self.config('fg')[4] == 'gray':
            self.delete(0, tk.END)
            self.config(fg='black')

class CustomCheckbox(tk.Checkbutton):
    def __init__(self, parent, **kwargs):
        self.var = tk.BooleanVar()
        super().__init__(parent, variable=self.var, **kwargs)
    
    def get(self):
        return self.var.get()

class Panel(tk.Frame):
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, **kwargs)
        if title:
            label = tk.Label(self, text=title, font=("Arial", 12, "bold"))
            label.pack(pady=5)


class BasicFormExample:
    def __init__(self, parent):
        self.parent = parent
        self.create_form()

    def create_form(self):
        # Main form panel
        form_panel = Panel(self.parent, title="User Registration")
        form_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Name field
        name_label = CustomLabel(form_panel, text="Full Name:")
        name_label.pack(anchor=tk.W, pady=(10, 0))
        self.name_entry = CustomEntry(form_panel, placeholder="Enter your full name")
        self.name_entry.pack(fill=tk.X, pady=(5, 10))

        # Email field
        email_label = CustomLabel(form_panel, text="Email:")
        email_label.pack(anchor=tk.W)
        self.email_entry = CustomEntry(form_panel, placeholder="Enter your email")
        self.email_entry.pack(fill=tk.X, pady=(5, 10))

        # Newsletter checkbox
        self.newsletter_check = CustomCheckbox(
            form_panel, 
            text="Subscribe to newsletter"
        )
        self.newsletter_check.pack(anchor=tk.W, pady=10)

        # Submit button
        submit_btn = CustomButton(
            form_panel, 
            text="Register", 
            command=self.submit_form
        )
        submit_btn.pack(pady=20)

    def submit_form(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        newsletter = self.newsletter_check.get()
        
        print(f"Form submitted: {name}, {email}, Newsletter: {newsletter}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Basic Form Example")
    root.geometry("400x300")
    
    app = BasicFormExample(root)
    root.mainloop()
