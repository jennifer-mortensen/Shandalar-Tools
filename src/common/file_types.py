"""
File-related type definitions for Shandalar Tools.

Defines enums and other file handling types used for
encoding detection and file processing operations.
"""
from enum import Enum

class EncodingScanMode(Enum):
    """
    Controls how aggressively file encodings are detected.

    AUTO uses tool-defined defaults, FAST performs a partial
    scan for improved performance, and FULL scans the entire
    file for maximum reliability.
    """    
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

        Returns:
            True if a full encoding scan should be performed,
            otherwise False.                
        """        
        if self is EncodingScanMode.FULL:
            return True
        if self is EncodingScanMode.FAST:
            return False
        return default_full_scan
    
    @classmethod    
    def options(cls) -> list[str]:
        """
        Return the valid string values for encoding scan mode.
        """        
        return [e.value for e in cls]