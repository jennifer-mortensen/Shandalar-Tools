"""
Helpers for working with collections and sequences.

Provides utilities for duplicate detection, sequence merging,
and collection conversion operations.
"""
from collections.abc import Iterable, Sequence
from typing import Any

# ==============================
# PUBLIC FUNCTIONS
# ==============================
def find_duplicates(sets: Iterable[set[Any]]) -> list[Any]:
    """
    Identify duplicate entries across multiple sets. Set contents must be hashable.

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