import os
import logging

def center_window(window):
    """Zentriert ein Fenster auf dem Bildschirm."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def ensure_directory_exists(directory, logger=None):
    """Ensure a directory exists, creating it if necessary."""
    try:
        os.makedirs(directory, exist_ok=True)
        if logger:
            logger.debug(f"Ensured directory exists: {directory}")
    except Exception as e:
        if logger:
            logger.error(f"Failed to create directory '{directory}': {e}")
        raise
