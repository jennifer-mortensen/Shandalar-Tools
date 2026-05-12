"""
Logging utilities for Shandalar Tools.

Provides helpers for configuring logging across all CLI entry points,
and for logging previews and duplicate entries with consistent formatting.
"""
from common import common_const, common_utils
from config import config_runtime
from typing import Callable, Iterable
import logging

logger = logging.getLogger(__name__)

def configure_logging() -> None:
    """
    Configure logging for both CLI and file output.

    CLI logging displays human-readable messages, while file logging
    includes debug information and full exception tracebacks.
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
        mode=common_const.LOGGER_FILE_MODE,
        encoding=common_const.DEFAULT_ENCODING
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers = [console, file_handler]

def log_preview_if_any(
        items: Iterable[str],
        message: str,
        log_function: Callable = logger.warning,
        delimiter: str = common_const.LOG_PREVIEW_DEFAULT_DELIMITER
) -> bool:
    """
    Log a preview of a collection if it is non-empty.

    Displays up to preview_limit items as a preview. If additional items
    exist beyond the preview, notes that the full list was written to the
    log file at debug level.

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

    preview_limit = config_runtime.get_common_config().log_preview_limit
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

    logger.debug("Full list: %s", sorted_items)
    return True

def log_duplicates(
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
    sorted_duplicates: list[str] = sorted(duplicates)
    entry_type = common_utils.pluralize(quantity=len(sorted_duplicates), singular=entry_type_singular, plural=entry_type_plural)
    message: str = f"{preamble}{len(sorted_duplicates)} duplicate {entry_type} detected across the {list_name_1} and {list_name_2} lists."
    return log_preview_if_any(items=sorted_duplicates, message=message, log_function=log_function)