"""
Shared constants for Shandalar Tools.

Defines file paths, directory structure, logging configuration, encoding
settings, and parsing constants used across all modules. Directory creation
for user-facing and log directories is handled at import time.
"""
from enum import Enum
from pathlib import Path
import sys

# ==============================
# FILE PATHS
# ==============================
def get_base_dir() -> Path:
    """
    Resolve the base directory for Shandalar Tools.

    Returns the directory containing the executable when running as a
    PyInstaller bundle, or the project root when running from source.
    """    
    # When running as a Pyinstaller executable
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    
    # When running from source
    return Path(__file__).resolve().parent.parent.parent

# root
BASE_DIR = get_base_dir()
# data
DATA_DIR = BASE_DIR / "data"
EDITIONS_DIR = DATA_DIR / "editions"
# logs
LOG_DIR = BASE_DIR / "logs"
# user
USER_DIR = BASE_DIR / "user"
CONFIG_DIR = USER_DIR / "config"
FORMATS_DIR =  USER_DIR / "formats"
OUTPUT_DECK_TRANSLATOR_DIR = USER_DIR / "output_deck_translator"
OUTPUT_FORMAT_GENERATOR_DIR = USER_DIR / "output_format_generator"

for d in [LOG_DIR, CONFIG_DIR, FORMATS_DIR, OUTPUT_DECK_TRANSLATOR_DIR, OUTPUT_FORMAT_GENERATOR_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ==============================
# FILE NAMES & TYPES
# ==============================
FILE_NAME_CONFIG = "config"
FILE_NAME_LOG = "shandalar_tools"

FILE_TYPE_CONFIG = "toml"
FILE_TYPE_FORGE_EDITION = "txt"
FILE_TYPE_LOG = "log"
FILE_TYPE_SHANDALAR_DATA = "csv"

# ==============================
# LOGGER CONSTANTS
# ==============================

LOGGER_FORMAT_CLI = "%(levelname)s: %(message)s"
LOGGER_FORMAT_FILE = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOGGER_FILE_MODE = "w" # "w" = overwrite each run
LOG_PREVIEW_DEFAULT_DELIMITER = ";"

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
        """
        Resolve the encoding scan mode to a boolean full_scan value.

        Returns True for FULL, False for FAST, and the value of
        default_full_scan for AUTO.

        Args:
            default_full_scan: Fallback value used when mode is AUTO.
                Defaults to False.
        """        
        if self == EncodingScanMode.FULL:
            return True
        if self == EncodingScanMode.FAST:
            return False
        return default_full_scan
    
ENCODING_SCAN_VALID_VALUES = [m.name.lower() for m in EncodingScanMode]

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
EDITION_FILE_SUFFIX = ".txt"
EDITIONS_CARD_NAME_STARTING_COLUMN = 2
FORGE_CARDS_HEADER = "[cards]"
FORGE_EDITION_CARD_DELIMITER = " @"
SCRYFALL_CODE_PREFIX = "ScryfallCode="

# ==============================
# OUTPUT / DISPLAY
# ==============================
PREVIEW_LIMIT = 5