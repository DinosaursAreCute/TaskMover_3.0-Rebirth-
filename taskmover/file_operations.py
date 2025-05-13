"""
File operation utilities for the TaskMover application.

This module provides functions for organizing files, moving files, and
extracting zip files based on user-defined rules.
"""

import os
import shutil
import fnmatch
import zipfile
from tkinter import messagebox, Toplevel
from tkinter import ttk
import logging

logger = logging.getLogger("FileOperations")
def organize_files(settings, rules, logger, organisation_folder=None):
    """
    Organize files in the organization folder based on rules.

    Args:
        settings (dict): Application settings containing the organization folder.
        rules (dict): Dictionary of rules for organizing files.
        logger (logging.Logger): Logger for logging updates.
    """
    # Access the organization folder from settings if not provided
    if not organisation_folder:
        organisation_folder = settings.get("organisation_folder", "")
    if not organisation_folder or not os.path.exists(organisation_folder):
        logger.error(f"Directory '{organisation_folder}' does not exist.")
        return

    # Initialize root for Toplevel
    root = Toplevel()
    root.withdraw()  # Hide the root window

    # Get the list of files and total files
    files = [item for item in os.listdir(organisation_folder) if os.path.isfile(os.path.join(organisation_folder, item))]
    total_files = len(files)
def organize_files(settings, rules, logger):
    """
    Organize files in the organization folder based on rules.

    Args:
        settings (dict): Application settings containing the organization folder.
        rules (dict): Dictionary of rules for organizing files.
        logger (logging.Logger): Logger for logging updates.
    """
    # Create a progress bar window
    progress_window = Toplevel(root)
    progress_window.title("Organizing Files")
    progress_window.geometry("400x200")
    ttk.Label(progress_window, text="Organizing files, please wait...").pack(pady=10)
    
    # Progress bar
    progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)
    progress_bar["maximum"] = total_files

    # Label to display the current file being processed
    current_file_label = ttk.Label(progress_window, text="Current file: None")
    current_file_label.pack(pady=10)

    for index, file_name in enumerate(files, start=1):
        file_path = os.path.join(organisation_folder, file_name)
        logger.info(f"Processing file {index}/{total_files}: {file_name}")
        
        # Update the current file label
        current_file_label.config(text=f"Current file: {file_name}")
        progress_window.update_idletasks()

        # Process the file
        move_file(file_path, organisation_folder, rules, logger)

        # Update progress bar
        progress_bar["value"] = index
        progress_window.update_idletasks()

    logger.info("File organization completed.")
    progress_window.destroy()

def move_file(file_path, organization_folder, rules, logger):
    """
    Move a file to its target directory based on matching rules.

    Args:
        file_path (str): Path to the file to move.
        organization_folder (str): Path to the organization folder.
        rules (dict): Dictionary of rules for organizing files.
        logger (logging.Logger): Logger for logging updates.
    """
    file_name = os.path.basename(file_path)
    for folder, rule in rules.items():
        if rule.get('active') and any(fnmatch.fnmatch(file_name, pattern) for pattern in rule['patterns']):
            target_folder = rule['path'] or os.path.join(organization_folder, folder)
            if not os.path.exists(target_folder):
                logger.error(f"Target folder '{target_folder}' does not exist for rule '{folder}'.")
                raise FileNotFoundError(f"Target folder '{target_folder}' does not exist for rule '{folder}'.")
            shutil.move(file_path, os.path.join(target_folder, file_name))
            logger.info(f"Moved file '{file_name}' to '{target_folder}'")
            return
    logger.warning(f"No matching rule found for file '{file_name}'")

def unzip_file(zip_path, extract_to, logger):
    """
    Extract a zip file to the specified directory.

    Args:
        zip_path (str): Path to the zip file.
        extract_to (str): Directory to extract the contents to.
        logger (logging.Logger): Logger for logging updates.
    """
    try:
        zip_name = os.path.splitext(os.path.basename(zip_path))[0]
        target_dir = os.path.join(extract_to, zip_name)
        os.makedirs(target_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
            logger.info(f"Unzipped '{zip_path}' to '{target_dir}'")
    except zipfile.BadZipFile:
        logger.error(f"Failed to unzip '{zip_path}': Bad zip file")
        messagebox.showerror("Error", f"Failed to unzip '{zip_path}': Bad zip file")

def start_organization(settings, rules, logger):
    """
    Organize files in the organization folder with progress updates.

    Args:
        settings (dict): Application settings containing the organization folder.
        rules (dict): Dictionary of rules for organizing files.
        logger (logging.Logger): Logger for logging updates.
    """
    organisation_folder = settings.get("organisation_folder","")
    if not organisation_folder or not os.path.exists(organisation_folder):
        logger.error(f"Directory '{organisation_folder}' does not exist.")
        return

    files = [item for item in os.listdir(organisation_folder) if os.path.isfile(os.path.join(organisation_folder, item))]
    total_files = len(files)
    logger.info(f"Found {total_files} files in '{organisation_folder}'.")

    for index, file_name in enumerate(files, start=1):
        file_path = os.path.join(organisation_folder, file_name)
        logger.info(f"Processing file {index}/{total_files}: {file_name}")
        move_file(file_path, organisation_folder, rules, logger)

    logger.info("File organization completed.")
