import os
import shutil
import fnmatch
import zipfile
from tkinter import messagebox
import logging

logger = logging.getLogger("FileOperations")

def organize_files(base_directory, rules, logger):
    """Organize files in the base directory based on rules."""
    if not os.path.exists(base_directory):
        logger.error(f"Directory '{base_directory}' does not exist.")
        return

    files = [item for item in os.listdir(base_directory) if os.path.isfile(os.path.join(base_directory, item))]
    logger.info(f"Found {len(files)} files in '{base_directory}'.")

    for file_name in files:
        move_file(os.path.join(base_directory, file_name), base_directory, rules, logger)

def move_file(file_path, base_directory, rules, logger):
    """Move a file to its target directory based on matching rules."""
    file_name = os.path.basename(file_path)
    for folder, rule in rules.items():
        if rule.get('active') and any(fnmatch.fnmatch(file_name, pattern) for pattern in rule['patterns']):
            target_folder = rule['path'] or os.path.join(base_directory, folder)
            os.makedirs(target_folder, exist_ok=True)
            shutil.move(file_path, os.path.join(target_folder, file_name))
            logger.info(f"Moved file '{file_name}' to '{target_folder}'")
            return
    logger.warning(f"No matching rule found for file '{file_name}'")

def unzip_file(zip_path, extract_to, logger):
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

def start_organization(base_directory, rules, logger):
    """Organize files in the base directory with progress updates."""
    if not os.path.exists(base_directory):
        logger.error(f"Directory '{base_directory}' does not exist.")
        return

    files = [item for item in os.listdir(base_directory) if os.path.isfile(os.path.join(base_directory, item))]
    total_files = len(files)
    logger.info(f"Found {total_files} files in '{base_directory}'.")

    for index, file_name in enumerate(files, start=1):
        file_path = os.path.join(base_directory, file_name)
        logger.info(f"Processing file {index}/{total_files}: {file_name}")
        move_file(file_path, base_directory, rules, logger)

    logger.info("File organization completed.")
