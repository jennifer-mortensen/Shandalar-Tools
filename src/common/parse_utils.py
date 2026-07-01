"""
Parsing utilities for Shandalar Tools.

Provides helpers for safely converting user and file input
into strongly typed values.
"""

# ==============================
# PUBLIC FUNCTIONS
# ==============================
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
