"""
File operations for TaskMover Redesigned.
Streamlined file organization with better progress tracking.
"""

import os
import shutil
import zipfile
import logging
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional, Tuple
import threading
import time

logger = logging.getLogger("TaskMover.FileOps")


class FileOrganizer:
    """Handles file organization operations with progress tracking."""
    
    def __init__(self, organization_folder: str, rules: Dict[str, Any]):
        self.organization_folder = Path(organization_folder)
        self.rules = rules
        self.is_running = False
        self.should_stop = False
        
    def start_organization(self, 
                          progress_callback: Optional[Callable] = None,
                          file_moved_callback: Optional[Callable] = None,
                          completion_callback: Optional[Callable] = None) -> bool:
        """Start the file organization process."""
        if self.is_running:
            logger.warning("Organization already in progress")
            return False
        
        self.is_running = True
        self.should_stop = False
        
        # Run organization in a separate thread
        thread = threading.Thread(
            target=self._organize_files_thread,
            args=(progress_callback, file_moved_callback, completion_callback)
        )
        thread.daemon = True
        thread.start()
        
        return True
    
    def stop_organization(self) -> None:
        """Stop the organization process."""
        self.should_stop = True
        logger.info("Organization stop requested")
    
    def _organize_files_thread(self, 
                              progress_callback: Optional[Callable],
                              file_moved_callback: Optional[Callable],
                              completion_callback: Optional[Callable]) -> None:
        """Internal method to run organization in a thread."""
        try:
            results = self._organize_files(progress_callback, file_moved_callback)
            if completion_callback:
                completion_callback(True, results)
        except Exception as e:
            logger.error(f"Organization failed: {e}")
            if completion_callback:
                completion_callback(False, str(e))
        finally:
            self.is_running = False
    
    def _organize_files(self,
                       progress_callback: Optional[Callable],
                       file_moved_callback: Optional[Callable]) -> Dict[str, Any]:
        """Internal file organization logic."""
        if not self.organization_folder.exists():
            raise FileNotFoundError(f"Organization folder does not exist: {self.organization_folder}")
        
        # Get all files in the organization folder
        all_files = []
        for file_path in self.organization_folder.iterdir():
            if file_path.is_file():
                all_files.append(file_path)
        
        if not all_files:
            logger.info("No files to organize")
            return {"moved": 0, "errors": 0, "skipped": 0}
        
        # Get active rules sorted by priority
        active_rules = {name: rule for name, rule in self.rules.items() 
                       if rule.get('active', True)}
        sorted_rules = sorted(active_rules.items(), 
                            key=lambda x: x[1].get('priority', 0))
        
        moved_count = 0
        error_count = 0
        skipped_count = 0
        
        logger.info(f"Starting organization of {len(all_files)} files with {len(sorted_rules)} active rules")
        
        for i, file_path in enumerate(all_files):
            if self.should_stop:
                logger.info("Organization stopped by user")
                break
            
            # Update progress
            if progress_callback:
                progress_callback(i + 1, len(all_files), file_path.name)
            
            try:
                # Find matching rule
                matching_rule = self._find_matching_rule(file_path, sorted_rules)
                
                if matching_rule:
                    rule_name, rule_data = matching_rule
                    success = self._move_file(file_path, rule_data, rule_name)
                    
                    if success:
                        moved_count += 1
                        if file_moved_callback:
                            file_moved_callback(file_path.name, rule_data['path'])
                    else:
                        error_count += 1
                else:
                    skipped_count += 1
                    logger.debug(f"No rule matched file: {file_path.name}")
                    
            except Exception as e:
                logger.error(f"Error processing file {file_path.name}: {e}")
                error_count += 1
            
            # Small delay to prevent UI freezing
            time.sleep(0.01)
        
        results = {
            "moved": moved_count,
            "errors": error_count, 
            "skipped": skipped_count,
            "total": len(all_files)
        }
        
        logger.info(f"Organization complete: {results}")
        return results
    
    def _find_matching_rule(self, file_path: Path, 
                           sorted_rules: List[Tuple[str, Dict[str, Any]]]) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Find the first rule that matches the file."""
        import fnmatch
        
        for rule_name, rule_data in sorted_rules:
            patterns = rule_data.get('patterns', [])
            
            for pattern in patterns:
                if fnmatch.fnmatch(file_path.name.lower(), pattern.lower()):
                    logger.debug(f"File '{file_path.name}' matches rule '{rule_name}' pattern '{pattern}'")
                    return (rule_name, rule_data)
        
        return None
    
    def _move_file(self, file_path: Path, rule_data: Dict[str, Any], rule_name: str) -> bool:
        """Move a file according to rule specifications."""
        try:
            destination_dir = Path(rule_data['path'])
            destination_dir.mkdir(parents=True, exist_ok=True)
            
            destination_file = destination_dir / file_path.name
            
            # Handle file name conflicts
            if destination_file.exists():
                destination_file = self._get_unique_filename(destination_file)
            
            # Move the file
            shutil.move(str(file_path), str(destination_file))
            logger.info(f"Moved '{file_path.name}' to '{destination_dir}' (rule: {rule_name})")
            
            # Handle unzipping if required
            if rule_data.get('unzip', False) and self._is_archive(destination_file):
                self._extract_archive(destination_file)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to move file '{file_path.name}': {e}")
            return False
    
    def _get_unique_filename(self, file_path: Path) -> Path:
        """Generate a unique filename to avoid conflicts."""
        counter = 1
        stem = file_path.stem
        suffix = file_path.suffix
        parent = file_path.parent
        
        while file_path.exists():
            new_name = f"{stem} ({counter}){suffix}"
            file_path = parent / new_name
            counter += 1
        
        return file_path
    
    def _is_archive(self, file_path: Path) -> bool:
        """Check if a file is a supported archive format."""
        archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.tar.gz'}
        return file_path.suffix.lower() in archive_extensions or \
               ''.join(file_path.suffixes[-2:]).lower() in archive_extensions
    
    def _extract_archive(self, archive_path: Path) -> bool:
        """Extract an archive file."""
        try:
            extract_dir = archive_path.parent / archive_path.stem
            extract_dir.mkdir(exist_ok=True)
            
            if archive_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Delete the original archive after successful extraction
                archive_path.unlink()
                logger.info(f"Extracted and removed archive: {archive_path.name}")
                return True
            else:
                logger.warning(f"Archive format not supported for extraction: {archive_path.suffix}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to extract archive '{archive_path.name}': {e}")
            return False


# Backward compatibility function
def start_organization(settings: Dict[str, Any], 
                      rules: Dict[str, Any], 
                      logger_instance: logging.Logger,
                      progress_callback: Optional[Callable] = None,
                      file_moved_callback: Optional[Callable] = None) -> None:
    """Legacy function for backward compatibility."""
    organization_folder = settings.get('organisation_folder', str(Path.home() / 'Downloads'))
    
    organizer = FileOrganizer(organization_folder, rules)
    
    def completion_callback(success: bool, result):
        if success:
            logger_instance.info(f"Organization completed: {result}")
        else:
            logger_instance.error(f"Organization failed: {result}")
    
    organizer.start_organization(progress_callback, file_moved_callback, completion_callback)
