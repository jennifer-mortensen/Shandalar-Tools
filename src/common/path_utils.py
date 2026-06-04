"""
Path construction utilities for Shandalar Tools.

Provides centralized helpers for building normalized file paths used
throughout the application, including deck files, Forge edition data,
and Shandalar card pool resources.
"""
from common import common_const, file_utils
from common.common_types import DeckType
from config import runtime
from pathlib import Path

def build_edition_file_path(edition_name: str) -> Path:
    """
    Build the file path for a Forge edition file.

    Args:
        edition_name: The name of the edition.

    Raises:
        ValueError: If the edition name is empty.
    """    
    if not edition_name:
        raise ValueError("Edition name cannot be empty.")

    return common_const.EDITIONS_DIR / f"{edition_name}{common_const.EDITION_FILE_SUFFIX}"

def build_input_deck_file_path(deck_name: str) -> Path:
    """
    Build the normalized path for an input deck file.

    Resolves the deck path within the configured input deck directory and
    automatically applies the default deck file extension if missing.

    Args:
        deck_name: The name of the deck file, with or without extension.

    Returns:
        The normalized input deck file path.
    """    
    return file_utils.ensure_extension(file_path=common_const.INPUT_DECK_DIR / deck_name, extension=common_const.FILE_TYPE_DECK)

def build_log_file_path(log_name: str) -> Path:
    """
    Build the path to a log file within the application's log directory.

    Ensures the expected log file extension is present and returns
    the normalized path.

    Args:
        log_name: Log file name or stem. The file extension is optional.

    Returns:
        Path to the log file.
    """    
    return file_utils.ensure_extension(file_path=common_const.LOG_DIR / log_name, extension=common_const.FILE_TYPE_LOG)

def build_output_deck_file_path(deck_name: str, deck_type: DeckType) -> Path:
    """
    Build the normalized path for an output deck file.

    Selects the appropriate output directory based on the target deck type
    and automatically applies the default deck file extension if missing.

    Args:
        deck_name: The name of the deck file, with or without extension.
        deck_type: The target deck format type.

    Returns:
        The normalized output deck file path.
    """    
    output_dir = common_const.OUTPUT_FORGE_DECK_DIR if deck_type is DeckType.FORGE else common_const.OUTPUT_SHANDALAR_DECK_DIR
    return file_utils.ensure_extension(file_path=output_dir / deck_name, extension=common_const.FILE_TYPE_DECK)

def build_shandalar_card_pool_path() -> Path:
    """
    Build the path to the active Shandalar card pool data file.

    Uses the currently configured card pool name from runtime
    configuration and ensures the expected file extension is present.

    Returns:
        Path to the active Shandalar card pool data file.
    """    
    return file_utils.ensure_extension(
        file_path=common_const.DATA_DIR / runtime.get_shandalar_card_pool(),
        extension=common_const.FILE_TYPE_SHANDALAR_DATA
    )