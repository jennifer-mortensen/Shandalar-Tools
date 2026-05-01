"""
Centralized constants for shandalar-tools.

This module defines file paths, logging formats, and encoding settings.
"""
from enum import Enum
from pathlib import Path
import sys

# TODO: Migrate constants to their correct directories: format_generator or deck_translator.

# ==============================
# FILE PATHS
# ==============================

def get_base_dir() -> Path:
    # When running as a Pyinstaller executable
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    
    # When running from source
    return Path(__file__).resolve().parent.parent

# Data folders
BASE_DIR = get_base_dir()
DATA_DIR = BASE_DIR / "data"
EDITIONS_DIR = DATA_DIR / "editions"
LOG_DIR = BASE_DIR / "logs"
USER_CONFIG_DIR = BASE_DIR / "user_config"
USER_OUTPUT_DIR = BASE_DIR / "user_output"

LOG_DIR.mkdir(exist_ok=True)
USER_OUTPUT_DIR.mkdir(exist_ok=True)

# Data / Config Files
FILE_SHANDALAR_CSV = DATA_DIR / "shandalar_2016.csv"
FILE_NAME_CONFIG = "config"
FILE_TYPE_CONFIG = "csv"
FILE_NAME_OUTPUT = "Standard"
FILE_TYPE_OUTPUT = "txt"
FILE_NAME_USER_BANNED = "user_banned"
FILE_TYPE_USER_BANNED = "csv"
FILE_NAME_LOG = "shandalar_tools"
FILE_TYPE_LOG = "log"

# ==============================
# LOGGER CONSTANTS
# ==============================

LOGGER_FORMAT_CLI = "%(levelname)s: %(message)s"
LOGGER_FORMAT_FILE = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOGGER_FILE_MODE = "w" # "w" = overwrite each run

# ==============================
# FILE ENCODING
# ==============================
DEFAULT_ENCODING = "utf-8"
FALLBACK_ENCODING = "latin-1"
FILE_ENCODINGS = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
FILE_ENCODING_READ_SIZE_DEFAULT = 10240

class EncodingScanMode(Enum):
    AUTO = "auto"
    FAST = "fast"
    FULL = "full"

    def resolve(self, default_full_scan: bool = False) -> bool:
        if self == EncodingScanMode.FULL:
            return True
        if self == EncodingScanMode.FAST:
            return False
        return default_full_scan

# ==============================
# FILE NAMING
# ==============================
EDITION_FILE_SUFFIX = ".txt"

# ==============================
# CSV / TEXT PARSING
# ==============================
DEFAULT_CSV_DELIMITER = ","
COMMENT_PREFIX = "#"

# ==============================
# SHANDALAR DATA
# ==============================
SHANDALAR_CARD_NAME_STARTING_COLUMN = 0

# ==============================
# FORGE DATA
# ==============================
EDITIONS_CARD_NAME_STARTING_COLUMN = 2
FORGE_CARDS_HEADER = "[cards]"
FORGE_EDITION_CARD_DELIMITER = " @"
SCRYFALL_CODE_PREFIX = "ScryfallCode="

# ==============================
# OUTPUT / DISPLAY
# ==============================
PREVIEW_LIMIT = 5