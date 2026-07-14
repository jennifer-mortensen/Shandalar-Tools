"""
Parsing utilities for Shandalar Tools.

Provides helpers for safely converting user and file input
into strongly typed values.
"""
from common import parse_const, string_utils

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def parse_bool(value: str) -> bool | None:
    """
    Attempt to parse a string as a boolean.

    Accepts any supported truthy or falsy value after
    sanitization.

    Args:
        value: The string to parse.

    Returns:
        The parsed boolean if successful; otherwise None.
    """
    value = string_utils.sanitize_string(value)
    return True if value in parse_const.TRUE_VALUES else False if value in parse_const.FALSE_VALUES else None

def parse_int(value: str) -> int | None:
    """
    Attempt to parse a string as an integer.

    Args:
        value: The string to parse.

    Returns:
        The parsed integer if successful, otherwise None.
    """
    # NOTE: 
    # Restricting to str is intentional. int("5.7") raises ValueError,
    # while int(5.7) truncates to 5 and would incorrectly return the value.      
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
    
def parse_positive_int(value: str) -> int | None:
    """
    Attempt to parse a string as a positive integer.

    Args:
        value: The string to parse.

    Returns:
        The parsed integer if successful; otherwise None.
    """
    try:
        number = int(value)
    except ValueError:
        return None

    return number if number > 0 else None    
