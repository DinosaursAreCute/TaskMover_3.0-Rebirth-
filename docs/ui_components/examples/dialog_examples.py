"""
Dialog Examples

Demonstrates various dialog types using TaskMover UI components.
"""

import tkinter as tk

from ui.dialog_components import ConfirmationDialog, InputDialog, MessageDialog
from ui.input_components import CustomButton
from ui.layout_components import Panel


class DialogExamples:
    def __init__(self, parent):
        self.parent = parent
        self.create_dialog_buttons()

    def create_dialog_buttons(self):
        panel = Panel(self.parent, title="Dialog Examples")
        panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Message dialog button
        msg_btn = CustomButton(
            panel, text="Show Message Dialog", command=self.show_message_dialog
        )
        msg_btn.pack(pady=10)

        # Confirmation dialog button
        confirm_btn = CustomButton(
            panel,
            text="Show Confirmation Dialog",
            command=self.show_confirmation_dialog,
        )
        confirm_btn.pack(pady=10)

        # Input dialog button
        input_btn = CustomButton(
            panel, text="Show Input Dialog", command=self.show_input_dialog
        )
        input_btn.pack(pady=10)

    def show_message_dialog(self):
        dialog = MessageDialog(
            self.parent, title="Information", message="This is a sample message dialog."
        )
        dialog.show()

    def show_confirmation_dialog(self):
        dialog = ConfirmationDialog(
            self.parent,
            title="Confirm Action",
            message="Are you sure you want to proceed?",
        )
        result = dialog.show()
        print(f"Confirmation result: {result}")

    def show_input_dialog(self):
        dialog = InputDialog(
            self.parent,
            title="Enter Value",
            message="Please enter a value:",
            default_value="Default text",
        )
        result = dialog.show()
        print(f"Input result: {result}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Dialog Examples")
    root.geometry("400x300")

    example = DialogExamples(root)
    root.mainloop()
