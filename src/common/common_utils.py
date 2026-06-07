"""
Shared utility functions for Shandalar Tools.

Provides generic helpers for data manipulation, including sequence
deduplication, merging, and duplicate detection. Additional utilities
will be added here as needed.
"""
from collections.abc import Iterable, Sequence
from common import common_const
from typing import Any
import logging

logger = logging.getLogger(__name__)

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def filter_prefixes_from_set(items: set[str], prefixes: list[str]) -> set[str]:
    """
    Return a copy of a set with prefixed entries removed.

    Filters out any strings that begin with one of the specified
    prefixes. Prefix matching is case-sensitive and assumes any
    required normalization has already been applied.

    Args:
        items: The set of strings to filter.
        prefixes: Prefixes used to identify entries to remove.
    """    
    return {i for i in items if not has_any_prefix(i, prefixes)}

def find_duplicates(sets: Iterable[set[Any]]) -> list[Any]:
    """
    Identify duplicate entries across multiple sets. Set data must be hashable.

    Returns a sorted list of any values that appear in more than one set.
    It is recommended to sanitize sets before passing them for consistent comparison.

    Args:
        sets: An iterable of sets to check for duplicates across.
    """ 
    seen: set[Any] = set()
    duplicates: set[Any] = set()

    for s in sets:
        for item in s:
            if item in seen:
                duplicates.add(item)
            else:
                seen.add(item)

    return sorted(duplicates)

def has_any_prefix(line: str, prefixes: list[str]) -> bool:
    """
    Check if a string starts with any of the given prefixes.

    Args:
        line: The string to check.
        prefixes: A list of prefixes to test against.        
    """    
    return any(line.startswith(p) for p in prefixes)

def is_comment(line: str, prefixes: list[str] | None = None) -> bool:
    """
    Check whether a string should be treated as a comment line.
    """
    prefixes = prefixes or [common_const.COMMENT_PREFIX]
    return has_any_prefix(line.strip(), prefixes)


def list_to_lookup(items: list[str]) -> set[str]:
    """
    Convert a list of user-provided strings into a sanitized lookup set.

    Sanitizes entries for consistent case-insensitive comparison and
    removes any entries that begin with the configured comment prefix
    after sanitization. Intended for normalizing user-authored TOML
    list fields into lookup sets.

    Args:
        items: The raw list of strings to normalize.
    """    
    lookup: set[str] = sanitize_set(set(items))
    lookup = filter_prefixes_from_set(lookup, [common_const.COMMENT_PREFIX])
    return lookup

def merge_and_dedupe_sequences(seq_1: Sequence[Any], seq_2: Sequence[Any]) -> list[Any]:
    """
    Merge two sequences into a single deduplicated list.
    Sequences must contain hashable data.

    Preserves the order of seq_1, then appends any items from seq_2
    that are not already present. Does not sanitize input.

    Args:
        seq_1: The primary sequence. Order is preserved.
        seq_2: The secondary sequence. Items not in seq_1 are appended.
    """    
    merged: list[Any] = list(seq_1)
    seen: set[Any] = set(merged)

    for item in seq_2:
        if item not in seen:
            merged.append(item)
            seen.add(item)

    return merged

def parse_int(val: str) -> int | None:
    """
    Attempt to parse a string as an integer.

    Args:
        val: The string to parse.

    Returns:
        The parsed integer if successful, otherwise None.
    """
    # NOTE: 
    # Restricting to str is intentional. int("5.7") raises ValueError,
    # while int(5.7) truncates to 5 and would incorrectly return the value.      
    try:
        return int(val)
    except (TypeError, ValueError):
        return None

def pluralize(quantity: int, singular: str, plural: str) -> str:
    """
    Return the singular or plural form of a word based on quantity.

    Args:
        quantity: The quantity used to determine plurality.
        singular: The singular form to return when quantity is 1.
        plural: The plural form to return for all other quantities.
    """    
    return singular if quantity == 1 else plural

def sanitize_set(items: set[str]) -> set[str]:
    """
    Sanitize a set of strings for consistent comparison.

    Applies sanitize_string to each item in the set.

    Args:
        items: The set of strings to sanitize.
    """    
    return {sanitize_string(i) for i in items}

def sanitize_string(string: str) -> str:
    """
    Sanitize a string for consistent comparison.

    Strips leading and trailing whitespace and converts to lowercase.

    Args:
        string: The string to sanitize.
    """    
    return string.strip().lower()

def to_list(value: str | Iterable[str] | None) -> list[str]:
    """
    Convert a string, iterable, or None into a list of strings.

    Returns an empty list for None, wraps a bare string in a list,
    and converts any other iterable to a list.

    Args:
        value: The value to convert. Can be None, a string, or an iterable of strings.
    """      
    if value is None:
        return []
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return list(value)
    return [value]

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