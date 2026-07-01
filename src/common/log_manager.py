"""
Logging system management.

Provides functions for initializing and reconfiguring the
application's logging subsystem. These functions configure
Python's logging infrastructure but do not perform
application-specific logging.
"""
from common import file_const, log_const, paths
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def initialize_logging(log_file_name: Path) -> None:
    """
    Initialize bootstrap logging for the application.

    Configures console and file logging before runtime configuration
    has been loaded. The specified log file is normalized and opened
    in append mode during bootstrap. Runtime logging behavior may be
    updated later after CommonConfig initialization.

    Args:
        log_file_name: Name of the the log file to use.
    """
    formatter = logging.Formatter(log_const.LOGGER_FORMAT_FILE)

    # CLI-level logging. Prioritize readability.
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(log_const.LOGGER_FORMAT_CLI))

    # Filter out exception tracebacks from CLI
    class NoExceptionTracebackFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.exc_info is None

    console.addFilter(NoExceptionTracebackFilter())

    # File-level logging. Full fidelity.
    file_handler = logging.FileHandler(
        filename=paths.build_log_file_path(log_file_name),
        mode="a",
        encoding=file_const.DEFAULT_ENCODING
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers = [console, file_handler]

def refresh_logging(log_file_name: Path, overwrite: bool) -> None:
    """
    Refresh file logging.

    Rebuilds the active file handler using the specified log file
    name and overwrite behavior. Existing console logging handlers
    are preserved.

    Args:
        log_file_name: Name of the active log file.
        overwrite: Whether to overwrite the log file if it exists.
            If False, log output is appended.
    """
    root = logging.getLogger()

    # Remove existing file handlers
    for handler in root.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            root.removeHandler(handler)
            handler.close()

    # Create replacement file handler
    file_handler = logging.FileHandler(
        filename=paths.build_log_file_path(log_file_name),
        mode="w" if overwrite else "a",
        encoding=file_const.DEFAULT_ENCODING
    )

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_const.LOGGER_FORMAT_FILE))

    root.addHandler(file_handler)