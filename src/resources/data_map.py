"""
Provides a managed, persistent key-value data map.

DataMap wraps a dictionary-backed data map with support for
loading from disk, dirty-state tracking, and automatic
persistence during runtime termination. Data maps are stored
using the project's standard JSON data map schema and may be
used for artifacts such as edition maps, normalization maps,
and reconciliation maps.
"""
from collections.abc import ValuesView, ItemsView, KeysView
from common import file_utils, runtime
from dataclasses import dataclass, field, InitVar
from pathlib import Path
from resources import data_map_const
from resources.managed_resource import ManagedResource, ResourceKey
import json
import logging

logger = logging.getLogger(__name__)

# ==============================
# DATACLASSES
# ==============================
@dataclass
class DataMap(ManagedResource):
    """
    Represents a managed persistent data map.

    Stores key-value mappings loaded from a JSON data map file
    and tracks modifications for automatic persistence. DataMap
    instances may be registered with the runtime as managed
    resources to ensure changes are written to disk when the
    resource is terminated.
    """
    display_name: str
    map_key: str
    version: str
    init_path: InitVar[Path | None] = None    

    _data: dict[str, str] = field(default_factory=dict)
    _dirty: bool = False
    _path: Path | None = None

    # Initialization
    def __post_init__(self, path: Path | None) -> None:
        """
        Initialize the data map after construction.

        Loads the data map from disk when a backing file path has
        been assigned.
        """  
        self._path = path
        if self._path:
            self._load()

    # Interface Functions
    def on_terminate(self) -> None:
        """
        Handle pre-termination behavior.

        Writes the map to disk when it contains unsaved changes.
        """        
        self.write()
    
    # Public Functions

    def get_display_name(self) -> str:
        """
        Retrieve a user-friendly display name for the data map.

        Returns:
            The configured data map name, or "data map" when
            no name has been specified.
        """        
        return f"{self.display_name}" if self.display_name else "data map"

    def is_dirty(self) -> bool:
        """
        Determine whether the data map has been modified.

        Returns:
            True if the map contains unsaved changes; otherwise
            False.
        """        
        return self._dirty
    
    def persist_to(self, file_path: Path) -> None:
        """
        Persist the data map to a new backing file.

        Archives the current backing file, adopts the specified file
        as the data map's canonical backing file, replaces any
        existing managed resource for that file, registers this
        instance with the runtime, and writes the current map
        contents to disk.

        Any existing file at the destination is archived before being
        replaced.

        Args:
            file_path: The file to persist the data map to.
        """
        if file_path == self._path:
            return

        if self._path and self._path.exists():
            file_utils.archive(self._path)

        old_key: ResourceKey = ResourceKey(resource_type=type(self), path=self._path)
        if runtime.get_resource(old_key):
            runtime.delete_resource(key=old_key, invoke_termination=False)

        if file_path.exists():
            file_utils.archive(file_path)

        self._path = file_path
        key: ResourceKey = ResourceKey(resource_type=type(self), path=self._path)

        if runtime.get_resource(key):
            logger.info("Replacing existing managed resource for '%s'.", file_path)
            runtime.delete_resource(key=key, invoke_termination=False)

        runtime.register_resource(key, self)

        # Force persistence after changing the backing file.
        self._dirty = True
        self.write()

    def write(self) -> None:
        """
        Write the data map to its backing file.

        Writes the current map contents to disk when unsaved changes
        exist. If the map is not dirty, no action is taken.

        Raises:
            AssertionError: If no backing file has been assigned.
        """
        if not self._dirty:
            return
        
        assert self._path is not None, (
            "Attempted to write a data map before assigning a backing file."
        )        

        sorted_data: dict[str, str] = dict(sorted(self._data.items()))
        output: dict[str, str] = {
            data_map_const.DATA_MAP_VERSION_FIELD: self.version,
            self.map_key: sorted_data
        }
        
        logger.info("Writing %s to path: %s", self.get_display_name(), self._path)

        with self._path.open("w", encoding="utf-8") as file:
            json.dump(output, file, indent=4, ensure_ascii=False)
        self._dirty = False        

    # Dictionary Functions
    def __contains__(self, key: str) -> bool:
        """
        Determine whether a key exists in the data map.

        Args:
            key: The key to look up.

        Returns:
            True if the key exists in the data map, otherwise False.
        """
        return key in self._data
    
    def __getitem__(self, key: str) -> str:
        """
        Retrieve a value from the data map.

        Raises:
            KeyError: If the key does not exist.
        """
        return self._data[key]
    
    def __setitem__(self, key: str, value: str) -> None:
        """
        Store a value in the data map.

        Marks the map as dirty when the stored value changes.
        """
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        """
        Remove a value from the data map.

        Raises:
            KeyError: If the key does not exist.
        """
        del self._data[key]
        self._dirty = True           

    def __len__(self) -> int:
        """
        Retrieve the number of entries in the data map.

        Returns:
            The number of key-value pairs stored in the map.
        """
        return len(self._data)

    def get(self, key: str) -> str | None:
        """
        Retrieve a value from the data map.

        Args:
            key: The key to retrieve.

        Returns:
            The mapped value when present; otherwise None.
        """        
        return self._data.get(key)
    
    def set(self, key: str, value: str) -> None:
        """
        Store a value in the data map.

        Updates the specified key and marks the map as dirty when
        the stored value changes.

        Args:
            key: The key to update.
            value: The value to store.

        Raises:
            AssertionError: If the data map is read-only.
        """
        if self._data.get(key) == value:
            return
        self._data[key] = value
        self._dirty = True

    def contains(self, key: str) -> bool:
        """
        Determine whether a key exists in the data map.

        Args:
            key: The key to check.

        Returns:
            True if the key exists; otherwise False.
        """        
        return key in self._data
    
    def items(self) -> ItemsView[str, str]:
        """
        Retrieve all key-value pairs in the data map.

        Returns:
            A dynamic view of the key-value pairs stored in the map.
        """        
        return self._data.items()

    def keys(self) -> KeysView[str]:
        """
        Retrieve all keys in the data map.

        Returns:
            A dynamic view of the keys stored in the map.
        """        
        return self._data.keys()    

    def values(self) -> ValuesView[str]:
        """
        Retrieve all values in the data map.

        Returns:
            A dynamic view of the values stored in the map.
        """        
        return self._data.values() 
  
    # Private Functions        
    def _load(self) -> None:
        """
        Load the data map from disk.

        Reads the configured data map file and populates the
        in-memory map contents.
        """  
        logger.info("Loading %s from path: %s", self.get_display_name(), self._path)        
        
        with self._path.open("r", encoding="utf-8") as file:
            self._data = json.load(file)[self.map_key]
    
    # Properties
    @property
    def path(self) -> Path | None:
        """
        Retrieve the data map's backing file path.

        Returns:
            The canonical backing file for the data map, or None
            if the map has not been assigned a backing file.
        """        
        return self._path