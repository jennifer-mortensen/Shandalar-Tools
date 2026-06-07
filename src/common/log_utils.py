"""
Logging utilities for Shandalar Tools.

Provides helpers for configuring logging across all CLI entry points,
and for logging previews and duplicate entries with consistent formatting.
"""
from collections.abc import Collection
from common import common_const, common_utils
from common import runtime
from typing import Callable, Iterable
from pathlib import Path
import logging
import sys

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def initialize_logging(file_path: Path) -> None:
    """
    Initialize bootstrap logging for the application.

    Configures console and file logging before runtime configuration
    has been loaded. The specified log file is normalized and opened
    in append mode during bootstrap. Runtime logging behavior may be
    updated later after CommonConfig initialization.

    Args:
        file_path: Path to the log file to use.
    """
    formatter = logging.Formatter(common_const.LOGGER_FORMAT_FILE)

    # CLI-level logging. Prioritize readability.
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(common_const.LOGGER_FORMAT_CLI))

    # Filter out exception tracebacks from CLI
    class NoExceptionTracebackFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.exc_info is None

    console.addFilter(NoExceptionTracebackFilter())

    # File-level logging. Full fidelity.
    file_handler = logging.FileHandler(
        filename=file_path,
        mode="a",
        encoding=common_const.DEFAULT_ENCODING
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers = [console, file_handler]

def log_duplicates_if_any(
        duplicates: Iterable[str],
        list_name_1: str,
        list_name_2: str,
        entry_type_singular: str = "entry",        
        entry_type_plural: str = "entries",
        preamble: str = "",
        log_function: Callable = logger.warning
) -> bool:
    """
    Log a preview of duplicate entries detected across two named lists.

    Builds a pluralized conflict message and delegates preview logging
    to log_preview_if_any.

    Args:
        duplicates: The duplicate entries to log.
        list_name_1: Name of the first list, used in the log message.
        list_name_2: Name of the second list, used in the log message.
        entry_type_singular: Singular form of the entry type used in the
            log message. Defaults to "entry".
        entry_type_plural: Plural form of the entry type used in the
            log message. Defaults to "entries".
        preamble: Optional string prepended to the log message.
        log_function: Logging function to use. Defaults to logger.warning.

    Returns:
        True if duplicates were logged, otherwise False.
    """
    duplicates_list: list[str] = list(duplicates)

    entry_type: str = common_utils.pluralize(quantity=len(duplicates_list), singular=entry_type_singular, plural=entry_type_plural)
    message: str = f"{preamble}{len(duplicates_list)} duplicate {entry_type} detected across the {list_name_1} and {list_name_2} lists."

    return log_preview_if_any(items=duplicates_list, message=message, log_function=log_function)

def log_preview_if_any(
        items: Collection[str],
        message: str,
        log_function: Callable = logger.warning,
        delimiter: str = common_const.LOG_PREVIEW_DEFAULT_DELIMITER
) -> bool:
    """
    Log a preview of a collection if it is non-empty.

    Displays up to the configured runtime preview limit as a preview. If
    additional items exist beyond the preview, notes that the full list
    was written to the log file at debug level.

    Args:
        items: The collection to preview.
        message: The message to prepend to the preview.
        log_function: Logging function to use. Defaults to logger.warning.
        delimiter: Delimiter used between preview items.

    Returns:
        True if any items were logged, otherwise False.
    """
    sorted_items: list[str] = sorted(items)

    if not sorted_items:
        return False

    preview_limit = runtime.get_log_preview_limit()
    is_truncated: bool = len(sorted_items) > preview_limit

    preview: str = (delimiter + " ").join(sorted_items[:preview_limit])

    suffix: str = ""
    extra_args: tuple = () # pass nothing by default

    if is_truncated:
        suffix = "...\nFull details written to the log file (%s)"
        extra_args = (runtime.get_log_file_path(),)

    log_function(f"%s %s: %s{suffix}",
        message,
        common_utils.pluralize(quantity=len(sorted_items), singular="Example",  plural="Examples"),
        preview,
        *extra_args
    )

    if is_truncated:
        logger.debug("Full list: %s", sorted_items)
    return True    

def log_unexpected_and_exit() -> None:
    """
    Log and report an unexpected CLI exception, then terminate execution.

    Writes the full exception traceback to the configured log file,
    displays a simplified user-facing error message pointing to the
    log location, and exits the process with a non-zero status code.
    """        
    logger.exception("Unexpected error")
    # Separate CLI-level output. Full exception is logged externally just above.        
    print(f"ERROR: An unexpected error occurred. See the log file ({runtime.get_log_file_path()}) for details.")
    sys.exit(1)    

def refresh_logging() -> None:
    """
    Refresh file logging using the current runtime configuration.

    Rebuilds the active FileHandler using the current runtime log
    file path and overwrite mode. Existing console logging handlers
    are preserved.
    """
    root = logging.getLogger()
    overwrite: bool = runtime.get_log_overwrite()

    # Remove existing file handlers
    for handler in root.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            root.removeHandler(handler)
            handler.close()

    # Create replacement file handler
    file_handler = logging.FileHandler(
        filename=runtime.get_log_file_path(),
        mode="w" if overwrite else "a",
        encoding=common_const.DEFAULT_ENCODING
    )

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(common_const.LOGGER_FORMAT_FILE))

    root.addHandler(file_handler)