"""
TOML parsing utilities for Shandalar Tools.

Provides helpers for safely reading values from parsed TOML data,
with logging and fallback to defaults when keys or sections are missing.
"""
from typing import Callable
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def verify_and_set(
    target: object,
    field: str,
    section: dict,
    key: str,
    expected_type: type,
    transform: Callable | None = None
) -> None:
    """
    Set a field on a target object from a TOML section if the key is present and valid.

    Logs a warning and leaves the field unchanged if the key is missing or
    the value is not of the expected type.

    Args:
        target: The object whose field will be set.
        field: The name of the field to set on the target.
        section: The TOML section dict to read from.
        key: The key to look up in the section.
        expected_type: The expected type of the value.
        transform: Optional callable to apply to the value before setting.
    """    
    value = section.get(key)
    if value is None or not isinstance(value, expected_type):
        logger.warning("Key %s missing or invalid; using default", key)
    else:
        setattr(target, field, transform(value) if transform else value)

def verify_section(data: dict, section_name: str) -> dict | None:
    """
    Retrieve a section from parsed TOML data by name.

    Logs a warning and returns None if the section is missing.

    Args:
        data: The top-level parsed TOML dict.
        section_name: The name of the section to retrieve.
    """    
    section = data.get(section_name)
    if section is None:
         logger.warning("Section [%s] is missing; using default values", section_name)
    return section