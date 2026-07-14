"""
Configuration resource loaders.

Loads and caches configuration resources for internal use.
Most callers should access configuration values through
settings.py rather than retrieving configuration resources
directly.
"""
from resources.common_config import CommonConfig
from resources.deck_converter_config import DeckConverterConfig
from resources.format_builder_config import FormatBuilderConfig
from resources.managed_resource import ManagedResource, ResourceKey
from common import runtime
from typing import cast

# ==============================
# PUBLIC FUNCTIONS
# ==============================  
def get_common_config() -> CommonConfig:
    """
    Retrieve the common runtime configuration.

    Returns the registered configuration when available.
    Otherwise, creates, registers, and returns a new
    configuration instance.

    Returns:
        The common runtime configuration.
    """
    return _get_config(ResourceKey(CommonConfig))

def get_deck_converter_config() -> DeckConverterConfig:
    """
    Retrieve the deck converter configuration.

    Returns the registered configuration when available.
    Otherwise, creates, registers, and returns a new
    configuration instance.

    Returns:
        The deck converter configuration.
    """ 
    return _get_config(ResourceKey(DeckConverterConfig))

def get_format_builder_config() -> FormatBuilderConfig:
    """
    Retrieve the format builder configuration.

    Returns the registered configuration when available.
    Otherwise, creates, registers, and returns a new
    configuration instance.

    Returns:
        The format builder configuration.
    """   
    return _get_config(ResourceKey(FormatBuilderConfig))

# ==============================
# PRIVATE FUNCTIONS
# ============================== 
def _get_config[T: ManagedResource](key: ResourceKey) -> T:
    """
    Retrieve a managed configuration resource.

    Returns the registered configuration associated with the
    specified resource key when available. Otherwise, creates,
    registers, and returns a new configuration instance.

    Args:
        key: Resource key identifying the configuration to
            retrieve.

    Returns:
        The requested configuration resource.
    """
    resource: T | None = cast(T, runtime.get_resource(key))

    if resource is None:
        resource = cast(T, key.resource_type())
        runtime.register_resource(key=key, resource=resource)

    return resource