"""
UI license dialog helpers for TaskMover.
"""

import ttkbootstrap as ttkb
from tkinter import WORD, END, BOTH, DISABLED

# License dialog helpers

def show_license_info():
    """Display the license information in a modern, scrollable dialog window."""
    license_window = ttkb.Toplevel()
    license_window.title("License Information")
    license_window.geometry("500x400")

    text_area = ttkb.Text(license_window, wrap=WORD)
    license_text = """
MIT License

Copyright (c) 2025 Noah

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    text_area.insert(END, license_text)
    text_area.pack(fill=BOTH, expand=True, padx=10, pady=10)
    text_area.config(state=DISABLED)

    # Restore custom color coding for the Close button
    close_button = ttkb.Button(license_window, text="Close", command=license_window.destroy)
    close_button.pack(pady=10)
    # Apply custom color (e.g., red background, white text)
    close_button.configure(style="danger.TButton")
