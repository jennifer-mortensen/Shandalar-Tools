"""
Application logging helpers.

Provides reusable helpers for logging common application
messages with consistent formatting, including previews,
duplicate entries, and unexpected failures.
"""
from collections.abc import Collection
from common import log_const, settings, string_utils
from typing import Callable, Iterable
import logging, sys

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
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

    entry_type: str = string_utils.pluralize(quantity=len(duplicates_list), singular=entry_type_singular, plural=entry_type_plural)
    message: str = f"{preamble}{len(duplicates_list)} duplicate {entry_type} detected across the {list_name_1} and {list_name_2} lists."

    return log_preview_if_any(items=duplicates_list, message=message, log_function=log_function)

def log_preview_if_any(
        items: Collection[str],
        message: str,
        log_function: Callable = logger.warning,
        delimiter: str = log_const.LOG_PREVIEW_DEFAULT_DELIMITER
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

    preview_limit = settings.get_log_preview_limit()
    is_truncated: bool = len(sorted_items) > preview_limit

    preview: str = (delimiter + " ").join(sorted_items[:preview_limit])

    suffix: str = ""
    extra_args: tuple = () # pass nothing by default

    if is_truncated:
        suffix = "...\nFull details written to the log file (%s)"
        extra_args = (settings.get_log_file_path(),)

    log_function(f"%s %s: %s{suffix}",
        message,
        string_utils.pluralize(quantity=len(sorted_items), singular="Example",  plural="Examples"),
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
    print(f"ERROR: An unexpected error occurred. See the log file ({settings.get_log_file_path()}) for details.")
    sys.exit(1)    