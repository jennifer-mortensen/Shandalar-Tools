"""
Shared resource types for Shandalar Tools.

Defines the managed resource contract and resource identifiers
used by the runtime resource management system.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

# ==============================
# CLASSES
# ==============================
class ManagedResource(ABC):
    @abstractmethod
    def on_terminate(self) -> None:
        """
        Signals that the resource is being terminated, allowing
        the resource to perform any required shutdown logic.
        """
        pass

@dataclass(frozen=True)
class ResourceKey:
    """
    Identifies a managed resource in the runtime registry.

    A resource key consists of the resource's concrete type and,
    when applicable, its canonical backing path.
    """    
    resource_type: type
    path: Path | None = None