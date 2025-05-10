import os
import sys

# Add the parent directory to the system path to ensure the package is recognized
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from taskmover.logging_config import configure_logger
from taskmover.app import main
from taskmover.config import load_rules, create_default_rules

def ensure_directory_exists(directory, logger):
    """Ensure a directory exists, creating it if necessary."""
    try:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")
    except Exception as e:
        logger.error(f"Failed to create directory '{directory}': {e}")
        raise

def load_or_initialize_rules(config_path, fallback_path, logger):
    """Load rules from a configuration file or initialize default rules."""
    try:
        if not os.path.exists(config_path):
            logger.warning("Configuration file not found. Creating default rules.")
            return create_default_rules(config_path)
        logger.info("Loading rules from configuration file.")
        return load_rules(config_path, fallback_path)
    except Exception as e:
        logger.error(f"Error loading or initializing rules: {e}")
        raise

def run():
    logger = configure_logger()

    # Define configuration paths
    config_directory = os.path.expanduser("~/default_dir/config")
    ensure_directory_exists(config_directory, logger)

    config_path = os.path.join(config_directory, "rules.yml")
    fallback_path = os.path.join(config_directory, "fallback_conf.yml")

    # Load or initialize rules
    rules = load_or_initialize_rules(config_path, fallback_path, logger)

    # Start the main application
    logger.info("Starting TaskMover application.")
    try:
        main(rules, logger)
    except Exception as e:
        logger.critical(f"Critical error in application: {e}")
        raise

if __name__ == "__main__":
    run()
