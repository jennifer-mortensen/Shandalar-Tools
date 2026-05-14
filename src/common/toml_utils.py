"""
TOML parsing utilities for Shandalar Tools.

Provides helpers for validating and reading values from parsed TOML
data, with optional fallback behavior for missing or invalid keys
and sections.
"""
from common import common_utils
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
    item_type: type | None = None,
    transform: Callable | None = None,
    allow_fallback: bool = False,
    error_suffix: str = ""   
) -> None:
    """
    Set a field on a target object from a TOML section if the key is present and valid.

    Validates key presence, outer value type, optional collection item
    types, and optional transform logic before assigning the final value.

    Logs a warning and leaves the field unchanged if fallback is allowed
    and validation or transformation fails.

    Args:
        target: The object whose field will be set.
        field: The name of the field to set on the target.
        section: The TOML section dict to read from.
        key: The key to look up in the section.
        expected_type: The expected outer type of the value.
        item_type: Optional expected type for collection contents.
        transform: Optional callable to apply to the value before setting.
        allow_fallback: If True, preserves the existing field value when
            validation fails.
        error_suffix: Optional message appended to raised ValueErrors.
    """
    # Read and validate type
    value = section.get(key)    
    if value is None or not isinstance(value, expected_type):
        if allow_fallback:
            logger.warning("Key '%s' missing or invalid; using default", key)
            return
        raise ValueError(f"Mandatory key '{key}' is missing or invalid{error_suffix}")
    
    # Validate container contents
    if item_type is not None and not common_utils.validate_collection_items(collection=value, expected_type=item_type):
        raise ValueError(f"Type mismatch: Key '{key}' must contain only values of type {item_type.__name__}.")

    # Transform and validate value
    try:
        final_value = transform(value) if transform else value
    except ValueError as e:
        if allow_fallback:
            logger.warning("Key '%s' failed validation (%s); using default", key, e)
            return

        raise ValueError(f"Mandatory key '{key}' is missing or invalid{error_suffix}") from e

    # Assign value
    setattr(target, field, final_value)

def verify_section(data: dict, section_name: str, allow_fallback: bool = False, error_suffix: str = "") -> dict | None:
    """
    Retrieve a section from parsed TOML data by name.

    Logs a warning and returns None if fallback is allowed and the
    section is missing or invalid. Otherwise raises ValueError.

    Args:
        data: The top-level parsed TOML dict.
        section_name: The name of the section to retrieve.
    """    
    section = data.get(section_name)
    if section is None or not isinstance(section, dict):
        if allow_fallback:
            logger.warning("Section [%s] is missing or invalid; using default values", section_name)
            return
        raise ValueError(f"Mandatory section [{section_name}] is missing or invalid{error_suffix}")
    return section