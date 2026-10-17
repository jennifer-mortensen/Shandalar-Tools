"""
Data map retrieval and lifecycle management.

Provides centralized access to application data maps and
integrates them with the runtime resource system. Data maps
are created on demand, cached as managed resources, and
reused for the lifetime of the application.

This module exposes helpers for retrieving commonly used
data maps such as edition maps, card maps, normalization
maps, and Forge edition code maps while ensuring consistent
initialization and registration behavior.
"""
from common import paths, runtime, settings
from resources import data_map_const
from resources.managed_resource import ResourceKey
from resources.data_map import DataMap
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Resolved active edition map. Prevents multiple resolution logs.
_active_edition_map_cache: dict[str, DataMap] = {}
# Missing file cache. Prevents repeated failed file lookups.
_missing_shandalar_to_forge_edition_map_cache: set[str] = set()
_missing_shandalar_card_to_forge_edition_map_cache: set[str] = set()

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def get_active_shandalar_to_forge_edition_map(cache: bool = True) -> DataMap:
    """
    Retrieve the active Shandalar-to-Forge edition map.

    Returns the dataset-specific edition map for the active
    Shandalar dataset when available. Otherwise, returns the
    default edition map.

    Args:
        cache: If True, retrieve and register the map through the
            runtime resource cache. If False, always load a new map
            without registering it.    

    Returns:
        The active Shandalar-to-Forge edition map.

    Raises:
        FileNotFoundError: If neither the dataset-specific nor the
            default edition map exists.
    """
    dataset: str = settings.get_shandalar_dataset()
    
    if cache:
        cached_map: DataMap = _active_edition_map_cache.get(dataset)

        if cached_map:
            return cached_map

    data_map: DataMap | None = get_shandalar_to_forge_edition_map(dataset=dataset, cache=cache)

    if data_map is None:
        logger.info("Dataset-specific edition map not found. Falling back to default edition map.")
        data_map = get_shandalar_to_forge_edition_map()

    # Satisfy the type checker. This value can never be None.
    assert data_map is not None

    if cache:
        _active_edition_map_cache[dataset] = data_map

    return data_map

def get_shandalar_to_forge_edition_map(dataset: str | None = None, cache: bool = True) -> DataMap | None:
    """
    Retrieve a Shandalar-to-Forge edition map.

    Returns the registered map for the requested dataset when
    available. Otherwise, attempts to load, register, and return
    the requested map.

    Dataset-specific maps are optional. If no map exists for the
    requested dataset, None is returned.

    Args:
        dataset: Optional dataset whose edition map should be
            retrieved.
        cache: If True, retrieve and register the map through the
            runtime resource cache. If False, always load a new map
            without registering it.

    Returns:
        The requested Shandalar-to-Forge edition map, or None if
        no map exists for the specified dataset.
    """
    if dataset in _missing_shandalar_to_forge_edition_map_cache:
        return None
    
    file_path: Path = paths.build_shandalar_to_forge_edition_map_file_path(dataset)
    try:
        return _get_data_map(
            display_name=data_map_const.SHANDALAR_TO_FORGE_EDITION_MAP_DISPLAY_NAME,
            map_key=data_map_const.SHANDALAR_TO_FORGE_EDITION_MAP_KEY,
            version=data_map_const.SHANDALAR_TO_FORGE_EDITION_MAP_VERSION,
            file_path=file_path,
            cache=cache
        )
    except FileNotFoundError:
        # Default map must exist.
        if dataset is None:
            raise
        logger.info("Shandalar to Forge edition map for dataset '%s' does not exist at path: %s", dataset, file_path)
        _missing_shandalar_to_forge_edition_map_cache.add(dataset)
        return None
    

def create_shandalar_to_forge_edition_map(dataset: str | None = None, register: bool = True) -> DataMap:
    """
    Create a Shandalar-to-Forge edition data map.

    Args:
        dataset: The Shandalar dataset associated with the map. If None,
            the default dataset is used.
        register: Whether to register the data map with the runtime
            resource manager.

    Returns:
        The newly created Shandalar-to-Forge edition data map.
    """    
    return _create_data_map(
            display_name=data_map_const.SHANDALAR_TO_FORGE_EDITION_MAP_DISPLAY_NAME,
            map_key=data_map_const.SHANDALAR_TO_FORGE_EDITION_MAP_KEY,
            version=data_map_const.SHANDALAR_TO_FORGE_EDITION_MAP_VERSION,
            file_path=paths.build_shandalar_to_forge_edition_map_file_path(dataset),
            register=register       
    )


