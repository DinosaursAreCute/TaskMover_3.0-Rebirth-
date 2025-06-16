import logging
import colorlog
import traceback
import inspect

# Global dictionary to store logger descriptions for UI settings
LOGGER_DESCRIPTIONS = {}

def configure_logger(name,developer_mode=False):
    # Set up root logger with colorlog if not already set
    if not logging.getLogger().handlers:
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        ))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.DEBUG if developer_mode else logging.INFO)

    # Component loggers with descriptions (displayed in settings)
    component_loggers = {
        "UI": "User interface events and updates",
        "Developer": "Developer-specific actions and debugging",
        "UI Events": "User interaction events and responses",
        "UI Widgets": "Widget creation and management",
        "TaskMover": "Main application events and state changes",
        "File Operations": "File system operations",
        "Rules": "Rule management and processing",
        "Settings": "Settings management",
        "geometry": "UI layout and sizing calculations",
        "frames": "Frame management and widget hierarchy",
        "rule_ids": "Rule ID tracking and lifecycle",
        "scrolling": "Scrolling behavior and scrollregion updates"    }
    
    # Ensure all component loggers are properly configured
    for comp, description in component_loggers.items():
        comp_logger = logging.getLogger(comp)
        comp_logger.propagate = True
        comp_logger.handlers = []
        # Store descriptions in our global dict for settings UI
        LOGGER_DESCRIPTIONS[comp] = description
        # Ensure logger levels are set dynamically based on settings
        comp_logger.setLevel(logging.DEBUG if developer_mode else logging.INFO)

    # Main app logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if developer_mode else logging.INFO)
    return logger

def apply_logging_component_settings(settings):
    """
    Enable or disable logging for each component based on settings.
    
    Args:
        settings: Dictionary containing logging configuration:
            - logging_components: Dict mapping logger names to 0/1 (disabled/enabled)
            - logging_levels: Dict mapping logger names to level names
            - logging_level: Default level name if not specified per-component
    """
    # Make sure we include all defined loggers
    for logger_name in LOGGER_DESCRIPTIONS.keys():
        logger = logging.getLogger(logger_name)
        
        # Check if this logger is enabled in settings
        enabled = settings.get("logging_components", {}).get(logger_name, 1)
        
        # Get the specific level for this logger, or fall back to default
        levels = settings.get("logging_levels", {})
        level_name = levels.get(logger_name, settings.get("logging_level", "WARNING"))
        level = getattr(logging, level_name, logging.WARNING)
        
        if enabled:
            logger.setLevel(level)
        else:
            # Set to a level higher than CRITICAL to effectively disable
            logger.setLevel(logging.CRITICAL + 1)
              # Log the configuration for debugging
        settings_logger = logging.getLogger("Settings")
        if enabled:
            settings_logger.debug(f"Logger '{logger_name}' enabled at level {level_name}")
        else:
            settings_logger.debug(f"Logger '{logger_name}' disabled")

def get_caller_info():
    """Get the filename and function name of the caller for logging context."""
    frame = inspect.currentframe()
    try:
        # Go back two frames: get_caller_info -> logger call -> actual function
        if frame and frame.f_back and frame.f_back.f_back:
            caller_frame = frame.f_back.f_back
            filename = caller_frame.f_code.co_filename.split('\\')[-1]  # Get just the filename
            function_name = caller_frame.f_code.co_name
            line_number = caller_frame.f_lineno
            return f"{filename}:{function_name}:{line_number}"
    except:
        pass
    return "unknown:unknown:0"

# Enhanced logging functions that include file context for warnings and errors
def log_warning_with_context(logger, message):
    """Log a warning with file context information."""
    context = get_caller_info()
    logger.warning(f"[{context}] {message}")

def log_error_with_context(logger, message):
    """Log an error with file context information."""
    context = get_caller_info()
    logger.error(f"[{context}] {message}")

def log_exception_with_context(logger, message):
    """Log an exception with file context and traceback."""
    context = get_caller_info()
    logger.error(f"[{context}] {message}", exc_info=True)
