"""
Runtime services for Shandalar Tools.

Initializes application services, manages cached resources, and
maintains shared runtime state for the current application instance.
"""
from common import log_manager, paths
from pathlib import Path
from resources.managed_resource import ManagedResource, ResourceKey
from resources.common_config import CommonConfig
import logging

logger = logging.getLogger(__name__)

_log_file_name: str | None = None
_managed_resources: dict[ResourceKey, ManagedResource] = {}

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def initialize_runtime(log_file_name: str) -> None:
    """
    Initialize shared runtime services for the application.

    Establishes bootstrap logging, loads the shared CommonConfig,
    configures the active log file, and applies runtime-controlled
    logging behavior.

    Args:
        log_file_name: Name of the log file to use for the current tool.
            The file extension is optional.
    """
    global _log_file_name
    _log_file_name = log_file_name
    log_manager.initialize_logging(log_file_name)
    config: CommonConfig = CommonConfig()
    register_resource(key=ResourceKey(CommonConfig), resource=config)

    # NOTE:
    # Runtime configuration is populated directly during initialization
    # and therefore bypasses the runtime setters that normally refresh
    # logging automatically. Refresh explicitly after initialization to
    # apply the loaded logging configuration.
    log_manager.refresh_logging(log_file_name=log_file_name, overwrite=config.io_encoding_scan_mode)

def delete_resource(key: ResourceKey, invoke_termination: bool = True) -> bool:
    """
    Remove a managed resource from the runtime.

    Removes the specified resource from the runtime registry and,
    optionally, invokes its termination callback before removal.

    Args:
        key: The key of the resource to remove.
        invoke_termination: Whether to invoke the resource's
            termination callback before removing it from the
            runtime.

    Returns:
        True if the resource was found and removed; otherwise
        False.
    """  
    resource: ManagedResource | None = _managed_resources.pop(key, None)

    if resource is not None:
        if invoke_termination:
            resource.on_terminate()
        return True

    logger.debug("Unable to delete resource with key '%s'. No such resource exists.", key)
    return False

def register_resource(key: ResourceKey, resource: ManagedResource) -> bool:
    """
    Register a managed resource with the runtime.

    Associates a resource with a unique key so it can be
    tracked, retrieved, and terminated by the runtime.
    Validates that the resource type matches the type
    expected by the specified resource key.

    Args:
        key: Unique identifier for the resource.
        resource: The resource instance to register.

    Returns:
        True if the resource was registered; otherwise False
        if a resource with the same key already exists.

    Raises:
        AssertionError: If the resource type does not match
            the type expected by the specified resource key.
    """
    assert isinstance(resource, key.resource_type), (
        f"Attempted to register resource of type "
        f"'{type(resource).__name__}', but expected "
        f"'{key.resource_type.__name__}'."
    )

    if _managed_resources.get(key) is None:
        _managed_resources[key] = resource
        return True
    
    logger.warning("Unable to register resource with key '%s'. A previous instance already exists.", key)
    return False

def terminate_resources() -> None:
    """
    Terminate all managed resources.

    Invokes termination on every registered managed resource
    and removes each resource from the runtime registry.
    """    
    for key in list(_managed_resources.keys()):
        delete_resource(key) 

# ==============================
# PUBLIC GETTERS/SETTERS
# ==============================
def get_log_file_name() -> str:
    """
    Retrieve the active runtime log file name.

    Returns:
        The configured log file name.

    Raises:
        AssertionError: If runtime has not been initialized.
    """    
    assert _log_file_name is not None, "Attempted to retrieve log file name before runtime initialization."
    return _log_file_name

def set_log_file_name(file_name: str) -> None:
    """
    Set the active runtime log file name.

    Refreshes the logging system when the configured log file
    changes.

    Args:
        file_name: The new log file name.
    """    
    global _log_file_name
    assert _log_file_name is not None, "Attempted to override log file name before runtime initialization."

    if _log_file_name == file_name:
        return

    _log_file_name = file_name
    config: CommonConfig = get_resource(ResourceKey(CommonConfig))

    assert config is not None, "Required CommonConfig resource is not registered."

    log_manager.refresh_logging(log_file_name=file_name, overwrite=config.log_overwrite)

def get_log_file_path() -> Path:
    """
    Resolve the active runtime log file path.

    Builds the log file path from the active runtime log file
    name.

    Returns:
        The absolute path to the active log file.

    Raises:
        AssertionError: If runtime has not been initialized.
    """    
    return paths.build_log_file_path(get_log_file_name())

def get_resource(key: ResourceKey) -> ManagedResource | None:
    """
    Retrieve a managed resource from the runtime.

    Validates that any registered resource associated with the
    specified key matches the resource type defined by the key.

    Args:
        key: The resource identifier.

    Returns:
        The registered resource associated with the specified
        key, or None if no such resource exists.

    Raises:
        AssertionError: If a registered resource exists for the
            specified key but does not match the expected type.
    """
    resource: ManagedResource | None = _managed_resources.get(key)

    # Guard against manual modification of the resource registry.
    assert resource is None or isinstance(resource, key.resource_type), (
        f"Found resource of type '{type(resource).__name__}', "
        f"but expected type '{key.resource_type.__name__}'."
    )

    return resource