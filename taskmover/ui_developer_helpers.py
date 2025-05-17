"""
Developer and utility UI helpers for TaskMover.
"""

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from pathlib import Path
from .center_window import center_window
import logging

# Developer and utility helpers

def open_developer_settings(root, settings, save_settings, logger):
    dev_window = tk.Toplevel(root)
    dev_window.title("Developer Settings")
    dev_window.geometry("400x400")
    center_window(dev_window)

    ttkb.Label(dev_window, text="Developer Settings", font=("Helvetica", 12, "bold")).pack(pady=10)

    dev_mode_var = tk.StringVar(value="Enabled" if settings.get("developer_mode", False) else "Disabled")
    ttkb.Label(dev_window, text="Developer Mode:").pack(anchor="w", padx=10)
    dev_mode_dropdown = ttkb.Combobox(dev_window, textvariable=dev_mode_var, values=["Enabled", "Disabled"], state="readonly")
    dev_mode_dropdown.pack(fill="x", padx=10, pady=5)

    logging_level_var = tk.StringVar(value=logging.getLevelName(logger.level))
    ttkb.Label(dev_window, text="Logging Level:").pack(anchor="w", padx=10)
    logging_level_dropdown = ttkb.Combobox(dev_window, textvariable=logging_level_var, values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], state="readonly")
    logging_level_dropdown.pack(fill="x", padx=10, pady=5)

    ttkb.Label(dev_window, text="Logging Components:", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10)
    components_frame = ttkb.Frame(dev_window)
    components_frame.pack(fill="x", padx=10, pady=5)

    components = ["UI", "File Operations", "Rules", "Settings"]
    component_vars = {component: tk.IntVar(value=1) for component in components}

    for component, var in component_vars.items():
        ttkb.Checkbutton(components_frame, text=component, variable=var).pack(anchor="w")

    def save_dev_settings():
        settings["developer_mode"] = dev_mode_var.get() == "Enabled"
        save_settings(settings)
        logger.setLevel(logging_level_var.get())
        logger.info(f"Developer mode set to {dev_mode_var.get()}. Logging level set to {logging_level_var.get()}.")
        for component, var in component_vars.items():
            logger.info(f"Logging for {component}: {'Enabled' if var.get() else 'Disabled'}")
        dev_window.destroy()

    ttkb.Button(dev_window, text="Save", command=save_dev_settings).pack(pady=10)

def trigger_developer_function(base_directory: str, logger: logging.Logger) -> None:
    logger.info("Developer function triggered.")
    if not base_directory:
        logger.warning("Base directory is not set. Developer function aborted.")
        messagebox.showwarning("Warning", "Base directory is not set. Developer function aborted.")
        return
    try:
        base_path = Path(base_directory)
        base_path.mkdir(parents=True, exist_ok=True)
        dummy_files = [
            "test_document.pdf",
            "image_sample.jpg",
            "video_clip.mp4",
            "archive_file.zip",
            "random_file.txt"
        ]
        for file_name in dummy_files:
            file_path = base_path / file_name
            file_path.write_text(f"Dummy content for {file_name}")
            logger.info(f"Created dummy file: {file_path}")
        messagebox.showinfo("Developer Function", f"Dummy files created in {base_directory}.")
    except Exception as e:
        logger.error(f"Error creating dummy files: {e}")
        messagebox.showerror("Error", f"An error occurred while creating dummy files: {e}")

def execute_button(base_directory, rules, logger):
    if not base_directory or not Path(base_directory).exists():
        logger.error("Invalid or non-existent base directory.")
        messagebox.showerror("Error", "Invalid or non-existent base directory.")
        return
    logger.info("Starting file organization process...")
    try:
        from taskmover.file_operations import organize_files
        organize_files(base_directory, rules, logger)
        messagebox.showinfo("Success", "File organization completed successfully.")
        logger.info("File organization completed successfully.")
    except Exception as e:
        logger.error(f"Error during file organization: {e}")
        messagebox.showerror("Error", f"An error occurred during file organization: {e}")
