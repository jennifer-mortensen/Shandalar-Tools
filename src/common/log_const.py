"""
Logging-related constants for Shandalar Tools.

Defines shared logging formats, preview settings,
and validation metadata used by the logging subsystem.
"""

# ==============================
# LOGGER CONSTANTS
# ==============================
LOGGER_FORMAT_CLI: str = "%(levelname)s: %(message)s"
LOGGER_FORMAT_FILE: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_PREVIEW_DEFAULT_DELIMITER: str = ";"
LOG_PREVIEW_LIMIT_MINIMUM: int = 1
LOG_PREVIEW_LIMIT_FIELD_NAME: str = "Log preview limit"