def get_forge_edition_to_code_map(cache: bool = True) -> DataMap:
    """
    Retrieve the Forge edition-to-code map.

    Returns the registered Forge edition-to-code map when
    available. Otherwise, loads, registers, and returns the map
    from disk.

    The Forge edition-to-code map is used to translate Forge
    edition names into their corresponding Forge edition codes.

    Args:
        cache: If True, retrieve and register the map through the
            runtime resource cache. If False, always load a new map
            without registering it.        

    Returns:
        The Forge edition-to-code map.

    Raises:
        FileNotFoundError: If the Forge edition-to-code map file
            does not exist.
    """
    return _get_data_map(
        display_name=data_map_const.FORGE_EDITION_TO_CODE_MAP_DISPLAY_NAME,
        map_key=data_map_const.FORGE_EDITION_TO_CODE_MAP_KEY,
        version=data_map_const.FORGE_EDITION_TO_CODE_MAP_VERSION,
        file_path=paths.build_forge_edition_to_code_map_path(),
        cache=cache     
    )

def create_forge_edition_to_code_map(register: bool = True) -> DataMap:
    """
    Create a Forge edition-to-code data map.

    Args:
        register: Whether to register the data map with the runtime
            resource manager.

    Returns:
        The newly created Forge edition-to-code data map.
    """    
    return _create_data_map(
        display_name=data_map_const.FORGE_EDITION_TO_CODE_MAP_DISPLAY_NAME,
        map_key=data_map_const.FORGE_EDITION_TO_CODE_MAP_KEY,
        version=data_map_const.FORGE_EDITION_TO_CODE_MAP_VERSION,
        file_path=paths.build_forge_edition_to_code_map_path(),
        register=register           
    )

def get_name_to_normalized_name_map(cache: bool = True) -> DataMap:
    """
    Retrieve the project name normalization map.

    Returns the registered project name normalization map when
    available. Otherwise, loads, registers, and returns the map
    from disk.

    The project name normalization map is used to reconcile known
    naming inconsistencies between external data sources.

    Args:
        cache: If True, retrieve and register the map through the
            runtime resource cache. If False, always load a new map
            without registering it.        

    Returns:
        The project name normalization map.

    Raises:
        FileNotFoundError: If the project name normalization map
            file does not exist.
    """
    return _get_data_map(
        display_name=data_map_const.NAME_TO_NORMALIZED_NAME_MAP_DISPLAY_NAME,
        map_key=data_map_const.NAME_TO_NORMALIZED_NAME_MAP_KEY,
        version=data_map_const.NAME_TO_NORMALIZED_NAME_MAP_VERSION,
        file_path=paths.build_name_to_normalized_name_map_path(),
        cache=cache
    )

def create_name_to_normalized_name_map(register: bool = True) -> DataMap:
    """
    Create a name-to-normalized-name data map.

    Args:
        register: Whether to register the data map with the runtime
            resource manager.

    Returns:
        The newly created name-to-normalized-name data map.
    """    
    return _create_data_map(
        display_name=data_map_const.NAME_TO_NORMALIZED_NAME_MAP_DISPLAY_NAME,
        map_key=data_map_const.NAME_TO_NORMALIZED_NAME_MAP_KEY,
        version=data_map_const.NAME_TO_NORMALIZED_NAME_MAP_VERSION,
        file_path=paths.build_name_to_normalized_name_map_path(),
        register=register        
    )    

