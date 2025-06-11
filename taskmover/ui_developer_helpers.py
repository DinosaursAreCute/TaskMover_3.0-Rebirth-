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
def open_developer_settings(base_directory: str, logger: logging.Logger) -> None:
    return None  # Placeholder for future developer settings UI
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
