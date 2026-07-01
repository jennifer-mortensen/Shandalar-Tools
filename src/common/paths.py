"""
Path construction utilities for Shandalar Tools.

Provides centralized helpers for constructing normalized
application paths, including configuration files, logs,
data resources, decks, and generated output.
"""
from common import file_utils, path_const, settings
from mtg.mtg_types import DeckType
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ==============================
# DIRECTORIES
# ==============================
def get_forge_editions_dir() -> Path:
    """
    Retrieve the configured Forge editions directory.

    Returns:
        The directory used to store Forge edition definition files.
    """    
    return path_const.FORGE_EDITIONS_DIR

# ==============================
# COMMON FILES
# ==============================
def build_backup_file_path(file_path: Path) -> Path:
    """
    Build the backup file path for a file.

    Appends the standard backup extension to the file's existing
    extension.

    Args:
        file_path: The file to build a backup path for.

    Returns:
        The backup file path.
    """    
    return file_path.with_suffix(f"{file_path.suffix}.{path_const.FILE_EXTENSION_BACKUP}")

def build_config_file_path() -> Path:
    """
    Build the path to the shared application configuration file.

    Resolves the configuration file within the configured config
    directory and applies the expected file extension.

    Returns:
        The normalized configuration file path.
    """    
    return _resolve_path_from_string(
        path_string=path_const.FILE_NAME_CONFIG,
        extension=path_const.FILE_EXTENSION_PROJECT_CONFIG,
        target_dir=path_const.CONFIG_DIR,
        field_name="Config path")

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
        extension=path_const.FILE_EXTENSION_LOG,
        target_dir=path_const.LOG_DIR,
        field_name="Log file path")

# ==============================
# FORGE DATA FILES
# ==============================
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
        extension=path_const.FILE_EXTENSION_FORGE_EDITION,
        target_dir=path_const.FORGE_EDITIONS_DIR,
        field_name="Edition name")

# ==============================
# SHANDALAR DATA FILES
# ==============================
def build_shandalar_dataset_file_path(dataset: str | None = None) -> Path:
    """
    Build the path to a Shandalar dataset file.

    Uses the supplied dataset when provided. Otherwise, the
    currently configured card pool from runtime is used.

    Ensures the expected file extension is present.

    Args:
        dataset: Optional dataset name.

    Returns:
        Path to the requested Shandalar dataset file.
    """
    if dataset is None:
        dataset = settings.get_shandalar_dataset()

    return _resolve_path_from_string(
        path_string=dataset,
        extension=path_const.FILE_EXTENSION_SHANDALAR_DATA,
        target_dir=path_const.SHANDALAR_DATASETS_DIR,
        field_name="Shandalar dataset path")

# ==============================
# DATA MAP FILES
# ==============================
def build_forge_edition_to_code_map_path() -> Path:
    """
    Build the path to the Forge edition code map file.

    Returns:
        The path to the Forge edition code map file.
    """    
    return _resolve_path_from_string(
        path_string=path_const.FORGE_EDITION_TO_CODE_MAP_FILE_NAME,
        extension=path_const.FILE_EXTENSION_DATA_MAP,
        target_dir=path_const.FORGE_DATA_DIR,
        field_name="Forge edition code map")

def build_name_to_normalized_name_map_path() -> Path:
    """
    Build the path to the name normalization map file.

    Returns:
        The resolved path to the name normalization map.
    """    
    return _resolve_path_from_string(
        path_string=path_const.NAME_TO_NORMALIZED_NAME_MAP_FILE_NAME,
        extension=path_const.FILE_EXTENSION_DATA_MAP,
        target_dir=path_const.NAME_TO_NORMALIZED_NAME_MAP_DIR,
        field_name="Name normalization map"
    )

def build_shandalar_card_to_forge_edition_map_file_path() -> Path:
    """
    Build the path to the active Shandalar card map.

    Constructs the card map path for the currently active
    Shandalar card pool registered with the runtime.

    Returns:
        The resolved path to the active Shandalar card map.

    Raises:
        AssertionError: If no active Shandalar card pool has
            been registered with the runtime.
    """     
    return _resolve_path_from_string(
        path_string=f"{settings.get_shandalar_dataset()}{path_const.SHANDALAR_CARD_TO_FORGE_EDITION_MAP_FILE_NAME_SUFFIX}",
        extension=path_const.FILE_EXTENSION_DATA_MAP,
        target_dir=path_const.SHANDALAR_CARD_TO_FORGE_EDITION_MAP_DIR,
        field_name="Shandalar card map path")

def build_shandalar_to_forge_edition_map_file_path(dataset_name: str | None = None) -> Path:
    """
    Build the path to a Shandalar edition map.

    When a dataset name is provided, returns the path to the dataset's
    edition map override. Otherwise, returns the path to the default
    Shandalar edition map.

    Args:
        dataset_name: Optional dataset name used to construct a
            dataset-specific edition map path.

    Returns:
        The path to the resolved Shandalar edition map.
    """
    path_string: str
    extension: str = path_const.FILE_EXTENSION_DATA_MAP    
    target_dir: Path
    field_name: str

    if dataset_name is None:
        # Default Edition Map
        path_string = path_const.DEFAULT_SHANDALAR_TO_FORGE_EDITION_MAP_FILE_NAME
        target_dir = path_const.DEFAULT_SHANDALAR_TO_FORGE_EDITION_MAP_DIR
        field_name = "Default Shandalar edition map"
    else:
        # Dataset Edition Map
        path_string = f"{dataset_name}{path_const.SHANDALAR_TO_FORGE_EDITION_MAP_FILE_NAME_SUFFIX}"
        target_dir = path_const.SHANDALAR_DATASETS_DIR
        field_name = "Shandalar edition map"

    return _resolve_path_from_string(path_string=path_string, extension=extension, target_dir=target_dir, field_name=field_name)

def resolve_shandalar_edition_map_file_path(dataset_name: str | None) -> Path:
    """
    Resolve the appropriate Shandalar edition map path for a dataset.

    Attempts to locate a dataset-specific edition map. If no override
    exists, resolves to the default Shandalar edition map.

    Args:
        dataset_name: The dataset whose edition map should be resolved.

    Returns:
        The path to the dataset-specific edition map when present;
        otherwise the path to the default Shandalar edition map.
    """   
    if dataset_name is not None:
        file: Path = build_shandalar_to_forge_edition_map_file_path(dataset_name)

        if file.exists():
            logger.info("Shandalar edition map for dataset '%s' found.", dataset_name)
            return file

        logger.info("Shandalar edition map for dataset '%s' not found. Resolving to default edition map.", dataset_name)

    return build_shandalar_to_forge_edition_map_file_path()

# ==============================
# FORMAT GENERATOR FILES
# ==============================
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
        extension=path_const.FILE_EXTENSION_FORMAT_CONFIG,
        target_dir=path_const.FORMAT_CONFIG_DIR,
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
        extension=path_const.FILE_EXTENSION_FORGE_FORMAT,
        target_dir=path_const.FORMAT_DIR,
        field_name="Format file name")

# ==============================
# DECK CONVERTER FILES
# ==============================
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
        extension=path_const.FILE_EXTENSION_DECK,
        target_dir=path_const.INPUT_DECK_DIR,
        field_name="Input deck name")        

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
    output_dir = path_const.OUTPUT_FORGE_DECK_DIR if deck_type is DeckType.FORGE else path_const.OUTPUT_SHANDALAR_DECK_DIR
    
    return _resolve_path_from_string(
        path_string=deck_name,
        extension=path_const.FILE_EXTENSION_DECK,
        target_dir=output_dir,
        field_name="Output deck name")     

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