def get_shandalar_card_to_forge_edition_map(dataset: str, cache: bool = True) -> DataMap | None:
    """
    Retrieve the Shandalar card-to-Forge edition map.

    Returns the registered Shandalar card-to-Forge edition map
    when available. Otherwise, loads, registers, and returns the
    map from disk.

    The Shandalar card-to-Forge edition map functions as a
    persistent cache for card resolution. Cache misses may be
    added during execution and persisted to disk.

    Args:
        cache: If True, retrieve and register the map through the
            runtime resource cache. If False, always load a new map
            without registering it.        

    Returns:
        The Shandalar card-to-Forge edition map, or None if no
        persisted map exists for the specified dataset.
    """
    if dataset in _missing_shandalar_card_to_forge_edition_map_cache:
        return None

    file_path: Path = paths.build_shandalar_card_to_forge_edition_map_file_path(dataset)
    try:
        return _get_data_map(
            display_name=data_map_const.SHANDALAR_CARD_TO_FORGE_EDITION_MAP_DISPLAY_NAME,
            map_key=data_map_const.SHANDALAR_CARD_TO_FORGE_EDITION_MAP_KEY,
            version=data_map_const.SHANDALAR_CARD_TO_FORGE_EDITION_MAP_VERSION,
            file_path=file_path,
            cache=cache
        )
    except FileNotFoundError:
        logger.info("Shandalar card to Forge edition map for dataset '%s' does not exist at path: %s", dataset, file_path)
        _missing_shandalar_card_to_forge_edition_map_cache.add(dataset)
        return None

def create_shandalar_card_to_forge_edition_map(dataset: str, register: bool = True) -> DataMap:
    """
    Create a Shandalar-card-to-Forge-edition data map.

    Args:
        dataset: The Shandalar dataset associated with the map.
        register: Whether to register the data map with the runtime
            resource manager.

    Returns:
        The newly created Shandalar-card-to-Forge-edition data map.
    """    
    return _create_data_map(
            display_name=data_map_const.SHANDALAR_CARD_TO_FORGE_EDITION_MAP_DISPLAY_NAME,
            map_key=data_map_const.SHANDALAR_CARD_TO_FORGE_EDITION_MAP_KEY,
            version=data_map_const.SHANDALAR_CARD_TO_FORGE_EDITION_MAP_VERSION,
            file_path=paths.build_shandalar_card_to_forge_edition_map_file_path(dataset),
            register=register       
    )    

# ==============================
# PRIVATE FUNCTIONS
# ==============================
def _create_data_map(display_name: str, map_key: str, version: str, file_path: Path, register: bool = True) -> DataMap:
    """
    Create a DataMap and optionally register it with the runtime resource manager.

    Args:
        display_name: The display name of the data map.
        map_key: The key used to identify the data map.
        version: The version of the data map format.
        file_path: The path associated with the data map resource.
        register: Whether to register the data map with the runtime resource
            manager.

    Returns:
        The newly created DataMap.

    Raises:
        AssertionError: If register is True and a DataMap already exists
            for the same resource key.
    """    
    key: ResourceKey = ResourceKey(resource_type=DataMap, path=file_path)

    if register:
        assert runtime.get_resource(key) is None, (
            f"Unable to register Data Map when a Data Map assigned to the same resource key '{key}' already exists."
        )

    data_map: DataMap = DataMap(display_name=display_name, map_key=map_key, version=version)

    if register:
        runtime.register_resource(key=key, resource=data_map)

    return data_map
    

def _get_data_map(display_name: str, map_key: str, version: str, file_path: Path, cache: bool = True) -> DataMap:
    """
    Retrieve a managed data map.

    Returns the registered data map associated with the specified
    file when available. Otherwise, loads, registers, and returns
    the data map from disk.

    Args:
        display_name: User-friendly name used for logging.
        map_key: JSON field containing the map's key-value data.        
        version: Expected data map schema version.
        file_path: Path to the data map file.
        
        cache: If True, retrieve and register the map through the
            runtime resource cache. If False, always load a new map
            without registering it.                      

    Returns:
        The requested data map.

    Raises:
        FileNotFoundError: If the data map file does not exist.
    """    
    key: ResourceKey = ResourceKey(resource_type=DataMap, path=file_path)
    data_map: DataMap | None
    
    if cache:
        data_map = runtime.get_resource(key)

        if data_map:
            return data_map
    
    data_map = DataMap(display_name=display_name, map_key=map_key, version=version, init_path=file_path)

    if cache:
        runtime.register_resource(key=key, resource=data_map)

    return data_map