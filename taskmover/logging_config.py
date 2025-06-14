import logging
import colorlog

def configure_logger(name="TaskMover", developer_mode=False):
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

    # Ensure all component loggers propagate to root and have no extra handlers
    for comp in ["UI", "File Operations", "Rules", "Settings"]:
        comp_logger = logging.getLogger(comp)
        comp_logger.propagate = True
        comp_logger.handlers = []
        # Do not set level here; will be set by apply_logging_component_settings

    # Main app logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if developer_mode else logging.INFO)
    return logger

def apply_logging_component_settings(settings):
    """
    Enable or disable logging for each component based on settings['logging_components'] and filter by per-logger log level.
    """
    import logging
    loggers = ["UI", "File Operations", "Rules", "Settings", "geometry", "frames", "rule_ids"]
    levels = settings.get("logging_levels", {})
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        enabled = settings.get("logging_components", {}).get(logger_name, 1)
        level_name = levels.get(logger_name, settings.get("logging_level", "WARNING"))
        level = getattr(logging, level_name, logging.WARNING)
        if enabled:
            logger.setLevel(level)
        else:
            logger.setLevel(logging.CRITICAL + 1)
