"""
Shared enums and type helpers for Shandalar Tools.

Defines application-wide enums, typed configuration helpers, and other
shared type structures used across multiple modules.
"""
from enum import Enum

class EncodingScanMode(Enum):
    AUTO = "auto"
    FAST = "fast"
    FULL = "full"

    def resolve(self, default_full_scan: bool = False) -> bool:
        """
        Resolve the encoding scan mode to a boolean full_scan value.

        Returns True for FULL, False for FAST, and the value of
        default_full_scan for AUTO.

        Args:
            default_full_scan: Fallback value used when mode is AUTO.
                Defaults to False.
        """        
        if self is EncodingScanMode.FULL:
            return True
        if self is EncodingScanMode.FAST:
            return False
        return default_full_scan
    
ENCODING_SCAN_VALID_VALUES = [m.name.lower() for m in EncodingScanMode]

class DeckType(Enum):
    """
    Supported deck formats reflected in output paths.
    """    
    FORGE = "forge"
    SHANDALAR = "shandalar"
    NONE = "none" 

    def inverse(self) -> "DeckType":
        """
        Return the opposite supported deck type.

        Returns:
            The opposite deck type.

        Raises:
            AssertionError: If the deck type is unsupported.
        """        
        if self is DeckType.FORGE:
            return DeckType.SHANDALAR
        if self is DeckType.SHANDALAR:
            return DeckType.FORGE

        raise AssertionError(f"Unhandled deck type: {self}")    