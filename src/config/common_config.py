"""
Shared configuration dataclass for Shandalar Tools.

Defines settings common to all tools, including card pool selection,
encoding scan behavior, and logging preferences. Instantiated during
runtime initialization and accessed globally through runtime.py.
"""
from common.common_const import EncodingScanMode
from dataclasses import dataclass

# ==============================
# DEFAULTS
# ==============================
DATA_CARD_POOL_DEFAULT = "shandalar_2016"
IO_ENCODING_SCAN_DEFAULT = EncodingScanMode.AUTO
LOG_PREVIEW_LIMIT_DEFAULT = 5
LOG_OVERWRITE_DEFAULT = True

# ==============================
# DATA CLASSES
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