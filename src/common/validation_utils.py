"""
Validation utilities for Shandalar Tools.

Provides reusable helpers for validating collection contents,
numeric constraints, and other common application validation
operations.
"""
from collections.abc import Iterable
from typing import Any

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def validate_collection_items(collection: Iterable[Any], expected_type: type) -> bool:
    """
    Validate that all items in a collection match the expected type.

    Args:
        collection: The collection whose items should be validated.
        expected_type: The required type for all collection items.

    Returns:
        True if all items match the expected type, otherwise False.
    """
    # NOTE:
    # Guard against programmer misuse. This helper validates the contents
    # of a collection, not whether the supplied value is a collection.
    assert isinstance(collection, Iterable), f"Attempted to validate non-iterable value of type {type(collection).__name__}."

    return all(isinstance(i, expected_type) for i in collection)

def validate_minimum(value: int, minimum: int, field_name: str) -> int:
    """
    Validate that a numeric value meets a minimum threshold.

    Raises a ValueError if the value is less than the specified minimum.
    Returns the original value unchanged to support validation within
    transform-style pipelines.

    Args:
        value: The numeric value to validate.
        minimum: The minimum allowed value.
        field_name: Human-readable field name used in the error message.

    Returns:
        The original validated value.

    Raises:
        ValueError: If value is less than minimum.
    """   
    if value < minimum:
        raise ValueError(f"{field_name} must be at least {minimum}.")
    return value