"""
Common utilities for TaskMover Redesigned.
Streamlined utility functions with better organization.
"""

import tkinter as tk
import logging
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger("TaskMover.Utils")


def get_screen_dimensions(window: tk.Tk | tk.Toplevel) -> tuple[int, int]:
    """Get screen dimensions."""
    return window.winfo_screenwidth(), window.winfo_screenheight()


def calculate_proportional_size(screen_width: int, screen_height: int, 
                               width_ratio: float = 0.6, height_ratio: float = 0.7) -> tuple[int, int]:
    """Calculate proportional window size based on screen dimensions."""
    width = int(screen_width * width_ratio)
    height = int(screen_height * height_ratio)
    
    # Ensure minimum sizes
    min_width, min_height = 400, 300
    width = max(width, min_width)
    height = max(height, min_height)
    
    # Ensure maximum sizes (prevent windows from being too large)
    max_width = int(screen_width * 0.9)
    max_height = int(screen_height * 0.9)
    width = min(width, max_width)
    height = min(height, max_height)
    
    return width, height


def center_window(window: tk.Tk | tk.Toplevel, 
                 width: Optional[int] = None, 
                 height: Optional[int] = None,
                 proportional: bool = False,
                 width_ratio: float = 0.6,
                 height_ratio: float = 0.7) -> None:
    """Center a window on the screen with optional proportional sizing."""
    # Get screen dimensions
    screen_width, screen_height = get_screen_dimensions(window)
    
    # Calculate window dimensions
    if proportional or (width is None and height is None):
        # If proportional is requested or both width and height are None, use proportional sizing
        width, height = calculate_proportional_size(
            screen_width, screen_height, width_ratio, height_ratio
        )
    elif width is None:
        # If only width is None, use requested height and calculate width from window's requested width
        window.update_idletasks()
        width = window.winfo_reqwidth()
    elif height is None:
        # If only height is None, use requested width and calculate height from window's requested height
        window.update_idletasks()
        height = window.winfo_reqheight()
    # else: both width and height are provided, use as is
    
    # Calculate position (center on screen)
    x = int((screen_width - width) // 2)
    y = int((screen_height - height) // 2)
    
    # Ensure window doesn't go off-screen
    x = max(0, min(x, screen_width - width))
    y = max(0, min(y, screen_height - height))
    
    # Set window position and size
    window.geometry(f"{width}x{height}+{x}+{y}")
    logger.debug(f"Centered window: {width}x{height} at ({x}, {y}) (screen: {screen_width}x{screen_height})")


def center_window_on_parent(child: tk.Toplevel, parent: tk.Widget,
                           width: Optional[int] = None, 
                           height: Optional[int] = None,
                           proportional: bool = False,
                           width_ratio: float = 0.8,
                           height_ratio: float = 0.8) -> None:
    """Center a child window on its parent window."""
    # Get parent window info
    parent.update_idletasks()
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    
    # Calculate child window dimensions
    if proportional or (width is None and height is None):
        width = int(parent_width * width_ratio)
        height = int(parent_height * height_ratio)
        
        # Ensure minimum sizes
        min_width, min_height = 300, 200
        width = max(width, min_width)
        height = max(height, min_height)
    elif width is None or height is None:
        child.update_idletasks()
        if width is None:
            width = child.winfo_reqwidth()
        if height is None:
            height = child.winfo_reqheight()
    
    # Calculate position (center on parent)
    x = parent_x + (parent_width - width) // 2
    y = parent_y + (parent_height - height) // 2
    
    # Get screen dimensions to ensure child doesn't go off-screen
    screen_width, screen_height = get_screen_dimensions(child)
    x = max(0, min(x, screen_width - width))
    y = max(0, min(y, screen_height - height))
    
    # Set window position and size
    child.geometry(f"{width}x{height}+{x}+{y}")
    logger.debug(f"Centered child window: {width}x{height} at ({x}, {y}) on parent at ({parent_x}, {parent_y})")


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_safe_filename(filename: str) -> str:
    """Get a safe filename by removing invalid characters."""
    import re
    # Remove invalid characters for Windows/Unix filenames
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed"
    return safe_name


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def validate_path(path: Union[str, Path]) -> bool:
    """Validate if a path is accessible and writable."""
    try:
        path = Path(path)
        
        if not path.exists():
            # Try to create it
            path.mkdir(parents=True, exist_ok=True)
        
        # Test write access
        test_file = path / ".taskmover_test"
        test_file.touch()
        test_file.unlink()
        
        return True
        
    except Exception as e:
        logger.warning(f"Path validation failed for '{path}': {e}")
        return False


class ProgressTracker:
    """Simple progress tracking utility."""
    
    def __init__(self, total: int, name: str = "Task"):
        self.total = total
        self.current = 0
        self.name = name
        self.start_time = None
    
    def start(self) -> None:
        """Start tracking progress."""
        import time
        self.start_time = time.time()
        logger.info(f"Started {self.name}: 0/{self.total}")
    
    def update(self, increment: int = 1) -> None:
        """Update progress."""
        self.current = min(self.current + increment, self.total)
        if self.current % max(1, self.total // 10) == 0:  # Log every 10%
            percentage = (self.current / self.total) * 100
            logger.info(f"{self.name} progress: {self.current}/{self.total} ({percentage:.1f}%)")
    
    def finish(self) -> None:
        """Complete progress tracking."""
        import time
        if self.start_time:
            elapsed = time.time() - self.start_time
            logger.info(f"Completed {self.name}: {self.current}/{self.total} in {elapsed:.1f}s")
        else:
            logger.info(f"Completed {self.name}: {self.current}/{self.total}")


class SimpleCache:
    """Simple in-memory cache for frequently accessed data."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache = {}
        self.access_order = []
    
    def get(self, key: str, default=None):
        """Get a value from cache."""
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return default
    
    def set(self, key: str, value) -> None:
        """Set a value in cache."""
        if key in self.cache:
            # Update existing
            self.cache[key] = value
            self.access_order.remove(key)
            self.access_order.append(key)
        else:
            # Add new
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                oldest = self.access_order.pop(0)
                del self.cache[oldest]
            
            self.cache[key] = value
            self.access_order.append(key)
    
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        self.access_order.clear()


def setup_logging(level: str = "INFO", 
                 enable_file_logging: bool = False,
                 log_dir: Optional[Path] = None) -> None:
    """Setup logging configuration."""
    import logging.handlers
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(console_handler)
    
    # Setup file handler if requested
    if enable_file_logging:
        if log_dir is None:
            log_dir = Path.home() / "default_dir" / "logs"
        
        ensure_directory(log_dir)
        log_file = log_dir / "taskmover.log"
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=5
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        logger.info(f"File logging enabled: {log_file}")


# Legacy compatibility functions
def configure_logger(name: str, developer_mode: bool = False) -> logging.Logger:
    """Legacy function for backward compatibility."""
    level = "DEBUG" if developer_mode else "INFO"
    setup_logging(level)
    return logging.getLogger(name)
