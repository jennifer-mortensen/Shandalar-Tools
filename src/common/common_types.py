"""
Shared enums and type helpers for Shandalar Tools.

Defines application-wide enums, typed configuration helpers, and other
shared type structures used across multiple modules.
"""
from dataclasses import dataclass
from enum import Enum

# ==============================
# DATACLASSES
# ==============================
@dataclass(frozen=True)
class CliArgument:
    """
    Definition of a command-line argument.

    Stores the short and long argument names along with any
    associated help or migration guidance text used for
    user-facing messages.
    """
    short_name: str
    long_name: str
    help_text: str

# ==============================
# ENUMS
# ==============================
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

        Returns:
            True if a full encoding scan should be performed,
            otherwise False.                
        """        
        if self is EncodingScanMode.FULL:
            return True
        if self is EncodingScanMode.FAST:
            return False
        return default_full_scan