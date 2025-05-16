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
    # Load organization folder from settings
    organisation_folder = settings.get("organisation_folder", "")
    if not organisation_folder or not os.path.exists(organisation_folder):
        logger.error(f"Directory '{organisation_folder}' does not exist.")
        return
    # Get the list of files and total files
    files = [item for item in os.listdir(organisation_folder) if os.path.isfile(os.path.join(organisation_folder, item))]
    total_files = len(files)

    for index, file_name in enumerate(files, start=1):
        file_path = os.path.join(organisation_folder, file_name)
        logger.info(f"Processing file {index}/{total_files}: {file_name}")

        # Process the file
        move_file(file_path, organisation_folder, rules, logger)

def move_file(file_path, organization_folder, rules, logger, file_moved_callback=None):
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
    file_name = os.path.basename(file_path)
    for folder, rule in rules.items():
        if rule.get('active') and any(fnmatch.fnmatch(file_name, pattern) for pattern in rule['patterns']):
            target_folder = rule['path'] or os.path.join(organization_folder, folder)
            if not os.path.exists(target_folder):
                logger.error(f"Target folder '{target_folder}' does not exist for rule '{folder}'.")
                raise FileNotFoundError(f"Target folder '{target_folder}' does not exist for rule '{folder}'.")
            shutil.move(file_path, os.path.join(target_folder, file_name))
            logger.info(f"Moved file '{file_name}' to '{target_folder}'")
            if file_moved_callback:
                file_moved_callback(file_name, target_folder)
            return target_folder
    logger.warning(f"No matching rule found for file '{file_name}'")
    return None

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

def start_organization(settings, rules, logger, progress_callback=None, file_moved_callback=None):
    """
    Organize files in the organization folder with progress updates via callbacks.

    Args:
        settings (dict): Application settings containing the organization folder.
        rules (dict): Dictionary of rules for organizing files.
        logger (logging.Logger): Logger for logging updates.
        progress_callback (callable, optional): Called with (index, total, file_name) as each file is processed.
        file_moved_callback (callable, optional): Called with (file_name, target_folder) when a file is moved.
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
        target_folder = move_file(file_path, organisation_folder, rules, logger, file_moved_callback)
        if progress_callback:
            progress_callback(index, total_files, file_name)

    logger.info("File organization completed.")
