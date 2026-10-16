"""
File resource loading utilities for Shandalar Tools.

Provides functions for retrieving cached file resources and
registering new file resources with the runtime resource manager.
"""
from common import runtime
from pathlib import Path
from resources.file_resource import FileResource
from resources.managed_resource import ResourceKey

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def get_file_resource(path: Path, encoding: str | None = None, cache: bool = True) -> FileResource:
    """
    Retrieve a cached file resource or load and register a new one.

    When a file resource is already cached, an optional encoding is
    validated against the resource's encoding. When loading a new
    resource, an encoding must be provided.

    Args:
        path: Path to the file.
        encoding: Encoding to use when loading the file. Required when
            loading a new resource.
        cache: If True, retrieve and register the resource through the
            runtime resource cache. If False, always load a new resource
            without registering it.

    Returns:
        The requested file resource.
    """   
    key: ResourceKey = ResourceKey(resource_type=FileResource, path=path)
    file: FileResource | None

    if cache:
        file = runtime.get_resource(key)

        if file:
            assert encoding is None or encoding == file.encoding, (
                f"Requested encoding ('{encoding}') must match encoding of the cached file resource ('{file.encoding}') at path: {path}")
            return file

    assert encoding is not None, (
        f"Encoding cannot be 'None' when loading a file resource from disk. (Path: {path})"
    )

    file = FileResource(path, encoding)

    if cache:
        runtime.register_resource(key=key, resource=file)

    return file