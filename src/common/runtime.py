"""
Runtime initialization and shared configuration access for Shandalar Tools.

Initializes bootstrap logging, loads shared application configuration,
and exposes runtime configuration accessors for common cross-tool
settings such as encoding behavior, logging preferences, and active
Shandalar data selection.
"""
from common import common_const, common_utils, file_utils, log_utils, path_utils
from common.common_types import EncodingScanMode
from config import config_io
from config.common_config import CommonConfig
from pathlib import Path
import json, logging

logger = logging.getLogger(__name__)

_active_common_config: CommonConfig | None = None
_active_name_normalization_map: dict[str, str] | None = None

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def initialize_runtime(log_name: str) -> None:
    """
    Initialize shared runtime services for the application.

    Establishes bootstrap logging, loads the shared CommonConfig,
    configures the active log file, and applies runtime-controlled
    logging behavior.

    Args:
        log_name: Name of the log file to use for the current tool.
            The file extension is optional.
    """
    log_file_path: Path = path_utils.build_log_file_path(log_name)
    log_utils.initialize_logging(log_file_path)
    _initialize_common_config(log_file_path)

    # NOTE:
    # Runtime configuration is populated directly during initialization
    # and therefore bypasses the runtime setters that normally refresh
    # logging automatically. Refresh explicitly after initialization to
    # apply the loaded logging configuration.
    log_utils.refresh_logging()
    _initialize_name_normalization_map()

# ==============================
# PUBLIC GETTERS/SETTERS
# ==============================
def get_name_normalization_map() -> dict[str, str]:
    """
    Retrieve the active runtime name normalization map.

    Returns:
        The loaded name normalization map used to reconcile
        known naming inconsistencies between external data
        sources.
    """    
    return _active_name_normalization_map

def get_shandalar_card_pool() -> str:
    """
    Retrieve the configured Shandalar card pool name.

    Returns:
        The configured Shandalar card pool name.
    """
    return _get_common_config().data_shandalar_card_pool

def set_shandalar_card_pool(card_pool: str) -> None:
    """
    Override the active runtime Shandalar card pool name.

    Args:
        card_pool: The Shandalar card pool to use for runtime lookups.
    """    
    _get_common_config().data_shandalar_card_pool = card_pool

def get_encoding_scan_mode(default_full_scan: bool = False) -> bool:
    """
    Retrieve the resolved encoding scan behavior.
    """    
    return _get_common_config().io_encoding_scan.resolve(default_full_scan)

def set_encoding_scan_mode(scan_mode: EncodingScanMode) -> None:
    """
    Retrieve the resolved encoding scan behavior.

    Args:
        default_full_scan: Default behavior used when the runtime
            scan mode is AUTO.

    Returns:
        True if a full encoding scan should be performed,
        otherwise False.
    """
    _get_common_config().io_encoding_scan = scan_mode

def get_log_preview_limit() -> int:
    """
    Retrieve the configured log preview item limit.

    Returns:
        The maximum number of preview items displayed in log output.
    """
    return _get_common_config().log_preview_limit

def set_log_preview_limit(preview_limit: int) -> None:
    """
    Override the active runtime log preview limit.

    Args:
        preview_limit: Maximum number of preview items to display in logs.
    """
    common_utils.validate_minimum(preview_limit, common_const.LOG_PREVIEW_LIMIT_MINIMUM, common_const.LOG_PREVIEW_LIMIT_FIELD_NAME)   
    _get_common_config().log_preview_limit = preview_limit

def get_log_overwrite() -> bool:
    """
    Retrieve the configured log overwrite behavior.

    Returns:
        True if log files should be overwritten, otherwise False.
    """ 
    return _get_common_config().log_overwrite

def set_log_overwrite(overwrite_mode: bool) -> None:
    """
    Override the active runtime log overwrite behavior.

    Updates both the stored runtime setting and the active file logging
    handler configuration.

    Args:
        overwrite_mode: If True, recreate the log file in overwrite mode.
            If False, append to the existing log file.
    """
    config = _get_common_config()
    if config.log_overwrite == overwrite_mode: # avoid unnecessary handler updates
        return 
    config.log_overwrite = overwrite_mode
    log_utils.refresh_logging()

def get_log_file_path() -> Path:
    """
    Retrieve the active runtime log file path.

    Returns:
        The configured log file path for the current tool.
    """    
    return _get_common_config().log_file_path

def set_log_file_path(file_path: Path) -> None:
    """
    Update the active runtime log file path.

    Updates both the stored runtime setting and the active file
    logging handler configuration.

    Args:
        file_path: New log file path to use. The file extension
            is optional and will be normalized automatically.
    """
    normalized_path: Path = file_utils.ensure_extension(file_path=file_path, extension=common_const.FILE_TYPE_LOG)
    config = _get_common_config()
    if config.log_file_path == normalized_path: # avoid unnecessary handler updates
        return
    config.log_file_path = normalized_path
    log_utils.refresh_logging()

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _initialize_common_config(log_file_path: Path) -> None:
    """
    Load and store the active runtime CommonConfig.

    Builds the shared application configuration from config.toml,
    overrides the configured log file name with the value supplied
    by the caller, and stores the resulting configuration for
    runtime access throughout the application.

    Args:
        log_file_path: Path to the log file to use for the current tool.
            The file extension is optional.

    Raises:
        ValueError: If configuration values are missing or invalid.
        OSError: If the configuration file cannot be read.
    """
    global _active_common_config
    _active_common_config = config_io.build_common_config(log_file_path)

def _get_common_config() -> CommonConfig:
    """
    Retrieve the active runtime CommonConfig.

    Serves as a centralized assertion wrapper around runtime config
    access, ensuring runtime initialization has completed before
    shared configuration values are accessed.

    Returns:
        The active runtime CommonConfig.

    Notes:
        Runtime initialization must occur before this function is called.
    """  
    assert _active_common_config is not None, "Runtime configuration accessed before runtime initialization."
    return _active_common_config

def _initialize_name_normalization_map() -> None:
    """
    Load and cache the active name normalization map.

    Reads the project-wide normalization map from disk and stores
    it in runtime memory for fast lookup during string
    normalization operations.

    Raises:
        OSError: If the normalization map file cannot be read.
        KeyError: If the normalization map field is missing from
            the data file.
        json.JSONDecodeError: If the normalization map file
            contains invalid JSON.
    """    
    global _active_name_normalization_map
    
    logger.info("Loading name normalization map...")    
    with common_const.NAME_NORMALIZATION_MAP_PATH.open("r", encoding="utf-8") as file:
        _active_name_normalization_map = json.load(file)[common_const.DATA_MAP_NORMALIZATION_MAP_FIELD]