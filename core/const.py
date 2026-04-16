"""
Centralized constants for shandalar-tools.

This module defines file paths, logging formats, encoding settings,
and MTG: Forge format templates used throughout the application.
"""
from pathlib import Path
import sys

# ==============================
# FILE PATHS
# ==============================

def get_base_dir() -> Path:
    # When running as a PyInstaller executable
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    # When running from source
    return Path(__file__).resolve().parent.parent


# Data folders
BASE_DIR = get_base_dir()
DATA_DIR = BASE_DIR / "data"
EDITIONS_DIR = DATA_DIR / "editions"

# Data / Config Files
FILE_SHANDALAR_CSV = DATA_DIR / "Shandalar Card List.csv"
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
# FORGE FORMAT CONSTRUCTORS
# ==============================

FORGE_FORMAT_BODY_STANDARD = """[format]
Name:Standard
Order:101
Subtype:Standard
Type:Sanctioned
Banned: {banned_cards}
Sets: {set_codes}"""

# ==============================
# OUTPUT / DISPLAY
# ==============================
PREVIEW_LIMIT = 5