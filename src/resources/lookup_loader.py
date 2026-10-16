"""
Managed lookup resource loading and retrieval.

Provides lazy-loading accessors for cached lookup resources.
Resources are created on demand, registered with the runtime,
and reused for subsequent requests.
"""
from common import paths, runtime, settings
from pathlib import Path
from resources.forge_card_lookup import ForgeCardLookup
from resources.managed_resource import ResourceKey
from resources.shandalar_card_lookup import ShandalarCardLookup

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def get_forge_card_lookup(cache: bool = True) -> ForgeCardLookup:
    """
    Retrieve the Forge card lookup resource.

    Returns the registered Forge card lookup when available.
    Otherwise, creates, registers, and returns a new lookup.

    Args:
        cache: If True, retrieve and register the lookup through
            the runtime resource cache. If False, always load a new
            lookup without registering it.

    Returns:
        The Forge card lookup resource.
    """
    key: ResourceKey = ResourceKey(ForgeCardLookup)
    lookup: ForgeCardLookup | None 
    
    if cache:
        lookup = runtime.get_resource(key)

        if lookup:
            return lookup

    lookup = ForgeCardLookup()

    if cache:
        runtime.register_resource(key=key, resource=lookup)

    return lookup

def get_shandalar_card_lookup(dataset: str | None = None, cache: bool = True) -> ShandalarCardLookup:
    """
    Retrieve a Shandalar card lookup resource.

    Returns the registered lookup for the requested dataset when
    available. Otherwise, creates, registers, and returns a new
    lookup for that dataset.

    Args:
        dataset: Optional dataset whose lookup should be
            retrieved.
        cache: If True, retrieve and register the lookup through
            the runtime resource cache. If False, always load a new
            lookup without registering it.

    Returns:
        The requested Shandalar card lookup resource.
    """
    if dataset is None:
        dataset = settings.get_shandalar_dataset()

    file_path: Path = paths.build_shandalar_dataset_file_path(dataset)
    key: ResourceKey = ResourceKey(resource_type=ShandalarCardLookup, path=file_path)
    lookup: ShandalarCardLookup | None 
    
    if cache:
        lookup = runtime.get_resource(key)

        if lookup:
            return lookup

    lookup = ShandalarCardLookup(dataset)

    if cache:
        runtime.register_resource(key=key, resource=lookup)

    return lookup

