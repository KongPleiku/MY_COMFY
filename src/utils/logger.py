import logging
import sys
import flet as ft

LOG_COLORS = {
    "DEBUG": ft.colors.GREY,
    "INFO": ft.colors.WHITE,
    "WARNING": ft.colors.YELLOW,
    "ERROR": ft.colors.RED,
    "CRITICAL": ft.colors.RED_700,
}


class FletLogHandler(logging.Handler):
    def __init__(self, log_display: ft.ListView):
        super().__init__()
        self.log_display = log_display

    def emit(self, record):
        msg = self.format(record)
        color = LOG_COLORS.get(record.levelname, ft.colors.WHITE)
        self.log_display.controls.append(ft.Text(msg, color=color))
        if self.log_display.page:
            self.log_display.update()


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


def set_flet_logging(log_display: ft.ListView):
    flet_handler = FletLogHandler(log_display)
    flet_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    flet_handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    # Remove all existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add the new Flet handler
    root_logger.addHandler(flet_handler)


def set_default_logging():
    root_logger = logging.getLogger()

    # Remove all existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add the default stdout handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
