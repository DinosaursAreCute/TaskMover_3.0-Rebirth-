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
from pathlib import Path

logger = logging.getLogger("FileOperations")
def organize_files(settings: dict, rules: dict, logger: logging.Logger, organisation_folder: str = None) -> None:
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
    org_path = Path(organisation_folder)
    if not organisation_folder or not org_path.exists():
        logger.error(f"Directory '{organisation_folder}' does not exist.")
        messagebox.showerror("Directory Not Found", f"The folder '{organisation_folder}' does not exist. Please check your settings.")
        return

    # Get the list of files and total files
    files = [item for item in org_path.iterdir() if item.is_file()]
    total_files = len(files)
    for index, file_path in enumerate(files, start=1):
        logger.info(f"Processing file {index}/{total_files}: {file_path.name}")
        move_file(file_path, org_path, rules, logger)

def move_file(file_path: Path, organization_folder: Path, rules: dict, logger: logging.Logger, file_moved_callback = None) -> str | None:
    """
    Move a file to its target directory based on matching rules.

    Args:
        file_path (str): Path to the file to move.
        organization_folder (str): Path to the organization folder.
        rules (dict): Dictionary of rules for organizing files.
        logger (logging.Logger): Logger for logging updates.
        file_moved_callback (callable, optional): Called with (file_name, target_folder) when a file is moved.
    Returns:
        str: The target folder if moved, else None.
    """
    file_name = file_path.name
    for folder, rule in rules.items():
        if rule.get('active') and any(fnmatch.fnmatch(file_name, pattern) for pattern in rule['patterns']):
            target_folder = Path(rule['path']) if rule['path'] else organization_folder / folder
            if not target_folder.exists():
                logger.error(f"Target folder '{target_folder}' does not exist for rule '{folder}'.")
                messagebox.showerror("Target Folder Not Found", f"The target folder '{target_folder}' for rule '{folder}' does not exist. Please update your rule or create the folder.")
                return None
            shutil.move(str(file_path), str(target_folder / file_name))
            logger.info(f"Moved file '{file_name}' to '{target_folder}'")
            # Unzip if rule requests and file is a zip
            if rule.get('unzip', False) and file_name.lower().endswith('.zip'):
                try:
                    unzip_file(target_folder / file_name, target_folder, logger)
                except Exception as e:
                    logger.error(f"Failed to unzip '{file_name}': {e}")
            if file_moved_callback:
                file_moved_callback(file_name, str(target_folder))
            return str(target_folder)
    logger.warning(f"No matching rule found for file '{file_name}'")
    messagebox.showwarning("No Rule Match", f"No matching rule was found for file '{file_name}'. The file was not moved.")
    return None

def unzip_file(zip_path: Path, extract_to: Path, logger: logging.Logger) -> None:
    """
    Extract a zip file to the specified directory.

    Args:
        zip_path (str): Path to the zip file.
        extract_to (str): Directory to extract the contents to.
        logger (logging.Logger): Logger for logging updates.
    """
    try:
        zip_name = zip_path.stem
        target_dir = extract_to / zip_name
        target_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
            logger.info(f"Unzipped '{zip_path}' to '{target_dir}'")
    except zipfile.BadZipFile:
        logger.error(f"Failed to unzip '{zip_path}': Bad zip file")
        messagebox.showerror("Error", f"Failed to unzip '{zip_path}': Bad zip file")

def start_organization(settings: dict, rules: dict, logger: logging.Logger, progress_callback = None, file_moved_callback = None) -> None:
    """
    Organize files in the organization folder with progress updates via callbacks.

    Args:
        settings (dict): Application settings containing the organization folder.
        rules (dict): Dictionary of rules for organizing files.
        logger (logging.Logger): Logger for logging updates.
        progress_callback (callable, optional): Called with (index, total, file_name) as each file is processed.
        file_moved_callback (callable, optional): Called with (file_name, target_folder) when a file is moved.
    """
    organisation_folder = settings.get("organisation_folder", "")
    org_path = Path(organisation_folder)
    if not organisation_folder or not org_path.exists():
        logger.error(f"Directory '{organisation_folder}' does not exist.")
        messagebox.showerror("Directory Not Found", f"The folder '{organisation_folder}' does not exist. Please check your settings.")
        return
    files = [item for item in org_path.iterdir() if item.is_file()]
    total_files = len(files)
    logger.info(f"Found {total_files} files in '{organisation_folder}'.")
    for index, file_path in enumerate(files, start=1):
        logger.info(f"Processing file {index}/{total_files}: {file_path.name}")
        target_folder = move_file(file_path, org_path, rules, logger, file_moved_callback)
        if progress_callback:
            progress_callback(index, total_files, file_path.name)
    logger.info("File organization completed.")
