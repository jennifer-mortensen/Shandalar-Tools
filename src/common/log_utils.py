"""
Logging utilities for Shandalar Tools.

Provides helpers for configuring logging across all CLI entry points,
and for logging previews and duplicate entries with consistent formatting.
"""
from collections.abc import Collection
from common import common_const, common_utils
from config import runtime
from typing import Callable, Iterable
import logging

logger = logging.getLogger(__name__)

def initialize_logging() -> None:
    """
    Initialize bootstrap logging for the application.

    Configures console and file logging using safe append-mode behavior
    before runtime configuration has been loaded. Runtime logging behavior
    may be updated later after CommonConfig initialization.
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
        filename=common_const.LOG_DIR / f"{common_const.FILE_NAME_LOG}.{common_const.FILE_TYPE_LOG}",
        mode="a",
        encoding=common_const.DEFAULT_ENCODING
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers = [console, file_handler]

def update_logging_write_mode(overwrite: bool) -> None:
    """
    Update the file logging mode after runtime configuration is loaded.

    Replaces the existing FileHandler with a new handler using either
    overwrite ("w") or append ("a") mode while preserving existing
    console logging configuration.

    Args:
        overwrite: If True, recreate the log file in overwrite mode.
            If False, continue appending to the existing log.
    """
    root = logging.getLogger()

    # Remove existing file handlers
    for handler in root.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            root.removeHandler(handler)
            handler.close()

    # Create replacement file handler
    file_handler = logging.FileHandler(
        filename=common_const.LOG_DIR / f"{common_const.FILE_NAME_LOG}.{common_const.FILE_TYPE_LOG}",
        mode="w" if overwrite else "a",
        encoding=common_const.DEFAULT_ENCODING
    )

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(common_const.LOGGER_FORMAT_FILE))

    root.addHandler(file_handler)

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

    Returns True if anything was logged, False otherwise.

    Args:
        items: The collection to preview.
        message: The message to prepend to the preview.
        log_function: Logging function to use. Defaults to logger.warning.
        delimiter: Delimiter used between preview items.
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
        suffix = "...\nFull details written to the log file (default: %s)"
        extra_args = (common_const.LOG_DIR / f"{common_const.FILE_NAME_LOG}.{common_const.FILE_TYPE_LOG}",)

    log_function(f"%s %s: %s{suffix}",
        message,
        common_utils.pluralize(quantity=len(sorted_items), singular="Example",  plural="Examples"),
        preview,
        *extra_args
    )

    if is_truncated:
        logger.debug("Full list: %s", sorted_items)
    return True

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
    to log_preview_if_any. Returns True if duplicates were logged,
    False otherwise.

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
    """
    duplicates_list: list[str] = list(duplicates)

    entry_type: str = common_utils.pluralize(quantity=len(duplicates_list), singular=entry_type_singular, plural=entry_type_plural)
    message: str = f"{preamble}{len(duplicates_list)} duplicate {entry_type} detected across the {list_name_1} and {list_name_2} lists."

    return log_preview_if_any(items=duplicates_list, message=message, log_function=log_function)