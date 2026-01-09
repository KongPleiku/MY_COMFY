import logging
import sys


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set the lowest level to capture all logs

    # Create a handler to write logs to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)  # The handler also has a level

    # Create a formatter and set it for the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    # Avoid adding handlers multiple times
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
