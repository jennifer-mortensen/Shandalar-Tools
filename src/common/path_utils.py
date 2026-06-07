"""
Path construction utilities for Shandalar Tools.

Provides centralized helpers for building normalized file paths used
throughout the application, including deck files, Forge edition data,
and Shandalar card pool resources.
"""
from common import common_const, file_utils, runtime
from mtg.mtg_types import DeckType
from pathlib import Path

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def build_config_file_path() -> Path:
    """
    Build the path to the shared application configuration file.

    Resolves the configuration file within the configured config
    directory and applies the expected file extension.

    Returns:
        The normalized configuration file path.
    """    
    return _resolve_path_from_string(
        path_string=common_const.FILE_NAME_CONFIG,
        extension=common_const.FILE_TYPE_CONFIG,
        target_dir=common_const.CONFIG_DIR,
        field_name="Config path")

def build_edition_file_path(edition_name: str) -> Path:
    """
    Build the path to a Forge edition file.

    Resolves the edition file within the configured editions directory
    and automatically applies the expected file extension if missing.

    Args:
        edition_name: The name of the edition file, with or without
            extension.

    Returns:
        The normalized edition file path.
    """
    return _resolve_path_from_string(
        path_string=edition_name,
        extension=common_const.FILE_TYPE_FORGE_EDITION,
        target_dir=common_const.EDITIONS_DIR,
        field_name="Edition name")

def build_format_config_path(format_name: str) -> Path:
    """
    Build the normalized path for an input format configuration file.

    Resolves the format file within the configured format directory and
    automatically applies the expected file extension if missing.

    Args:
        format_name: The name of the format file, with or without
            extension.

    Returns:
        The normalized format configuration file path.
    """
    return _resolve_path_from_string(
        path_string=format_name,
        extension=common_const.FILE_TYPE_FORMAT_CONFIG,
        target_dir=common_const.FORMAT_CONFIG_DIR,
        field_name="Format config file path")

def build_format_path(format_name: str) -> Path:
    """
    Build the canonical path to a Forge format file.

    Resolves a format file name into a validated path within the
    configured formats directory, applying the Forge format file
    extension if needed.

    Args:
        format_name: The format file name or path fragment to resolve.

    Returns:
        The resolved path to the Forge format file.

    Raises:
        ValueError: If the format name is empty or otherwise invalid.
    """    
    return _resolve_path_from_string(
        path_string=format_name,
        extension=common_const.FILE_TYPE_FORGE_FORMAT,
        target_dir=common_const.FORMAT_DIR,
        field_name="Format file name")

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
    return _resolve_path_from_string(
        path_string=deck_name,
        extension=common_const.FILE_TYPE_DECK,
        target_dir=common_const.INPUT_DECK_DIR,
        field_name="Input deck name")        

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
    return _resolve_path_from_string(
        path_string=log_name,
        extension=common_const.FILE_TYPE_LOG,
        target_dir=common_const.LOG_DIR,
        field_name="Log file path")             

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
    
    return _resolve_path_from_string(
        path_string=deck_name,
        extension=common_const.FILE_TYPE_DECK,
        target_dir=output_dir,
        field_name="Output deck name")          

def build_shandalar_card_pool_path() -> Path:
    """
    Build the path to the active Shandalar card pool data file.

    Uses the currently configured card pool name from runtime
    configuration and ensures the expected file extension is present.

    Returns:
        Path to the active Shandalar card pool data file.
    """
    return _resolve_path_from_string(
        path_string=runtime.get_shandalar_card_pool(),
        extension=common_const.FILE_TYPE_SHANDALAR_DATA,
        target_dir=common_const.DATA_DIR,
        field_name="Shandalar data path")             

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _resolve_path_from_string(path_string: str, extension: str, target_dir: Path, field_name: str = "Path") -> Path:
    """
    Resolve a user-supplied path string into a normalized file path.

    Validates that the supplied path string is non-empty, appends the
    specified extension if one is not already present, and prepends
    the target directory when the path does not already include
    directory components.

    Args:
        path_string: The user-supplied path string to resolve.
        extension: The file extension to enforce, without a leading dot.
        target_dir: Default directory used for relative file names.
        field_name: Human-readable field name used in validation errors.

    Returns:
        The normalized file path.

    Raises:
        ValueError: If path_string is empty.
    """    
    if not path_string:
        raise ValueError(f"{field_name} cannot be empty.")
    
    normalized_path: Path = file_utils.ensure_extension(Path(path_string), extension)

    if len(normalized_path.parts) == 1:
        normalized_path = target_dir / normalized_path

    return normalized_path