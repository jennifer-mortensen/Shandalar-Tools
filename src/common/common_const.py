"""
Shared constants for Shandalar Tools.

Defines file paths, file types, logging settings, encoding behavior,
user-facing messages, and other application-wide constants used across
the project. Required user and log directories are created during
module initialization.
"""
from common.common_types import EncodingScanMode
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
FORMAT_CONFIG_DIR: Path = USER_DIR / "input_formats"
FORMAT_DIR: Path = USER_DIR / "output_formats"
# deck translator
INPUT_DECK_DIR: Path = USER_DIR / "input_decks"
OUTPUT_FORGE_DECK_DIR: Path = USER_DIR / "output_decks_forge"
OUTPUT_SHANDALAR_DECK_DIR: Path = USER_DIR / "output_decks_shandalar"

for d in [LOG_DIR, CONFIG_DIR, FORMAT_CONFIG_DIR, FORMAT_DIR, INPUT_DECK_DIR, OUTPUT_FORGE_DECK_DIR, OUTPUT_SHANDALAR_DECK_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ==============================
# FILE NAMES & TYPES
# ==============================
FILE_NAME_CONFIG: str = "config"
FILE_TYPE_CONFIG: str = "toml"
FILE_NAME_LOG: str = "shandalar_tools"
FILE_TYPE_LOG: str = "log"

FILE_TYPE_FORMAT_CONFIG: str = "toml"

# MTG Types
FILE_TYPE_DECK: str = "dck"

# Forge Types
FILE_TYPE_FORGE_EDITION: str = "txt"
FILE_TYPE_FORGE_FORMAT: str = "txt"

# Shandalar Types
FILE_TYPE_SHANDALAR_DATA: str = "csv"

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
# VALID VALUES
# ==============================
ENCODING_SCAN_VALID_VALUES: list[str] = [m.name.lower() for m in EncodingScanMode]