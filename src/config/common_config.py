"""
Shared configuration dataclass for Shandalar Tools.

Defines settings common to all tools, including card pool selection,
encoding scan behavior, and logging preferences. Instantiated during
runtime initialization and accessed globally through runtime.py.
"""
from common.common_types import EncodingScanMode
from common import common_const
from dataclasses import dataclass
from pathlib import Path

# ==============================
# DEFAULTS
# ==============================
DATA_CARD_POOL_DEFAULT: str = "shandalar_2016"
IO_ENCODING_SCAN_DEFAULT: EncodingScanMode = EncodingScanMode.AUTO
LOG_PREVIEW_LIMIT_DEFAULT: int = 5
LOG_OVERWRITE_DEFAULT: bool = True
LOG_FILE_PATH_DEFAULT: Path = common_const.LOG_DIR / f"shandalar_tools.{common_const.FILE_TYPE_LOG}" # default fallback

# ==============================
# DATACLASSES
# ==============================
@dataclass
class CommonConfig:
    """
    Configuration settings shared across all Shandalar Tools.

    Stores runtime-wide settings including card pool selection,
    encoding scan behavior, and logging preferences.
    """
    data_shandalar_card_pool: str = DATA_CARD_POOL_DEFAULT
    io_encoding_scan: EncodingScanMode = IO_ENCODING_SCAN_DEFAULT
    log_preview_limit: int = LOG_PREVIEW_LIMIT_DEFAULT
    log_overwrite: bool = LOG_OVERWRITE_DEFAULT
    log_file_path: Path = LOG_FILE_PATH_DEFAULT