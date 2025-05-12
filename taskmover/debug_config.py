"""
Debug configuration and utilities for the TaskMover application.

This module provides debugging tools such as visual markers, debug lines,
and widget highlighters for UI elements.
"""

# Debug configuration file for TaskMover

# Toggle debugging logs for UI elements
enable_ui_debug_logs = False

# Toggle visual markers for UI elements
enable_ui_visual_markers = False

# Toggle for enabling debug lines
enable_debug_lines = False

# Toggle for enabling widget highlighter
enable_widget_highlighter = False

# Debugging log function
def debug_log(message):
    """
    Log a debug message if UI debug logs are enabled.

    Args:
        message (str): The debug message to log.
    """
    if enable_ui_debug_logs:
        print(f"[DEBUG] {message}")

# Function to apply visual markers to UI elements
def apply_visual_marker(widget, color="red"):
    if enable_ui_visual_markers:
        widget.configure(background=color)

import random
import tkinter as tk

# Update draw_debug_lines to use the new toggle
def draw_debug_lines(canvas, widget, draw_to_center=False):
    """
    Draw colored lines around a widget and optionally to the center of the screen.

    Args:
        canvas (tk.Canvas): Canvas to draw the lines on.
        widget (tk.Widget): Widget to highlight.
        draw_to_center (bool): Whether to draw lines to the screen center.
    """
    if not enable_ui_visual_markers or not enable_debug_lines:
        return

    # Get widget's bounding box
    if hasattr(widget, "bbox"):
        bbox = widget.bbox("all")
        if bbox:
            x1, y1, x2, y2 = bbox
        else:
            return  # Skip if bbox is None
    else:
        x1, y1 = widget.winfo_rootx(), widget.winfo_rooty()
        x2, y2 = x1 + widget.winfo_width(), y1 + widget.winfo_height()

    # Generate a random color for the lines
    color = "#%06x" % random.randint(0, 0xFFFFFF)

    # Draw rectangle around the widget
    canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)

    if draw_to_center:
        # Calculate the center of the screen
        screen_width = canvas.winfo_screenwidth()
        screen_height = canvas.winfo_screenheight()
        center_x = screen_width // 2
        center_y = screen_height // 2

        # Draw lines from widget to the center of the screen
        canvas.create_line((x1 + x2) // 2, (y1 + y2) // 2, center_x, center_y, fill=color, width=2)

# Update display_widget_names to use the new toggle
def display_widget_names(widget_list):
    """
    Display a UI window with a list of widget names and highlight selected elements.

    Args:
        widget_list (list): List of widget names to display.
    """
    if not enable_ui_visual_markers or not enable_widget_highlighter:
        return

    # Create a new window
    highlight_window = tk.Toplevel()
    highlight_window.title("Widget Highlighter")
    highlight_window.geometry("300x400")

    # Add a label
    tk.Label(highlight_window, text="Select a Widget to Highlight", font=("Helvetica", 12, "bold")).pack(pady=10)

    # Create a listbox to display widget names
    listbox = tk.Listbox(highlight_window, selectmode=tk.SINGLE, width=40, height=15)
    listbox.pack(pady=10, padx=10)

    # Populate the listbox with widget names
    for widget_name in widget_list:
        listbox.insert(tk.END, widget_name)

    def highlight_selected():
        # Get the selected widget name
        selected_index = listbox.curselection()
        if selected_index:
            selected_widget_name = widget_list[selected_index[0]]
            debug_log(f"Highlighting widget: {selected_widget_name}")
            # Here you would add logic to highlight the actual widget in the main UI

    # Add a button to trigger highlighting
    tk.Button(highlight_window, text="Highlight", command=highlight_selected).pack(pady=10)

    # Add a close button
    tk.Button(highlight_window, text="Close", command=highlight_window.destroy).pack(pady=5)
