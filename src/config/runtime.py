"""
Runtime initialization and shared configuration access for Shandalar Tools.

Initializes bootstrap logging, loads shared application configuration,
and exposes runtime configuration accessors for common cross-tool
settings such as encoding behavior, logging preferences, and active
Shandalar data selection.
"""
from common import common_const, common_utils, log_utils
from common.common_const import EncodingScanMode
from config import config_io
from config.common_config import CommonConfig

_active_common_config: CommonConfig | None = None

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def initialize_runtime() -> None:
    """
    Initialize shared runtime services for the application.

    Establishes bootstrap logging, loads the shared CommonConfig,
    and applies runtime-controlled logging behavior.
    """    
    log_utils.initialize_logging()
    _initialize_common_config()
    log_utils.update_logging_write_mode(_active_common_config.log_overwrite)

# ==============================
# PUBLIC GETTERS/SETTERS
# ==============================
def get_shandalar_card_pool() -> str:
    """
    Retrieve the configured Shandalar card pool name.
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
    Override the active runtime encoding scan mode.

    Args:
        scan_mode: The encoding scan mode to apply for future file reads.
    """    
    _get_common_config().io_encoding_scan = scan_mode

def get_log_preview_limit() -> int:
    """
    Retrieve the configured log preview item limit.
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
    log_utils.update_logging_write_mode(overwrite_mode)

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _initialize_common_config() -> None:
    """
    Load and store the active runtime CommonConfig.

    Builds the shared application configuration from config.toml
    and stores it for runtime access throughout the application.

    Raises:
        ValueError: If configuration values are missing or invalid.
        OSError: If the configuration file cannot be read.
    """
    global _active_common_config
    _active_common_config = config_io.build_common_config()

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