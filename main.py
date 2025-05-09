import sys
import os
from taskmover.logging_config import configure_logger

# Add the current directory to the system path to ensure the package is recognized
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from taskmover.app import main
from taskmover.config import load_rules, create_default_rules

# Configure logger
logger = configure_logger()

if __name__ == "__main__":
    # Ensure rules are loaded before starting the application
    config_directory = os.path.expanduser("~/default_dir/config")
    os.makedirs(config_directory, exist_ok=True)
    config_path = os.path.join(config_directory, "rules.yml")
    fallback_path = os.path.join(config_directory, "fallback_conf.yml")

    # Load rules or create default ones if not present
    if not os.path.exists(config_path):
        logger.info("Creating default rules as no configuration file exists.")
        rules = create_default_rules(config_path)
    else:
        logger.info("Loading rules from configuration file.")
        rules = load_rules(config_path, fallback_path)

    # Start the main application
    main(rules, logger)
