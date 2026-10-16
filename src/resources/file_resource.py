"""
Read-only file resources for Shandalar Tools.

Defines a managed resource for caching file contents and providing
independent in-memory text streams to consumers.
"""
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from resources.managed_resource import ManagedResource

# ==============================
# CLASSES
# ==============================
@dataclass
class FileResource(ManagedResource):
    """
    Caches the text contents of a file using a specified encoding.

    Retains the contents in memory and returns a fresh StringIO
    stream on each access, allowing independent reading without
    modifying the cached contents.
    """
    path: Path
    encoding: str
    _contents: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Loads the file contents when the resource is initialized.
        """
        self._load()

    def _load(self) -> None:
        """
        Reads and caches the file contents using the configured encoding.
        """
        self._contents = self.path.read_text(encoding=self.encoding)


    def on_terminate(self) -> None:
        """
        Terminates the resource without writing to the source file.
        """
        # NOTE: This resource is designed to work as a cache.
        # The decision not to write file updates here is deliberate
        # in order to prevent accidental corruption of source data.
        pass

    def get_contents(self, newline: str | None = None) -> StringIO:
        """
        Return a fresh in-memory text stream.

        Args:
            newline: Controls universal newline handling for the stream.

        Returns:
            A fresh StringIO containing the cached file contents.
        """
        return StringIO(self._contents, newline=newline)    