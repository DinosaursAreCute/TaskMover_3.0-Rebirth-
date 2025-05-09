import os
import shutil
import fnmatch
import zipfile
from tkinter import messagebox
import logging

logger = logging.getLogger("FileOperations")

def organize_files(base_directory, rules, logger):
    if not os.path.exists(base_directory):
        messagebox.showerror("Error", f"Directory '{base_directory}' does not exist.")
        logger.error(f"Directory '{base_directory}' does not exist.")
        return

    files = [item for item in os.listdir(base_directory) if os.path.isfile(os.path.join(base_directory, item))]
    logger.info(f"Found {len(files)} files in '{base_directory}'.")

    for item in files:
        item_path = os.path.join(base_directory, item)
        move_file(item_path, base_directory, rules, logger)

def move_file(file_path, base_directory, rules, logger):
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1].lower()

    for folder, rule in rules.items():
        if not rule.get('active', True):
            continue

        patterns = rule['patterns']
        target_folder = rule['path'] if rule['path'] else os.path.join(base_directory, folder)
        unzip = rule['unzip']

        if file_extension in patterns or any(fnmatch.fnmatch(file_name, pattern) for pattern in patterns):
            os.makedirs(target_folder, exist_ok=True)
            shutil.move(file_path, os.path.join(target_folder, file_name))
            logger.info(f"Moved file '{file_name}' to '{target_folder}'")

            if unzip and file_extension == '.zip':
                unzip_file(os.path.join(target_folder, file_name), target_folder, logger)

            break
    else:
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
