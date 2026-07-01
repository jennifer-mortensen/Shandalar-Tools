"""
Constants used by the path construction subsystem.

Defines directory locations, file names, file suffixes, and
file extensions used to construct paths throughout Shandalar
Tools.
"""
from pathlib import Path
import sys

# ==============================
# DIRECTORIES
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
FORGE_DATA_DIR: Path = DATA_DIR / "forge"
FORGE_EDITIONS_DIR: Path = FORGE_DATA_DIR / "editions"
SHANDALAR_DATA_DIR: Path = DATA_DIR / "shandalar"
SHANDALAR_DATASETS_DIR: Path = SHANDALAR_DATA_DIR / "datasets"
# logs
LOG_DIR: Path = BASE_DIR / "logs"
# user
USER_DIR: Path = BASE_DIR / "user"
CONFIG_DIR: Path = USER_DIR / "config"
# format generator
FORMAT_CONFIG_DIR: Path = USER_DIR / "input_formats"
FORMAT_DIR: Path = USER_DIR / "output_formats"
# deck converter
INPUT_DECK_DIR: Path = USER_DIR / "input_decks"
OUTPUT_FORGE_DECK_DIR: Path = USER_DIR / "output_decks_forge"
OUTPUT_SHANDALAR_DECK_DIR: Path = USER_DIR / "output_decks_shandalar"

# Data Map Directories
# -- Common
NAME_TO_NORMALIZED_NAME_MAP_DIR: Path = DATA_DIR
# -- Forge
FORGE_EDITION_TO_CODE_MAP_DIR: Path = FORGE_DATA_DIR
# -- Shandalar
DEFAULT_SHANDALAR_TO_FORGE_EDITION_MAP_DIR: Path = SHANDALAR_DATA_DIR
SHANDALAR_TO_FORGE_EDITION_MAP_DIR: Path = SHANDALAR_DATASETS_DIR
SHANDALAR_CARD_TO_FORGE_EDITION_MAP_DIR: Path = SHANDALAR_DATASETS_DIR

for d in [LOG_DIR, CONFIG_DIR, FORMAT_CONFIG_DIR, FORMAT_DIR, INPUT_DECK_DIR, OUTPUT_FORGE_DECK_DIR, OUTPUT_SHANDALAR_DECK_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ==============================
# FILE NAMES
# ==============================
# Common Names
# -- Config
FILE_NAME_CONFIG: str = "config"
# -- Data Maps
NAME_TO_NORMALIZED_NAME_MAP_FILE_NAME: str = "name_normalization_map"
# -- Log
FILE_NAME_LOG: str = "shandalar_tools"

# MTG Names
# -- Forge
FORGE_EDITION_TO_CODE_MAP_FILE_NAME: str = "forge_code_map"
# -- Shandalar
DEFAULT_SHANDALAR_TO_FORGE_EDITION_MAP_FILE_NAME: str = "default_edition_map"

# ==============================
# FILE SUFFIXES
# ==============================
# MTG Names
# -- Shandalar
SHANDALAR_TO_FORGE_EDITION_MAP_FILE_NAME_SUFFIX: str = "_edition_map"
SHANDALAR_CARD_TO_FORGE_EDITION_MAP_FILE_NAME_SUFFIX: str = "_card_map"

# ==============================
# FILE EXTENSIONS
# ==============================
# Common Extensions
# -- Config
FILE_EXTENSION_FORMAT_CONFIG: str = "toml"
FILE_EXTENSION_PROJECT_CONFIG: str = "toml"
# -- Data Maps
FILE_EXTENSION_DATA_MAP: str = "json"
# -- Log
FILE_EXTENSION_LOG: str = "log"
# -- Temp Files
FILE_EXTENSION_BACKUP: str = "bak"

# MTG Extensions
# -- MTG
FILE_EXTENSION_DECK: str = "dck"
#  -- Forge
FILE_EXTENSION_FORGE_EDITION: str = "txt"
FILE_EXTENSION_FORGE_FORMAT: str = "txt"
# -- Shandalar
FILE_EXTENSION_SHANDALAR_DATA: str = "csv"