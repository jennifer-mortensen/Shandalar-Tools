"""
Runtime accessors for shared Shandalar Tools configuration.

Stores the active CommonConfig for the current application session,
allowing shared runtime settings to be accessed globally without
threading configuration values through utility/helper layers.
"""
from config.common_config import CommonConfig

_active_common_config: CommonConfig | None = None

def set_common_config(config: CommonConfig) -> None:
    """
    Set the active runtime CommonConfig.

    Intended to be called once during application startup after the
    configuration file has been parsed and validated.

    Args:
        config: The CommonConfig to store as the active runtime config.
    """    
    global _active_common_config
    _active_common_config = config

def get_common_config() -> CommonConfig:
    """
    Retrieve the active runtime CommonConfig.

    Returns:
        The currently active CommonConfig.

    Raises:
        RuntimeError: If the runtime config has not been initialized.
    """    
    if _active_common_config is None:
        raise RuntimeError("Runtime config has not been initialized.")

    return _active_common_config 