import logging
import colorlog

def configure_logger(name="TaskMover", developer_mode=False):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if developer_mode else logging.INFO)

    # Create a colored console handler
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    ))

    # Add the handler to the logger
    logger.handlers = [handler]
    return logger
