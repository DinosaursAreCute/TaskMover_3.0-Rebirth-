"""
Window centering utility for TaskMover.
"""
import tkinter

def center_window(window: tkinter.Tk | tkinter.Toplevel) -> None:
    """Center a window on the screen."""
    if not hasattr(window, 'update_idletasks'):
        raise AttributeError("Provided window object does not have 'update_idletasks' method.")
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")
