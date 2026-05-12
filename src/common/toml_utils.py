"""
TOML parsing utilities for Shandalar Tools.

Provides helpers for validating and reading values from parsed TOML
data, with optional fallback behavior for missing or invalid keys
and sections.
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
    transform: Callable | None = None,
    allow_fallback: bool = False,
    error_suffix: str = ""   
) -> None:
    """
    Set a field on a target object from a TOML section if the key is present and valid.

    Logs a warning and leaves the field unchanged if fallback is allowed
    and the value is missing, invalid, or fails transformation.

    Args:
        target: The object whose field will be set.
        field: The name of the field to set on the target.
        section: The TOML section dict to read from.
        key: The key to look up in the section.
        expected_type: The expected type of the value.
        transform: Optional callable to apply to the value before setting.
        allow_fallback: If True, preserves the existing field value when
            validation fails.
        error_suffix: Optional message appended to raised ValueErrors.
    """
    # Read and validate
    value = section.get(key)    
    if value is None or not isinstance(value, expected_type):
        if allow_fallback:
            logger.warning("Key %s missing or invalid; using default", key)
            return
        raise ValueError(f"Mandatory key [{key}] is missing{error_suffix}")

    # Transform and validate
    try:
        final_value = transform(value) if transform else value
    except Exception as e:
        if allow_fallback:
            logger.warning("Key %s failed validation (%s); using default", key, e)
            return

        raise ValueError(f"Mandatory key [{key}] is invalid{error_suffix}") from e

    # Assign value
    setattr(target, field, final_value)

def verify_section(data: dict, section_name: str, allow_fallback: bool = False, error_suffix: str = "") -> dict | None:
    """
    Retrieve a section from parsed TOML data by name.

    Logs a warning and returns None if fallback is allowed and the
    section is missing. Otherwise raises ValueError.

    Args:
        data: The top-level parsed TOML dict.
        section_name: The name of the section to retrieve.
    """    
    section = data.get(section_name)
    if section is None:
        if allow_fallback:
            logger.warning("Section [%s] is missing; using default values", section_name)
            return
        raise ValueError(f"Mandatory section [{section_name}] is missing{error_suffix}")
    return section