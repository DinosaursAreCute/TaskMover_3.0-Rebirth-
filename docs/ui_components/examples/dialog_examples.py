"""
Dialog Examples

Demonstrates dialog components and interactions.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog

# Placeholder components
class InputDialog(tk.Toplevel):
    def __init__(self, parent, title="Input", prompt="Enter value:"):
        super().__init__(parent)
        self.title(title)
        self.result = None
        
        tk.Label(self, text=prompt).pack(pady=10)
        self.entry = tk.Entry(self)
        self.entry.pack(pady=5)
        
        tk.Button(self, text="OK", command=self.ok_clicked).pack(pady=5)
    
    def ok_clicked(self):
        self.result = self.entry.get()
        self.destroy()

class MessageDialog:
    @staticmethod
    def show_info(title, message):
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_error(title, message):
        messagebox.showerror(title, message)

CustomButton = tk.Button

class Panel(tk.Frame):
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, **kwargs)
        if title:
            label = tk.Label(self, text=title, font=("Arial", 12, "bold"))
            label.pack(pady=5)


class DialogExamplesDemo:
    def __init__(self, parent):
        self.parent = parent
        self.create_dialog_demo()

    def create_dialog_demo(self):
        # Main panel
        panel = Panel(self.parent, title="Dialog Examples")
        panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Input dialog button
        input_btn = CustomButton(
            panel,
            text="Show Input Dialog",
            command=self.show_input_dialog
        )
        input_btn.pack(pady=10)

        # Message dialog buttons
        info_btn = CustomButton(
            panel,
            text="Show Info Dialog",
            command=self.show_info_dialog
        )
        info_btn.pack(pady=5)

        error_btn = CustomButton(
            panel,
            text="Show Error Dialog",
            command=self.show_error_dialog
        )
        error_btn.pack(pady=5)

    def show_input_dialog(self):
        dialog = InputDialog(self.parent, "User Input", "Enter your name:")
        self.parent.wait_window(dialog)
        if dialog.result:
            print(f"User entered: {dialog.result}")

    def show_info_dialog(self):
        MessageDialog.show_info("Information", "This is an info message!")

    def show_error_dialog(self):
        MessageDialog.show_error("Error", "This is an error message!")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Dialog Examples")
    root.geometry("300x250")
    
    app = DialogExamplesDemo(root)
    root.mainloop()
