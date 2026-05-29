"""
Shared constants for Shandalar Tools.

Defines file paths, directory structure, logging configuration, encoding
settings, and parsing constants used across all modules. Directory creation
for user-facing and log directories is handled at import time.
"""
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
BASE_DIR: Path = get_base_dir()
# data
DATA_DIR: Path = BASE_DIR / "data"
EDITIONS_DIR: Path = DATA_DIR / "editions"
# logs
LOG_DIR: Path = BASE_DIR / "logs"
# user
USER_DIR: Path = BASE_DIR / "user"
CONFIG_DIR: Path = USER_DIR / "config"
# format generator
INPUT_FORMAT_DIR: Path =  USER_DIR / "input_formats"
OUTPUT_FORMAT_DIR: Path = USER_DIR / "output_formats"
# deck translator
INPUT_DECK_DIR: Path = USER_DIR / "input_decks"
OUTPUT_FORGE_DECK_DIR: Path = USER_DIR / "output_decks_forge"
OUTPUT_SHANDALAR_DECK_DIR: Path = USER_DIR / "output_decks_shandalar"

for d in [LOG_DIR, CONFIG_DIR, INPUT_FORMAT_DIR, OUTPUT_FORMAT_DIR, INPUT_DECK_DIR, OUTPUT_FORGE_DECK_DIR, OUTPUT_SHANDALAR_DECK_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ==============================
# FILE NAMES & TYPES
# ==============================
FILE_NAME_CONFIG: str = "config"
FILE_NAME_LOG: str = "shandalar_tools"

FILE_TYPE_CONFIG: str = "toml"
FILE_TYPE_FORGE_EDITION: str = "txt"
FILE_TYPE_LOG: str = "log"
FILE_TYPE_SHANDALAR_DATA: str = "csv"
FILE_TYPE_DECK: str = "dck" # TODO: Separate into Forge and Shandalar constants

# ==============================
# LOGGER CONSTANTS
# ==============================
LOGGER_FORMAT_CLI: str = "%(levelname)s: %(message)s"
LOGGER_FORMAT_FILE: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_PREVIEW_DEFAULT_DELIMITER: str = ";"
LOG_PREVIEW_LIMIT_MINIMUM: int = 1
LOG_PREVIEW_LIMIT_FIELD_NAME: str = "Log preview limit"

# ==============================
# FILE ENCODING
# ==============================
DEFAULT_ENCODING: str = "utf-8"
FALLBACK_ENCODING: str = "latin-1"
FILE_ENCODINGS: list[str] = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
FILE_ENCODING_READ_SIZE_DEFAULT: int = 10240

# ==============================
# CSV / TEXT PARSING
# ==============================
DEFAULT_CSV_DELIMITER: str = ","
COMMENT_PREFIX: str = "#"

# ==============================
# SHANDALAR DATA FIELDS
# ==============================
SHANDALAR_DATA_FIELD_CARD_NAME: int = 0
SHANDALAR_DATA_FIELD_RELEASE_DATE: int = 1
SHANDALAR_DATA_FIELD_SET: int = 2
SHANDALAR_DATA_FIELD_RARITY: int = 3
SHANDALAR_DATA_FIELD_SHANDALAR_ID: int = 4
SHANDALAR_DATA_FIELD_GATHERER_ID: int = 5
SHANDALAR_DATA_FIELD_TYPE: int = 6
SHANDALAR_DATA_FIELD_COST: int = 7
SHANDALAR_DATA_FIELD_POWER: int = 8
SHANDALAR_DATA_FIELD_TOUGHNESS: int = 9
SHANDALAR_DATA_FIELD_TEXT: int = 10
SHANDALAR_DATA_FIELD_CTYPE: int = 11
SHANDALAR_DATA_FIELD_COLOR_IDENTITY: int = 12

# ==============================
# FORGE DATA
# ==============================
EDITION_FILE_SUFFIX: str = ".txt"
EDITIONS_CARD_NAME_STARTING_COLUMN: int = 2
FORGE_CARDS_HEADER: str = "[cards]"
FORGE_EDITION_CARD_DELIMITER: str = " @"
SCRYFALL_CODE_PREFIX: str = "ScryfallCode="