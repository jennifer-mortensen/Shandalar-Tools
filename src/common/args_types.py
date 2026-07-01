"""
Argument-related type definitions for Shandalar Tools.

Defines dataclasses and other shared types used by CLI
argument definitions and parsing helpers.
"""
from dataclasses import dataclass

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